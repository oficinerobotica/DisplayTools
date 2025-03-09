import FreeCAD
import FreeCADGui
import pivy.coin as coin

import create_scene_config
from Utils.resource_utils import iconPath

"""
class GeometryObserver:
    
    #Class to observe geometry changes in the 3D viewport.
    #Usage:
    #  observer = GeometryObserver()
      
    #To stop observing later:
    #  observer.detach()
    
    def __init__(self, callback):
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.scene_graph = self.view.getSceneGraph()
        self.sensor = coin.SoNodeSensor(self.on_geometry_change, self.scene_graph)
        self.sensor.attach(self.scene_graph)
        self.callback = callback  # Store the callback from ViewProviderDynamicGrid

    def on_geometry_change(self, node, sensor):
        if self.callback:
            self.callback()

    def detach(self):
        #Detach the observer to stop tracking geometry changes.
        if self.sensor:
            self.sensor.detach()
            self.scene_graph = None
"""

class GeometryObserver:
    def __init__(self, callback):
        self.callback = callback
        self.doc = FreeCAD.ActiveDocument
        if self.doc is None:
            print("No active document; observer not attached.")
            return
        FreeCAD.addDocumentObserver(self)
        print("GeometryObserver attached via FreeCAD document observer.")

    def relevant_object(self, obj):
        """Check if the object belongs to the document we're observing."""
        return self.doc and obj.Document == self.doc

    def slotCreatedObject(self, obj):
        if not self.relevant_object(obj):
            return
        print(f"Object created in {self.doc.Name}: {obj.Name}")
        if hasattr(obj, "Shape") and obj.ViewObject.isVisible():
            if self.callback:
                self.callback()

    def slotDeletedObject(self, obj):
        if not self.relevant_object(obj):
            return
        print(f"Object deleted from {self.doc.Name}: {obj.Name}")
        if hasattr(obj, "Shape") and obj.ViewObject.isVisible():
            if self.callback:
                self.callback()

    def slotChangedObject(self, obj, prop):
        if not self.relevant_object(obj):
            return
        print(f"Object {obj.Name} in {self.doc.Name} changed property: {prop}")
        if prop == "Shape" and obj.ViewObject.isVisible():
            if self.callback:
                self.callback()
        elif prop == "Placement" and obj.ViewObject.isVisible() and hasattr(obj, "Shape"):
            if self.callback:
                self.callback()
        elif prop == "Visibility" and hasattr(obj, "Shape"):
            if self.callback:
                self.callback()

    def detach(self):
        if hasattr(FreeCAD, "removeDocumentObserver"):
            FreeCAD.removeDocumentObserver(self)
            self.doc = None
            print("GeometryObserver detached.")

    def __del__(self):
        self.detach()


class DynamicGrid():
    def __init__(self, obj):
        obj.Proxy = self
        self.setProperties(obj)
        
    def setProperties(self, obj):
        pl = obj.PropertiesList
        if 'Placement' not in pl:
            obj.addProperty("App::PropertyPlacement", "Placement", "Base", "Defines the placement of the grid").Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), FreeCAD.Rotation(0, 0, 0))
        if 'Color' not in pl:
            obj.addProperty("App::PropertyColor", "Color", "Grid", "Grid color").Color = (0.5, 0.5, 0.5)
        if 'Size' not in pl:
            obj.addProperty("App::PropertyIntegerConstraint", "Size", "Grid", "Grid size").Size = (100, 1, 10**6, 5)
        if 'Spacing' not in pl:
            obj.addProperty("App::PropertyIntegerConstraint", "Spacing", "Grid", "Grid spacing").Spacing = (10, 1, 10**6, 5)
        if 'Dynamic' not in pl:
            obj.addProperty("App::PropertyBool", "Dynamic", "Grid", "Update grid position based on the 3d scene").Dynamic = True
    def onDocumentRestored(self, obj):
        self.setProperties(obj)
        
    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def execute(self, ob):
        pass

class LowestVisibleZ:
    def __init__(self, doc=None):
        self.doc = doc if doc else FreeCAD.ActiveDocument
        if not self.doc:
            raise ValueError("No active FreeCAD document found.")

    def get_visible_objects(self):
        """Return a list of objects that are visible in the scene."""
        return [obj for obj in self.doc.Objects if obj.ViewObject.isVisible()]

    def get_objects_with_volume(self):
        """Return a list of visible objects that have a valid shape and volume."""
        visible_objects = self.get_visible_objects()
        solids = []
        for obj in visible_objects:
            try:
                shape = obj.Shape
                if shape.isValid() and shape.Volume > 0:
                    solids.append(obj)
                else:
                    print(f"Skipping {obj.Name}: No volume or invalid shape.")
            except (AttributeError, RuntimeError):
                print(f"Skipping {obj.Name}: No shape or invalid geometry.")
        return solids

    def return_lowest_z(self):
        """Find the lowest Z value among visible objects with volume."""
        solids = self.get_objects_with_volume()
        if not solids:
            return None  # No valid solids found
        min_z = None
        for obj in solids:
            bbox = obj.Shape.BoundBox
            z_min = bbox.ZMin
            print(f"{obj.Name} (Solid) ZMin: {z_min}")
            if min_z is None or z_min < min_z:
                min_z = z_min
        return min_z

class ViewProviderDynamicGrid():
    def __init__(self, vobj):
        vobj.Proxy = self
        self.setProperties(vobj)

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        sceneGraph = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        
        self.geometry_observer = None
        self.switch = coin.SoSwitch()  # Node that controls visibility
        self.separator = coin.SoSeparator()  # Container for transform, material, and grid
        self.transform = coin.SoTransform()
        self.material = coin.SoMaterial()
        self.actualGrid = self.createGrid()
        
        # Build the scene graph for the grid
        self.separator.addChild(self.transform)
        self.separator.addChild(self.actualGrid)
        self.switch.addChild(self.separator)     
        # Add the switch to the scene graph
        sceneGraph.addChild(self.switch)
        self.place_grid_in_tree()
        
        vobj.addDisplayMode(self.switch, "DynamicGrid")
        self.updateColor()         # Apply initial color
        self.updateGridVisibility()  # Apply initial visibility state
        self.updateGridLocation()
        self.updateDynamicLocation()

    def setProperties(self, vobj):
        pl = vobj.PropertiesList
        # No extra properties needed here

    def createGrid(self):
        """Generate an XY plane grid with red X-axis and green Y-axis, using the grid color from the property view."""
        grid_node = coin.SoSeparator()  # Main container for the grid

        # Ensure correct normal orientation
        #shape_hints = coin.SoShapeHints()
        #shape_hints.vertexOrdering = coin.SoShapeHints.COUNTERCLOCKWISE  # Correct face normal
        #shape_hints.shapeType = coin.SoShapeHints.SOLID  # Treat as a solid surface
        #shape_hints.faceType = coin.SoShapeHints.FRONT  # Render only front-facing side


        # Get grid color from the property view
        self.grid_material = coin.SoMaterial()  # Store this reference
        grid_color = self.Object.Color
        self.grid_material.diffuseColor = coin.SbColor(grid_color[0], grid_color[1], grid_color[2])

        # === GRID FACE (for one-sided rendering) ===
        coords = coin.SoCoordinate3()
        faceSet = coin.SoIndexedFaceSet()


        # Define materials for the X and Y axes
        materialRed = coin.SoMaterial()
        materialRed.diffuseColor = coin.SbColor(1, 0, 0)  # Red for X-axis

        materialGreen = coin.SoMaterial()
        materialGreen.diffuseColor = coin.SbColor(0, 1, 0)  # Green for Y-axis

        size = self.Object.Size
        spacing = self.Object.Spacing
        half_size = size // 2  # Keep grid centered

        print(f"Creating grid: Size = {size}, Spacing = {spacing}, Grid Color = {grid_color}")

        # === GRID LINES ===
        grid_coords = coin.SoCoordinate3()
        grid_lines = coin.SoIndexedLineSet()
        points = []
        indices = []

        for y in range(-half_size, half_size + spacing, spacing):
            start_index = len(points)
            points.append(coin.SbVec3f(-half_size, y, 0))  # Left
            points.append(coin.SbVec3f(half_size, y, 0))   # Right
            indices.extend([start_index, start_index + 1, -1])  # -1 ends each line

        for x in range(-half_size, half_size + spacing, spacing):
            start_index = len(points)
            points.append(coin.SbVec3f(x, -half_size, 0))  # Bottom
            points.append(coin.SbVec3f(x, half_size, 0))   # Top
            indices.extend([start_index, start_index + 1, -1])  # -1 ends each line

        grid_coords.point.setValues(0, len(points), points)
        grid_lines.coordIndex.setValues(0, len(indices), indices)

        # === GRID NODE ===
        gridSeparator = coin.SoSeparator()
        #gridSeparator.addChild(shape_hints)
        gridSeparator.addChild(self.grid_material)
        gridSeparator.addChild(grid_coords)
        gridSeparator.addChild(grid_lines)
        gridSeparator.addChild(faceSet)

        # === X-AXIS ===
        x_axis_coords = coin.SoCoordinate3()
        x_axis_coords.point.setValues(0, 2, [
            coin.SbVec3f(-half_size, 0, 0),
            coin.SbVec3f(half_size, 0, 0)
        ])
        x_axis_lines = coin.SoIndexedLineSet()
        x_axis_lines.coordIndex.setValues(0, 3, [0, 1, -1])

        x_axis_style = coin.SoDrawStyle()
        x_axis_style.lineWidth = 2  # Slightly thicker X-axis

        x_axis_node = coin.SoSeparator()
        x_axis_node.addChild(x_axis_style)  # Apply line width
        x_axis_node.addChild(materialRed)
        x_axis_node.addChild(x_axis_coords)
        x_axis_node.addChild(x_axis_lines)

        # === Y-AXIS ===
        y_axis_coords = coin.SoCoordinate3()
        y_axis_coords.point.setValues(0, 2, [
            coin.SbVec3f(0, -half_size, 0),
            coin.SbVec3f(0, half_size, 0)
        ])
        y_axis_lines = coin.SoIndexedLineSet()
        y_axis_lines.coordIndex.setValues(0, 3, [0, 1, -1])

        y_axis_style = coin.SoDrawStyle()
        y_axis_style.lineWidth = 2  # Slightly thicker Y-axis

        y_axis_node = coin.SoSeparator()
        y_axis_node.addChild(y_axis_style)  # Apply line width
        y_axis_node.addChild(materialGreen)
        y_axis_node.addChild(y_axis_coords)
        y_axis_node.addChild(y_axis_lines)

        # === ENSURE X & Y AXES ARE DRAWN LAST BUT RESPECT DEPTH ===
        grid_node.addChild(gridSeparator)  # Add the grid first
        grid_node.addChild(x_axis_node)    # Add the X-axis second
        grid_node.addChild(y_axis_node)    # Add the Y-axis last

        return grid_node

    def getDisplayModes(self, obj):
        return ["DynamicGrid"]

    def getDefaultDisplayMode(self):
        return "DynamicGrid"

    def updateData(self, fp, prop):
        print(f"updateData: Property '{prop}' changed")
        if prop == 'Placement':
            self.updateGridLocation()
        elif prop == 'Color':
            print("Updating color...")
            self.updateColor()
        elif prop in ['Size', 'Spacing']:
            print("Updating grid due to Size or Spacing change...")
            # Remove the old grid (assuming it is the third child: index 2)
            while self.separator.getNumChildren() > 1:  # Remove all grid instances
                self.separator.removeChild(self.separator.getChild(1))

            # Create new grid and add it
            newGrid = self.createGrid()
            self.separator.addChild(newGrid)
        elif prop == 'Dynamic':
            self.updateDynamicLocation()
            FreeCADGui.updateGui()

    def onChanged(self, vp, prop):
        if prop == "Visibility":
            print(f"  Visibility changed: {vp.Visibility}")
            self.updateGridVisibility()

    def onDelete(self, obj, subelements):
        """Remove the grid from the viewport when the object is deleted."""
        print("onDelete called: Removing grid from scene graph")
        sceneGraph = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        if self.switch and sceneGraph:
            try:
                sceneGraph.removeChild(self.switch)
                print("Removed self.switch from sceneGraph")
            except Exception as e:
                print("Error removing switch:", e)
        if self.geometry_observer: # Detach observer when grid is deleted
            self.geometry_observer.detach()
            self.geometry_observer = None # Remove reference
        self.switch = None
        self.separator = None
        return True

    def execute(self, obj):
        print(f"execute: Placement = {obj.Placement}")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
    
    def place_grid_in_tree(self):
        doc = FreeCAD.ActiveDocument
        scene_folder = None
        for obj in doc.Objects:
            if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "type") and  obj.Proxy.type == 'SceneConfiguration':
                scene_folder = obj
                break
        if scene_folder:
            scene_folder.addObject(self.Object)
            
        else:
            scene_folder = create_scene_config.createSceneFolder()
            scene_folder.addObject(self.Object)


    def updateGridVisibility(self):
        print(f"updateGridVisibility: Visibility = {self.ViewObject.Visibility}")
        if self.ViewObject.Visibility:
            print("Setting switch to SHOW the grid")
            self.switch.whichChild = coin.SO_SWITCH_ALL
        else:
            print("Setting switch to HIDE the grid")
            self.switch.whichChild = coin.SO_SWITCH_NONE
        FreeCADGui.updateGui()

    def updateColor(self):
        """Update the grid material based on the selected Color property."""
        grid_color = self.Object.Color  # Get new color from property
        print(f"updateColor: Applying new grid color {grid_color}")

        # Update the material color
        self.grid_material.diffuseColor.setValue(grid_color[0], grid_color[1], grid_color[2])
        # Force FreeCAD to refresh the viewport
        FreeCADGui.updateGui()

    def updateGridLocation(self):
        """Update grid position based on Placement property."""
        placement = self.Object.Placement  # Now a FreeCAD.Placement object
        coinVector = coin.SbVec3f(placement.Base.x, placement.Base.y, placement.Base.z)  # Extract position
        self.transform.translation.setValue(coinVector)
        
    def updateDynamicLocation(self):
        """Activates or deactivates GeometryObserver based on 'Dynamic' property."""
        print(f"updateDynamicLocation: Dynamic property is {self.Object.Dynamic}")
        if self.Object.Dynamic:
            if not hasattr(self, "geometry_observer") or self.geometry_observer is None:
                self.geometry_observer = GeometryObserver(self.onSceneGeometryChanged)
                print("GeometryObserver initialized.")
            else:
                print("GeometryObserver is already active.")
        else:
            if hasattr(self, "geometry_observer") and self.geometry_observer is not None:
                self.geometry_observer.detach()
                self.geometry_observer = None
                print("GeometryObserver detached.")
        FreeCADGui.updateGui()

            

    def onSceneGeometryChanged(self):
        """Handle scene geometry changes by updating the grid's Z position."""
        if self.Object.Dynamic:  # Only update if the grid is dynamic
            min_z_calculator = LowestVisibleZ()
            min_z = min_z_calculator.return_lowest_z()
            if min_z is not None:
                print(f"Updating grid Z location to: {min_z}")
                self.updateGridZLocation(min_z)
            else:
                print("No valid solids found, cannot update grid Z.")

    def updateGridZLocation(self, z_value):
        """Update the grid's Z position to the given z_value."""
        placement = self.Object.Placement
        new_base = FreeCAD.Vector(placement.Base.x, placement.Base.y, z_value)
        self.Object.Placement = FreeCAD.Placement(new_base, placement.Rotation)
        print(f"Grid Z position updated to {z_value}")

    def getIcon(self):
        return iconPath('Grid.svg')
        

def createDynamicGrid():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "DynamicGrid")
    grid = DynamicGrid(obj)
    ViewProviderDynamicGrid(obj.ViewObject)

if __name__ == "__main__":
    createDynamicGrid()

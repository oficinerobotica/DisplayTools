import FreeCAD
import FreeCADGui
from pivy import coin

import create_scene_config

class UniversalLight():
    def __init__(self, obj):
        obj.Proxy = self
        self.setProperties(obj)
    def setProperties(self, obj):
        pl = obj.PropertiesList

        if not 'Color' in pl:
            obj.addProperty("App::PropertyColor", "Color", "Light", 
                            "The color of the light").Color = (1.0, 0.94, 0.91)
        
        if not 'Intensity' in pl:
            obj.addProperty("App::PropertyFloatConstraint", "Intensity", "Light", 
                            "The intensity of the light").Intensity = (1.0, 0.0, 1.0, 0.1)
            
        obj.addProperty("App::PropertyBool", "ShowManipulator", "Manipulator", "Show Manipulator Geometry").ShowManipulator = True
        obj.addProperty("App::PropertyIntegerConstraint", "Scale", "Manipulator", "Uniform scale factor for the manipulator").Scale = (5, 5, 200, 5)  # Default: 5, Min: 5, Max: 100, Step: 5
        self.type = 'coinLight'

    def onDocumentRestored(self, obj):
        self.setProperties(obj)

    def __getstate__(self):
        return None
 
    def __setstate__(self,state):
        return None

    def execute(self, ob):
        pass


class ViewProviderUniversalLight:
    def __init__(self, vobj):
        vobj.Proxy = self
        self.setProperties(vobj)
 
    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        
        sceneGraph = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        
        
        self.coinLight = self.createLightInstance()
        self.coinLightManip = self.createLightManipInstance()

        self.scale_node = coin.SoScale()
        self.scale_node.scaleFactor.setValue(1.0, 1.0, 1.0)
        
        # Set up the switch to choose between light and manipulator
        self.switch = coin.SoSwitch()
        #self.switch.addChild(self.coinLight)  # Index 0: original light
        scaled_manip_separator = coin.SoSeparator()
        scaled_manip_separator.addChild(self.scale_node)
        scaled_manip_separator.addChild(self.coinLightManip)
        self.switch.addChild(scaled_manip_separator)  # Index 1: scaled manipulator
        
        sceneGraph.insertChild(self.coinLight, 2)
        sceneGraph.insertChild(self.switch, 1)
        vobj.addDisplayMode(self.switch, "UniversalLight")
        self.place_light_in_tree()

        # Connect fields bidirectionally
        
        self.coinLightManip.color.connectFrom(self.coinLight.color)
        self.coinLight.color.connectFrom(self.coinLightManip.color)
        self.coinLightManip.intensity.connectFrom(self.coinLight.intensity)
        self.coinLight.intensity.connectFrom(self.coinLightManip.intensity)
        if self.coinLight.getField('location') is not None:
            self.coinLightManip.location.connectFrom(self.coinLight.location)
            self.coinLight.location.connectFrom(self.coinLightManip.location)
        if self.coinLight.getField('direction') is not None and self.coinLightManip.getField('direction') is not None:
            #self.coinLightManip.direction.connectFrom(self.coinLight.direction)
            self.coinLight.direction.connectFrom(self.coinLightManip.direction)
        if self.coinLight.getField('cutOffAngle') is not None and self.coinLightManip.getField('cutOffAngle') is not None:
            self.coinLightManip.cutOffAngle.connectFrom(self.coinLight.cutOffAngle)
            self.coinLight.cutOffAngle.connectFrom(self.coinLightManip.cutOffAngle)
        # Set up field sensors
        self.setupFieldSensors(self.coinLight)
        
        self.updateLightVisibility()
        self.updateDirection()
        self.updateColor()
        self.updateIntensity()
        self.updateScaleManipulator()
        self.updateManipulatorVisibility()
        
    def setProperties(self, vobj):
        pl = vobj.PropertiesList
    
    def createLightInstance(self):
        raise NotImplementedError()
    
    def createLightManipInstance(self):
        raise NotImplementedError()
    
    def getDisplayModes(self,obj):
        '''Return a list of display modes.'''
        return ["UniversalLight"]
    
    def getDefaultDisplayMode(self):
        '''Return the name of the default display mode. It must be defined in getDisplayModes.'''
        return "UniversalLight"
    
    def updateData(self, fp, prop):
        if prop in ['HorizontalRotation', 'VerticalRotation']:
            self.updateDirection()
        elif prop == 'Color':
            self.updateColor()
        elif prop == 'Intensity':
            self.updateIntensity()
        elif prop == 'Location':
           self.updateLocation()
        elif prop == 'Direction':
            self.updateDirection()
        elif prop == 'CutOffAngle':
            self.updateCutOffAngle()
        elif prop == 'Scale':
            self.updateScaleManipulator()
        elif prop == 'ShowManipulator':
            self.updateManipulatorVisibility()

    def onChanged(self, vp, prop):
        if prop == 'Visibility':
            self.updateLightVisibility()

    def onDelete(self, vobj, subelements):
        sceneGraph = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        # Detach the location sensor if it exists
        for sensorName in ['locationSensor', 'directionSensor', 'cutOffAngleSensor']:
            if hasattr(self, sensorName) and getattr(self, sensorName) is not None:
                getattr(self, sensorName).detach()
        if hasattr(self, 'coinLight'):
            sceneGraph.removeChild(self.coinLight)
        
        # Remove the switch node from the scene graph if it exists
        if hasattr(self, 'switch') and self.switch is not None:
            if self.switch in sceneGraph.getChildren():
                sceneGraph.removeChild(self.switch)
    
        # Allow the deletion to proceed
        return True

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None
    
    def place_light_in_tree(self):
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


    

    def setupFieldSensors(self, lightNode):
        # Dictionary mapping Coin3D fields to (FreeCAD property name, callback function)
        fieldSensorMappings = {
            'location': ('Location', self.locationChanged),
            'direction': ('Direction', self.directionChanged),
            'cutOffAngle': ('CutOffAngle', self.cutOffAngleChanged),
            # Add shadow-related fields if supported, e.g., 'shadowIntensity': ('ShadowIntensity', self.shadowIntensityChanged)
        }
        
        # Iterate over possible fields
        for fieldName, (propName, callback) in fieldSensorMappings.items():
            field = lightNode.getField(fieldName)
            # Check if the field exists in the light node and the property exists in the FreeCAD object
            if field is not None and hasattr(self.Object, propName):
                sensor = coin.SoFieldSensor(callback, self)
                sensor.attach(field)
                # Store the sensor as an attribute for later cleanup
                setattr(self, f"{fieldName}Sensor", sensor)

    def locationChanged(self, data, sensor):
        view_provider = data  # 'self' is passed as data
        new_location = view_provider.coinLight.location.getValue()
        current_location = view_provider.Object.Location
        new_vector = FreeCAD.Vector(new_location[0], new_location[1], new_location[2])
        if current_location != new_vector:
            view_provider.Object.Location = new_vector

    def directionChanged(self, data, sensor):
        view_provider = data
        new_direction = view_provider.coinLight.direction.getValue()
        current_direction = view_provider.Object.Direction
        new_vector = FreeCAD.Vector(new_direction[0], new_direction[1], new_direction[2])
        if current_direction != new_vector:
            view_provider.Object.Direction = new_vector

    def cutOffAngleChanged(self, data, sensor):
        """Callback for when the cut-off angle is changed via the manipulator"""
        try:
            view_provider = data  # 'self' is passed as data
            new_angle_radians = view_provider.coinLight.cutOffAngle.getValue()  # Coin3D value in radians
            new_angle_degrees = new_angle_radians * (180.0 / 3.141592653589793)  # Convert to degrees
            new_angle_degrees = max(0.0, min(180.0, new_angle_degrees))
            
            # Get the current angle value in degrees (strip the units)
            current_angle_str = str(view_provider.Object.CutOffAngle)
            current_angle = float(current_angle_str.split()[0])  # Get the numeric part only
            
            if abs(current_angle - new_angle_degrees) > 0.001:  # Small tolerance for floating-point comparison
                view_provider.Object.CutOffAngle = new_angle_degrees

        except Exception as e:
            print(f"Error in cutOffAngle callback: {e}")

    def updateLocation(self):
        if hasattr(self.Object, 'Location'):
            location = self.Object.Location
            coinVector = coin.SbVec3f(location.x, location.y, location.z)
            self.coinLight.location.setValue(coinVector)
    
    
    def updateDirection(self):
        if hasattr(self.Object, 'Direction'):
            direction = self.Object.Direction
            coinVector = coin.SbVec3f(direction.x, direction.y, direction.z)
            if self.coinLight.getField('direction') is not None:
                self.coinLight.direction.setValue(coinVector)

    
    def updateCutOffAngle(self):
        """Updates the cut-off angle in the Coin3D scene graph"""
        try:
            if hasattr(self.Object, 'CutOffAngle'):
                # Get the angle value in degrees (strip the units)
                angle_str = str(self.Object.CutOffAngle)
                angle_degrees = float(angle_str.split()[0])  # Get the numeric part only
                
                # Clamp the angle between 0 and 180 degrees
                angle_degrees = max(0.0, min(180.0, angle_degrees))
                
                # Convert to radians
                angle_radians = float(angle_degrees * (3.141592653589793 / 180.0))
                
                if self.coinLight.getField('cutOffAngle') is not None:
                    self.coinLight.cutOffAngle.setValue(angle_radians)
                    
        except Exception as e:
            print(f"Error updating cut-off angle: {e}")


    def updateManipulatorVisibility(self):
        if hasattr(self, 'switch'):
            show_manip = self.Object.ShowManipulator
            if show_manip:
                self.switch.whichChild.setValue(0)      # Show manipulator
                print("Manipulator on:", self.coinLightManip.on.getValue())
            else:
                self.switch.whichChild.setValue(coin.SO_SWITCH_NONE)  # -1 means no children are rendered
                print("Light on:", self.coinLight.on.getValue())

    def updateColor(self):
        color = self.Object.Color

        r = color[0]
        g = color[1]
        b = color[2]

        coinColor = coin.SbColor(r, g, b)

        self.coinLight.color.setValue(coinColor)
        #self.material.diffuseColor.setValue(coinColor)

    def updateIntensity(self):
        self.coinLight.intensity.setValue(self.Object.Intensity)

    def updateGeometryLocation(self, coinVector):
        self.transform.translation.setValue(coinVector)


    def updateLightVisibility(self):
        visible = self.ViewObject.Visibility
        self.coinLight.on.setValue(visible)
        self.coinLightManip.on.setValue(visible)

    def updateScaleManipulator(self):
        scale_value = self.Object.Scale / 5.0
        self.scale_node.scaleFactor.setValue(scale_value, scale_value, scale_value)
        print(f"Scale Manipulator called! Scale value: {scale_value}")


def createUniversalLight():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "DirectionalLight")
    light = UniversalLight(obj)
    ViewProviderUniversalLight(obj.ViewObject)

    return obj

if __name__ == "__main__":
    createUniversalLight()

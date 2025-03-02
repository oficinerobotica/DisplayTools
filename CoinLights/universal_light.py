import FreeCAD
import FreeCADGui
from pivy import coin

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
        
        
        self.switch = coin.SoSwitch()
        self.separator = coin.SoSeparator()
        self.transform = coin.SoTransform()
        self.material = coin.SoMaterial()
        self.scale = coin.SoScale()
        self.coinLight = self.createLightInstance()
        
        self.separator.addChild(self.scale)
        self.separator.addChild(self.transform)
        self.separator.addChild(self.material)
        

        sceneGraph.insertChild(self.coinLight, 1)
        self.switch.addChild(self.separator)
        vobj.addDisplayMode(self.switch, "UniversalLight")

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
    
    def create_nodes(self):
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
        elif prop == 'Scale':
            self.updateScaleManipulator()
        elif prop == 'ShowManipulator':
            self.updateManipulatorVisibility()

    def onChanged(self, vp, prop):
        if prop == 'Visibility':
            self.updateLightVisibility()
        """
        elif prop == 'ShowManipulator':
            self.ViewObject.Proxy.showManipulator()
        if prop == "Scale":  # If Scale is changed, update manipulator
            self.ViewObject.Proxy.scaleManipulator()
"""
    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def updateLocation(self):
        if hasattr(self.Object, 'Location'):
            location = self.Object.Location
            coinVector = coin.SbVec3f(location.x, location.y, location.z)
            self.coinLight.location.setValue(coinVector)
            self.updateGeometryLocation(coinVector)
    
    def updateDirection(self):
        if hasattr(self.Object, 'Direction'):
            direction = self.Object.Direction
            coinVector = coin.SbVec3f(direction.x, direction.y, direction.z)
            self.coinLight.direction.setValue(coinVector)
            #self.updateGeometryDirection(coinVector)
    
    def updateLightVisibility(self):
        self.coinLight.on.setValue(self.ViewObject.Visibility)

    def updateColor(self):
        color = self.Object.Color

        r = color[0]
        g = color[1]
        b = color[2]

        coinColor = coin.SbColor(r, g, b)

        self.coinLight.color.setValue(coinColor)
        self.material.diffuseColor.setValue(coinColor)

    def updateIntensity(self):
        self.coinLight.intensity.setValue(self.Object.Intensity)

    def updateGeometryLocation(self, coinVector):
        self.transform.translation.setValue(coinVector)

    def updateManipulatorVisibility(self):
        if self.Object.ShowManipulator: # Access the 'ShowManipulator' property from the Feature object
            self.switch.whichChild = 0   # Show manipulator (index 0 of switch's children)
            print("Manipulator is visible")
        else:
            self.switch.whichChild = coin.SO_SWITCH_NONE # hide manipulator 
            print("Manipulator is hidden")

    def updateScaleManipulator(self):
        scale_value = self.Object.Scale
        print(f"Scale Manipulator called! Scale value: {scale_value}") 
        self.scale.scaleFactor.setValue(scale_value, scale_value, scale_value)


def createUniversalLight():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "DirectionalLight")
    light = UniversalLight(obj)
    ViewProviderUniversalLight(obj.ViewObject)

    return obj

if __name__ == "__main__":
    createUniversalLight()
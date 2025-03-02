import FreeCAD
import FreeCADGui
from pivy import coin

import CoinLights.universal_light as light
from Utils import *
from Utils.resource_utils import iconPath

class SpotLight(light.Light):
    def __init__(self, obj):
        super().__init__(obj)
    
    def setProperties(self, obj):
        super().setProperties(obj)

        pl = obj.PropertiesList

        if not 'Location' in pl:
            obj.addProperty("App::PropertyVector", "Location", "Light",
                            "The position of the light in the scene.").Location = FreeCAD.Vector(0, -1, 0)
            
        if not 'Direction' in pl:
            obj.addProperty("App::PropertyVector", "Direction", "Light",
                            "The positiondirection of the light in the scene.").Direction = FreeCAD.Vector(1, 0, 0)
            
        obj.addProperty("App::PropertyAngle", "CutOffAngle", "SpotLight", "Cut-off angle").CutOffAngle = 45.0 
        obj.addProperty("App::PropertyFloat", "DropOffRate", "SpotLight", "Drop-off rate").DropOffRate = 0.2
        obj.addProperty("App::PropertyFloat", "LightIntensity", "SpotLight", "Intensity").LightIntensity = 0.8
        obj.addProperty("App::PropertyBool", "ShowManipulator", "SpotLight", "Show Manipulator Geometry").ShowManipulator = True
        
        self.type = 'SpotLight'

class ViewProviderSpotLight(light.ViewProviderLight):
    def __init__(self, vobj):
        super().__init__(vobj)
    
    def setProperties(self, vobj):
        super().setProperties(vobj)

    def attach(self, vobj):
        super().attach(vobj)

        self.updateLocation()

    def createLightInstance(self):
        return coin.SoSpotLight()
    
    def createSpotLightManipInstance(self):
        return coin.SospotLightManip()
    
    def createSpotLightSeparator(self):
        return coin.SoSeparator()
    
    def createSpotLightSwitch(self):
        return coin.SoSwitch()  # For toggling manipulator visibility

     # Build the scene graph structure.
    def createSpotLightSG(self): 
        self.separator.addChild(self.createLightInstance)
        self.switch.addChild(self.createSpotLightManipInstance)  # Add the manipulator to the switch
        self.separator.addChild(self.switch)  # Add the switch to the separator
    
    # Connect the manipulator *after* building the basic structure.
    def connectSpotLightSG(self):
        path = coin.SoPath()
        path.append(self.separator)
        path.append(self.light)
        manip = self.manip.replaceNode(path)
        return manip


    def getIcon(self):
        return iconPath("CreateSpotLight.svg")
    
def createSpotLight():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "SpotLight")
    light = SpotLight(obj)
    ViewProviderSpotLight(obj.ViewObject)


    return obj

if __name__ == "__main__":
    createSpotLight()
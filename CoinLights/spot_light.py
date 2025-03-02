import FreeCAD
import FreeCADGui
from pivy import coin

import CoinLights.universal_light as light
import CoinLights.manipulator as manipulator 
from Utils import *
from Utils.resource_utils import iconPath

class SpotLight(light.UniversalLight):
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
        #obj.addProperty("App::PropertyFloat", "LightIntensity", "SpotLight", "Intensity").LightIntensity = 0.8        
        
        
        self.type = 'SpotLight'

class Manipulator(manipulator.Manipulator):
    def __init__(self, obj):
        super().__init__(obj)
    
    def setProperties(self, obj):
        super().setProperties(obj)

class ViewProviderSpotLight(light.ViewProviderUniversalLight):
    def __init__(self, vobj):
        super().__init__(vobj)
    
    def setProperties(self, vobj):
        super().setProperties(vobj)

    def attach(self, vobj):
        super().attach(vobj)
        self.updateLocation()
        self.updateDirection()

        

    def createLightInstance(self):
        return coin.SoSpotLightManip()
    
    def showManipulator(self):
        manipulator.createLight()



    def updateManipulatorVisibility(self):
        show_manipulator = self.Object.getPropertyByName('ShowManipulator') # Get the property value
        if not hasattr(self.Object, "ShowManipulator"):
            print("ERROR: 'ShowManipulator' property is missing!")
            return  # Exit early if the property is missing

        if self.showManipulator:
            manipulator.ViewProviderLightManip.updateManipulatorVisibility(self)
            print(f"onChanged triggered: ShowManipulator = {show_manipulator}")

        else:
            manipulator.ViewProviderLightManip.updateManipulatorVisibility(self)
            print(f"onChanged triggered: ShowManipulator = {show_manipulator}")
    
    def updateScaleManipulator(self, scale_value):
        scale_value = self.Object.Scale
        print(f"Scale Manipulator IN SPOTLIGHT called! Scale value: {scale_value}") 
        manipulator.ViewProviderLightManip.scaleManipulator(scale_value)    
    """
    def onChanged(self, vp, prop):
            if prop == ['ShowManipulator']:
                show_manipulator = vp.getPropertyByName("ShowManipulator") # Get the property value
                print(f"onChanged triggered: ShowManipulator = {show_manipulator}") # Print the value
                print(f"Property 'ShowManipulator' value: {show_manipulator}") # ADD THIS LINE
    """    

    def getIcon(self):
        return iconPath("CreateSpotLight.svg")
    
def createSpotLight():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "SpotLight")
    light = SpotLight(obj)
    ViewProviderSpotLight(obj.ViewObject)


    return obj

if __name__ == "__main__":
    createSpotLight()
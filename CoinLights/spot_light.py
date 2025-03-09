import FreeCAD
import FreeCADGui
from pivy import coin

import CoinLights.universal_light as light
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
                            "The positiondirection of the light in the scene.").Direction = FreeCAD.Vector(-1, 0, 0)
            
        obj.addProperty("App::PropertyAngle", "CutOffAngle", "SpotLight", "Cut-off angle").CutOffAngle = 45.0 
        #obj.addProperty("App::PropertyFloat", "LightIntensity", "SpotLight", "Intensity").LightIntensity = 0.8        
        
        
        self.type = 'SpotLight'


class ViewProviderSpotLight(light.ViewProviderUniversalLight):
    def __init__(self, vobj):
        super().__init__(vobj)
    
    def setProperties(self, vobj):
        super().setProperties(vobj)

    def attach(self, vobj):
        super().attach(vobj)

    def createLightInstance(self):
        return coin.SoSpotLight()
    
    def createLightManipInstance(self):
        self.PointLightManip = coin.SoSpotLightManip()
        self.PointLightManip.intensity.setValue(0)
        return self.PointLightManip

    def getIcon(self):
        return iconPath("CreateSpotLight.svg")
    
def createSpotLight():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "SpotLight")
    light = SpotLight(obj)
    ViewProviderSpotLight(obj.ViewObject)


    return obj

if __name__ == "__main__":
    createSpotLight()
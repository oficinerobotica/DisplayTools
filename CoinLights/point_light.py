import FreeCAD
import FreeCADGui
from pivy import coin

import CoinLights.universal_light as light
from Utils.resource_utils import iconPath

class PointLight(light.UniversalLight):
    def __init__(self, obj):
        super().__init__(obj)
    
    def setProperties(self, obj):
        super().setProperties(obj)

        pl = obj.PropertiesList

        if not 'Location' in pl:
            obj.addProperty("App::PropertyVector", "Location", "Light",
                            "The position of the light in the scene.").Location = FreeCAD.Vector(0, -1, 0)
            
        
        self.type = 'PointLight'

class ViewProviderPointLight(light.ViewProviderUniversalLight):
    def __init__(self, vobj):
        super().__init__(vobj)
    
    def setProperties(self, vobj):
        super().setProperties(vobj)

    def attach(self, vobj):
        super().attach(vobj)
        #self.updateLocation()

    
    def createLightInstance(self):
        return coin.SoPointLight()
    
    def createLightManipInstance(self):
        self.PointLightManip = coin.SoPointLightManip()
        self.PointLightManip.intensity.setValue(0)
        return self.PointLightManip
        
    
    
    def getIcon(self):
        return iconPath("CreatePointLight.svg")
    
def createPointLight():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "PointLight")
    light = PointLight(obj)
    ViewProviderPointLight(obj.ViewObject)


    return obj

if __name__ == "__main__":
    createPointLight()

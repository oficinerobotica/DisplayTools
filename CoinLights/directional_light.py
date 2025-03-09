import FreeCAD
import FreeCADGui
from pivy import coin

from CoinLights import universal_light
from Utils.resource_utils import iconPath

class DirectionalLight(universal_light.UniversalLight):
    def __init__(self, obj):
        super().__init__(obj)

    def setProperties(self, obj):
        super().setProperties(obj)
    
        pl = obj.PropertiesList

        if 'Direction' not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Direction", "Light", "Direction of the light")     
    
        self.type = 'DirectionalLight'

class ViewProviderDirectionalLight(universal_light.ViewProviderUniversalLight):
    def __init__(self, vobj):
        super().__init__(vobj)

    def createLightInstance(self):
        return coin.SoDirectionalLight()
    
    def createLightManipInstance(self):
        self.PointLightManip = coin.SoDirectionalLightManip()
        self.PointLightManip.intensity.setValue(0)
        return self.PointLightManip

    """
    def updateData(self, fp, prop):
        if prop in ['HorizontalRotation', 'VerticalRotation', 'Distance']:
            self.updateLightDirection()
        super().updateData(fp, prop)



    def updateLightDirection(self):
        horizontalRotation = self.Object.HorizontalRotation
        verticalRotation = self.Object.VerticalRotation
        distance = self.Object.Distance
        
        # Create a rotation from the horizontal and vertical angles
        rotation = FreeCAD.Rotation(verticalRotation, horizontalRotation, 0)
        direction = rotation.multVec(FreeCAD.Vector(0, 0, -1))
        coinVector = coin.SbVec3f(direction.x, direction.y, direction.z)
        self.coinLight.direction.setValue(coinVector)
    """

    def getIcon(self):
        return iconPath("CreateDirectionalLight.svg")
    
def createDirectionalLight():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "DirectionalLight")
    light = DirectionalLight(obj)
    ViewProviderDirectionalLight(obj.ViewObject)
    return obj

if __name__ == "main":
    createDirectionalLight()


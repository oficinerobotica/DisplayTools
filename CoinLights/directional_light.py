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

        if not 'Distance' in pl:
            obj.addProperty("App::PropertyFloatConstraint", "Distance", "Light",
                            "The distance from the center of the scene.").Distance = (5000.0, 5, 100000.0, 5)  # Default: 5000, Min: 5, Max: 100000, Step: 5
            
        if not 'HorizontalRotation' in pl:
            obj.addProperty("App::PropertyAngle", "HorizontalRotation", "Light",
                            "The horizontal rotation around the origin. Zero means a light pointing from south to north.").HorizontalRotation = 0
        
        if not 'VerticalRotation' in pl:
            obj.addProperty("App::PropertyAngle", "VerticalRotation", "Light", 
                            "The up and downward rotation").VerticalRotation = 45        
    
        self.type = 'DirectionalLight'

class ViewProviderDirectionalLight(universal_light.ViewProviderUniversalLight):
    def __init__(self, vobj):
        super().__init__(vobj)

    def createLightInstance(self):
        return coin.SoDirectionalLightManip()
    
    def createGeometry(self):
        cone = coin.SoCone()
        return cone



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
        

    def getIcon(self):
        return iconPath("CreateDirectionalLight.svg")
    
def createDirectionalLight():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "DirectionalLight")
    light = DirectionalLight(obj)
    ViewProviderDirectionalLight(obj.ViewObject)
    return obj

if __name__ == "main":
    createDirectionalLight()


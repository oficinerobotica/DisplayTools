import FreeCAD, FreeCADGui
from pivy import coin
from CoinLights import manipulator
from Utils import *
from Utils.resource_utils import iconPath

class DirLightManip(manipulator.Manipulator):
    def __init__(self, obj):
        super().__init__(obj)

    def setProperties(self, obj):
        super().setProperties(obj)        
        self.type = 'TestLight'

class ViewProviderTestLightManip(manipulator.ViewProviderLightManip):
    def __init__(self, vobj):
        super().__init__(vobj)

    def attach(self, vobj):
        super().attach(vobj)

    def createSpotLightManipInstance(self):
        return manipulator.createLightManip()
    
    def getIcon(self):
        return iconPath("SpotLight.svg")

def createDirLightManip():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "DirLightManipulator")
    dirLightManip = DirLightManip(obj)
    ViewProviderTestLightManip(obj.ViewObject)
    return obj

if __name__ == "__main__":
    ViewProviderTestLightManip()


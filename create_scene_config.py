import FreeCAD, FreeCADGui
from Utils.resource_utils import iconPath

class CreateSceneConfig(object):
    def __init__(self, obj):
        obj.Proxy = self  # Link the object to this class
        self.create_tree_folder(obj)  # Ensure correct function call
    
    def setProperties(self, obj):
        pass  # No properties to set for now

    def create_tree_folder(self, obj):  
        # Create "Lights" inside SceneFolder
        lights_part = FreeCAD.ActiveDocument.addObject("App::Part", "Lights")
        lights_part.Visibility = False
        obj.addObject(lights_part)  # Add Lights directly to SceneFolder
        FreeCAD.ActiveDocument.recompute()
        self.type = 'SceneConfiguration'

class ViewProviderCreateSceneFolder:
    def __init__(self, vobj):
        vobj.Proxy = self
        self.ViewObject = vobj
        self.Object = vobj.Object

    def updateData(self, fp, prop):
        FreeCADGui.updateGui()

    def onChanged(self, vp, prop):
        """Called when something changes (not just properties)."""
        pass

    def getIcon(self):
        return iconPath('FolderTreeIcon.svg')

def createSceneFolder():
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "SceneFolder")
    CreateSceneConfig(obj)  # Create the object and add Lights to it
    ViewProviderCreateSceneFolder(obj.ViewObject)  # Assign View Provider
    FreeCAD.ActiveDocument.recompute()  # Update document
    return obj

if __name__ == "__main__":
    createSceneFolder()

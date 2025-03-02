import FreeCAD, FreeCADGui
from Utils.resource_utils import iconPath
#from Utils import qtutils
import create_scene_config
from CoinLights import point_light, directional_light, spot_light, manipulator 


class CreateSceneConfigCommand:
    toolbarName = 'Light_Tools'
    commandName = 'Create_Scene_Config'

    def GetResources(self):
        return {'MenuText': "Create Scene Config",
                'ToolTip' : "Create a new scene default configuration",
                'Pixmap': iconPath('CreateCustomScene.svg')
                }
    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if doc:
            scene_folder_exists = False
            for obj in doc.Objects:
                try:
                    if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "type") and obj.Proxy.type == 'SceneConfiguration':
                        scene_folder_exists = True
                        break
                except AttributeError:
                    pass
            if scene_folder_exists:
                error_message = " A scene lighting configuration folder already exists in the document tree. Only one scene lighting configuration is permitted per document. Please utilize the existing folder or remove it before attempting to create a new one."
                FreeCAD.Console.PrintError(error_message + "\n")
            else:
                create_scene_config.createSceneFolder()

    def IsActive(self):
        """If there is no active document we can't do anything."""
        return not FreeCAD.ActiveDocument is None



class CreatePointLightCommand:
    toolbarName = 'Light_Tools'
    commandName = 'Create_PointLight'

    def GetResources(self):
        return {'MenuText': "Create Pointlight",
                'ToolTip' : "Create a new point light in the scene",
                'Pixmap': iconPath('CreatePointLight.svg')
                }

    def Activated(self):
        point_light.createPointLight()

    def IsActive(self):
        """If there is no active document we can't do anything."""
        return not FreeCAD.ActiveDocument is None
    
class CreateDirectionalLightCommand:
    toolbarName = 'Light_Tools'
    commandName = 'Create_Directional Light'

    def GetResources(self):
        return {'MenuText': "Create Directionallight",
                'ToolTip' : "Create a new Directional light in the scene",
                'Pixmap': iconPath('CreateDirectionalLight.svg')
                }

    def Activated(self):
        directional_light.createDirectionalLight()

    def IsActive(self):
        """If there is no active document we can't do anything."""
        return not FreeCAD.ActiveDocument is None
    
class CreateSpotLightCommand:
    toolbarName = 'Light_Tools'
    commandName = 'Create_SpotLight'

    def GetResources(self):
        return {'MenuText': "Create Spotlight",
                'ToolTip' : "Create a new spot light in the scene",
                'Pixmap': iconPath('CreateSpotLight.svg')
                }

    def Activated(self):
        spot_light.createSpotLight()

    def IsActive(self):
        """If there is no active document we can't do anything."""
        return not FreeCAD.ActiveDocument is None
    
class CreateTestCommand:
    toolbarName = 'Light_Tools'
    commandName = 'Create_Test'

    def GetResources(self):
        return {'MenuText': "Create Test",
                'ToolTip' : "Create test, for development purpose ",
                'Pixmap': iconPath('TestIcon.svg')
                }

    def Activated(self):
        pass
    
    def IsActive(self):
        """If there is no active document we can't do anything."""
        return not FreeCAD.ActiveDocument is None
    
class CreateSeparator:
    toolbarName = 'Light_Tools'
    commandName = 'Separator'

    def GetResources(self):
        return {}  # No icon or text is needed for a separator

    def Activated(self):
        pass  # No action needed when the separator is "activated"

    def IsActive(self):
        return False  # The separator itself is not an active command

    
    
if __name__ == "__main__":
    command = CreatePointLightCommand();
    
    if command.IsActive():
        command.Activated()
    else:
        import Utils.qtutils as qtutils
        qtutils.showInfo("No open Document", "There is no open document")
else:
    import displaytools_toolbars
    displaytools_toolbars.toolbarManager.registerCommand(CreateSceneConfigCommand())
    displaytools_toolbars.toolbarManager.registerCommand(CreateSeparator())
    displaytools_toolbars.toolbarManager.registerCommand(CreatePointLightCommand())
    displaytools_toolbars.toolbarManager.registerCommand(CreateDirectionalLightCommand())
    displaytools_toolbars.toolbarManager.registerCommand(CreateSpotLightCommand())
    displaytools_toolbars.toolbarManager.registerCommand(CreateSeparator())
    displaytools_toolbars.toolbarManager.registerCommand(CreateTestCommand())
    
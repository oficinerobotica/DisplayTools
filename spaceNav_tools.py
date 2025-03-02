import FreeCAD, FreeCADGui
from Utils.resource_utils import iconPath
from SpaceNav import spacenav_commands

class CreateSeparator:
    toolbarName = 'Light_Tools'
    commandName = 'Separator'

    def GetResources(self):
        return {}  # No icon or text is needed for a separator

    def Activated(self):
        pass  # No action needed when the separator is "activated"

    def IsActive(self):
        return False  # The separator itself is not an active command

class SpToolsLockRot:
    toolbarName = 'SpaceNav_Tools'
    commandName = 'Lock_Rotation'

    def GetResources(self):
        return {'MenuText': "Lock SpaceNav rotation",
                'ToolTip' : "Lock SpaceNav rotation",
                'Pixmap': iconPath('SpNav.svg')
                }
    
    def Activated(self):
        spacenav_commands.SpaceNavCommands()

    def IsActive(self):
        """If there is no active document we can't do anything."""
        return not FreeCAD.ActiveDocument is None

class SpToolsLockTrans:
    toolbarName = 'SpaceNav_Tools'
    commandName = 'Lock_Translation'

    def GetResources(self):
        return {'MenuText': "Lock SpaceNav translation",
                'ToolTip' : "Lock SpaceNav translation",
                'Pixmap': iconPath('SpNav_LockTrans.svg')
                }
    
    def Activated(self):
        spacenav_commands.SpaceNavCommands()

    def IsActive(self):
        """If there is no active document we can't do anything."""
        return not FreeCAD.ActiveDocument is None

class SpToolsLockHorizon:
    toolbarName = 'SpaceNav_Tools'
    commandName = 'Lock_Horizon'

    def GetResources(self):
        return {'MenuText': "Lock SpaceNav horison",
                'ToolTip' : "Lock SpaceNav horison",
                'Pixmap': iconPath('SpNav_LockHor.svg')
                }
    
    def Activated(self):
        spacenav_commands.SpaceNavCommands()

    def IsActive(self):
        """If there is no active document we can't do anything."""
        return not FreeCAD.ActiveDocument is None
    
import displaytools_toolbars
displaytools_toolbars.toolbarManager.registerCommand(CreateSeparator())
displaytools_toolbars.toolbarManager.registerCommand(SpToolsLockRot())
displaytools_toolbars.toolbarManager.registerCommand(SpToolsLockTrans())
displaytools_toolbars.toolbarManager.registerCommand(SpToolsLockHorizon())



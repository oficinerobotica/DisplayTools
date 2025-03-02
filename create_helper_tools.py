import FreeCAD, FreeCADGui
from Utils.resource_utils import iconPath
from HelperTools import dynamic_grid


class CreateSeparator:
    toolbarName = 'Helper_Tools'
    commandName = 'Separator'

    def GetResources(self):
        return {}  # No icon or text is needed for a separator

    def Activated(self):
        pass  # No action needed when the separator is "activated"

    def IsActive(self):
        return False  # The separator itself is not an active command
    
class CreateDynamicGrid:
    toolbarName = 'Helper_Tools'
    commandName = 'Dynamic_Grid'

    def GetResources(self):
        return {'MenuText' : 'Create dynamic grid',
                'ToolTip' : 'Create dynamic grid',
                'Pixmap' : iconPath('CreateDynamicGrid.svg')
                }
    
    def Activated(self):
        dynamic_grid.createDynamicGrid()

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None
    
import displaytools_toolbars
displaytools_toolbars.toolbarManager.registerCommand(CreateDynamicGrid())
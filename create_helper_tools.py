import FreeCAD, FreeCADGui
from Utils.resource_utils import iconPath
from HelperTools import dinamic_grid


class CreateSeparator:
    toolbarName = 'Helper_Tools'
    commandName = 'Separator'

    def GetResources(self):
        return {}  # No icon or text is needed for a separator

    def Activated(self):
        pass  # No action needed when the separator is "activated"

    def IsActive(self):
        return False  # The separator itself is not an active command
    
class CreateDinamicGrid:
    toolbarName = 'Helper_Tools'
    commandName = 'Dinamic_Grid'

    def GetResources(self):
        return {'MenuText' : 'Create dinamic grid',
                'ToolTip' : 'Create dinamic grid',
                'Pixmap' : iconPath('CreateDinamicGrid.svg')
                }
    
    def Activated(self):
        dinamic_grid.createDinamicGrid()

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None
    
import displaytools_toolbars
displaytools_toolbars.toolbarManager.registerCommand(CreateDinamicGrid())
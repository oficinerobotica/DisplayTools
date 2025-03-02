from collections import OrderedDict
import FreeCAD, FreeCADGui

class DisplayToolsToolbarManage:
    Toolbars =  OrderedDict()

    def registerCommand(self, command):
        FreeCADGui.addCommand(command.commandName, command)
        self.Toolbars.setdefault(command.toolbarName, []).append(command)

toolbarManager = DisplayToolsToolbarManage()

# import commands here
import create_light
import spaceNav_tools
import create_helper_tools
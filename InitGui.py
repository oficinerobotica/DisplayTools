import FreeCAD, FreeCADGui

class DisplayToolsWorkbench (Workbench):
    MenuText = "Display tools"
    ToolTip = "Create and manage lighting and other visual aids in the display view"

    def __init__(self):
        """Initialize the workbench."""
        from Utils.resource_utils import iconPath
        self.__class__.Icon = iconPath("Workbench.svg")
        self.commands = [] # initialize the command list

    def Initialize(self):
        """This function is executed after the workbench is activated."""
        pass
        import displaytools_toolbars
        for name,commands in displaytools_toolbars.toolbarManager.Toolbars.items():
            self.appendToolbar(name,[command.commandName for command in commands])

    def Activated(self):
        """This function is executed whenever the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed whenever the workbench is deactivated"""
        return

    def GetClassName(self):
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(DisplayToolsWorkbench())
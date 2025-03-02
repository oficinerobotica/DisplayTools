import FreeCAD
import FreeCADGui

from pivy import coin



class Manipulator():
    def __init__(self, obj):
        obj.Proxy = self
        self.setProperties(obj)

    def setProperties(self, obj):

        obj.addProperty("App::PropertyBool", "ShowManipulator", "Manipulator", "Show Manipulator Geometry").ShowManipulator = True
        obj.addProperty("App::PropertyIntegerConstraint", "Scale", "Manipulator", "Uniform scale factor for the manipulator").Scale = (5, 5, 200, 5)  # Default: 5, Min: 5, Max: 100, Step: 5
        self.type = 'Manipulator'
    def onChanged(self, obj, prop):    
        if prop == "ShowManipulator":
            # Check if ViewObject and its Proxy exist
            if obj.ViewObject and hasattr(obj.ViewObject, 'Proxy') and obj.ViewObject.Proxy:
                obj.ViewObject.Proxy.updateManipulatorVisibility()

        if prop == "Scale":  # If Scale is changed, update manipulator
            if obj.ViewObject and hasattr(obj.ViewObject, 'Proxy') and obj.ViewObject.Proxy:
                obj.ViewObject.Proxy.scaleManipulator()



    def onDocumentRestored(self, obj):
        self.setProperties(obj)

    def __getstate__(self):
        return None
 
    def __setstate__(self,state):
        return None

    def execute(self, ob):
        pass



class ViewProviderLightManip:
    def __init__(self, vobj):
        vobj.Proxy = self


 
    def attach(self, vobj):
        vobj.Proxy = self
        self.Object = vobj.Object # Store the Feature object in the ViewProvider

        # Setting properties does not work here as the pl is not filled yet :/
        # Building the sceene graph:        
        
        sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        self.switch_node = coin.SoSwitch()
        self.separator_node = coin.SoSeparator()
        self.manipulator_node = coin.SoDirectionalLightManip()
        self.scale_node = coin.SoScale()
        #self.scale_node.scaleFactor.setValue(10.0, 10.0, 10.0) # Scale by 5x in all dimensions
        
        self.separator_node.addChild(self.scale_node)
        self.separator_node.addChild(self.manipulator_node)
        self.switch_node.addChild(self.separator_node)
        sg.addChild(self.switch_node)  # Add separator to the scene graph
        vobj.addDisplayMode(self.switch_node, "Manipulator")
        
        self.updateManipulatorVisibility()
        self.scaleManipulator()

    def scaleManipulator(self):
        scale_value = self.Object.Scale
        self.scale_node.scaleFactor.setValue(scale_value, scale_value, scale_value)

    def updateManipulatorVisibility(self):
        if not hasattr(self.Object, "ShowManipulator"):
            print("ERROR: 'ShowManipulator' property is missing!")
            return  # Exit early if the property is missing

        if self.Object.ShowManipulator:
            self.switch_node.whichChild = 0
        else:
            self.switch_node.whichChild = coin.SO_SWITCH_NONE

    
    
    
    def getDisplayModes(self,obj):
        '''Return a list of display modes.'''
        return ["Manipulator"]
    
    def getDefaultDisplayMode(self):
        '''Return the name of the default display mode. It must be defined in getDisplayModes.'''
        return "Manipulator"

        
    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None
      
    
    def create_spot_light_manip(self):
        print("Manipulator is created in the viewport:")
        spot_light_manip = coin.SoDirectionalLightManip()

        
def createLightManip():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Manipulator")
    lightManip = Manipulator(obj)
    ViewProviderLightManip(obj.ViewObject)
    return obj

if __name__ == "__main__":
    createLightManip()
    


        
    

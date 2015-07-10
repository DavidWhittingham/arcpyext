import arcpy


class Toolbox(object):
    def __init__(self):
        self.label='Test Toolbox'
        self.alias='TestToolbox'
        self.description='<p>Test toolbox</p>'
        self.summary=self.description

        # List of tool classes associated with this toolbox
        self.tools=[TestTool]


class TestTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label='Test Tool'
        self.description='A test tool.'
        self.summary=self.description


    def getParameterInfo(self):
        """Define parameter definitions"""
        inParam=arcpy.Parameter(
            displayName='Input param',
            name='inParam',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')
        inParam.description='<p>Input param desc</p>'
        outParam=arcpy.Parameter(
            displayName='Output param',
            name='outParam',
            datatype='GPString',
            parameterType='Derived',
            direction='Output')
        outParam.description='<p>Output param desc</p>'
        
        return [inParam,outParam]


    def updateParameters(self,parameters): return
    def updateMessages(self,parameters): return


    def execute(self,parameters,messages):
        pass

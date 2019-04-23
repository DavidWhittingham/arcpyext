import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""
        self.description = "Toolbox description."
        self.summary = "Summary of this toolbox."

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.canRunInBackground = False
        self.summary = "Tool summary"

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

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        return

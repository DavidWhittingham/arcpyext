import sys,os
import imp
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

import arcpy



class PythonToolbox(object):
    def __init__(self,toolboxPath):
        self.toolboxPath=toolboxPath


    def load(self):
        # load the pyt file so that we can work with the objects
        self.toolbox=imp.load_source('PythonToolbox',self.toolboxPath).Toolbox()
        self.tools=[PythonTool(self,t()) for t in self.toolbox.tools]
        # and let arcpy do it's convoluted thing too - this generates the xml files if they didn't exist
        arcpy.ImportToolbox(self.toolboxPath)


    @property
    def xmlPath(self):
        return self.toolboxPath+'.xml'


    def loadXml(self):
        self.xmlRoot=etree.parse(self.xmlPath)
        # and load tools too
        for t in self.tools:
            t.loadXml()


    def getOrCreateElement(self,baseElementXpath,name):
        b=self.xmlRoot.find(baseElementXpath)
        e=b.find(name)
        if e is None:
            e=etree.Element(name)
            b.append(e)
        return e


    def setDescriptionInXml(self,description):
        e=self.getOrCreateElement('dataIdInfo','idAbs')
        e.text=description

    def setSummaryInXml(self,summary):
        e=self.getOrCreateElement('dataIdInfo','idPurp')
        e.text=summary


    def applyToolboxDescriptions(self):
        """Applies the description attributes on the Toolbox model to the xml sitting beside the toolbox file."""
        self.setDescriptionInXml(self.toolbox.description)
        self.setSummaryInXml(self.toolbox.summary)

        # and do tools too
        for t in self.tools:
            t.applyToolDescriptions()


    def saveDefinitions(self):
        with open(self.xmlPath,'w') as fout:
            self.xmlRoot.write(fout,encoding='utf-8')
        # and save tools too
        for t in self.tools:
            t.saveDefinitions()



class PythonTool(object):
    def __init__(self,pythonToolbox,tool):
        self.pythonToolbox=pythonToolbox
        self.tool=tool
        self.toolName=self.tool.__class__.__name__


    @property
    def xmlPath(self):
        return os.path.splitext(self.pythonToolbox.toolboxPath)[0]+'.'+self.toolName+'.pyt.xml'


    def loadXml(self):
        self.xmlRoot=etree.parse(self.xmlPath)
        

    def getOrCreateElement(self,baseElementXpath,name):
        b=self.xmlRoot.find(baseElementXpath)
        e=b.find(name)
        if e is None:
            e=etree.Element(name)
            b.append(e)
        return e


    def setDescriptionInXml(self,description):
        e=self.getOrCreateElement('dataIdInfo','idAbs')
        e.text=description

    def setSummaryInXml(self,summary):
        xpath='tool[@name=\'{}\']'.format(self.toolName)
        e=self.getOrCreateElement(xpath,'summary')
        e.text=summary


    def setParameterDescriptionInXml(self,paramName,description):
        xpath='tool[@name=\'{}\']/parameters/param[@name=\'{}\']'.format(self.toolName,paramName)
        e=self.getOrCreateElement(xpath,'dialogReference')
        e.text=description


    def applyToolDescriptions(self):
        """Applies the description attributes on the Tool model to the xml sitting beside the toolbox file."""
        self.setDescriptionInXml(self.tool.description)
        self.setSummaryInXml(self.tool.summary)

        # and set parameter descriptions too
        for p in self.tool.getParameterInfo():
            if p.direction=='Input':
                self.setParameterDescriptionInXml(p.name,p.description)


    def saveDefinitions(self):
        with open(self.xmlPath,'w') as fout:
            self.xmlRoot.write(fout,encoding='utf-8')

import sys,os
import imp
import xml.etree.ElementTree as etree

import arcpy



class PythonToolbox(object):
    def __init__(self,toolboxPath):
        self.toolboxPath=toolboxPath


    def load(self):
        # let arcpy do it's convoluted thing - this generates the xml files if they didn't exist
        arcpy.ImportToolbox(self.toolboxPath)
        # and load the pyt file so that we can work with the actual objects (in this order, we get better exceptions if there are errors loading the module a second time)
        # this may not work if you can't import a module twice, eg. with Django Models, so may need to re-work your toolbox code to only import packages when necessary 
        self.toolbox=imp.load_source('PythonToolbox',self.toolboxPath).Toolbox()
        self.tools=[PythonTool(self,t()) for t in self.toolbox.tools]


    @property
    def xmlPath(self):
        return self.toolboxPath+'.xml'


    def loadXml(self):
        self.xmlTree=etree.parse(self.xmlPath)
        # and load tools too
        for t in self.tools:
            t.loadXml()


    @classmethod
    def getOrCreateElement(cls,element,name,attributes={}):
        xpath=name
        if attributes: xpath+='['+','.join(['@'+k+"='"+v+"'" for k,v in attributes.items()])+']'
        e=element.find(xpath)
        if e is None:
            e=etree.Element(name)
            for k,v in attributes.items(): e.set(k,v)
            element.append(e)
        return e


    def setDescriptionInXml(self,description):
        e=self.getOrCreateElement(self.xmlTree.getroot(),'dataIdInfo')
        e=self.getOrCreateElement(e,'idAbs')
        e.text=description

    def setSummaryInXml(self,summary):
        e=self.getOrCreateElement(self.xmlTree.getroot(),'dataIdInfo')
        e=self.getOrCreateElement(e,'idAbs')
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
            self.xmlTree.write(fout,encoding='utf-8')
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
        self.xmlTree=etree.parse(self.xmlPath)


    def setDescriptionInXml(self,description):
        e=PythonToolbox.getOrCreateElement(self.xmlTree.getroot(),'dataIdInfo')
        e=PythonToolbox.getOrCreateElement(e,'idAbs')
        e.text=description

    def setSummaryInXml(self,summary):
        e=PythonToolbox.getOrCreateElement(self.xmlTree.getroot(),'tool',attributes={'name':self.toolName})
        e=PythonToolbox.getOrCreateElement(e,'summary')
        e.text=summary


    def setParameterDescriptionInXml(self,paramName,description):
        e=PythonToolbox.getOrCreateElement(self.xmlTree.getroot(),'tool',attributes={'name':self.toolName})
        e=PythonToolbox.getOrCreateElement(e,'parameters')
        e=PythonToolbox.getOrCreateElement(e,'param',attributes={'name':paramName})
        e=PythonToolbox.getOrCreateElement(e,'dialogReference')
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
            self.xmlTree.write(fout,encoding='utf-8')

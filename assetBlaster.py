'''
WIP WIP WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP  WIP
'''

import maya.cmds as cmds
import os, glob, time, sys, getpass, random, re
import maya.mel as mel
import pymel.core as pm
import os.path
from functools import partial
import json
import collections
from collections import defaultdict
from random import choice
import string
from distutils.dir_util import copy_tree
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import time

import Qt
from Qt import QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from shiboken2 import wrapInstance

import NXTPXL
from NXTPXL import blaster_UI_path as BLUI
from NXTPXL import projectsDir as projectsDir
from NXTPXL import filePathFixed
from NXTPXL import currentProjectUsersDir as currentProjectUsersDir

class assBlaster():
    
    # class variable 
    # will get over written by project resoultion only to be used for render done off project
    renderResolution = [1920, 1080]
    
    # instalce variable
    self.render_Resolution = [2120, 1120]
    
    def __init__(self):
        # for local use only
        path = BLUI
        self.rvDir = r'C:/Program Files/Shotgun/RV-7.1.1'
        self.mainProjectDir = projectsDir

        self.UserDir = currentProjectUsersDir
        self.btn01_icon = os.path.join(path, 'toggle_grid.jpg')
        self.btn02_icon = os.path.join(path, 'toggle_ImagPlane.jpg')
        self.btn03_icon = os.path.join(path, 'toggle_ResGate.jpg')
        self.btn04_icon = os.path.join(path, 'toggle_Geo.jpg')
        self.btn05_icon = os.path.join(path, 'toggle_BG_color.jpg')
        self.btn06_icon = os.path.join(path, 'Render_playblast.jpg')

    @classmethod
    def setRenderResolution(cls, resolution):
        cls.renderResolution = resolution   
 
    # for network use only
    def toggleResGate(self, *args):
        currentPanel=str(pm.getPanel(withFocus=1))
        currentCam=str(pm.modelPanel(currentPanel, q=1, cam=1))
        # get the current camera from the modelPanel
        # query the resolution gate and see if it's hidden
        isResGateOn=int(pm.optionVar(q="resolutionGate"))
        # if it's hidden let's show it
        if isResGateOn != 0:
            pm.optionVar(iv=("resolutionGate", 0))
            # turn the res gate on
            pm.camera(currentCam, ovr=1.3, dr=True, dfg=False, e=1)
        else:
            pm.optionVar(iv=("resolutionGate", 1))
            pm.camera(currentCam, ovr=1.0, dr=False, dfg=False, e=1)
    def toggleImagePlane(self, *args):
        currentPanel=str(pm.getPanel(withFocus=1))
        currentCam=str(pm.modelPanel(currentPanel, q=1, cam=1))
        isImagePlane = cmds.modelEditor(currentPanel, q=True, imagePlane=True )
        if isImagePlane != 0:
            cmds.modelEditor(currentPanel, imagePlane=False, e=1)
            pm.optionVar(iv=("ImagePlane", 0))
        else:
            cmds.modelEditor(currentPanel, imagePlane=True, e=1)
            pm.optionVar(iv=("ImagePlane", 1))
    
    @staticmethod
    def cam_loader():
        cameras = cmds.ls(cameras = 1)
        transforms = cmds.listRelatives(cameras, parent=1)
        #transforms.remove('persp')
        transforms.remove('side')
        transforms.remove('top')
        transforms.remove('front')
        return transforms

    @staticmethod
    def getCamera(*args):
        view = OpenMayaUI.M3dView.active3dView()
        cam = OpenMaya.MDagPath()
        view.getCamera(cam)
        camPath = (cam.fullPathName()).split('|')[1]
        return camPath

    def updateframeRangeFromCamera(self, currentCam):
        channel = 'translateX'
        keyframes = cmds.keyframe('{0}.{1}'.format(currentCam, channel), query=True)
        INI_Path = self.maya_env_paths()
        self.UI_values = self.reading_ini_file_values(INI_Path)
        if keyframes:
            first, last = keyframes[0], keyframes[-1]
            cmds.intField( self.firstFrame, edit = True, value =  first)
            cmds.intField( self.lastFrame, edit = True, value =  last)
            cmds.playbackOptions(min=first, max=last, ast=first, aet=last)
        else:
            first, last = 1, 2
            cmds.playbackOptions(min=first, max=last, ast=first, aet=last)
            cmds.intField( self.firstFrame, edit = True, value =  0)
            cmds.intField( self.lastFrame, edit = True, value =  0)

    @staticmethod
    def hideAllButGeo(*args):
        """show only geometry"""
        currentCam = ""
        if pm.mel.getApplicationVersionAsFloat()<=2008:
            currentCam=str(pm.getPanel(withFocus=1))
        else:
            currentCam=str(pm.playblast(ae=1))

        isEverythingHidden=int(pm.optionVar(q="everythingIsHidden"))
        if isEverythingHidden != 0:
            pm.optionVar(iv=("everythingIsHidden", 0))
            # show everything
            pm.modelEditor(currentCam, allObjects=True, e=1)
        else:
            pm.optionVar(iv=("everythingIsHidden", 1))
            # hide everything
            pm.modelEditor(currentCam, allObjects=False, e=1)
            # show polymeshes
            pm.modelEditor(currentCam, e=1, polymeshes=True)
            # show nurbssurfaces
            pm.modelEditor(currentCam, e=1, nurbsSurfaces=True)

    @staticmethod        
    def toggleWireframe(*args):
        currentCam = ""
        currentCam=str(pm.playblast(ae=1))
        wireFrameOn=int(pm.modelEditor(currentCam, q=1, wos=1))
        if wireFrameOn != 0:
            pm.mel.setWireframeOnShadedOption(False, currentCam)
            pm.modelEditor(currentCam, e=1, smoothWireframe=False)
        else:
            pm.mel.setWireframeOnShadedOption(True, currentCam)
            pm.modelEditor(currentCam, e=1, smoothWireframe=True)

    @staticmethod        
    def toggleWireframeViewport_currentval(status):
        currentCam = ""
        currentCam=str(pm.playblast(ae=1))
        wireFrameOn=int(pm.modelEditor(currentCam, q=1, wos=1))
        if status == 'enable':
            pm.mel.setWireframeOnShadedOption(True, currentCam)
            # turn wireframe on shaded on
            # turn the smoothing back on
            pm.modelEditor(currentCam, e=1, smoothWireframe=True)

        if status == 'disable':
            print 'turn it off'
            pm.mel.setWireframeOnShadedOption(False, currentCam)
            # turn wireframe on shaded off
            # turn the smoothing off as well
            pm.modelEditor(currentCam, e=1, smoothWireframe=False)

    @staticmethod        
    def defMatValue(status):
        currentCam = ""
        currentCam=str(pm.playblast(ae=1))
        def_Material=int(pm.modelEditor(currentCam, q=1, udm=True))
        if status == 'enable':
            pm.modelEditor(currentCam, e=1, useDefaultMaterial=True)

        if status == 'disable':
            print 'turn it off'
            pm.modelEditor(currentCam, e=1, useDefaultMaterial=False)

    @staticmethod        
    def defHardwareFogValue(status):
        currentCam = ""
        currentCam=str(pm.playblast(ae=1))
        def_Material=int(pm.modelEditor(currentCam, q=1, udm=1))
        if status == 'enable':
            mel.eval('modelEditor -e -fogging true %s;'%currentCam)
            pm.modelEditor(currentCam, e=1, fogging=True)
            mel.eval('setAttr "hardwareRenderingGlobals.hwFogStart" 0.0;')
        if status == 'disable':
            print 'turn it off'
            mel.eval('modelEditor -e -fogging false %s;'%currentCam)
            pm.modelEditor(currentCam, e=1, fogging=False)

    @staticmethod        
    def toggleDefMaterial(*args):
        currentCam = ""
        currentCam=str(pm.playblast(ae=1))
        chkStatus = pm.modelEditor(currentCam, q=True, useDefaultMaterial=True)
        print (chkStatus)
        if chkStatus == False:
            pm.modelEditor(currentCam, e=1, useDefaultMaterial=True)
        else:
            pm.modelEditor(currentCam, e=1, useDefaultMaterial=False)
    
    @staticmethod
    def queryFogDistance(*args):
        distance = mel.eval('getAttr "hardwareRenderingGlobals.hwFogEnd";')
        return distance

    def reduceFog(self, *args):
        dis =int(self.queryFogDistance())
        dis = float(dis - 100)
        mel.eval('setAttr "hardwareRenderingGlobals.hwFogEnd" %f;'%dis)
    
    def increaseFog(self, *args):
        dis =int(self.queryFogDistance())
        dis = float(dis + 100)
        mel.eval('setAttr "hardwareRenderingGlobals.hwFogEnd" %f;'%dis)
    
    def changeFogColor(self, *args):
        result = cmds.colorEditor()
        buffer = result.split()
        if '1' == buffer[3]:
            values = cmds.colorEditor(query=True, rgb=True)
            alpha  = cmds.colorEditor(query=True, alpha=True)
        else:
            print 'Editor was dismissed'
        if values:
            colValues = values[0],values[1],values[2]
            mel.eval('setAttr "hardwareRenderingGlobals.hwFogColor" -type double3 %f %f %f ;'%(colValues[0], colValues[1], colValues[2]))
            mel.eval('setAttr "hardwareRenderingGlobals.hwFogAlpha" %f;'%alpha)

        else:
            pass

    def toggleHardwareFOG(self, *args):
        currentCam = ""
        currentCam=str(pm.playblast(ae=1))
        chkStatus = pm.modelEditor(currentCam, q=True, fogging=True)
        print (chkStatus)
        if chkStatus == False:
            mel.eval('modelEditor -e -fogging true %s;'%currentCam)
            pm.modelEditor(currentCam, e=1, fogging=True, fogMode = 'linear')
            mel.eval('setAttr "hardwareRenderingGlobals.hwFogStart" 0.0;')
            cmds.button( self.fogReduceButton, e = True , enable = True, bgc=(.55, .25, .25) )
            cmds.button( self.fogAddButton, e = True , enable = True, bgc=(.25, .55, .25) )
            cmds.button( self.fogColorButton, e = True , enable = True, bgc=(.55, .55, .55) )
        else:
            mel.eval('modelEditor -e -fogging true %s;'%currentCam)
            pm.modelEditor(currentCam, e=1, fogging=False)
            cmds.button( self.fogReduceButton, e = True , enable = False, bgc=(.22, .22, .22) )
            cmds.button( self.fogAddButton, e = True , enable = False, bgc=(.22, .22, .22) )
            cmds.button( self.fogColorButton, e = True , enable = False, bgc=(.22, .22, .22) )

    def playblastGridHide(self, *args):
        """toggle to hide the grid or not"""
        currentCam = ""
        if pm.mel.getApplicationVersionAsFloat()<=2008:
            currentCam=str(pm.getPanel(withFocus=1))
        else:
            currentCam=str(pm.playblast(ae=1))
        isGridHidden=int(pm.modelEditor(currentCam, q=1, grid=1))
        if isGridHidden != 0:
            pm.modelEditor(currentCam, grid=False, e=1)
        else:
            pm.modelEditor(currentCam, grid=True, e=1)

    def lookThrougCamera(self, item):
        selectedCam = item
        timeLineCondition = self.queryFrameRange()
        currentPanel=str(pm.getPanel(withFocus=1))
        cmds.lookThru( selectedCam, currentPanel )
        updateFrameRange = str(self.queryFrameRange())
        if updateFrameRange == 'YES ':
            self.updateframeRangeFromCamera(selectedCam)
        else:
            pass


    def queryFrameRange(self, *args):
        rangeCondition = cmds.radioCollection(self.timeRangeRadio, q = True)
        updateFrameRange = str(self.passValue())
        return updateFrameRange

    def changeBackgroundColor(self, *args):
        pm.mel.cycleBackgroundColor()

    def function1(self, value1,value2):
        print(value1)

    def function2(self, value):
        print(value)

    def passValue(self, *args):
        self.radioCol = cmds.radioCollection(self.timeRangeRadio, query=True, sl=True)
        getSelectRadioVal = cmds.radioButton(self.radioCol, query=True, label=True)
        return getSelectRadioVal
    def projectRadioButtonDef(self, *args):
        self.projectPathSelection('project')

    def projectPathSelection(self, pathType):

        filePath = cmds.file(query=True, l=True)[0]
        dir = (filePath.split('/'))
        contentPath = dir[0]+'/'+dir[1]+'/'+dir[2]+'/'+dir[3]

        if contentPath == self.mainProjectDir:
            existingProjects = os.listdir(self.mainProjectDir)
            if dir[4] in existingProjects:
                if str(dir[8]) in ("animation", "compositing", "fx", "layout", "lighting", "rnd"):
                    file_Path = dir[4] +'/'+dir[5]+'/'+dir[6]+'/'+dir[7]+'/'+dir[8]+'/'+dir[9]
                    shotDir = self.filePathFixed(os.path.join(self.mainProjectDir,file_Path))
                    versionNum =  os.path.basename(filePath)
                    playblastFileName =  versionNum.split('.')[0]
                    mayaFIlesInDir = self.getFilesWithExtension(shotDir, 'ma')
                    if versionNum in mayaFIlesInDir:
                        playBlastDir = self.filePathFixed(os.path.join(shotDir,'playBlasts'))
                        if os.path.isdir(playBlastDir):
                            pass
                        else:
                            os.mkdir(playBlastDir)
                        cmds.button(self.selectFolderBtn, e = True, bgc=(.55, .11, .11), enable = False)
                        cmds.textField( self.selectedPlayblastPath, e = True , enable = False, bgc=(.01, .01, .01), text = playBlastDir )
                        if pathType == 'project':
                            cmds.textField(self.playblastname, e = True , enable = False, bgc=(.01, .01, .01), text = playblastFileName  )
                        if pathType == 'network':
                            cmds.textField(self.playblastname, e = True , enable = True, bgc=(.01, .01, .01)  )
        else:
            cmds.button(self.selectFolderBtn, e = True, bgc=(.55, .11, .11), enable = False)
            cmds.textField( self.selectedPlayblastPath, e = True , enable = False, bgc=(.01, .01, .01), text = ('Save file on Network') )
            cmds.textField( self.playblastname, e = True , enable = False, bgc=(.01, .01, .01), text = 'Error :' )



    def getFilesWithExtension(self, path, extension):
        files = os.listdir(path)
        files_txt = [i for i in files if i.endswith('.%s'%extension)]
        return files_txt


    def confirmingNetworkDirStructure(self):
        shotPath = self.getShotContext()
        cmds.button(self.selectFolderBtn, e = True, bgc=(.55, .11, .11), enable = False)
        if os.path.isdir(shotPath[4]):
            pass
        else:
            os.mkdir(shotPath[4])
        assBlasterDir = os.path.join(shotPath[4], 'assBlaster')
        if os.path.isdir(assBlasterDir):
            pass
        else:
            os.mkdir(assBlasterDir)
        with open(os.path.join(assBlasterDir,'DO_NOT_Delete.txt'), 'w') as file:
            json.dump('DO not delete or modify the assBlaster dir for your own good :- Nitin.Singh',file)

        shotDir = os.path.join(assBlasterDir, shotPath[1])
        takeNum = shotPath[3][1]
        if os.path.isdir(shotDir):
            pass
        else:
            os.mkdir(shotDir)
        takeDir = os.path.join(shotDir,takeNum )

        print (takeDir)
        if os.path.isdir(takeDir):
            pass
        else:
            os.mkdir(takeDir)
        return  shotDir, takeDir


    def networkRadioButtonDef(self, *args):
        #print ('network radio button selected')
        self.projectPathSelection('network')


    def localRadioButtonDef(self, *args):
        cmds.button(self.selectFolderBtn, e = True, bgc=(.25, .55, .25), enable = True)
        cmds.textField( self.selectedPlayblastPath, bgc=(.01, .01, .01), e = True , enable = True , text = '')
        cmds.textField( self.playblastname, e = True , enable = True, bgc=(.01, .01, .01) )

    def updatingWidgets(self, *agrs):
        INI_Path = self.maya_env_paths()
        self.UI_values = self.reading_ini_file_values(INI_Path)
        #print '------------------------------------------'
        #print self.UI_values
        #print '------------------------------------------'
        # updating UI widgets after loading default settings
        cmds.checkBox(self.Use_Default_Material ,edit=True, value=(self.UI_values['Use_Default_Material']) )
        cmds.checkBox(self.play_in_RV ,edit=True, value=(self.UI_values['play_in_RV']) )
        cmds.checkBox(self.Hardware_Fog ,edit=True, value=(self.UI_values['Hardware_Fog'])  )
        cmds.checkBox(self.WireFrame_On_shaded,edit=True, value=(self.UI_values['WireFrame_On_shaded']))

        cmds.menuItem( self.motion_Blur, edit = True, checkBox=(self.UI_values['motionBlur']) )
        cmds.menuItem( self.NURBS_Curves, edit = True, checkBox=(self.UI_values['NURBS_Curves']) )
        cmds.menuItem( self.NURBS_Surface, edit = True, checkBox=(self.UI_values['NURBS_Surface']) )
        cmds.menuItem(self.NURBS_CVs,edit = True, checkBox=(self.UI_values['NURBS_CVs']) )
        cmds.menuItem(self.NURBS_Hulls ,edit = True, checkBox=(self.UI_values['NURBS_Hulls']) )
        cmds.menuItem(self.Polygons ,edit = True, checkBox=(self.UI_values['Polygons']) )
        cmds.menuItem(self.Subdiv_Surfaces ,edit = True, checkBox=(self.UI_values['Subdiv_Surfaces']) )
        cmds.menuItem(self.Planes ,edit = True, checkBox=(self.UI_values['Planes']) )
        cmds.menuItem(self.Lights ,edit = True, checkBox=(self.UI_values['Lights']) )
        cmds.menuItem(self.Cameras ,edit = True, checkBox=(self.UI_values['Cameras']) )

        cmds.menuItem(self.Image_Planes ,edit = True, checkBox=(self.UI_values['Image_Planes']) )
        cmds.menuItem(self.Joints ,edit = True, checkBox=(self.UI_values['Joints']) )
        cmds.menuItem(self.IK_Handeles ,edit = True, checkBox=(self.UI_values['IK_Handeles']) )
        cmds.menuItem(self.Deformers ,edit = True, checkBox=(self.UI_values['Deformers']) )
        cmds.menuItem(self.Dynamics ,edit = True, checkBox=(self.UI_values['Dynamics']) )
        cmds.menuItem(self.Particle_Instances ,edit = True, checkBox=(self.UI_values['Particle_Instances']) )
        cmds.menuItem(self.Fluids ,edit = True, checkBox=(self.UI_values['Fluids']) )
        cmds.menuItem(self.Hair_Systems ,edit = True, checkBox=(self.UI_values['Hair_Systems']) )

        cmds.menuItem(self.Follicles ,edit = True, checkBox=(self.UI_values['Follicles']) )
        cmds.menuItem(self.nCloths ,edit = True, checkBox=(self.UI_values['nCloths']) )
        cmds.menuItem(self.nParticles ,edit = True, checkBox=(self.UI_values['nParticles']) )
        cmds.menuItem(self.nRigids ,edit = True, checkBox=(self.UI_values['nRigids']) )
        cmds.menuItem(self.Dynamic_Constraints ,edit = True, checkBox=(self.UI_values['Dynamic_Constraints']) )
        cmds.menuItem(self.Locators ,edit = True, checkBox=(self.UI_values['Locators']) )
        cmds.menuItem(self.Dimensions ,edit = True, checkBox=(self.UI_values['Dimensions']) )

        cmds.menuItem(self.Pivots ,edit = True, checkBox=(self.UI_values['Pivots']) )
        cmds.menuItem(self.Handles ,edit = True, checkBox=(self.UI_values['Handles']) )
        cmds.menuItem(self.Texture_Placements ,edit = True, checkBox=(self.UI_values['Texture_Placements']) )
        cmds.menuItem(self.Strokes ,edit = True, checkBox=(self.UI_values['Strokes']) )
        cmds.menuItem(self.Motion_Trails ,edit = True, checkBox=(self.UI_values['Motion_Trails']) )
        cmds.menuItem(self.Plugin_Shapes ,edit = True, checkBox=(self.UI_values['Plugin_Shapes']) )
        cmds.menuItem(self.Clip_Ghosts ,edit = True, checkBox=(self.UI_values['Clip_Ghosts']) )
        cmds.menuItem(self.Grease_Pencil,edit = True, checkBox=(self.UI_values['Grease_Pencil']) )

        cmds.menuItem(self.Gpu_Cache ,edit = True, checkBox=(self.UI_values['Gpu_Cache']) )
        cmds.menuItem(self.Manipulators ,edit = True, checkBox=(self.UI_values['Manipulators']) )
        cmds.menuItem(self.Grid ,edit = True, checkBox=(self.UI_values['Grid']) )
        cmds.menuItem(self.HUD ,edit = True, checkBox=(self.UI_values['HUD']) )
        cmds.menuItem(self.Hold_Outs,edit = True, checkBox=(self.UI_values['Hold_Outs']) )
        cmds.menuItem(self.Selecting_Highligting,edit = True, checkBox=(self.UI_values['Selecting_Highligting']) )
        cmds.intField( self.width, edit = True, value = int(self.UI_values['width']))
        cmds.intField( self.height, edit = True, value = int(self.UI_values['height']))
        cmds.intField( self.ratio, edit = True, value = int(self.UI_values['ratio']) )
        self.updateMAYA_ui_from_INI_data(INI_Path)

    def aspectRation(self, *args):
        width = self.query_UI_widget_values()[47]
        height = self.query_UI_widget_values()[46]
        apRatio = (  width  / height  )

    def maya_env_paths(self):
        allPaths = mel.eval('getenv "MAYA_SCRIPT_PATH"')
        allPaths = allPaths.split(';')
        dirVar = 'C:/Users/nitin.singh/Documents/maya/scripts'
        INI_filePath = []
        for path in allPaths:
            #print path
            if dirVar in path:
                INI_filePath.append(path)
        assetBalsterFilePath = os.path.join(INI_filePath[0], 'assBlaster.ini')

        if os.path.exists(assetBalsterFilePath):
            print ('.ini file exists')
        else:
            self.creatingNew_ini_File(assetBalsterFilePath)
        return assetBalsterFilePath

    def ini_FileToWriteValues(self, valuesType):
        if valuesType == 'default':
            val = [1,0,1,0,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,'YES',100,100,'Network', 1156, 2048, 1, 0]
        else:
            val = self.query_UI_widget_values()

        values = {}
        values = {  'Use_Default_Material'       : val[0],
                    'Hardware_Fog'               : val[1],
                    'play_in_RV'                 : val[2],
                    'WireFrame_On_shaded'        : val[3],
                    'NURBS_Curves'               : val[4],
                    'NURBS_Surface'              : val[5],
                    'NURBS_CVs'                  : val[6],
                    'NURBS_Hulls'                : val[7],
                    'Polygons'                   : val[8],

                    'Subdiv_Surfaces'            : val[9],
                    'Planes'                     : val[10],
                    'Lights'                     : val[11],
                    'Cameras'                    : val[12],
                    'Image_Planes'               : val[13],
                    'IK_Handeles'                : val[14],
                    'Joints'                     : val[15],
                    'Deformers'                  : val[16],
                    'Dynamics'                   : val[17],
                    'Particle_Instances'         : val[18],
                    'Fluids'                     : val[19],
                    'Hair_Systems'               : val[20],
                    'Follicles'                  : val[21],
                    'nCloths'                    : val[22],
                    'nParticles'                 : val[23],

                    'nRigids'                    : val[24],
                    'Dynamic_Constraints'        : val[25],
                    'Locators'                   : val[26],
                    'Dimensions'                 : val[27],
                    'Pivots'                     : val[28],
                    'Handles'                    : val[29],
                    'Texture_Placements'         : val[30],
                    'Strokes'                    : val[31],
                    'Motion_Trails'              : val[32],
                    'Plugin_Shapes'              : val[33],
                    'Clip_Ghosts'                : val[34],
                    'Grease_Pencil'              : val[35],
                    'Gpu_Cache'                  : val[36],
                    'Manipulators'               : val[37],
                    'Grid'                       : val[38],
                    'HUD'                        : val[39],
                    'Hold_Outs'                  : val[40],
                    'Selecting_Highligting'      : val[41],
                    'camera_frameRange_Update'   : val[42],
                    'Quality'                    : val[43],
                    'Scale'                      : val[44],
                    'PlayBlastDir'               : val[45],
                    'height'                     : val[46],
                    'width'                      : val[47],
                    'ratio'                      : val[48],
                    'motionBlur'                 : val[49]
                 }
        return  values
    def export_curent_UI_option(self, *args):
        currentValues = self.query_UI_widget_values()
        ini_filePath = self.maya_env_paths()
        with open(ini_filePath, 'w') as file:
            json.dump(self.ini_FileToWriteValues('custom'),file, sort_keys=True, indent=1)

    def reset_UI_To_default_option(self, *args):
        currentValues = self.query_UI_widget_values()
        ini_filePath = self.maya_env_paths()
        with open(ini_filePath, 'w') as file:
            json.dump(self.ini_FileToWriteValues('default'),file, sort_keys=True, indent=1)
        self.updatingWidgets()

    def query_UI_widget_values(self, *args):
        # gathering all the values of the tools from the UI
        Use_Default_Material = int(cmds.checkBox(self.Use_Default_Material, q = True, value = True))
        play_in_RV = int(cmds.checkBox(self.play_in_RV, q = True, value = True))
        Hardware_Fog = int(cmds.checkBox(self.Hardware_Fog, q = True, value = True))
        WireFrame_On_shaded = int(cmds.checkBox(self.WireFrame_On_shaded, q = True, value = True))
        NURBS_Curves = int(cmds.menuItem(self.NURBS_Curves, q = True, checkBox = True))
        NURBS_Surface = int(cmds.menuItem(self.NURBS_Surface, q = True, checkBox = True))
        NURBS_CVs = int(cmds.menuItem(self.NURBS_CVs, q = True, checkBox = True))
        NURBS_Hulls = int(cmds.menuItem(self.NURBS_Hulls, q = True, checkBox = True))
        Polygons = int(cmds.menuItem(self.Polygons, q = True, checkBox = True))
        Subdiv_Surfaces = int(cmds.menuItem(self.Subdiv_Surfaces, q = True, checkBox = True))
        Planes = int(cmds.menuItem(self.Planes, q = True, checkBox = True))
        Lights = int(cmds.menuItem(self.Lights, q = True, checkBox = True))
        Cameras = int(cmds.menuItem(self.Cameras, q = True, checkBox = True))
        Image_Planes = int(cmds.menuItem(self.Image_Planes, q = True, checkBox = True))
        Joints = int(cmds.menuItem(self.Joints, q = True, checkBox = True))
        IK_Handeles = int(cmds.menuItem(self.IK_Handeles, q = True, checkBox = True))
        Deformers = int(cmds.menuItem(self.Deformers, q = True, checkBox = True))
        Dynamics = int(cmds.menuItem(self.Dynamics, q = True, checkBox = True))
        Particle_Instances = int(cmds.menuItem(self.Particle_Instances, q = True, checkBox = True))

        Fluids = int(cmds.menuItem(self.Fluids, q = True, checkBox = True))
        Hair_Systems = int(cmds.menuItem(self.Hair_Systems, q = True, checkBox = True))
        Follicles = int(cmds.menuItem(self.Follicles, q = True, checkBox = True))
        nCloths = int(cmds.menuItem(self.nCloths, q = True, checkBox = True))
        nParticles = int(cmds.menuItem(self.nParticles, q = True, checkBox = True))
        nRigids = int(cmds.menuItem(self.nRigids, q = True, checkBox = True))
        Dynamic_Constraints = int(cmds.menuItem(self.Dynamic_Constraints, q = True, checkBox = True))
        Locators = int(cmds.menuItem(self.Locators, q = True, checkBox = True))
        Dimensions = int(cmds.menuItem(self.Dimensions, q = True, checkBox = True))

        Pivots = int(cmds.menuItem(self.Pivots, q = True, checkBox = True))
        Handles = int(cmds.menuItem(self.Handles, q = True, checkBox = True))
        Texture_Placements = int(cmds.menuItem(self.Texture_Placements, q = True, checkBox = True))
        Strokes = int(cmds.menuItem(self.Strokes, q = True, checkBox = True))
        Motion_Trails = int(cmds.menuItem(self.Motion_Trails, q = True, checkBox = True))
        Plugin_Shapes = int(cmds.menuItem(self.Plugin_Shapes, q = True, checkBox = True))
        Clip_Ghosts = int(cmds.menuItem(self.Clip_Ghosts, q = True, checkBox = True))
        Grease_Pencil = int(cmds.menuItem(self.Grease_Pencil, q = True, checkBox = True))
        Gpu_Cache = int(cmds.menuItem(self.Gpu_Cache, q = True, checkBox = True))

        Manipulators = int(cmds.menuItem(self.Manipulators, q = True, checkBox = True))
        Grid = int(cmds.menuItem(self.Grid, q = True, checkBox = True))
        HUD = int(cmds.menuItem(self.HUD, q = True, checkBox = True))
        Hold_Outs = int(cmds.menuItem(self.Hold_Outs, q = True, checkBox = True))
        Selecting_Highligting = int(cmds.menuItem(self.Selecting_Highligting, q = True, checkBox = True))
        timeRangeRadio = cmds.radioCollection(self.timeRangeRadio, q = True, select = True)
        qualitySlider = cmds.floatSliderGrp('quality_slider', q = True, value = True )
        scaleSlider = cmds.floatSliderGrp('scale_slider', q = True, value = True )

        PlayBlastDir = cmds.radioCollection(self.playblastPathRadioCollection, q = True, select = True)
        height = cmds.intField( self.height,q = True, value = True  )
        width = cmds.intField( self.width,q = True, value = True )
        ratio = cmds.intField( self.ratio,q = True, value = True )

        motion_Blur = int(cmds.menuItem(self.motion_Blur, q = True, checkBox = True))

        return (Use_Default_Material,play_in_RV,Hardware_Fog,WireFrame_On_shaded,NURBS_Curves,NURBS_Surface,NURBS_CVs,NURBS_Hulls,
                Polygons,Subdiv_Surfaces,Planes,Lights,Cameras,Image_Planes,Joints,IK_Handeles,Deformers,Dynamics,Particle_Instances,Fluids,Hair_Systems,
                Follicles,nCloths,nParticles,nRigids,Dynamic_Constraints,Locators,Dimensions,Pivots,Handles,Texture_Placements,Strokes,Motion_Trails,
                Plugin_Shapes,Clip_Ghosts,Grease_Pencil,Gpu_Cache,Manipulators,Grid,HUD,Hold_Outs,Selecting_Highligting,timeRangeRadio,qualitySlider,
                scaleSlider,PlayBlastDir, height, width, ratio, motion_Blur)

    def creatingNew_ini_File(self, Ini_filePath):
        with open(Ini_filePath, 'w') as file:
            json.dump(self.ini_FileToWriteValues('default'),file, sort_keys=True, indent=1)

    def reading_ini_file_values(self, Ini_filePath):
        with open(Ini_filePath, 'r') as file:
            jsondata = json.load(file)
        return jsondata


    def select_playBlastDir(self, *args):
        selectedDir = cmds.fileDialog2( dialogStyle=2, fileMode = 3)[0]
        selectedDir =  (selectedDir)
        cmds.textField(self.selectedPlayblastPath, edit = True, text=selectedDir )


    def run(self, *args):
        global UI
        UI = assblaster_log()
        UI.ui.show()

    def updateMAYA_ui_from_INI_data(self, *args):
        INI_Path = self.maya_env_paths()
        self.UI_values = self.reading_ini_file_values(INI_Path)
        #print ('--------------------------------------------------------------------------------------')
        #print self.UI_values
        #print ('--------------------------------------------------------------------------------------')

        mel.eval('optionVar -intValue playblastShowNURBSCurves %d; updatePlayblastMenus("playblastShowNURBSCurves", "showNurbsCurvesItemPB");'%self.UI_values['NURBS_Curves'])
        mel.eval('optionVar -intValue playblastShowNURBSSurfaces %d; updatePlayblastMenus("playblastShowNURBSSurfaces", "showNurbsSurfacesItemPB");'%self.UI_values['NURBS_Surface'])
        mel.eval('optionVar -intValue playblastShowCVs %d; updatePlayblastMenus("playblastShowCVs", "showNurbsCVsItemPB");'%self.UI_values['NURBS_CVs'])
        mel.eval('optionVar -intValue playblastShowHulls %d; updatePlayblastMenus("playblastShowHulls", "showNurbsHullsItemPB");'%self.UI_values['NURBS_Hulls'])
        mel.eval('optionVar -intValue playblastShowPolyMeshes %d; updatePlayblastMenus("playblastShowPolyMeshes", "showPolymeshesItemPB");'%self.UI_values['Polygons'])

        mel.eval('optionVar -intValue playblastShowSubdivSurfaces %d; updatePlayblastMenus("playblastShowSubdivSurfaces", "showSubdivSurfacesItemPB");'%self.UI_values['Subdiv_Surfaces'])
        mel.eval('optionVar -intValue playblastShowPlanes %d; updatePlayblastMenus("playblastShowPlanes", "showPlanesItemPB");'%self.UI_values['Planes'])
        mel.eval('optionVar -intValue playblastShowLights %d; updatePlayblastMenus("playblastShowLights", "showLightsItemPB");'%self.UI_values['Lights'])
        mel.eval('optionVar -intValue playblastShowCameras %d; updatePlayblastMenus("playblastShowCameras", "showCamerasItemPB");'%self.UI_values['Cameras'])
        mel.eval('optionVar -intValue playblastShowImagePlane %d; updatePlayblastMenus("playblastShowImagePlane", "showImagePlaneItemPB");'%self.UI_values['Image_Planes'])
        mel.eval('optionVar -intValue playblastShowJoints %d; updatePlayblastMenus("playblastShowJoints", "showJointsItemPB");'%self.UI_values['Joints'])

        mel.eval('optionVar -intValue playblastShowIKHandles %d; updatePlayblastMenus("playblastShowIKHandles", "showIkHandlesItemPB");'%self.UI_values['IK_Handeles'])
        mel.eval('optionVar -intValue playblastShowDeformers %d; updatePlayblastMenus("playblastShowDeformers", "showDeformersItemPB");'%self.UI_values['Deformers'])
        mel.eval('optionVar -intValue playblastShowDynamics %d; updatePlayblastMenus("playblastShowDynamics", "showDynamicsItemPB");'%self.UI_values['Dynamics'])
        mel.eval('optionVar -intValue playblastShowParticleInstancers %d; updatePlayblastMenus("playblastShowParticleInstancers", "showParticleInstancersItemPB");'%self.UI_values['Particle_Instances'])
        mel.eval('optionVar -intValue playblastShowFluids %d; updatePlayblastMenus("playblastShowFluids", "showFluidsItemPB");'%self.UI_values['Fluids'])

        mel.eval('optionVar -intValue playblastShowHairSystems %d; updatePlayblastMenus("playblastShowHairSystems", "showHairSystemsItemPB");'%self.UI_values['Hair_Systems'])
        mel.eval('optionVar -intValue playblastShowFollicles %d; updatePlayblastMenus("playblastShowFollicles", "showFolliclesItemPB");'%self.UI_values['Follicles'])
        mel.eval('optionVar -intValue playblastShowNCloths %d; updatePlayblastMenus("playblastShowNCloths", "showNClothsItemPB");'%self.UI_values['nCloths'])
        mel.eval('optionVar -intValue playblastShowNParticles %d; updatePlayblastMenus("playblastShowNParticles", "showNParticlesItemPB");'%self.UI_values['nParticles'])
        mel.eval('optionVar -intValue playblastShowNRigids %d; updatePlayblastMenus("playblastShowNRigids", "showNRigidsItemPB");'%self.UI_values['nRigids'])

        mel.eval('optionVar -intValue playblastShowDynamicConstraints %d; updatePlayblastMenus("playblastShowDynamicConstraints", "showDynamicConstraintsItemPB");'%self.UI_values['Dynamic_Constraints'])
        mel.eval('optionVar -intValue playblastShowLocators %d; updatePlayblastMenus("playblastShowLocators", "showLocatorsItemPB");'%self.UI_values['Locators'])
        mel.eval('optionVar -intValue playblastShowDimensions %d; updatePlayblastMenus("playblastShowDimensions", "showDimensionsItemPB");'%self.UI_values['Dimensions'])
        mel.eval('optionVar -intValue playblastShowPivots %d; updatePlayblastMenus("playblastShowPivots", "showPivotsItemPB");'%self.UI_values['Pivots'])
        mel.eval('optionVar -intValue playblastShowHandles %d; updatePlayblastMenus("playblastShowHandles", "showHandlesItemPB");'%self.UI_values['Handles'])

        mel.eval('optionVar -intValue playblastShowTextures %d; updatePlayblastMenus("playblastShowTextures", "showTexturesItemPB");'%self.UI_values['Texture_Placements'])
        mel.eval('optionVar -intValue playblastShowStrokes %d; updatePlayblastMenus("playblastShowStrokes", "showStrokesItemPB");'%self.UI_values['Strokes'])
        mel.eval('optionVar -intValue playblastShowMotionTrails %d; updatePlayblastMenus("playblastShowMotionTrails", "showMotionTrailsItemPB");'%self.UI_values['Motion_Trails'])
        mel.eval('optionVar -intValue playblastShowPluginShapes %d; updatePlayblastMenus("playblastShowPluginShapes", "showPluginShapesItemPB");'%self.UI_values['Plugin_Shapes'])

        mel.eval('optionVar -intValue playblastShowClipGhosts %d; updatePlayblastMenus("playblastShowClipGhosts", "showClipGhostsItemPB");'%self.UI_values['Clip_Ghosts'])
        mel.eval('optionVar -intValue playblastShowGreasePencil %d; updatePlayblastMenus("playblastShowGreasePencil", "showGreasePencilItemPB");'%self.UI_values['Grease_Pencil'])
        mel.eval('togglePlayblastMenuItem gpuCacheDisplayFilter %d; updatePlayblastPluginMenus();'%self.UI_values['Gpu_Cache'])
        mel.eval('optionVar -intValue playblastShowGrid %d; updatePlayblastMenus("playblastShowGrid", "showGridItemPB");'%self.UI_values['Grid'])
        mel.eval('optionVar -intValue playblastShowHUD %d; updatePlayblastMenus("playblastShowHUD", "showHUDItemPB");'%self.UI_values['HUD'])

        mel.eval('optionVar -intValue playblastShowHoldOuts %d; updatePlayblastMenus("playblastShowHoldOuts", "showHoldOutsItemPB");'%self.UI_values['Hold_Outs'])
        mel.eval('optionVar -intValue playblastShowSelectionHighlighting %d; updatePlayblastMenus("playblastShowSelectionHighlighting", "showSelectionItemPB");'%self.UI_values['Selecting_Highligting'])

    def query_modelEditor(self, widgetName, typeName, uiWidgetName):
        #print widgetName
        varname = uiWidgetName
        value = getattr(self, varname)
        queryWidgeState = int(cmds.menuItem(value, q = True, checkBox = True))
        val = queryWidgeState
        # reverting the existing state with lambda
        #state = (lambda val: 0 if val else 1)
        #state = state(val)
        mel.eval('optionVar -intValue %s %d; updatePlayblastMenus("%s", "%s");'% (widgetName, queryWidgeState, widgetName, typeName))

    def updatePlayblast_GUP_option(self, *args):
        GPU_cacheOptionvalue = int(cmds.menuItem(self.Gpu_Cache, q = True, checkBox = True))
        mel.eval('togglePlayblastMenuItem gpuCacheDisplayFilter %s; updatePlayblastPluginMenus();'%GPU_cacheOptionvalue)

    def filePathFixed(self, path):
        if platform.system()=='Windows':
            filePath = path
            separator = os.path.normpath("/")
            newPath = re.sub(re.escape(separator), "/", filePath)
            return newPath
        else:
            return filePath

    def playBlast(self, *args):
        val = cmds.radioCollection(self.playblastPathRadioCollection, q = True, select = True)

        if val == 'Project':
            print 'project'
            self.projectPathSelection('project')
            exportDir = cmds.textField(self.selectedPlayblastPath, q = True , text = True)
            exportFileName = cmds.textField(self.playblastname, q = True , text = True)
            if  exportDir == 'Save file on Network':
                print ('filePath is invalid')
            else:
                self.executePlayblast(exportDir, exportFileName)

        if val == 'Network':
            print 'network'
            self.projectPathSelection('network')
            exportDir = cmds.textField(self.selectedPlayblastPath, q = True , text = True)
            if  exportDir == 'Save file on Network':
                print ('filePath is invalid')
            else:
                exportName = cmds.textField(self.playblastname, q = True , text = True).lstrip()
                if exportName == 'Error :':
                    print ('filePath is invalid')
                else:
                    self.executePlayblast(exportDir, exportName)

        if val == 'Local':
            exportDir = cmds.textField(self.selectedPlayblastPath, q = True , text = True)
            if os.path.exists(exportDir):
                exportName = cmds.textField(self.playblastname, q = True , text = True).lstrip()
                if exportName == '':
                    print 'no name give'
                else:
                    self.executePlayblast(exportDir, exportName)
            else:
                print('please select a dir for the playoblast ')
        else:
            pass

    def percentage(self, percent, whole):
      return (percent * whole) / 100.0

    def executePlayblast(self, exportDir, exportFileName, *args):
        exportpath = os.path.join(exportDir, exportFileName)

        # reading UI values
        self.value = self.query_UI_widget_values()
        firstFrame = cmds.intField( self.firstFrame, q = True, value =  True)
        lastFrame =  cmds.intField( self.lastFrame, q = True, value =  True)
        qualitySlider = self.value[43]
        scaleSlider = self.value[44]
        offScreen = self.value[1]
        height = self.value[46]
        width = self.value[47]
        playBlastCamera = cmds.optionMenu( self.SceneCams, q = True, value =  True)
        currentAttr = mel.eval('getAttr "defaultRenderGlobals.imageFormat";')
        exportAttr = mel.eval('setAttr "defaultRenderGlobals.imageFormat" 8;')

        if os.path.isdir(exportDir):
            pbo = self.query_UI_widget_values()
            window = cmds.window(title = exportDir, menuBarVisible=False, titleBar=False, visible=True
                                ,w= int(self.percentage(scaleSlider,(width/2)))
                                ,h = int(self.percentage(scaleSlider,(height/2)))
                                ,sizeable= False)

            cmds.paneLayout(configuration = 'single', noBackground = False
                            ,w= int(self.percentage(scaleSlider,(width/2)))
                            ,h = int(self.percentage(scaleSlider,(height/2))))

            panel = cmds.modelPanel(menuBarVisible=False,label='CapturePanel')
            bar_layout = cmds.modelPanel(panel, q=True, barLayout=True)
            cmds.frameLayout(bar_layout, edit=True, collapse=True, w= int(self.percentage(scaleSlider,(width/2))))
            cmds.showWindow(window)

            assBlasterEditor = cmds.modelPanel(panel, query=True, modelEditor=True)
            cmds.modelEditor(assBlasterEditor, edit=True, activeView=True, camera = playBlastCamera, displayAppearance='smoothShaded'
            ,useDefaultMaterial     = self.value[0]
            ,fogging                = self.value[2]
            ,wireframeOnShaded      = self.value[3]
            ,nurbsCurves            = self.value[4]
            ,nurbsSurfaces          = self.value[5]
            ,controlVertices        = self.value[6]
            ,hulls                  = self.value[7]
            ,polymeshes             = self.value[8]
            ,subdivSurfaces         = self.value[9]
            ,planes                 = self.value[10]
            ,lights                 = self.value[11]
            ,cameras                = self.value[12]
            ,imagePlane             = self.value[13]
            ,joints                 = self.value[14]
            ,ikHandles              = self.value[15]
            ,deformers              = self.value[16]
            ,dynamics               = self.value[17]
            ,nParticles             = self.value[18]
            ,fluids                 = self.value[19]
            ,hairSystems            = self.value[20]
            ,follicles              = self.value[21]
            ,nCloths                = self.value[22]
            ,nRigids                = self.value[24]
            ,dynamicConstraints     = self.value[25]
            ,locators               = self.value[26]
            ,dimensions             = self.value[27]
            ,pivots                 = self.value[28]
            ,handles                = self.value[29]
            ,displayTextures        = self.value[30]
            ,strokes                = self.value[31]
            ,motionTrails           = self.value[32]
            ,pluginShapes           = self.value[33]
            ,manipulators           = self.value[37]
            ,grid                   = self.value[38]
            ,headsUpDisplay         = self.value[39]
            ,selectionHiliteDisplay = self.value[41])
            # Force a draw refresh of Maya so it keeps focus on the new panel
            # This focus is required to force preview playback in the independent panel
            cmds.refresh(force=True)
            cmds.playblast( format = 'image',
                            filename = exportpath,
                            clearCache = 1,
                            viewer = False,
                            height = height,
                            width = width,
                            showOrnaments = True,
                            startTime = firstFrame,
                            endTime =  lastFrame,
                            quality = qualitySlider,
                            offScreen = False,
                            fp = 4,
                            percent = scaleSlider)
            # Delete the panel to fix memory leak (about 5 mb per capture)
            cmds.deleteUI(panel, panel=True)
            cmds.deleteUI(window)

            currentDT = datetime.datetime.now()
            userDir = self.UserDir

            userName = getpass.getuser()
            logDir = self.filePathFixed(os.path.join(userDir, userName, 'assBlaster_Logs'))
            if os.path.exists(logDir):
                pass
            else:
                os.mkdir(logDir)
            logFilePath = os.path.join(logDir, 'assBlasterLog.txt')
            print logFilePath
            print logFilePath
            date = (currentDT.strftime("%Y/%m/%d"))
            time = (currentDT.strftime("%I:%M:%S %p"))
            res = (str(width)+' X '+str(height))
            range =  (str(firstFrame)+' - '+str(lastFrame))
            sequenceName = 'FRZW'
            shotNumber = 'FRZW_1021'
            cameraName = playBlastCamera
            self.updateAssBlasterLogFile( logFilePath, exportFileName, date, time, res,range ,self.filePathFixed(exportpath), sequenceName, shotNumber, cameraName)
            mel.eval('setAttr "defaultRenderGlobals.imageFormat" %s;'%currentAttr)
            play_in_RV = int(cmds.checkBox(self.play_in_RV, q = True, value = True))
            if play_in_RV == True:
                sequencepath = self.filePathFixed(exportpath+'.@@@@.jpg')
                rv = str(self.rvDir + '/bin/rv.exe')
                RVDirShortName = rv.replace("Program Files", "Progra~1")
                os.system("start " + RVDirShortName + " " + sequencepath)


        else:
            print ('Selected DIR doesnt exists')


    def updateAssBlasterLogFile(self, logFilePath, exportFileName, date, time, res, range ,exportpath, sequenceName, shotNumber, cameraName ):
        newVal = [exportFileName, date, time, res, range, exportpath, sequenceName, shotNumber, cameraName]
        #converting everything to unicdoe to be used propery between windows and liux
        newVal = [i.decode('UTF-8') if isinstance(i, basestring) else i for i in newVal]
        existing_log_list = self.readingexistingsLOGs(logFilePath)
        dicts = {}
        values = sorted(existing_log_list)
        values.append(newVal)
        overWriteval = []
        if values:
            for i, listName in enumerate(values, 1):
                #print i, listName
                if listName[5] == newVal[5]:
                    if listName == newVal:
                        dicts[i] = listName
                    else:
                        pass
                else:
                    dicts[i] = listName

        with open(os.path.join(logFilePath), 'w') as file:
            json.dump(dicts,file)

    def readingexistingsLOGs(self,logFilePath, *args):
        dicts = {}
        logFile = os.path.join(logFilePath)
        fileCheck = os.path.isfile(logFile)
        if fileCheck == True:
            pass
        else:
            with open(os.path.join(logFile), 'w') as file:
                json.dump(dicts,file)

        with open(logFile, 'r') as file:
            jsondata = json.load(file)
        existingList = []
        for key, value in jsondata.iteritems():
            #print key, value
            existingList.append(value)
        return existingList

    def updateFrameRange_RadioClick(self, *args):
        cameraName = self.getCamera()
        self.updateframeRangeFromCamera(cameraName)

    def refresh_cameraOptionMenu(self, *args):
        currentameraName = cmds.optionMenu( self.SceneCams, q = True, value =  True)
        allExistingCameras = self.cam_loader()
        for item in cmds.optionMenu(self.SceneCams , q=True, ill=True) or []:cmds.deleteUI(item)
        for item in self.cam_loader():cmds.menuItem(label = item, parent = self.SceneCams)
        if cmds.objExists(currentameraName):cmds.optionMenu(self.SceneCams, e=True, v = currentameraName )

    def edit_options(self, *args ):
        allExistingCameras = self.cam_loader()
        for item in cmds.optionMenu(self.SceneCams , q=True, ill=True) or []:cmds.deleteUI(item)
        for item in self.cam_loader():cmds.menuItem(label = item, parent = self.SceneCams)

    def assBlasterUI(self):
        INI_Path = self.maya_env_paths()
        self.UI_values = self.reading_ini_file_values(INI_Path)
        if cmds.dockControl('assBlaster', query=True, exists=True):
            cmds.deleteUI('assBlaster', control=True)
        if cmds.window('Scene_Manager', query=True, exists=True):
            cmds.deleteUI('Scene_Manager', window=True)

        snapFunction = cmds.window(backgroundColor = [0.15, 0.15, 0.15])
        cmds.rowColumnLayout(numberOfRows=1)
        #self.updateMAYA_ui_from_INI_data(INI_Path)
        cmds.button(w=15, h=50, bgc=(.01, .01, .01), label='', enable=False)
        btn01 = cmds.symbolButton(image=self.btn01_icon, w=100, h=50,ann='swap a', c = self.playblastGridHide)
        cmds.button(w=15, h=50, bgc=(.01, .01, .01), label='', enable=False)
        btn02 = cmds.symbolButton(image=self.btn02_icon, w=100, h=50,ann='sed', c = self.toggleImagePlane)
        cmds.button(w=15, h=50, bgc=(.01, .01, .01), label='', enable=False)
        btn03 = cmds.symbolButton(image=self.btn03_icon, w=100, h=50,ann='create n ', c = self.toggleResGate)
        cmds.button(w=15, h=50, bgc=(.01, .01, .01), label='', enable=False)
        btn04 = cmds.symbolButton(image=self.btn04_icon, w=100, h=50,ann='creatt ', c = self.hideAllButGeo )
        cmds.button(w=15, h=50, bgc=(.01, .01, .01), label='', enable=False)
        btn05 = cmds.symbolButton(image=self.btn05_icon, w=100, h=50,ann='create n', c = self.changeBackgroundColor )
        cmds.button(w=15, h=50, bgc=(.01, .01, .01), label='', enable=False, enableBackground = False)
        cmds.rowColumnLayout(numberOfRows=2, rowHeight=[(1, 30), (2, 30)])
        #savedPrefs for UI
        wireframe = self.UI_values['WireFrame_On_shaded']
        useDefaultmaterial = self.UI_values['Use_Default_Material']
        hardwareFog = self.UI_values['Hardware_Fog']
        wireFramevalue = []
        defMatValue = []
        hardwareFogValue = []
        if wireframe == 1:
            self.toggleWireframeViewport_currentval('enable')
            wireFramevalue.append(1)
        if wireframe == 0:
            self.toggleWireframeViewport_currentval('disable')
            wireFramevalue.append(0)
        #print useDefaultmaterial
        if useDefaultmaterial == 1:
            self.defMatValue('enable')
            defMatValue.append(1)
        if useDefaultmaterial == 0:
            self.defMatValue('disable')
            defMatValue.append(0)
        if hardwareFog == 1:
            self.defHardwareFogValue('enable')
            hardwareFogValue.append(1)
        if hardwareFog == 0:
            self.defHardwareFogValue('disable')
            hardwareFogValue.append(0)

        self.Use_Default_Material = cmds.checkBox(label='Use Default Material', align='left', editable=True, value=defMatValue[0], cc = self.toggleDefMaterial )
        self.WireFrame_On_shaded  = cmds.checkBox(label='WireFrame on Shaded ', align='left', editable=True, value=wireFramevalue[0], cc = self.toggleWireframe)
        cmds.rowColumnLayout(numberOfRows=1, rowHeight=[(1, 30)])
        self.Hardware_Fog  = cmds.checkBox(label='Hardware Fog', align='left', editable=True, value=hardwareFogValue[0], cc = self.toggleHardwareFOG  )
        self.fogReduceButton = cmds.button('fogReduce',label = '-', w = 20, h = 5, bgc=(.55, .25, .25), c = self.increaseFog)
        self.fogAddButton    = cmds.button('fogAdd',label = '+', w = 20, h = 5, bgc=(.25, .55, .25), c = self.reduceFog)
        self.fogColorButton  = cmds.button('fogColor',label = 'C\nL', w = 20, h = 5, bgc=(.55, .55, .55), c = self.changeFogColor)
        cmds.setParent('..')
        self.play_in_RV = cmds.checkBox( label='Play finished render in RV    ',align='left', editable=True , value=(self.UI_values['play_in_RV']), enable=True )
        # updating butons status for FOG
        if hardwareFog == 1:
            cmds.button( self.fogReduceButton, e = True , enable = True, bgc=(.55, .25, .25) )
            cmds.button( self.fogAddButton, e = True , enable = True, bgc=(.25, .55, .25) )
            cmds.button( self.fogColorButton, e = True , enable = True, bgc=(.55, .55, .55) )

        if hardwareFog == 0:
            cmds.button( self.fogReduceButton, e = True , enable = False, bgc=(.22, .22, .22) )
            cmds.button( self.fogAddButton, e = True , enable = False, bgc=(.22, .22, .22) )
            cmds.button( self.fogColorButton, e = True , enable = False, bgc=(.22, .22, .22) )

        PlayblastMenu = cmds.button(w=100, h=60, bgc=(.25, .25, .25), label='PlayBlast (only)\nViewport\nOptions ', enable=True )
        popup2 = cmds.popupMenu(parent=PlayblastMenu, button=1)
        cmds.menuItem( divider=True )
        cmds.menuItem( label='Save My Settings',c=self.export_curent_UI_option)
        #cmds.menuItem( label='Save My Settings', c = self.query_UI_widget_values)
        cmds.menuItem( label='Reset to Default Tool Settings', c=self.reset_UI_To_default_option )
        cmds.menuItem( divider=True )
        #self.NURBS_Curves = cmds.menuItem( label='NURBS Curves', checkBox=(self.UI_values['NURBS_Curves']) )
        self.motion_Blur = cmds.menuItem( label='Motion Blur', checkBox=(self.UI_values['motionBlur']), optionBox=True,  enable=False )
        cmds.menuItem( optionBox=True )
        cmds.menuItem( divider=True )

        self.NURBS_Curves = cmds.menuItem( label='NURBS Curves', checkBox=(self.UI_values['NURBS_Curves'])
        , c=lambda x: self.query_modelEditor('playblastShowNURBSCurves','showNurbsCurvesItemPB','NURBS_Curves' ) )

        self.NURBS_Surface =cmds.menuItem( label='NURBS Surface', checkBox=(self.UI_values['NURBS_Surface'])
        , c=lambda x: self.query_modelEditor('playblastShowNURBSSurfaces','showNurbsSurfacesItemPB','NURBS_Surface' ) )

        self.NURBS_CVs =cmds.menuItem( label='NURBS CVs', checkBox=(self.UI_values['NURBS_CVs'])
        , c=lambda x: self.query_modelEditor('playblastShowCVs','showNurbsCVsItemPB','NURBS_CVs' ) )

        self.NURBS_Hulls =cmds.menuItem( label='NURBS Hulls', checkBox=(self.UI_values['NURBS_Hulls'])
        , c=lambda x: self.query_modelEditor('playblastShowHulls','showNurbsHullsItemPB','NURBS_Hulls' ) )

        self.Polygons =cmds.menuItem( label='Polygons', checkBox=(self.UI_values['Polygons'])
        , c=lambda x: self.query_modelEditor('playblastShowPolyMeshes','showPolymeshesItemPB','Polygons' ) )

        self.Subdiv_Surfaces =cmds.menuItem( label='Subdiv Surfaces', checkBox=(self.UI_values['Subdiv_Surfaces'])
        , c=lambda x: self.query_modelEditor('playblastShowSubdivSurfaces','showSubdivSurfacesItemPB','Subdiv_Surfaces' ) )

        self.Planes =cmds.menuItem( label='Planes', checkBox=(self.UI_values['Planes'])
        , c=lambda x: self.query_modelEditor('playblastShowPlanes','showPlanesItemPB','Planes' ) )

        self.Lights =cmds.menuItem( label='Lights', checkBox=(self.UI_values['Lights'])
        , c=lambda x: self.query_modelEditor('playblastShowLights','showLightsItemPB','Lights' ) )

        self.Cameras =cmds.menuItem( label='Cameras', checkBox=(self.UI_values['Cameras'])
        , c=lambda x: self.query_modelEditor('playblastShowCameras','showCamerasItemPB','Cameras' ) )

        self.Image_Planes =cmds.menuItem( label='Image Planes', checkBox=(self.UI_values['Image_Planes'])
        , c=lambda x: self.query_modelEditor('playblastShowImagePlane','showImagePlaneItemPB','Image_Planes' ) )

        self.Joints =cmds.menuItem( label='Joints', checkBox=(self.UI_values['Joints'])
        , c=lambda x: self.query_modelEditor('playblastShowJoints','showJointsItemPB','Joints' ) )

        self.IK_Handeles =cmds.menuItem( label='IK Handeles', checkBox=(self.UI_values['IK_Handeles'])
        , c=lambda x: self.query_modelEditor('playblastShowIKHandles','showIkHandlesItemPB','IK_Handeles' ) )

        self.Deformers =cmds.menuItem( label='Deformers', checkBox=(self.UI_values['Deformers'])
        , c=lambda x: self.query_modelEditor('playblastShowDeformers','showDeformersItemPB','Deformers' ) )

        self.Dynamics =cmds.menuItem( label='Dynamics', checkBox=(self.UI_values['Dynamics'])
        , c=lambda x: self.query_modelEditor('playblastShowDynamics','showDynamicsItemPB','Dynamics' ) )

        self.Particle_Instances =cmds.menuItem( label='Particle Instances', checkBox=(self.UI_values['Particle_Instances'])
        , c=lambda x: self.query_modelEditor('playblastShowParticleInstancers','showParticleInstancersItemPB','Particle_Instances' ) )

        self.Fluids =cmds.menuItem( label='Fluids', checkBox=(self.UI_values['Fluids'])
        , c=lambda x: self.query_modelEditor('playblastShowFluids','showFluidsItemPB','Fluids' ) )

        self.Hair_Systems =cmds.menuItem( label='Hair Systems', checkBox=(self.UI_values['Hair_Systems'])
        , c=lambda x: self.query_modelEditor('playblastShowHairSystems','showHairSystemsItemPB','Hair_Systems' ) )

        self.Follicles =cmds.menuItem( label='Follicles', checkBox=(self.UI_values['Follicles'])
        , c=lambda x: self.query_modelEditor('playblastShowFollicles','showFolliclesItemPB','Follicles' ) )

        self.nCloths =cmds.menuItem( label='nCloths', checkBox=(self.UI_values['nCloths'])
        , c=lambda x: self.query_modelEditor('playblastShowNCloths','showNClothsItemPB','nCloths' ) )

        self.nParticles =cmds.menuItem( label='nParticles', checkBox=(self.UI_values['nParticles'])
        , c=lambda x: self.query_modelEditor('playblastShowNParticles','showNParticlesItemPB','nParticles' ) )

        self.nRigids =cmds.menuItem( label='nRigids', checkBox=(self.UI_values['nRigids'])
        , c=lambda x: self.query_modelEditor('playblastShowNRigids','showNRigidsItemPB','nRigids' ) )

        self.Dynamic_Constraints =cmds.menuItem( label='Dynamic Constraints', checkBox=(self.UI_values['Dynamic_Constraints'])
        , c=lambda x: self.query_modelEditor('playblastShowDynamicConstraints','showDynamicConstraintsItemPB','Dynamic_Constraints' ) )

        self.Locators =cmds.menuItem( label='Locators', checkBox=(self.UI_values['Locators'])
        , c=lambda x: self.query_modelEditor('playblastShowLocators','showLocatorsItemPB','Locators' ) )

        self.Dimensions =cmds.menuItem( label='Dimensions', checkBox=(self.UI_values['Dimensions'])
        , c=lambda x: self.query_modelEditor('playblastShowDimensions','showDimensionsItemPB','Dimensions' ) )

        self.Pivots =cmds.menuItem( label='Pivots', checkBox=(self.UI_values['Pivots'])
        , c=lambda x: self.query_modelEditor('playblastShowPivots','showPivotsItemPB','Pivots' ) )

        self.Handles =cmds.menuItem( label='Handles', checkBox=(self.UI_values['Handles'])
        , c=lambda x: self.query_modelEditor('playblastShowHandles','showHandlesItemPB','Handles' ) )

        self.Texture_Placements =cmds.menuItem( label='Texture Placements', checkBox=(self.UI_values['Texture_Placements'])
        , c=lambda x: self.query_modelEditor('playblastShowTextures','showTexturesItemPB','Texture_Placements' ) )

        self.Strokes =cmds.menuItem( label='Strokes', checkBox=(self.UI_values['Strokes'])
        , c=lambda x: self.query_modelEditor('playblastShowStrokes','showStrokesItemPB','Strokes' ) )

        self.Motion_Trails =cmds.menuItem( label='Motion Trails', checkBox=(self.UI_values['Motion_Trails'])
        , c=lambda x: self.query_modelEditor('playblastShowMotionTrails','showMotionTrailsItemPB','Motion_Trails' ) )

        self.Plugin_Shapes =cmds.menuItem( label='Plugin Shapes', checkBox=(self.UI_values['Plugin_Shapes'])
        , c=lambda x: self.query_modelEditor('playblastShowPluginShapes','showPluginShapesItemPB','Plugin_Shapes' ) )

        self.Clip_Ghosts =cmds.menuItem( label='Clip Ghosts', checkBox=(self.UI_values['Clip_Ghosts'])
        , c=lambda x: self.query_modelEditor('playblastShowClipGhosts','showClipGhostsItemPB','Clip_Ghosts' ) )

        self.Grease_Pencil =cmds.menuItem( label='Grease Pencil', checkBox=(self.UI_values['Grease_Pencil'])
        , c=lambda x: self.query_modelEditor('playblastShowGreasePencil','showGreasePencilItemPB','Grease_Pencil' ) )

        self.Gpu_Cache =cmds.menuItem( label='Gpu Cache', checkBox=(self.UI_values['Gpu_Cache']), c=self.updatePlayblast_GUP_option )

        self.Manipulators =cmds.menuItem( label='Manipulators', checkBox=(self.UI_values['Manipulators']) )

        self.Grid =cmds.menuItem( label='Grid', checkBox=(self.UI_values['Grid'])
        , c=lambda x: self.query_modelEditor('playblastShowGrid','showGridItemPB','Grid' ) )

        self.HUD =cmds.menuItem( label='HUD', checkBox=(self.UI_values['HUD'])
        , c=lambda x: self.query_modelEditor('playblastShowHUD','showHUDItemPB','HUD' ) )

        self.Hold_Outs =cmds.menuItem( label='Hold-Outs', checkBox=(self.UI_values['Hold_Outs'])
        , c=lambda x: self.query_modelEditor('playblastShowHoldOuts','showHoldOutsItemPB','Hold_Outs' ) )

        self.Selecting_Highligting =cmds.menuItem( label='Selecting Highligting', checkBox=(self.UI_values['Selecting_Highligting'])
        , c=lambda x: self.query_modelEditor('playblastShowSelectionHighlighting','showSelectionItemPB','Selecting_Highligting' ) )

        cmds.rowLayout(adjustableColumn=True)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=1)
        cmds.button(w=15, h=60, bgc=(.01, .01, .01), label='', enable=False, enableBackground = False)
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=4, rowHeight=[(1, 30), (1, 30)])
        cmds.rowColumnLayout(numberOfRows=1, rowHeight=[(1, 30)])
        self.SceneCams = cmds.optionMenu('camera_all',  label='Cameras :', changeCommand = self.lookThrougCamera, backgroundColor = [0.25, 0.25, 0.25], h = 30, w = 230 )
        cmds.button(label = 'R', w = 20, h = 11, bgc=(.25, .55, .25), c = self.refresh_cameraOptionMenu)
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=1, rowHeight=[(2, 30)])
        cmds.button(label = '', w = 250, h = 2, bgc=(.25, .55, .25), enable=False)
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=1, rowHeight=[(2, 30)])
        cmds.text( label='Update Range: ' , font = 'boldLabelFont')
        self.timeRangeRadio = cmds.radioCollection()
        yes_range = cmds.radioButton('YES', label='YES ' , onCommand = self.updateFrameRange_RadioClick)
        no_range = cmds.radioButton('NO',  label='NO  ' )
        self.firstFrame = cmds.intField( ' firstFrame', w = 38 )
        self.lastFrame = cmds.intField( ' lastFrame' , w = 38 )
        self.timeRangeRadio = cmds.radioCollection( self.timeRangeRadio, edit=True, select=str(self.UI_values['camera_frameRange_Update']) )
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=1, rowHeight=[(2, 30)])
        cmds.button(label = '', w = 250, h = 2, bgc=(.25, .55, .25), enable=False)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=1)
        cmds.button(w=15, h=60, bgc=(.01, .01, .01), label='', enable=False, enableBackground = False)
        cmds.rowColumnLayout(numberOfRows=2, rowHeight=[(1, 30), (2, 30)])
        cmds.text( label='  Quality:  ' , font = 'boldLabelFont')
        cmds.text( label='  Scale  :  ' , font = 'boldLabelFont')
        self.qualitySlider = cmds.floatSliderGrp('quality_slider', field=True, minValue=10, maxValue=100, h = 35,value = float(self.UI_values['Quality']) )
        self.scaleSlider = cmds.floatSliderGrp('scale_slider', field=True, minValue=0.0, maxValue=100.0, h = 35,value = float(self.UI_values['Scale']) )
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=1)
        cmds.button(w=15, h=60, bgc=(.01, .01, .01), label='', enable=False, enableBackground = False)
        cmds.rowColumnLayout(numberOfRows=3, rowHeight=[(1, 20), (2, 20), (3, 20)])
        cmds.text( label=' Height :' , font = 'boldLabelFont')
        cmds.text( label=' Width  :' , font = 'boldLabelFont')
        cmds.text( label=' Ratio  :' , font = 'boldLabelFont', enable = False)
        self.width = cmds.intField( 'width',w = 38 , h = 20, editable = True, value=int(self.UI_values['width']), enterCommand = self.aspectRation )
        self.height = cmds.intField('height', w = 38  ,h = 20, editable = True, value=int(self.UI_values['height']), enterCommand = self.aspectRation )
        self.ratio = cmds.intField('ratio',h = 20, w = 38  , editable = True, value=int(self.UI_values['ratio']), enable = False)
        self.edit_options(self.SceneCams)
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=1)
        cmds.button(w=15, h=60, bgc=(.01, .01, .01), label='', enable=False, enableBackground = False)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=2, rowHeight=[(1, 30), (1, 30)])
        cmds.rowColumnLayout(numberOfRows=1, rowHeight=[(1, 30)])
        cmds.text( label='  playBlast Dir path         :  ' , font = 'boldLabelFont')
        self.playblastPathRadioCollection =cmds.radioCollection()
        self.project_radio_btn = cmds.radioButton('Project', label='Project        ', onCommand = self.projectRadioButtonDef)
        self.network_radio_btn = cmds.radioButton('Network',  label='Network        ', onCommand = self.networkRadioButtonDef )
        self.local_radio_btn = cmds.radioButton('Local',  label=' Local          ', onCommand = self.localRadioButtonDef)
        self.selectFolderBtn = cmds.button(label = 'select Folder', w = 180, h = 11, c = self.select_playBlastDir)
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=1, rowHeight=[(2, 30)])
        self.selectedPlayblastPath = cmds.textField('playBlastDir', text='path', w = 390, h = 28 )
        self.playblastname = cmds.textField('filename', text='FileName', w = 180 )
        self.playblastPathRadioCollection = cmds.radioCollection( self.playblastPathRadioCollection, edit=True, select=str(self.UI_values['PlayBlastDir']) )
        cmds.setParent('..')
        btn06 = cmds.symbolButton(image=self.btn06_icon, w=100, h=60,ann='create ', c = self.playBlast )
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=1, rowHeight=[(2, 30)])
        cmds.button(w=15, h=60, bgc=(.01, .01, .01), label='', enable=False, enableBackground = False)
        cmds.button(w=30, h=60, bgc=(.55, .88, .13), label='O  L\nL  O\nD  G', enable=True, enableBackground = False, c = self.run)
        cmds.button(w=15, h=60, bgc=(.15, .15, .15), label='', enable=False, enableBackground = False)

        #updating maya_UI with latest INI data
        #print ('updated maya UI from INI data')
        self.updateMAYA_ui_from_INI_data(INI_Path)
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfRows=1, rowHeight=[(2, 30)], w = 150)
        cmds.showWindow()
        allowedAreas = ['top', 'bottom']
        cmds.dockControl('assBlaster', area='top', content=snapFunction, allowedArea=allowedAreas,
                         label='{ --ASSETBLAST-- }', w=200)


class assblaster_log(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.path = []
        self.sharedpath = 'L:/NXTPXLENT/pipe___RND/users'
        self.rvDir = r'C:/Program Files/Shotgun/RV-7.1.1'
        if platform.system()=='Windows':
            path = "C:/Users/nitin.singh/Dropbox/MAYA_2018_python_code/assBlaster_LOG.ui"
            self.path.append(path)

        if platform.system()=='Darwin':
            path = "/Users/nitin/Dropbox/MAYA_2018_python_code/assBlaster_LOG_001.ui"
            self.path.append(path)
        p = (self.path)[0]
        self.ui = QUiLoader().load(p)
        ''' This will keep UI always on top of other windows linke normal maya behaviour'''
        #self.ui.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.ui.playBlasts_tableWidget.resizeColumnsToContents()
        header = self.ui.playBlasts_tableWidget.horizontalHeader()
        #self.ui.refresh_pushButton.clicked.connect(self.refreshBlastLogList)
        #self.ui.run_in_RV_pushButton.clicked.connect(self.selectedFileVersion)
        self.ui.users_comboBox.currentIndexChanged.connect(self.refreshBlastLogList)

        #self.getAllUsersList()
        self.updateUsersList()

        self.ui.groupBox.setStyleSheet("""QGroupBox { background-color: rgb(70, 70, 70)}
                                             QGroupBox { border: 3px solid green;}""")
        self.ui.float_on_top_checkBox.toggled.connect(self.AlwaysOn_top)
        self.ui.float_on_top_checkBox.setStyleSheet("color: grey")

        self.ui.playBlasts_tableWidget.setCornerButtonEnabled (True)
        self.ui.playBlasts_tableWidget.resizeColumnsToContents()
        self.ui.playBlasts_tableWidget.setColumnWidth(0,150)
        self.ui.playBlasts_tableWidget.setColumnWidth(1,85)
        self.ui.playBlasts_tableWidget.setColumnWidth(2,85)
        self.ui.playBlasts_tableWidget.setColumnWidth(3,85)
        self.ui.playBlasts_tableWidget.setColumnWidth(4,125)
        self.ui.playBlasts_tableWidget.setColumnWidth(5,100)

        #self.ui.playBlasts_tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.ui.playBlasts_tableWidget.setSelectionBehavior(QTableView.SelectRows)
        #self.ui.playBlasts_tableWidget.verticalHeader().resizeSections(QHeaderView.ResizeToContents);

        self.ui.playBlasts_tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.ui.playBlasts_tableWidget.customContextMenuRequested.connect(self.job_____popup)

        self.ui.playBlasts_tableWidget.setCornerButtonEnabled (True)
        self.ui.playBlasts_tableWidget.setSortingEnabled(True)


    def AlwaysOn_top(self):
        if self.ui.float_on_top_checkBox.isChecked():
            self.ui.setWindowFlags(self.ui.windowFlags() | Qt.WindowStaysOnTopHint)
            self.ui.float_on_top_checkBox.setStyleSheet("color: lightGreen")
            self.ui.show()
        else:
            self.ui.setWindowFlags(self.ui.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.ui.float_on_top_checkBox.setStyleSheet("color: grey")
            self.ui.show()

    def filePathFixed(self, path):
        if platform.system()=='Windows':
            filePath = path
            #print (filePath)
            separator = os.path.normpath("/")
            newPath = re.sub(re.escape(separator), "/", filePath)
            return newPath
            #print (path)
        else:
            return filePath

    def job_____popup(self, point):
        menu = QMenu()

        font1 = QFont()
        font1.setPointSize(11)
        font1.setBold(True)
        menu.setFont(font1)
        menu = QMenu()
        menu.setStyleSheet("""QMenu {background-color: blue;}
                                  QMenu::item:selected {background-color: black}
                                  QMenu::separator {height: 1px;background: lightblue;margin-left: 10px;margin-right: 5px;}
                               """)
        menu.setFont(font1)
        menu.addSeparator()
        menuOption_1 = menu.addAction("Play selected Playblast in RV  ")
        menu.addSeparator()
        menuOption_2 = menu.addAction("Copy Playblast UID to clipboard   ")
        menu.addSeparator()
        menuOption_3 = menu.addAction("Publish Playblast  ")
        menu.addSeparator()
        menuOption_3 = menu.addAction("Copy Playblast to another location  ")
        action = menu.exec_(self.ui.playBlasts_tableWidget.mapToGlobal(point))
        if action == menuOption_1:
            self.selectedFileVersion()
        if action == menuOption_2:
            self.importingSelectedLayout()
        if action == menuOption_3:
            self.readingLogFile()

    def getsamerowcell(self, widget,columnname):

        row = widget.currentItem().row()
        #col = widget.currentItem().column()

        #loop through headers and find column number for given column name
        headercount = widget.columnCount()
        for x in range(0,headercount,1):
            headertext = widget.horizontalHeaderItem(x).text()
            if columnname == headertext:
                matchcol = x
                break

        cell = widget.item(row,matchcol).text()   # get cell at row, col
        return cell

    def selectedFileVersion(self):
        fileName = self.getsamerowcell(self.ui.playBlasts_tableWidget, 'Path')
        #fileName = str(self.ui.playBlasts_tableWidget.currentItem().text())
        #print fileName
        sequencepath = self.filePathFixed(fileName+'.@@@@.jpg')
        #print (sequencepath)
        rv = str(self.rvDir + '/bin/rv.exe')
        RVDirShortName = rv.replace("Program Files", "Progra~1")
        os.system("start " + RVDirShortName + " " + sequencepath)

    def updateUsersList(self):
        toolUsers = []
        for dir in os.listdir(self.sharedpath):
            if os.path.isdir(os.path.join(self.sharedpath, dir)):
                #print dir
                if os.path.isdir(os.path.join(self.sharedpath, dir, 'assBlaster_Logs')):
                    print (dir)
                    toolUsers.append(dir)
            else:
                pass
        #print toolUsers
        if toolUsers:
            self.ui.users_comboBox.addItems(toolUsers)

    def refreshBlastLogList(self):
        user_name = str(self.ui.users_comboBox.currentText())
        #print user_name
        path = self.filePathFixed(os.path.join(self.sharedpath , user_name, 'assBlaster_Logs','assBlasterLog.txt'))
        #print path
        if os.path.isfile(path):
            #print path
            self.readingJSONfile(path)
        else:
            self.ui.playBlasts_tableWidget.clearContents()
            self.ui.playBlasts_tableWidget.setRowCount(0)

    def refreshBlastLogList2(self, username):
        filepath = self.getAllUsersList()
        self.readingJSONfile(filepath[1])

    def readingJSONfile(self, logFile):
        self.ui.playBlasts_tableWidget.clearContents()
        self.ui.playBlasts_tableWidget.setRowCount(0)
        with open(logFile, 'r') as file:
            jsondata = json.load(file)
        existingList = []
        for key, value in jsondata.iteritems():
            #print key, value
            existingList.append(value)

        self.ui.playBlasts_tableWidget.setRowCount(len(existingList))
        for i, log in enumerate(existingList):
            self.ui.playBlasts_tableWidget.setItem(i, 0, QTableWidgetItem(log[0]))
            self.ui.playBlasts_tableWidget.setItem(i, 1, QTableWidgetItem(log[1]))
            self.ui.playBlasts_tableWidget.setItem(i, 2, QTableWidgetItem(log[7]))
            self.ui.playBlasts_tableWidget.setItem(i, 3, QTableWidgetItem(log[7]))
            self.ui.playBlasts_tableWidget.setItem(i, 4, QTableWidgetItem(log[8]))
            self.ui.playBlasts_tableWidget.setItem(i, 5, QTableWidgetItem(log[2]))
            self.ui.playBlasts_tableWidget.setItem(i, 6, QTableWidgetItem(log[3]))
            self.ui.playBlasts_tableWidget.setItem(i, 7, QTableWidgetItem(log[4]))
            self.ui.playBlasts_tableWidget.setItem(i, 8, QTableWidgetItem(log[5]))
        self.ui.playBlasts_tableWidget.sortByColumn(1)
        self.ui.playBlasts_tableWidget.sortByColumn(5)

        return existingList

def assBlasterRun():
    start = assBlaster()
    start.assBlasterUI()

assBlasterRun()

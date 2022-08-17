import os
import unittest
import logging
import vtk, qt, ctk, slicer
import numpy as np  
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# UltrasoundProbeCalibration
#to do: space bar to unfreeze 

#check reload etc
if '4.11' or '4.12' or '4.13' in slicer.__path__[0]: 
  try: 
    import pandas as pd
  except ImportError:
    slicer.util.pip_install('pandas')
    import pandas as pd 
class UltrasoundProbeCalibration(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundProbeCalibration"  # TODO: make this more human readable by adding spaces
    self.parent.categories=["IGT"]
    self.parent.dependencies = ["VolumeResliceDriver", "CreateModels", "PointToLineRegistration"]
    self.parent.contributors=["Leah Groves", "Adam Rankin", "Elvis C. S. Chen"]
    self.parent.helpText="""This is a scripted loadable module that performs ultrasound calibration."""
    self.parent.helpText = self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """ The point to line registration algorithm was originally developed by Elvis Chen (). The C++ implementation was developed by Adam Rankin."""

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", registerSampleData)

#
# Register sample data sets in Sample Data module
#

def registerSampleData():
  """
  Add data sets to Sample Data module.
  """
  # It is always recommended to provide sample data for users to make it easy to try the module,
  # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

  import SampleData
  iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

  # To ensure that the source code repository remains small (can be downloaded and installed quickly)
  # it is recommended to store data sets that are larger than a few MB in a Github release.

  # UltrasoundProbeCalibration1
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='UltrasoundProbeCalibration',
    sampleName='UltrasoundProbeCalibration1',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'UltrasoundProbeCalibration1.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
    fileNames='UltrasoundProbeCalibration1.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
    # This node name will be used when the data set is loaded
    nodeNames='UltrasoundProbeCalibration1'
  )

  # UltrasoundProbeCalibration2
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='UltrasoundProbeCalibration',
    sampleName='UltrasoundProbeCalibration2',
    thumbnailFileName=os.path.join(iconsPath, 'UltrasoundProbeCalibration2.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
    fileNames='UltrasoundProbeCalibration2.nrrd',
    checksums = 'SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
    # This node name will be used when the data set is loaded
    nodeNames='UltrasoundProbeCalibration2'
  )

#
# UltrasoundProbeCalibrationWidget
#

class UltrasoundProbeCalibrationWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False
    slicer.mymod = self 
    self.connectCheck = None 
    self.logic = UltrasoundProbeCalibrationLogic()
    self.iconsPath = os.path.join(os.path.dirname(__file__), 'Resources//Icons')
  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/UltrasoundProbeCalibration.ui'))
    
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.copyButton.setIcon(qt.QIcon(self.iconsPath+'\\copy.png'))
  
    # self.ui.stylusStatus.hide() 
    # self.ui.copyButton.setIcon(qt.QIcon(os.path.join(os.path.dirname(__file__), 'Resources//Icons//copy.png')))
    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)
    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.ui.browserSelector.hide() 
    self.ui.Browser.hide()
    # self.logic.setupScene()
    # Connections
    if slicer.mrmlScene.GetNodesByClass("vtkMRMLSequenceNode").GetNumberOfItems() > 0:
      self.ui.portInput.hide()
      self.ui.serverInput.hide()
      self.ui.connectButton.hide()
      self.ui.Port.hide()
      self.ui.Server.hide()
      self.ui.browserSelector.show() 
      self.ui.Browser.show()
      self.numFid = 0 
      # slicer.modules.sequences.setToolBarVisible(1)
      # parameterNode = self.logic.getParameterNode()
      # node = slicer.util.getNodesByClass('vtkMRMLSequenceBrowserNode')
      # SB = node[0]
      # parameterNode.SetNodeReferenceID(self.logic.SEQUENCE_BROWSER, SB.GetID())
      # slicer.modules.sequences.setToolBarActiveBrowserNode(SB)
      self.ui.freezeButton.text = "Start Playback ('f')"
    else: 
      PN = self.logic.getParameterNode()
      PN.SetNodeReferenceID(self.logic.SEQUENCE_BROWSER, "None")
    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)
    slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeAddedEvent, self.onNodeAdded)
    
    self.ui.serverInput.connect('textChanged(QString)', self.onInputChanged)
    self.ui.portInput.connect('textChanged(QString)', self.onInputChanged)   
    
    self.connectShortcut = qt.QShortcut(qt.QKeySequence('f'), slicer.util.mainWindow())
    self.connectShortcut = qt.QShortcut(qt.QKeySequence('SPACE'), slicer.util.mainWindow())
    self.ui.connectButton.connect('clicked(bool)', self.onConnectButtonClicked)
    self.ui.freezeButton.connect('clicked(bool)', self.onConnectButtonClicked)
    self.connectShortcut.connect('activated()', self.onConnectButtonClicked)
    self.ui.copyButton.connect('clicked(bool)', self.onCopyButtonClicked)
    self.ui.imageSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onImageChanged)
    self.ui.transformSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onTransformChanged)
    self.ui.imageToProbeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onItoPChanged)
    self.ui.visualizeButton.connect('clicked(bool)', self.onVisualizeButtonClicked) 
    self.ui.pointToLine.connect('toggled(bool)', self.onRadioButtonSelected)
    self.ui.pointToPoint.connect('toggled(bool)', self.onRadioButtonSelected)
    self.ui.undoButton.connect('clicked(bool)', self.onUndoButtonClicked)
    self.ui.browserSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onBrowserSelected) 
    # self.uShortcut.connect('activated()', self.onUndoButtonClicked)
    self.ui.redoButton.connect('clicked(bool)', self.onRedoButtonClicked)
    # self.rShortcut.connect('activated()', self.onRedoButtonClicked)
     
    self.initializeParameterNode()
    
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self, caller, event,callData):
    if type(callData) is slicer.vtkMRMLSequenceBrowserNode:
      self.ui.portInput.hide()
      self.ui.serverInput.hide()
      self.ui.connectButton.hide()
      self.ui.Port.hide()
      self.ui.Server.hide()
      self.numFid = 0 
      self.ui.browserSelector.show() 
      self.ui.Browser.show() 
  def onBrowserSelected(self):
    SB = self.ui.browserSelector.currentNode() 
    self._parameterNode.SetNodeReferenceID(self.logic.SEQUENCE_BROWSER, SB.GetID())
    slicer.modules.sequences.setToolBarActiveBrowserNode(SB)
    self.ui.freezeButton.text = "Start Playback ('f')"
  def onImageChanged(self, newNode):
    if slicer.mrmlScene.IsImporting() or self.logic.isImporting:
      return
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return
    if newNode is None:
      self._parameterNode.SetNodeReferenceID(self.logic.IMAGE_NODE, None)
      logging.info("Set image Node ID: None")
    else:
      resliceLogic = slicer.modules.volumereslicedriver.logic()
      self._parameterNode.SetNodeReferenceID(self.logic.IMAGE_NODE, newNode.GetID())
      logging.info("Set image node: {}".format(newNode.GetName()))
      newNode.GetDisplayNode().SetAutoWindowLevel(0)
      newNode.GetDisplayNode().SetWindowLevelMinMax(100,256)
      slicer.app.layoutManager().sliceWidget('Red').sliceLogic().GetSliceCompositeNode().SetBackgroundVolumeID(newNode.GetID())
      # Configure volume reslice driver, transverse
      resliceLogic.SetDriverForSlice(newNode.GetID(), slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed'))
      resliceLogic.SetModeForSlice(resliceLogic.MODE_TRANSVERSE, slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed'))
      slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)    
      viewNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
      viewNode.SetSliceResolutionMode(viewNode.SliceFOVMatch2DViewSpacingMatchVolumes)
      slicer.app.layoutManager().sliceWidget("Red").sliceController().fitSliceToBackground()

  def onItoPChanged(self,newNode):
    if slicer.mrmlScene.IsImporting() or self.logic.isImporting:
      return
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return
    if newNode is None:
      self._parameterNode.SetNodeReferenceID(self.logic.IMAGE_PROBE, 'None')
      logging.info("Set Image To Probe Node: None")
      newNode.RemoveObserver() 
    else:
      self._parameterNode.SetNodeReferenceID(self.logic.IMAGE_PROBE, newNode.GetID())
      newNode.SetName('ImageToProbe') 
      newNode.AddObserver(vtk.vtkCommand.AnyEvent,self.updateTable)
      logging.info("Set Image To Probe node: {}".format(newNode.GetName()))
  def onTransformChanged(self, newNode):
    if slicer.mrmlScene.IsImporting() or self.logic.isImporting:
      return
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return
    if newNode is None:
      self._parameterNode.SetNodeReferenceID(self.logic.TRANSFORM_NODE, None)
      logging.info("Set transform Node: None")
    else:
      self._parameterNode.SetNodeReferenceID(self.logic.TRANSFORM_NODE, newNode.GetID())
      logging.info("Set transform node: {}".format(newNode.GetName()))
      mat = slicer.util.arrayFromTransformMatrix(newNode)
      if (mat == np.eye(4)).all() == True: 
        self.ui.trackingStatus.setPixmap(qt.QPixmap(self.iconsPath+'\\RedSmall.png'))
      else: 
        self.ui.trackingStatus.setPixmap(qt.QPixmap(self.iconsPath+'\\GreenSmall.png'))
      self.ui.trackingStatus.show() 
      needleNode = self._parameterNode.GetNodeReference(self.logic.NEEDLE_MODEL)
      if needleNode is None: 
        needleNode = slicer.modules.createmodels.logic().CreateNeedle(140, 0.4, 0, False)
        self._parameterNode.SetNodeReferenceID(self.logic.NEEDLE_MODEL, needleNode.GetID())
      else:
        needleNode.SetAndObserveTransformNodeID(None) 
      needleNode.SetAndObserveTransformNodeID(newNode.GetID())
      newNode.AddObserver("ModifiedEvent",self.checkNeedleConnection)
  def onInputChanged(self):
    if self.ui.serverInput.text != '' and self.ui.portInput.text != '':
      self.ui.connectButton.enabled = True
  def onConnectButtonClicked(self):
    markupNode = self._parameterNode.GetNodeReference(self.logic.INPUT_MARKUP)
    transformNode = self._parameterNode.GetNodeReference(self.logic.TRANSFORM_NODE)
    if slicer.mrmlScene.GetNodesByClass("vtkMRMLSequenceNode").GetNumberOfItems() == 0:
      connectorNode = slicer.mrmlScene.GetNodeByID(self._parameterNode.GetNodeReferenceID(self.logic.CONNECTOR_NODE))
      if self.connectCheck is None: 
        connectorNode.SetTypeClient(self.ui.serverInput.text, int(self.ui.portInput.text))
        connectorNode.Start()
        self.connectCheck =1 
        self.ui.connectButton.text = "Connected"
        self.ui.freezeButton.text = "Stop and Place Markup ('SPACE')"
        self.ui.imageSelector.enabled = True 
        self.ui.transformSelector.enabled = True 
        self.numFid = 0 
      else:
        if transformNode is None: 
          logging.info('Transform Node: None') 
        else: 
          if connectorNode.GetState() == 0: 
            connectorNode.Start() 
            # self.ui.connectButton = "Disconnect"
            self.ui.freezeButton.text = "Freeze ('SPACE')"
            interactionNode = self._parameterNode.GetNodeReference(self.logic.INTERACTION_NODE)
            interactionNode.SetPlaceModePersistence(0)
            interactionNode.SetCurrentInteractionMode(0)
            interactionNode.SetPlaceModePersistence(1)
          else:
            connectorNode.Stop()
            # self.ui.connectButton.text = "Connect"
            self.ui.freezeButton.text = "Unfreeze ('SPACE')"
            selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
            selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
            interactionNode = self._parameterNode.GetNodeReference(self.logic.INTERACTION_NODE)
            interactionNode.SetPlaceModePersistence(1)
            interactionNode.SetCurrentInteractionMode(1)
            interactionNode.SetPlaceModePersistence(0)
            selectionNode.SetActivePlaceNodeID(self._parameterNode.GetNodeReferenceID(self.logic.INPUT_MARKUP))
    else:
      if transformNode is None: 
        logging.info('Transform Node: None') 
      else:
        SB = self._parameterNode.GetNodeReference(self.logic.SEQUENCE_BROWSER)
        if SB.GetPlaybackActive() is False:   
          if self.numFid == 0:
            self.ui.freezeButton.text = "Stop and Place Markup ('f')"
            SB.SetPlaybackActive(1)
            slicer.app.layoutManager().sliceWidget("Red").sliceController().fitSliceToBackground()
          else: 
            self.ui.freezeButton.text = "Stop and Place Markup ('f')"
            SB.SetPlaybackActive(1)
            selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
            selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
            interactionNode = self._parameterNode.GetNodeReference(self.logic.INTERACTION_NODE)
            interactionNode.SetPlaceModePersistence(0)
            interactionNode.SetCurrentInteractionMode(0)
            slicer.app.layoutManager().sliceWidget("Red").sliceController().fitSliceToBackground()
        else:
          SB.SetPlaybackActive(0)        
          self.ui.freezeButton.text = "Start Playback ('f')"
          selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
          selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
          interactionNode = self._parameterNode.GetNodeReference(self.logic.INTERACTION_NODE)
          interactionNode.SetPlaceModePersistence(1)
          interactionNode.SetCurrentInteractionMode(1)
          selectionNode.SetActivePlaceNodeID(markupNode.GetID())
          interactionNode.SetPlaceModePersistence(0)
        # interactionNode.AddObserver(interactionNode.InteractionModeChangedEvent,self.logic.onMarkupAdded)
  def onVisualizeButtonClicked(self):
    markupNode = self._parameterNode.GetNodeReference(self.logic.INPUT_MARKUP)
    imageNode = self._parameterNode.GetNodeReference(self.logic.IMAGE_NODE)
    imageToProbeNode = self._parameterNode.GetNodeReference(self.logic.IMAGE_PROBE)
    if markupNode is not None:
      markupNode.RemoveAllMarkups()
    if slicer.app.layoutManager().layout == 4:
      slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)    
      self.ui.visualizeButton.text = 'Show 3D Scene'
      # imageToProbeNode.SetMatrixTransformToParent(None)
      imageNode.SetAndObserveTransformNodeID(None)
    elif slicer.app.layoutManager().layout == 6:
      if slicer.mrmlScene.GetNodesByClass("vtkMRMLSequenceNode").GetNumberOfItems() != 0:
        SB = self._parameterNode.GetNodeReference(self.logic.SEQUENCE_BROWSER)
        SB.SetPlaybackActive(1)        
        self.ui.freezeButton.text = "Stop and Place Markup ('f')"
        selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
        selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
        interactionNode = self._parameterNode.GetNodeReference(self.logic.INTERACTION_NODE)
        interactionNode.SetPlaceModePersistence(0)
        interactionNode.SetCurrentInteractionMode(0)
        selectionNode.SetActivePlaceNodeID(markupNode.GetID())
        interactionNode.SetPlaceModePersistence(0)
      slicer.app.layoutManager().sliceWidget("Red").sliceController().fitSliceToBackground()
      slicer.app.layoutManager().sliceWidget('Red').sliceLogic().GetSliceNode().SetSliceVisible(True)
      slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
      self.ui.visualizeButton.text = 'Show ultrasound stream'
      imageNode.SetAndObserveTransformNodeID(imageToProbeNode.GetID())
  def onRadioButtonSelected(self):
    if self.ui.pointToLine.isChecked() is True: 
      self._parameterNode.SetParameter(self.logic.REGISTRATION_TYPE, "PointToLine")
      logging.info('Registration Type Set:' + self._parameterNode.GetParameter(self.logic.REGISTRATION_TYPE))
    if self.ui.pointToPoint.isChecked() is True: 
      self._parameterNode.SetParameter(self.logic.REGISTRATION_TYPE, "PointToPoint")
      logging.info('Registration Type Set:' + self._parameterNode.GetParameter(self.logic.REGISTRATION_TYPE))
  def updateTable(self,caller,event): 
    imageToProbeNode = self._parameterNode.GetNodeReference(self.logic.IMAGE_PROBE)
    imageToProbe = vtk.vtkMatrix4x4()
    imageToProbeNode.GetMatrixTransformToWorld(imageToProbe) 
    for i in range (0,4): 
      for j in range(0,4): 
        self.ui.transformTable.setValue(i,j,(imageToProbe.GetElement(i,j)))
  def checkNeedleConnection(self,Caller, event): 
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources//Icon')
    transformNode = self._parameterNode.GetNodeReference(self.logic.TRANSFORM_NODE)
    mat = slicer.util.arrayFromTransformMatrix(transformNode)
    if (mat == np.eye(4)).all() == True: 
      self.ui.trackingStatus.setPixmap(qt.QPixmap(self.iconsPath+'\\RedSmall.png'))
    else: 
      self.ui.trackingStatus.setPixmap(qt.QPixmap(self.iconsPath+'\\GreenSmall.png')) 
  def onUndoButtonClicked(self):
    self.numFid = self.numFid -1 
    self.ui.numFid.setText(str(self.numFid))
    self.logic.onUndo()   
  def onRedoButtonClicked(self):
    self.numFid = self.numFid +1 
    self.ui.numFid.setText(str(self.numFid))
    self.logic.onRedo() 
  def onCopyButtonClicked(self): 
    imageToProbeNode = self._parameterNode.GetNodeReference(self.logic.IMAGE_PROBE)
    if imageToProbeNode is None: 
      mat = vtk.vtkMatrix4x4()
      A = slicer.util.arrayFromVTKMatrix(mat)
    else: 
      A = slicer.util.arrayFromTransformMatrix(imageToProbeNode) 
    df = pd.DataFrame(A, columns=[' ' ,' ',' ',' '])
    df.to_clipboard(index=False)
    
  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    #self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
 
  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately

    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.
    self.setParameterNode(self.logic.getParameterNode())
    
    imageToProbe = self._parameterNode.GetNodeReference(self.logic.IMAGE_PROBE)
    if imageToProbe is not None: 
      self.removeObserver(imageToProbe,vtk.vtkCommand.ModifiedEvent,self.updateTable)  
      imageToProbeNode = None 
      self._parameterNode.SetNodeReferenceID(self.logic.IMAGE_PROBE, 'None')
    fidNode = self._parameterNode.GetNodeReference(self.logic.INPUT_MARKUP) 
    if fidNode is not None: 
      slicer.mrmlScene.RemoveNode(fidNode) 
      self._parameterNode.SetNodeReferenceID(self.logic.INPUT_MARKUP,'None')
    imageNode = self._parameterNode.GetNodeReference(self.logic.IMAGE_NODE) 
    if imageNode is not None: 
      self._parameterNode.SetNodeReferenceID(self.logic.IMAGE_NODE, 'None') 
    transformNode = self._parameterNode.GetNodeReference(self.logic.TRANSFORM_NODE) 
    if transformNode is not None: 
      self._parameterNode.SetNodeReferenceID(self.logic.TRANSFORM_NODE,'None') 
    if slicer.mrmlScene.GetNodesByClass("vtkMRMLSequenceNode").GetNumberOfItems() > 0:
      self.ui.portInput.hide()
      self.ui.serverInput.hide()
      self.ui.connectButton.hide()
      self.ui.Port.hide()
      self.ui.Server.hide()
      self.ui.browserSelector.show() 
      self.ui.Browser.show()
      self.numFid = 0 
      slicer.modules.sequences.setToolBarVisible(1)
      node = slicer.util.getNodesByClass('vtkMRMLSequenceBrowserNode')
      SB = self._parameterNode.GetNodeReference(self.logic.SEQUENCE_BROWSER)
      slicer.modules.sequences.setToolBarActiveBrowserNode(SB)
      self.ui.freezeButton.text = "Start Playback ('f')" 
    else:
      self._parameterNode.SetNodeReferenceID(self.logic.SEQUENCE_BROWSER, "None")
    self.logic.setupScene()
      
  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    # self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller, event):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """
    if str(event) == "ModifiedEvent": 
      if self._parameterNode.GetParameter(self.logic.MARKUP_ADDED) == 'True':
        self.ui.freezeButton.text = "Stop and Place Markup ('f')" 
        self.numFid = self.numFid + 1 
        self.ui.numFid.setText(str(self.numFid))
        self._parameterNode.SetParameter(self.logic.MARKUP_ADDED, "False")

    if slicer.mrmlScene.IsImporting() or self.logic.isImporting:
      return

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)

    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders

    inputNode = self._parameterNode.GetNodeReference(self.logic.INPUT_MARKUP)
    # self.ui.inputMarkupSelector.setCurrentNode(inputNode)
    # Update buttons states and tooltips

    # if self._parameterNode.GetNodeReference(self.logic.INPUT_MARKUP) is not None:
      # self.ui.applyButton.toolTip = "Compute output volume"
      # self.ui.autoUpdateCheckBox.enabled = True
      # self.ui.applyButton.enabled = True
    # else:
      # self.ui.applyButton.toolTip = "Select input and output volume nodes"
      # self.ui.autoUpdateCheckBox.enabled = False
      # self.ui.applyButton.enabled = False
    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False



#
# UltrasoundProbeCalibrationLogic
#

class UltrasoundProbeCalibrationLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  INPUT_MARKUP = "InputMarkup"
  NEEDLE_MODEL = "NeedleModel"
  DATA_LIST = "dataList"
  IMAGE_NODE = "ImageNode"
  TRANSFORM_NODE = "TransformNode"
  CONNECTOR_NODE = "ConnectorNode"
  IMAGE_PROBE = "ImageToProbeNode"
  INTERACTION_NODE = "InteractionNode"
  REGISTRATION_TYPE = "None"
  SEQUENCE_BROWSER = "SequenceNode"
  MARKUP_ADDED = "False" 
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
    VTKObservationMixin.__init__(self)
    self.inputMarkup = None 
    self.needleModel = None 
    self.dataList = None 
    self.redoStack = None 
    self.connectorNode = None
    self.imageToProbeNode = None 
    self.observedMarkupNode = None
    self.interactionNode = None
    self.isImporting = False
    self.sequenceNode = None
    self.pointToLineRegistrationLogic = slicer.vtkSlicerPointToLineRegistrationLogic()
    self.pointToLineRegistrationLogic.SetLandmarkRegistrationModeToAnisotropic()
    self.pointToPointRegistrationLogic = vtk.vtkLandmarkTransform()
    self.pointToPointRegistrationLogic.SetModeToSimilarity()
    self.movingPts = vtk.vtkPoints()
    self.fixedPts = vtk.vtkPoints() 
    self.markupAdded = False
  def setupScene(self): 
    parameterNode = self.getParameterNode()
    needleModel = parameterNode.GetNodeReference(self.NEEDLE_MODEL)
    if needleModel is None:
      needleModel = slicer.modules.createmodels.logic().CreateNeedle(140, 0.4, 0, False)
      needleModel.SetName(self.NEEDLE_MODEL)    
      needleModel.CreateDefaultDisplayNodes()
      parameterNode.SetNodeReferenceID(self.NEEDLE_MODEL,needleModel.GetID())
      self.needleModel = needleModel
    inputMarkup = parameterNode.GetNodeReference(self.inputMarkup) 
    if inputMarkup is None: 
      inputMarkup = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode')
      inputMarkup.CreateDefaultDisplayNodes()
      inputMarkup.GetDisplayNode().SetGlyphType(6)
      inputMarkup.GetDisplayNode().SetGlyphScale(1.75)
      inputMarkup.GetDisplayNode().SetTextScale(0)
      inputMarkup.GetDisplayNode().PointLabelsVisibilityOff()
      inputMarkup.GetDisplayNode().SetSelectedColor(0, 0, 1)
      parameterNode.SetNodeReferenceID(self.INPUT_MARKUP,inputMarkup.GetID())
    # data = parameterNode.GetParameter(self.DATA_LIST)
    # if data is None: 
      # parameterNode.SetParameter(self.DATA_LIST, "None")
    connectorNode = parameterNode.GetNodeReference(self.connectorNode) 
    if connectorNode is None:
      connectorNode = slicer.vtkMRMLIGTLConnectorNode()
      slicer.mrmlScene.AddNode(connectorNode)
      parameterNode.SetNodeReferenceID(self.CONNECTOR_NODE, connectorNode.GetID())
    interactionNode = parameterNode.GetNodeReference(self.interactionNode)
    if self.interactionNode is None: 
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      parameterNode.SetNodeReferenceID(self.INTERACTION_NODE, interactionNode.GetID())
      interactionNode.AddObserver(interactionNode.InteractionModeChangedEvent,self.onMarkupAdded)
    if self.REGISTRATION_TYPE == "None":
      parameterNode.SetParameter(self.REGISTRATION_TYPE,"None") 
    if self.sequenceNode is None: 
      parameterNode.SetNodeReferenceID(self.SEQUENCE_BROWSER, "None")
    if self.MARKUP_ADDED == "False": 
      parameterNode.SetParameter(self.MARKUP_ADDED,"None") 
    self.addObserver(slicer.mrmlScene, slicer.vtkMRMLScene.StartImportEvent, self.onSceneImportStart)
    self.addObserver(slicer.mrmlScene, slicer.vtkMRMLScene.EndImportEvent, self.onSceneImportEnd)

  def onSceneImportStart(self, event, caller):
    """
    Saves existing nodes in member variables to be able to compare them with new nodes about to be loaded.
    """
    logging.info("onSceneImportStart")
    self.isImporting = True
    parameterNode = self.getParameterNode()
    # self.sphereNode = parameterNode.GetNodeReference(self.NEEDLE_MODEL)
    self.fiducialNode = parameterNode.GetNodeReference(self.INPUT_MARKUP)

  def onSceneImportEnd(self, event, caller):
    """
    When loading a saved scene ends, this function cleans up orphan nodes.
    """
    logging.info("onSceneImportEnd")
 

    parameterNode = self.getParameterNode()
    currentNeedleNode = parameterNode.GetNodeReference(self.NEEDLE_MODEL)

    # Discard the sphere loaded, in case we set up better properties (e.g. color) for illustration

    if self.needleModel != currentNeedleNode:
      parameterNode.SetNodeReferenceID(self.NEEDLE_MODEL, self.needleModel.GetID())
      self.removeNode(currentNeedleNode)

    # Use the markup loaded, because that data belongs to the "case" (e.g. patient) loaded

    currentMarkup = parameterNode.GetNodeReference(self.INPUT_MARKUP)

    if self.fiducialNode != currentMarkup:
      self.removeNode(self.fiducialNode)
      self.fiducialNode = currentMarkup

    self.isImporting = False

    parameterNode.Modified()  # Trigger GUI update
  def removeNode(self, node):
    """
    Removes node and its display and storage nodes from the scene.
    """
    if node is None:
      return

    for i in range(node.GetNumberOfDisplayNodes()):
      slicer.mrmlScene.RemoveNode(node.GetNthDisplayNode(i))

    for i in range(node.GetNumberOfStorageNodes()):
      slicer.mrmlScene.RemoveNode(node.GetNthStorageNode(i))

    slicer.mrmlScene.RemoveNode(node)
    

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    
    if not parameterNode.GetParameter("Threshold"):
      parameterNode.SetParameter("Threshold", "100.0")
  def onRedo(self): 
    parameterNode = self.getParameterNode()
    registrationType = parameterNode.GetParameter(self.REGISTRATION_TYPE)
    if registrationType == "None":
      logging.info('Select registration type')
    elif registrationType == "PointToLine":
      self.pointToLineRegistrationLogic.Reset() 
      imageToProbeNode = parameterNode.GetNodeReference(self.IMAGE_PROBE)
      markupNode = parameterNode.GetNodeReference(self.INPUT_MARKUP)    
      if self.redoStack is None: 
        logging.info('There is nothing to redo')
      else:
       self.dataStack.append(self.redoStack[-1])
       markupNode.arkupNode.AddFiducialFromArray([self.redoStack[-1][0],self.redoStack[-1][1],0])
       self.redoStack.pop(-1) 
       for i in range(0,len(self.dataList)):
        self.logic.AddPointAndLine([self.dataList[i][0],self.dataList[i][1],0], self.dataList[i][2], self.dataList[i][3])
        self.imageToProbe = self.logic.registrationLogic.CalculateRegistration()
  def onUndo(self):
    parameterNode = self.getParameterNode()
    registrationType = parameterNode.GetParameter(self.REGISTRATION_TYPE)
    if registrationType == "None":
      logging.info('Select registration type')
    elif registrationType == "PointToLine":  
      self.pointToLineRegistrationLogic.Reset() 
      imageToProbeNode = parameterNode.GetNodeReference(self.IMAGE_PROBE)
      markupNode = parameterNode.GetNodeReference(self.INPUT_MARKUP)
      if self.dataList is None:
        logging.info('There is nothing to undo') 
      else: 
        if self.redoStack is None: 
          self.redoStack = [self.dataList[-1]] 
        else: 
          self.redoStack.append(self.dataList[-1])
        self.dataList.pop(-1)
        for i in range(0,len(self.dataList)):
          self.pointToLineRegistrationLogic.AddPointAndLine([self.dataList[i][0],self.dataList[i][1],0], self.dataList[i][2], self.dataList[i][3])
        imageToProbe = self.pointToLineRegistrationLogic.CalculateRegistration()
        imageToProbeNode.SetMatrixTransformToParent(imageToProbe)
        markupNode.RemoveMarkup(markupNode.GetNumberOfMarkups()-1)
  def onMarkupAdded(self,event, caller):
    parameterNode = self.getParameterNode()
    registrationType = parameterNode.GetParameter(self.REGISTRATION_TYPE)
    if registrationType == "None":
      logging.info('Select registration type')
    elif registrationType == "PointToLine":     
      interactionNode = parameterNode.GetNodeReference(self.INTERACTION_NODE) 
      if interactionNode.GetInteractionModeAsString() == 'ViewTransform':
        # Set the location and index to zero because its needs to be initialized
        centroid = [0,0,0]
        origin = []
        direction = [] 
        markupNode = parameterNode.GetNodeReference(self.INPUT_MARKUP)
        imageToProbeNode = parameterNode.GetNodeReference(self.IMAGE_PROBE)
        markupNode.GetMarkupPoint(markupNode.GetNumberOfMarkups()-1, 0, centroid)
        tipToProbeTransform = vtk.vtkMatrix4x4()
        transformNode = parameterNode.GetNodeReference(self.TRANSFORM_NODE)
        transformNode.GetMatrixTransformToWorld(tipToProbeTransform)
        origin = [tipToProbeTransform.GetElement(0, 3), tipToProbeTransform.GetElement(1,3), tipToProbeTransform.GetElement(2,3)]
        direction = [tipToProbeTransform.GetElement(0, 2), tipToProbeTransform.GetElement(1,2), tipToProbeTransform.GetElement(2,2)]
        self.pointToLineRegistrationLogic.AddPointAndLine([centroid[0],centroid[1],0], origin, direction)
        if self.pointToLineRegistrationLogic.GetCount() > 2:
          imageToProbe = self.pointToLineRegistrationLogic.CalculateRegistration()
          imageToProbeNode.SetMatrixTransformToParent(imageToProbe)
        if self.dataList is None: 
          self.dataList = [[centroid[0],centroid[1], origin, direction]]
        else: 
          self.dataList.append([centroid[0],centroid[1], origin, direction])
        slicer.app.layoutManager().sliceWidget("Red").sliceController().fitSliceToBackground()
        if parameterNode.GetNodeReferenceID(self.SEQUENCE_BROWSER) != "None":
          SB = parameterNode.GetNodeReference(self.SEQUENCE_BROWSER)
          SB.SetPlaybackActive(1)
          parameterNode.SetParameter(self.MARKUP_ADDED, "True")
        else:
          parameterNode.GetNodeReference(self.CONNECTOR_NODE).Start()
          parameterNode.SetParameter(self.MARKUP_ADDED, "True")
    elif registrationType == "PointToPoint":
      interactionNode = parameterNode.GetNodeReference(self.INTERACTION_NODE) 
      if interactionNode.GetInteractionModeAsString() == 'ViewTransform':
        centroid = [0,0,0]
        origin = []
        markupNode = parameterNode.GetNodeReference(self.INPUT_MARKUP)
        imageToProbeNode = parameterNode.GetNodeReference(self.IMAGE_PROBE)
        markupNode.GetMarkupPoint(markupNode.GetNumberOfMarkups()-1, 0, centroid)
        tipToProbeTransform = vtk.vtkMatrix4x4()
        transformNode = parameterNode.GetNodeReference(self.TRANSFORM_NODE)
        transformNode.GetMatrixTransformToWorld(tipToProbeTransform)
        origin = [tipToProbeTransform.GetElement(0, 3), tipToProbeTransform.GetElement(1,3), tipToProbeTransform.GetElement(2,3)]
        self.fixedPts.InsertNextPoint(origin)
        self.movingPts.InsertNextPoint(centroid) 
        if self.pointToPointRegistrationLogic.GetSourceLandmarks() is None:
          self.pointToPointRegistrationLogic.SetSourceLandmarks(self.movingPts)
          self.pointToPointRegistrationLogic.SetTargetLandmarks(self.fixedPts)
        if self.movingPts.GetNumberOfPoints() >2: 
          self.pointToPointRegistrationLogic.Update()
          imageToProbe = vtk.vtkMatrix4x4()
          self.pointToPointRegistrationLogic.GetMatrix(imageToProbe)
          imageToProbeNode.SetMatrixTransformToParent(imageToProbe) 
        
        if self.dataList is None:
          self.dataList = [[centroid[0],centroid[1],0], origin]
        else: 
          self.dataList.append([[centroid[0],centroid[1],0], origin])
        if parameterNode.GetNodeReferenceID(self.SEQUENCE_BROWSER) != "None":
          SB = parameterNode.GetNodeReference(self.SEQUENCE_BROWSER)
          SB.SetPlaybackActive(1)
        else:
          parameterNode.GetNodeReference(self.CONNECTOR_NODE).Start()
          parameterNode.SetParameter(self.MARKUP_ADDED, "True")
  def process(self, inputVolume, outputVolume, imageThreshold, invert=False, showResult=True):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param inputVolume: volume to be thresholded
    :param outputVolume: thresholding result
    :param imageThreshold: values above/below this threshold will be set to 0
    :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
    :param showResult: show output volume in slice viewers
    """

    if not inputVolume or not outputVolume:
      raise ValueError("Input or output volume is invalid")

    import time
    startTime = time.time()
    logging.info('Processing started')

    # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
    cliParams = {
      'InputVolume': inputVolume.GetID(),
      'OutputVolume': outputVolume.GetID(),
      'ThresholdValue' : imageThreshold,
      'ThresholdType' : 'Above' if invert else 'Below'
      }
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
    # We don't need the CLI module node anymore, remove it to not clutter the scene with it
    slicer.mrmlScene.RemoveNode(cliNode)

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds'.format(stopTime-startTime))

#
# UltrasoundProbeCalibrationTest
#

class UltrasoundProbeCalibrationTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_UltrasoundProbeCalibration()

  def test_UltrasoundProbeCalibration(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """
    #TO COLLECT FIDS/POSES AND RESAVE 
    self.delayDisplay("Starting the test")
    
    # Get/create input data

    path = os.path.join(os.path.dirname(__file__), 'Resources/SampleData')  
    slicer.util.loadScene(path+'UsCalibration.mrb')

    self.delayDisplay('Loaded test data set')

    parameterNode= self.logic.getParameterNode() 
    parameterNode.SetParameter(self.REGISTRATION_TYPE, "PointToPoint")
    
    if self.logic.dataStack is None: 
      self.logic.dataStack = None 

    self.delayDisplay('Test passed')

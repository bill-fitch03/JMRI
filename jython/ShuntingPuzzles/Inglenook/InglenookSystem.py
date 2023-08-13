import java
from java.awt import Dimension
from javax.swing import JButton, JFrame,JPanel,BoxLayout,Box
from javax.swing import JLabel, JMenu, JMenuItem, JMenuBar
from javax.swing import JFileChooser,JTextField, BorderFactory
from javax.swing import SwingWorker, SwingUtilities
from javax.swing import WindowConstants, JDialog, JTextArea
from java.awt import Color, Font
import jmri

import sys
my_path_to_jars = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/jars/pyj2d.jar')
sys.path.append(my_path_to_jars) # add the jar to your path
import threading
import time
import webbrowser
import os

inglenook = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/Inglenook')
sys.path.append(inglenook)  # add my_path_to_pyj2d to your path
from timeout import alternativeaction, variableTimeout, print_name, timeout
################################################################################################################
# procedures
################################################################################################################

def btnpanelLocation_action(event):
    global icons_file
    global run_file
    global start_file
    #print "clicked"

    chooser = jmri.configurexml.LoadStoreBaseAction.getUserFileChooser()
    returnVal = chooser.showOpenDialog(frame)
    current_file = str(chooser.getSelectedFile())
    #print current_file
    filepath = os.path.dirname(current_file)
    root = os.path.splitext(os.path.basename(current_file))
    old_filename = root[0]
    filetype  = root[1]
    start_file = current_file
    label_panel_location.text = start_file


def get_start_filename():
    global start_filename
    global start_file
    chooser = jmri.configurexml.LoadStoreBaseAction.getUserFileChooser()
    #returnVal = chooser.showOpenDialog(frame)
    current_file = str(chooser.getSelectedFile())
    #print current_file
    filepath = os.path.dirname(current_file)
    directory = filepath
    root = os.path.splitext(os.path.basename(current_file))
    old_filename = root[0]
    filetype  = root[1]
    #print old_filename
    # if "run" not in old_filename and "icons" not in old_filename:
    #print "run not in filepath"
    start_file = current_file
    icons_file = filepath + "/" + old_filename + "_icons" + filetype
    run_file = filepath + "/" + old_filename + "_run" + filetype
    start_filename = old_filename
    loaded_filename = old_filename


def get_backup_filename():
    global backup_file
    global backup_filename
    panel_name = start_file

    filepath = os.path.dirname(panel_name)
    root = os.path.splitext(os.path.basename(panel_name))
    filename_root = root[0]
    filetype  = root[1]
    orig_panel_path = filepath + "/" + filename_root + "_backup" + filetype
    orig_panel_name = filename_root + "_backup"
    i = 0
    while os.path.exists(orig_panel_path):
        i+=1
        orig_panel_path = filepath + "/" + filename_root + "_backup" + "_" + str(i) + filetype
        orig_panel_name = filename_root + "_backup" + "_" + str(i)
        #print "orig_panel_path", orig_panel_path

    backup_file = orig_panel_path
    backup_filename = orig_panel_name

def saveOrigPanel():
    global backup_file
    global backup_filename
    get_backup_filename()
    store_panel(backup_file)


def get_backup_filename():
    global backup_file
    global backup_filename
    panel_name = start_file

    filepath = os.path.dirname(panel_name)
    root = os.path.splitext(os.path.basename(panel_name))
    filename_root = root[0]
    filetype  = root[1]
    orig_panel_path = filepath + "/" + filename_root + "_backup" + filetype
    orig_panel_name = filename_root + "_backup"
    i = 0
    while os.path.exists(orig_panel_path):
        i+=1
        orig_panel_path = filepath + "/" + filename_root + "_backup" + "_" + str(i) + filetype
        orig_panel_name = filename_root + "_backup" + "_" + str(i)
        #print "orig_panel_path", orig_panel_path

    backup_file = orig_panel_path
    backup_filename = orig_panel_name


def store_panel(filename):
    #if self.logLevel > 1: print "storing orig file in " + filename
    file = java.io.File(filename)
    cm = jmri.InstanceManager.getNullableDefault(jmri.ConfigureManager)
    result = cm.storeUser(file)
    if result :
        msg = "store was successful"
    else:
        msg = "store failed"
    #if self.logLevel > 1: print(msg)


def CreateIcons_action(event):
    global f1
    initialPanelFilename = start_file
    finalPanelFilename = icons_file

    #stage0
    saveOrigPanel()
    #stage1
    p = processPanels()
    print "Processed panels"
    #stage2
    #CreateTransits()
    #print "Created Transits"

# @print_name()
def get_siding_block(siding):
    print "q"
    s = siding.split("#")[1]
    print "siding", siding
    for block in blocks.getNamedBeanSet():
        comment = block.getComment()
        if comment != None:
            #print "comment" , comment
            if "#" in comment:
                #print "comment" , comment
                #print "s", s, "comment.split('#')[0]", str(comment.split('#')[1]), "sensor", sensor, sensor.getUserName()
                if s == str(comment.split('#')[1]):
                    return block.getUserName()
                print "s",s,"x", str(comment.split('#')[1])
    return None

def delete_block_comment(siding_name):
    # delete the comment for block 'siding_name'
    for block in blocks.getNamedBeanSet():
        comment = block.getComment()
        if comment != None:
            if siding_name in comment:
                comment_without_siding_name = ""
                str_list = comment.split(siding_name)
                for element in str_list:
                    if element != siding_name and "#" not in element:
                        comment_without_siding_name += element
                block.setComment(comment_without_siding_name)
# @print_name()
def update_block_comment(siding_name, siding_block):

    delete_block_comment(siding_name)

    # insert th comment siding_name
    print "spur_block = ", siding_block.getUserName()
    siding_block_comment = siding_block.getComment()
    if siding_block_comment == None or siding_block_comment == "":
        siding_block_comment = siding_name
    else:
        siding_block_comment = siding_block_comment + " " + siding_name
    siding_block.setComment(siding_block_comment)

# @print_name()
def get_siding_sensor(siding):
    s = siding.split("#")[1]
    for sensor in sensors.getNamedBeanSet():
        comment = sensor.getComment()
        if comment != None:
            if "#" in comment:
                if s == str(comment.split('#')[1]):
                    return sensor.getUserName()
    return None

def delete_comment(siding_name):
    for sensor in sensors.getNamedBeanSet():
        comment = sensor.getComment()
        if comment != None:
            if siding_name in comment:
                comment_without_siding_name = ""
                str_list = comment.split(siding_name)
                for element in str_list:
                    if element != siding_name and "#" not in element:
                        comment_without_siding_name += element
                sensor.setComment(comment_without_siding_name)

# @print_name()
def update_comment(siding_name, siding_sensor):
    delete_comment(siding_name)
    # insert the comment siding_name
    siding_sensor_comment = siding_sensor.getComment()
    if siding_sensor_comment == None or siding_sensor_comment == "":
        siding_sensor_comment = siding_name
    else:
        siding_sensor_comment = siding_sensor_comment + " " + siding_name
    siding_sensor.setComment(siding_sensor_comment)


def OK_action(event):

    global sensorComboBox, blockComboBox
    [spur_cb, sensor1_cb, sensor2_cb, sensor3_cb]= sensorComboBox

    spur_sensor_name = spur_cb.getSelectedItem()
    if spur_sensor_name != None:
        spur_sensor = sensors.getSensor(str(spur_sensor_name))
        update_comment("#IS_spur_sensor#", spur_sensor)
    else:
        delete_comment("#IS_spur_sensor#")

    siding1_name = sensor1_cb.getSelectedItem()
    if siding1_name != None:
        siding1_sensor = sensors.getSensor(str(siding1_name))
        update_comment("#IS_siding1_sensor#", siding1_sensor)
    else:
        delete_comment("#IS_siding1_sensor#")

    siding2_name = sensor2_cb.getSelectedItem()
    if siding2_name != None:
        siding2_sensor = sensors.getSensor(str(siding2_name))
        update_comment("#IS_siding2_sensor#", siding2_sensor)
    else:
        delete_comment("#IS_siding2_sensor#")

    siding3_block_name = sensor3_cb.getSelectedItem()
    if siding3_block_name != None:
        siding3_sensor = sensors.getSensor(str(siding3_block_name))
        print "siding3_sensor = ", siding3_sensor.getUserName()
        update_comment("#IS_siding3_sensor#", siding3_sensor)
    else:
        delete_comment("#IS_siding3_sensor#")

    [spur_block_cb, mid_block_cb, block1_cb, block2_cb, block3_cb]= blockComboBox

    spur_block_name = spur_block_cb.getSelectedItem()
    if spur_block_name != None:
        spur_block = blocks.getBlock(str(spur_block_name))
        update_block_comment("#IS_block_spur#", spur_block)
    else:
        delete_block_comment("#IS_block_spur#")

    mid_block_name = mid_block_cb.getSelectedItem()
    if mid_block_name != None:
        mid_block = blocks.getBlock(str(mid_block_name))
        update_block_comment("#IS_block_mid#", mid_block)
    else:
        delete_block_comment("#IS_block_mid#")

    siding1_block_name = block1_cb.getSelectedItem()
    if siding1_block_name != None:
        siding1_block = blocks.getBlock(str(siding1_block_name))
        update_block_comment("#IS_block_siding1#", siding1_block)
    else:
        delete_block_comment("#IS_block_siding1#")

    siding2_block_name = block2_cb.getSelectedItem()
    if siding2_block_name != None:
        siding2_block = blocks.getBlock(str(siding2_block_name))
        update_block_comment("#IS_block_siding2#", siding2_block)
    else:
        delete_block_comment("#IS_block_siding2#")

    siding3_name = block3_cb.getSelectedItem()
    if siding3_name != None:
        siding3_block = blocks.getBlock(str(siding3_name))
        update_block_comment("#IS_block_siding3#", siding3_block)
    else:
        delete_block_comment("#IS_block_siding3#")

    comp = event.getSource()
    win = SwingUtilities.getWindowAncestor(comp)
    win.dispose()
def Cancel_action(event):
    global sensorComboBox, blockComboBox
    sensor = sensors.getSensor("CB11")
    sensorComboBox[0].setSelectedItem(sensor)
    item = sensorComboBox[0].getSelectedItem()
    print item
    comp = event.getSource()
    win = SwingUtilities.getWindowAncestor(comp)
    win.dispose()
def set_sensors_in_sidings(msg):
    global sensorComboBox, blockComboBox
    print "a"
    dialog = JDialog(None, 'Set sensors in sidings', False)

    #panel = JPanel()
    panel = jmri.jmrit.beantable.beanedit.BeanItemPanel()
    panel.setLayout(BoxLayout(panel, BoxLayout.Y_AXIS))
    print "e"
    l = JLabel("   "+msg)
    # l.add(Box.createHorizontalGlue())
    # l.setAlignmentX(l.RIGHT_ALIGNMENT)
    l.setFont(l.getFont().deriveFont(Font.BOLD, 13))
    panel.add(leftJustify(l))
    #panel.add(JTextArea(msg))
    print "d"
    #BeanItemPanel panel = new BeanItemPanel();
    panel.setName("fred")
    bean = None
    print "B"
    n = jmri.NamedBean.DisplayOptions.DISPLAYNAME
    print "B"
    #p = bean.getSensor()
    print "B"
    sensorComboBox=[]
    rowTitle_22=[]
    for i in range(4):
        if i == 0:
            msg = "spur    "
        else:
            msg = "siding " + str(i)
        #panel.add(JTextArea(msg))
        sensorComboBox.append(jmri.swing.NamedBeanComboBox(jmri.InstanceManager.getNullableDefault(jmri.SensorManager)))
        sensorComboBox[i].setAllowNull(True)
        siding = "#IS_"+msg.replace(" ","")+"_sensor#"
        sensorName = get_siding_sensor(siding)
        if sensorName != None:
            sensor = sensors.getSensor(sensorName)
            sensorComboBox[i].setSelectedItem(sensor)
            item = sensorComboBox[i].getSelectedItem()
        jmri.util.swing.JComboBoxUtil.setupComboBoxMaxRows(sensorComboBox[i])
        #item = jmri.jmrit.beantable.beanedit.BeanEditItem(sensorComboBox, z, z1)
        #panel.addItem(item)
        rowTitle_22.append(JPanel())
        rowTitle_22[i].add(Box.createVerticalGlue())
        rowTitle_22[i].add(Box.createRigidArea(Dimension(20, 0)))
        rowTitle_22[i].add(JTextArea(msg))
        rowTitle_22[i].add(Box.createRigidArea(Dimension(20, 0)))
        rowTitle_22[i].add(sensorComboBox[i])
        panel.add(leftJustify(rowTitle_22[i]))
        if sensorName != None:
            print "setting cb" , sensorName
            sensorComboBox[i].setSelectedItem(str(sensorName))
            item = sensorComboBox[i].getSelectedItem()
            print "set cb box item ", item
        #panel.add(sensorComboBox[i])
        # panel.add(JTextArea(msg))
        # panel.add(sensorComboBox2)
    print "y"

    l1 = JLabel("   " + "Set the blocks for the siding and mid section")
    # l1.add(Box.createHorizontalGlue())
    # l1.setAlignmentX(l1.RIGHT_ALIGNMENT)
    l1.setFont(l1.getFont().deriveFont(Font.BOLD, 13))
    panel.add(leftJustify(l1))

    blockComboBox=[]
    rowTitle_23=[]
    for i in range(5):
        if i == 0:
            msg = "spur    "
        elif i == 1:
            msg = "mid     "
        else:
            msg = "siding   " + str(i-1)

        #panel.add(JTextArea(msg))
        blockComboBox.append(jmri.swing.NamedBeanComboBox(jmri.InstanceManager.getNullableDefault(jmri.BlockManager)))
        blockComboBox[i].setAllowNull(True)
        siding = "#IS_block_"+msg.replace(" ","")+"#"
        blockName = get_siding_block(siding)
        if blockName != None:
            print "blockname not none", blockName
            block = blocks.getBlock(blockName)
            blockComboBox[i].setSelectedItem(block)
            item = blockComboBox[i].getSelectedItem()
        jmri.util.swing.JComboBoxUtil.setupComboBoxMaxRows(blockComboBox[i])
        #item = jmri.jmrit.beantable.beanedit.BeanEditItem(blockComboBox, z, z1)
        #panel.addItem(item)
        rowTitle_23.append(JPanel())
        rowTitle_23[i].add(Box.createVerticalGlue())
        rowTitle_23[i].add(Box.createRigidArea(Dimension(20, 0)))
        rowTitle_23[i].add(JTextArea(msg))
        rowTitle_23[i].add(Box.createRigidArea(Dimension(20, 0)))
        rowTitle_23[i].add(blockComboBox[i])
        panel.add(leftJustify(rowTitle_23[i]))
        if blockName != None:
            print "setting cb" , blockName
            blockComboBox[i].setSelectedItem(str(blockName))
            item = blockComboBox[i].getSelectedItem()
            print "set cb box item ", item

    rowStage1Button_1 = JButton("OK", actionPerformed = OK_action)
    rowStage1Button_2 = JButton("Cancel", actionPerformed = Cancel_action)
    rowTitle_24 = JPanel()
    rowTitle_24.add(Box.createVerticalGlue())
    rowTitle_24.add(Box.createRigidArea(Dimension(20, 0)))
    rowTitle_24.add(rowStage1Button_1)
    rowTitle_24.add(Box.createRigidArea(Dimension(20, 0)))
    rowTitle_24.add(rowStage1Button_2)
    panel.add(leftJustify(rowTitle_24))


    print "YYYYY"

    dialog.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
    dialog.getContentPane().add(panel);
    dialog.pack();
    dialog.setVisible(True);
    # sensorComboBox[0].setSelectedItem("CB11")
    # item = sensorComboBox[i].getSelectedItem()
    # print "set cb box item ", item

def ChangeOptions_action(event):

    # y = threading.Timer(0.1, function = show_options_pane)
    # y.start()

    msg = "Set the sensors for the sidings"
    x = threading.Timer(2.0, function=set_sensors_in_sidings, args=(msg,))
    x.start()

def initialise_panel_location(stage1Button, stage3Button):
    global icons_file
    global run_file
    global start_file
    global directory
    global start_filename
    global loaded_filename
    global backup_file
    global backup_filename
    #print "clicked"
    chooser = jmri.configurexml.LoadStoreBaseAction.getUserFileChooser()

    robot = java.awt.Robot()
    #press the save tab
    KeyEvent = java.awt.event.KeyEvent
    #button.requestFocus();
    #robot.delay(1000)
    # robot.keyPress(KeyEvent.VK_TAB)
    # robot.delay(10)
    # robot.keyRelease(KeyEvent.VK_TAB)
    # robot.delay(10)
    # robot.keyPress(KeyEvent.VK_SPACE)
    # robot.delay(10)
    # robot.keyRelease(KeyEvent.VK_SPACE)
    # robot.delay(10)
    # robot.keyPress(KeyEvent.VK_ENTER)
    # robot.delay(10)
    # robot.keyRelease(KeyEvent.VK_ENTER)
    # robot.delay(10)
    #returnVal = chooser.showOpenDialog(frame)
    current_file = str(chooser.getSelectedFile())
    #print current_file
    filepath = os.path.dirname(current_file)
    directory = filepath
    root = os.path.splitext(os.path.basename(current_file))
    old_filename = root[0]
    filetype  = root[1]
    #print old_filename
    # if "run" not in old_filename and "icons" not in old_filename:
    #print "run not in filepath"
    start_file = current_file
    icons_file = filepath + "/" + old_filename + "_icons" + filetype
    run_file = filepath + "/" + old_filename + "_run" + filetype
    start_filename = old_filename
    loaded_filename = old_filename
    stage_to_run = "Stage 1"

    label_panel_location.text = start_file

    #msg = "Panel Directory: " + str(directory)
    #rowTitle_1_2.text = msg
    get_backup_filename()
    #rowStage1Title_2.text = "Modifies: " + start_filename + "  Creates backup: " + backup_filename
    #row42b2.text = "Produces: " + start_filename + "_run" + filetype + " (from " + start_filename + "_icons" + filetype + ")"
    rowTitle_2_1.text = "You have " + loaded_filename + filetype + " loaded. You may run " + stage_to_run
    rowTitle_2_1.text = "Inglenook System: Sorts trucks in siding automatically"
    rowTitle_2_1.setFont(rowTitle_2_1.getFont().deriveFont(Font.BOLD, 13));

def leftJustify( panel ):
    b = Box.createHorizontalBox()
    b.add( panel )
    b.add( Box.createHorizontalGlue() )
    # (Note that you could throw a lot more components
    # and struts and glue in here.)
    return b

################################################################################################################
# main file
################################################################################################################
global start_filename
global backup_filename
start_file = ""
run_file = ""
directory = ""

logLevel = 0


#*****************
# Set Program locations, and include code
#*****************
CreateIcons = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/Inglenook/CreateIcons.py')
execfile(CreateIcons)

#*****************
frame = jmri.util.JmriJFrame('Inglenook Sidings');
frame.addHelpMenu('html.scripthelp.DispatcherSystem.DispatcherSystem' , True)

panel = JPanel()
panel.setLayout(BoxLayout(panel, BoxLayout.Y_AXIS))
frame.add(panel)

row0 = JPanel()
row0.setLayout(BoxLayout(row0, BoxLayout.X_AXIS))
txt = JTextField(140)
txt.setMaximumSize( txt.getPreferredSize() );
txt.setBorder(BorderFactory.createCompoundBorder(
    BorderFactory.createLineBorder(Color.red),
    txt.getBorder()));
label_panel_location = JLabel()
btnpanelLocation = JButton("Set Panel Location", actionPerformed = btnpanelLocation_action)
row0.add(Box.createVerticalGlue())
row0.add(Box.createRigidArea(Dimension(20, 0)))
row0.add(btnpanelLocation)
row0.add(Box.createRigidArea(Dimension(20, 0)))
row0.add(label_panel_location)
row0.add(Box.createRigidArea(Dimension(20, 0)))


rowTitle_22 = JPanel()
rowTitle_22.setLayout(BoxLayout(rowTitle_22, BoxLayout.X_AXIS))
rowStage1Title_1 = JLabel("Stage1: ")
get_start_filename()
get_backup_filename()
rowStage1Title_1 = JLabel("    Modifies: " + start_filename + "  Creates backup: " + backup_filename)
rowStage1Title_1.add(Box.createHorizontalGlue());
rowStage1Title_1.setAlignmentX(rowStage1Title_1.LEFT_ALIGNMENT)
rowStage1Title_2 = JLabel("")     #start_filename + "_icons"

rowTitle_22.add(Box.createVerticalGlue())
rowTitle_22.add(Box.createRigidArea(Dimension(20, 0)))
rowTitle_22.add(rowStage1Title_1)
rowTitle_22.add(Box.createRigidArea(Dimension(20, 0)))
rowTitle_22.add(rowStage1Title_2)

rowStage2Title = JPanel()
rowStage2Title.setLayout(BoxLayout(rowStage2Title, BoxLayout.X_AXIS))
rowStage2Title_1 = JLabel("Stage2: Check the Dispatcher Options are set correctly (essential)")
rowStage2Title_1.add(Box.createHorizontalGlue());
rowStage2Title_1.setAlignmentX(rowStage2Title_1.LEFT_ALIGNMENT)
rowStage2Title_2 = JLabel("")     #start_filename + "_icons"

rowStage2Title.add(Box.createVerticalGlue())
rowStage2Title.add(Box.createRigidArea(Dimension(20, 0)))
rowStage2Title.add(rowStage2Title_1)
rowStage2Title.add(Box.createRigidArea(Dimension(20, 0)))
rowStage2Title.add(rowStage2Title_2)

rowTitle_2 = JPanel()
rowTitle_2.setLayout(BoxLayout(rowTitle_2, BoxLayout.X_AXIS))
rowTitle_2_1 = JLabel("Stage3: Modify the Dispatcher Options so the trains move")
rowTitle_2_1.add(Box.createHorizontalGlue());
rowTitle_2_1.setAlignmentX(rowTitle_2_1.LEFT_ALIGNMENT)
rowTitle_2_2 = JLabel("")     #start_filename + "_icons"

rowTitle_2.add(Box.createVerticalGlue())
rowTitle_2.add(Box.createRigidArea(Dimension(20, 0)))
rowTitle_2.add(rowTitle_2_1)
rowTitle_2.add(Box.createRigidArea(Dimension(20, 0)))
rowTitle_2.add(rowTitle_2_2)

row_Title_3 = JPanel()
row_Title_3.setLayout(BoxLayout(row_Title_3, BoxLayout.X_AXIS))
rowTitle_3_1 = JLabel("*******************************************************************")
rowTitle_3_1.add(Box.createHorizontalGlue());
rowTitle_3_1.setAlignmentX(rowTitle_3_1.LEFT_ALIGNMENT)
rowTitle_3_2 = JLabel("")

row_Title_3.add(Box.createVerticalGlue())
row_Title_3.add(Box.createRigidArea(Dimension(20, 0)))
row_Title_3.add(rowTitle_3_1)
row_Title_3.add(Box.createRigidArea(Dimension(20, 0)))
row_Title_3.add(rowTitle_3_2)

rowStage2Separator = JPanel()
rowStage2Separator.setLayout(BoxLayout(rowStage2Separator, BoxLayout.X_AXIS))
rowStage2Separator_1 = JLabel("*******************************************************************")
rowStage2Separator_1.add(Box.createHorizontalGlue());
rowStage2Separator_1.setAlignmentX(rowStage2Separator_1.LEFT_ALIGNMENT)
rowStage2Separator_2 = JLabel("")

rowStage2Separator.add(Box.createVerticalGlue())
rowStage2Separator.add(Box.createRigidArea(Dimension(20, 0)))
rowStage2Separator.add(rowStage2Separator_1)
rowStage2Separator.add(Box.createRigidArea(Dimension(20, 0)))
rowStage2Separator.add(rowStage2Separator_2)

rowStage1Separator = JPanel()
rowStage1Separator.setLayout(BoxLayout(rowStage1Separator, BoxLayout.X_AXIS))
rowStage1Separator_1 = JLabel("*******************************************************************")
rowStage1Separator_1.add(Box.createHorizontalGlue());
rowStage1Separator_1.setAlignmentX(rowStage1Separator_1.LEFT_ALIGNMENT)
rowStage1Separator_2 = JLabel("")

rowStage1Separator.add(Box.createVerticalGlue())
rowStage1Separator.add(Box.createRigidArea(Dimension(20, 0)))
rowStage1Separator.add(rowStage1Separator_1)
rowStage1Separator.add(Box.createRigidArea(Dimension(20, 0)))
rowStage1Separator.add(rowStage1Separator_2)

rowStage1Button = JPanel()
rowStage1Button.setLayout(BoxLayout(rowStage1Button, BoxLayout.X_AXIS))
rowrowStage1Button_2 = JLabel("Sets Up truck indicators to show sorting progress")
rowrowStage1Button_2.setFont(rowTitle_2_1.getFont().deriveFont(Font.BOLD, 13));

rowrowStage1Button_2.add(Box.createHorizontalGlue());
rowrowStage1Button_2.setAlignmentX(rowrowStage1Button_2.LEFT_ALIGNMENT)
rowStage1Button_1 = JButton("Stage1", actionPerformed = CreateIcons_action)
stage1Button = rowStage1Button_1


rowStage1Button.add(Box.createVerticalGlue())
rowStage1Button.add(Box.createRigidArea(Dimension(20, 0)))
rowStage1Button.add(rowStage1Button_1)
rowStage1Button.add(Box.createRigidArea(Dimension(20, 0)))
rowStage1Button.add(rowrowStage1Button_2)

#initialise_panel_location(stage1Button, stage2Button, stage3Button)
robot = java.awt.Robot()
KeyEvent = java.awt.event.KeyEvent

#setAdvancedRouting()

rowStage2 = JPanel()
rowStage2.setLayout(BoxLayout(rowStage2, BoxLayout.X_AXIS))
rowStage2_1 = JLabel("Set up sensors for stopping in sidings")
rowStage2_1.setFont(rowTitle_2_1.getFont().deriveFont(Font.BOLD, 13));
rowStage2_1.add(Box.createHorizontalGlue());
rowStage2_1.setAlignmentX(rowStage2_1.LEFT_ALIGNMENT)

rowStage2_2 = JButton("Stage2", actionPerformed = ChangeOptions_action)
stage2Button = rowStage2_2

rowStage2.add(Box.createVerticalGlue())
rowStage2.add(Box.createRigidArea(Dimension(20, 0)))
rowStage2.add(rowStage2_2)
rowStage2.add(Box.createRigidArea(Dimension(20, 0)))
rowStage2.add(rowStage2_1)

initialise_panel_location(stage1Button, stage2Button)
#rowStage1Title_1 = JLabel("    Modifies: " + start_filename + "  Creates backup: " + backup_filename)

#Title
panel.add(leftJustify(rowTitle_2))
panel.add(leftJustify(rowTitle_22))
panel.add(leftJustify(row_Title_3))

#stage1
panel.add(leftJustify(rowStage1Button))
panel.add(leftJustify(rowStage1Separator))

#stage2
panel.add(leftJustify(rowStage2))
panel.add(leftJustify(rowStage2Separator))

frame.pack()
frame.setVisible(True)

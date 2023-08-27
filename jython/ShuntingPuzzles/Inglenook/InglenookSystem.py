import java
from java.awt import Dimension
from javax.swing import JButton, JFrame,JPanel,BoxLayout,Box
from javax.swing import JLabel, JMenu, JMenuItem, JMenuBar
from javax.swing import JFileChooser,JTextField, BorderFactory
from javax.swing import SwingWorker, SwingUtilities
from javax.swing import WindowConstants, JDialog, JTextArea, JComboBox
from java.awt import Color, Font, Frame
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

# @print_name()
def get_siding_turnout(siding):
    print "q"
    s = siding.split("#")[1]
    print "siding", siding
    for turnout in turnouts.getNamedBeanSet():
        comment = turnout.getComment()
        if comment != None:
            #print "comment" , comment
            if "#" in comment:
                #print "comment" , comment
                #print "s", s, "comment.split('#')[0]", str(comment.split('#')[1]), "sensor", sensor, sensor.getUserName()
                if s == str(comment.split('#')[1]):
                    return turnout.getUserName()
                print "s",s,"x", str(comment.split('#')[1])
    return None

def get_turnout_direction(turnoutName):
    print "x"
    turnout = turnouts.getTurnout(turnoutName)
    print "x1"
    comment = turnout.getComment()
    print "x2", comment
    if "$" in comment:
        s = comment.split("$")[1]
        print "x3"
        s = s.replace("$","")
        print "x4"
        return s
    else:
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

def delete_turnout_comment(siding_name):
    # delete the comment for turnout 'siding_name'
    for turnout in turnouts.getNamedBeanSet():
        comment = turnout.getComment()
        if comment != None:
            if siding_name in comment:
                comment_without_siding_name = ""
                str_list = comment.split(siding_name)
                for element in str_list:
                    if element != siding_name and "#" not in element:
                        comment_without_siding_name += element
                turnout.setComment(comment_without_siding_name)

def delete_turnout_direction_comment(turnout):
    # delete the comment for turnout 'siding_name'
    comment = turnout.getComment()
    if comment != None:
        if "$" in comment:
            comment_without_siding_name = ""
            str_list = comment.split("$")
            print "str_list",str_list
            for element in str_list:
                element = element.replace("  ","")
                if element != "Thrown" and element != "Closed":
                    comment_without_siding_name += element
            turnout.setComment(comment_without_siding_name)
# @print_name()
def update_turnout_comment(siding_name, siding_turnout):

    delete_turnout_comment(siding_name)

    # insert the comment siding_name
    print "spur_turnout = ", siding_turnout.getUserName()
    siding_turnout_comment = siding_turnout.getComment()
    if siding_turnout_comment == None or siding_turnout_comment == "":
        siding_turnout_comment = siding_name
    else:
        siding_turnout_comment = siding_turnout_comment + " " + siding_name
    siding_turnout.setComment(siding_turnout_comment)

def update_turnout_direction_comment(turnout_direction, siding_turnout):

    delete_turnout_direction_comment(siding_turnout)

    # insert th comment siding_name
    print "turnout = ", siding_turnout.getUserName()
    siding_turnout_comment = siding_turnout.getComment()
    if siding_turnout_comment == None or siding_turnout_comment == "":
        siding_turnout_comment = "$" + turnout_direction + "$"
    else:
        siding_turnout_comment = siding_turnout_comment + " $" + turnout_direction + "$"
    siding_turnout.setComment(siding_turnout_comment)

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

    global sensorComboBox, blockComboBox, turnoutComboBox, turnoutComboBox2
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
        
    #**********************************************************************

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

    #**********************************************************************
    [T12_turnout_cb, T3_turnout_cb, main_turnout_cb]= turnoutComboBox

    T12_turnout_name = T12_turnout_cb.getSelectedItem()
    if T12_turnout_name != None:
        T12_turnout = turnouts.getTurnout(str(T12_turnout_name))
        update_turnout_comment("#IS_turnout_12#", T12_turnout)
    else:
        delete_turnout_comment("#IS_turnout_12#")

    T3_turnout_name = T3_turnout_cb.getSelectedItem()
    if T3_turnout_name != None:
        T3_turnout = turnouts.getTurnout(str(T3_turnout_name))
        update_turnout_comment("#IS_turnout_3#", T3_turnout)
    else:
        delete_turnout_comment("#IS_turnout_3#")

    main_turnout_name = main_turnout_cb.getSelectedItem()
    if main_turnout_name != None:
        main_turnout = turnouts.getTurnout(str(main_turnout_name))
        update_turnout_comment("#IS_turnout_main#", main_turnout)
    else:
        delete_turnout_comment("#IS_turnout_Tmain#")

    #**********************************************************************

    [T12_turnout_direction_cb, T3_turnout_direction_cb, main_turnout_direction_cb]= turnoutComboBox2

    T12_turnout_direction = T12_turnout_direction_cb.getSelectedItem()
    if T12_turnout_direction != None:
        # T12_turnout_direction1 = str(T12_turnout_direction)
        print "T12_turnout_direction",T12_turnout_direction
        update_turnout_direction_comment(T12_turnout_direction, T12_turnout)
    else:
        delete_turnout_direction_comment(T12_turnout)

    T3_turnout_direction = T3_turnout_direction_cb.getSelectedItem()
    if T3_turnout_direction != None:
        print "T3_turnout_direction", T3_turnout_direction
        # T3_turnout_direction = turnouts.getTurnout(str(T3_turnout_name))
        update_turnout_direction_comment(T3_turnout_direction, T3_turnout)
    else:
        delete_turnout_comment(T3_turnout)

    main_turnout_direction = main_turnout_direction_cb.getSelectedItem()
    if main_turnout_direction != None:
        print "Tmain_turnout_direction", main_turnout_direction
        # Tmain_turnout_direction = turnouts.getTurnout(str(Tmain_turnout_name))
        update_turnout_direction_comment(main_turnout_direction, main_turnout)
    else:
        delete_turnout_comment(Tmain_turnout)

    #**********************************************************************

    comp = event.getSource()
    win = SwingUtilities.getWindowAncestor(comp)
    win.dispose()
def Cancel_action(event):
    global sensorComboBox, blockComboBox, turnoutComboBox, turnoutComboBox2
    sensor = sensors.getSensor("CB11")
    sensorComboBox[0].setSelectedItem(sensor)
    item = sensorComboBox[0].getSelectedItem()
    print item
    comp = event.getSource()
    win = SwingUtilities.getWindowAncestor(comp)
    win.dispose()

def set_sensors_in_sidings(msg):
    global sensorComboBox, blockComboBox, turnoutComboBox, turnoutComboBox2
    print "a"
    dialog = JDialog(None, 'Set sensors in sidings', False)
    panel = jmri.jmrit.beantable.beanedit.BeanItemPanel()
    panel.setLayout(BoxLayout(panel, BoxLayout.Y_AXIS))
    msg = "Set the sensors for the sidings"
    l = JLabel("   "+msg)
    l.setFont(l.getFont().deriveFont(Font.BOLD, 13))
    panel.add(leftJustify(l))
    bean = None
    n = jmri.NamedBean.DisplayOptions.DISPLAYNAME
    sensorComboBox=[]
    rowTitle_22=[]
    for i in range(4):
        if i == 0:
            msg = "spur      "
        else:
            msg = "siding   " + str(i)
        sensorComboBox.append(jmri.swing.NamedBeanComboBox(sensors))
        sensorComboBox[i].setAllowNull(True)
        sensorComboBox[i].setPreferredSize(Dimension(300, 20));
        siding = "#IS_"+msg.replace(" ","")+"_sensor#"
        sensorName = get_siding_sensor(siding)
        print "sensorName", i, sensorName
        if sensorName != None:
            sensor = sensors.getSensor(sensorName)
            sensorComboBox[i].setSelectedItem(sensor)
            item = sensorComboBox[i].getSelectedItem()
        jmri.util.swing.JComboBoxUtil.setupComboBoxMaxRows(sensorComboBox[i])
        rowTitle_22.append(JPanel())
        rowTitle_22[i].add(Box.createVerticalGlue())
        if i == 3:
            msg = "long sid " + str(i)
        rowTitle_22[i].add(JTextArea(msg))
        rowTitle_22[i].add(Box.createRigidArea(Dimension(20, 0)))
        rowTitle_22[i].add(Box.createHorizontalGlue())
        rowTitle_22[i].add(sensorComboBox[i])
        panel.add(leftJustify(rowTitle_22[i]))

    l1 = JLabel("   " + "Set the blocks for the siding and mid section")
    l1.setFont(l1.getFont().deriveFont(Font.BOLD, 13))
    panel.add(leftJustify(l1))

    blockComboBox=[]
    rowTitle_23=[]
    for i in range(5):
        if i == 0:
            msg = "spur      "
        elif i == 1:
            msg = "mid       "
        else:
            msg = "siding   " + str(i-1)
        blockComboBox.append(jmri.swing.NamedBeanComboBox(jmri.InstanceManager.getNullableDefault(jmri.BlockManager)))
        blockComboBox[i].setAllowNull(True)
        blockComboBox[i].setPreferredSize(Dimension(300, 20));
        siding = "#IS_block_"+msg.replace(" ","")+"#"
        blockName = get_siding_block(siding)
        if blockName != None:
            print "blockname not none", blockName
            block = blocks.getBlock(blockName)
            blockComboBox[i].setSelectedItem(block)
        jmri.util.swing.JComboBoxUtil.setupComboBoxMaxRows(blockComboBox[i])
        rowTitle_23.append(JPanel())
        rowTitle_23[i].add(Box.createVerticalGlue())
        if i == 4:
            msg = "long sid " + str(i-1)
        rowTitle_23[i].add(JTextArea(msg))
        rowTitle_23[i].add(Box.createRigidArea(Dimension(20, 0)))
        rowTitle_23[i].add(Box.createHorizontalGlue())
        rowTitle_23[i].add(blockComboBox[i])
        panel.add(leftJustify(rowTitle_23[i]))

    l2 = JLabel("   " + "Set the turnouts for the sidings and mainline")
    l2.setFont(l.getFont().deriveFont(Font.BOLD, 13))
    panel.add(leftJustify(l2))
    bean = None
    n = jmri.NamedBean.DisplayOptions.DISPLAYNAME
    turnoutComboBox=[]
    turnoutComboBox2 = []
    rowTitle_24=[]
    for i in range(3):
        if i == 0:
            msg = "turnout to 1 & 2"
        elif i == 1:
            msg = "turnout to 3    "
        elif i == 2:
            msg = "turnout to main "
        turnoutComboBox.append(jmri.swing.NamedBeanComboBox(turnouts))
        turnoutComboBox[i].setAllowNull(True)
        turnoutComboBox2.append(JComboBox(("Thrown", "Closed")))
        siding = "#IS_"+msg.replace(" ","").replace("to","_").replace("&","")+"#"
        turnoutName = get_siding_turnout(siding)
        print "turnoutName", i, turnoutName
        turnoutDirection = None
        if turnoutName != None:
            turnout = turnouts.getTurnout(turnoutName)
            turnoutComboBox[i].setSelectedItem(turnout)
            # item = turnoutComboBox[i].getSelectedItem()
            turnoutDirection = get_turnout_direction(turnoutName)
        print "a2"
        print "turnoutDirection", turnoutDirection
        print "a1"
        if turnoutDirection != None:
            turnoutComboBox2[i].setSelectedItem(turnoutDirection)
            # item = turnoutComboBox2[i].getSelectedItem()
        print "b"
        jmri.util.swing.JComboBoxUtil.setupComboBoxMaxRows(turnoutComboBox[i])
        rowTitle_24.append(JPanel())
        rowTitle_24[i].add(Box.createVerticalGlue())
        rowTitle_24[i].add(JTextArea(msg))
        rowTitle_24[i].add(Box.createRigidArea(Dimension(20, 0)))
        rowTitle_24[i].add(Box.createHorizontalGlue())
        rowTitle_24[i].add(turnoutComboBox[i])
        rowTitle_24[i].add(Box.createRigidArea(Dimension(20, 0)))
        print "a"
        if i == 0:
            msg = "to 1:   "
        elif i == 1:
            msg = "to 3:   "
        else:
            msg = "to main:"
        rowTitle_24[i].add(JTextArea(msg))
        # rowTitle_24[i].add(Box.createHorizontalGlue())
        rowTitle_24[i].add(turnoutComboBox2[i])
        panel.add(leftJustify(rowTitle_24[i]))
    print "c"
    rowStage1Button_1 = JButton("OK", actionPerformed = OK_action)
    rowStage1Button_2 = JButton("Cancel", actionPerformed = Cancel_action)
    rowTitle_25 = JPanel()
    rowTitle_25.add(Box.createVerticalGlue())
    rowTitle_25.add(Box.createRigidArea(Dimension(20, 0)))
    rowTitle_25.add(rowStage1Button_1)
    rowTitle_25.add(Box.createRigidArea(Dimension(20, 0)))
    rowTitle_25.add(rowStage1Button_2)
    panel.add(leftJustify(rowTitle_25))


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

def delete_open_inglenook_panels():
    for frame in Frame.getFrames ():
        if frame.getTitle() == 'Inglenook Sidings':
            print ("panel found Inglenook Sidings")
            frame.dispose()

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

delete_open_inglenook_panels()

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
rowrowStage1Button_2 = JLabel("Set up sensors for stopping in sidings")
rowrowStage1Button_2.setFont(rowTitle_2_1.getFont().deriveFont(Font.BOLD, 13));

rowrowStage1Button_2.add(Box.createHorizontalGlue());
rowrowStage1Button_2.setAlignmentX(rowrowStage1Button_2.LEFT_ALIGNMENT)
rowStage1Button_1 = JButton("Stage1", actionPerformed = ChangeOptions_action)

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
rowStage2_1 = JLabel("Set Up truck indicators to show sorting progress")
rowStage2_1.setFont(rowTitle_2_1.getFont().deriveFont(Font.BOLD, 13));
rowStage2_1.add(Box.createHorizontalGlue());
rowStage2_1.setAlignmentX(rowStage2_1.LEFT_ALIGNMENT)

rowStage2_2 = JButton("Stage2", actionPerformed = CreateIcons_action)
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

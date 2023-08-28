###############################################################################
#
# class OptionDialog
# Some Swing dialogs
#

# class OffActionMaster *
# allows actions when buttons are turned off
#
# class ResetButtonMaster *
# if a button is turned on, this class turns off all the others.
# allows only one station button to be active at a time
#
# class MoveTrain
# Calls dispatcher to move train from one station to another
# given engine and start and end positions
#
# class InglenookMaster *
#
#
# class RunInglenookMaster
# starts the classes marked with * above in threads so they can do their work
#
#
###############################################################################
import java
import jmri
import re
from javax.swing import JOptionPane
import os
import imp
import copy
import org

from javax.swing import JOptionPane, JFrame, JLabel, JButton, JTextField, JFileChooser, JMenu, JMenuItem, JMenuBar,JComboBox,JDialog,JList

import sys

# # include the graphcs library
# my_path_to_jars = jmri.util.FileUtil.getExternalFilename('scripts:DispatcherSystem/jars/jgrapht.jar')
# sys.path.append(my_path_to_jars) # add the jar to your path
# from org.jgrapht.alg import DijkstraShortestPath
# from org.jgrapht.graph import DefaultWeightedEdge
# from org.jgrapht.graph import DirectedWeightedMultigraph

#allow import of pyj2D
my_path_to_pyj2d = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/jars')
sys.path.append(my_path_to_pyj2d)  # add my_path_to_pyj2d to your path

# my_path_to_pyj2d = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/pyj2d2/pyj2d.jar')
# sys.path.append(my_path_to_pyj2d)  # add my_path_to_pyj2d to your path
import pyj2d as pygame

#allow import of inglenook and other classes in py files in directory Inglenook
inglenook = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/Inglenook')
sys.path.append(inglenook)  # add my_path_to_pyj2d to your path
import inglenook



#############################################################################################
#from inglenookMaster import RunInglenook
InglenookMaster1 = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/Inglenook/inglenookMaster.py')
execfile(InglenookMaster1)

MoveTrain = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/Inglenook/move_train.py')
exec(open (MoveTrain).read())

#import inglenook

#exec(open (InglenookMaster).read())

#
# Set some global variables
#

logLevel = 0          # for debugging
trains = {}           # dictionary of trains shared over classes
instanceList=[]       # instance list of threads shared over classes
g = None              # graph shared over classes

time_to_stop_in_station = 10000   # time to stop in station in stopping mode(msec)

#############################################################################################
# the file was split up to avoid errors
# so now include the split files

# FileMoveTrain has to go before CreateScheduler
# FileMoveTrain = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/MoveTrain.py')
# execfile(FileMoveTrain)
#
# CreateScheduler = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/Scheduler.py')
# execfile(CreateScheduler)
#
# LogixNG_functions = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/Simulation.py')
# execfile(LogixNG_functions)

#LogixNG_functions = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntinPuzzles/Inglenook/logicNGScripts/getSidingSensor.py')
#execfile(LogixNG_functions)

#############################################################################################

class OptionDialog( jmri.jmrit.automat.AbstractAutomaton ) :
    CLOSED_OPTION = False
    logLevel = 0

    def List(self, title, list_items):
        list = JList(list_items)
        list.setSelectedIndex(0)
        i = []
        self.CLOSED_OPTION = False
        options = ["OK"]
        while len(i) == 0:
            s = JOptionPane.showOptionDialog(None,
            list,
            title,
            JOptionPane.YES_NO_OPTION,
            JOptionPane.PLAIN_MESSAGE,
            None,
            options,
            options[0])
            if s == JOptionPane.CLOSED_OPTION:
                self.CLOSED_OPTION = True
                if self.logLevel > 1 : print "closed Option"
                return
            i = list.getSelectedIndices()
        index = i[0]
        return list_items[index]


    #list and option buttons
    def ListOptions(self, list_items, title, options):
        list = JList(list_items)
        list.setSelectedIndex(0)
        self.CLOSED_OPTION = False
        s = JOptionPane.showOptionDialog(None,
            list,
            title,
            JOptionPane.YES_NO_OPTION,
            JOptionPane.PLAIN_MESSAGE,
            None,
            options,
            options[1])
        if s == JOptionPane.CLOSED_OPTION:
            self.CLOSED_OPTION = True
            return
        index = list.getSelectedIndices()[0]
        return [list_items[index], options[s]]

        # call using
        # list_items = ["list1","list2"]
        # options = ["opt1", "opt2", "opt3"]
        # title = "title"
        # result = OptionDialog().ListOptions(list_items, title, options)
        # list= result[0]
        # option = result[1]
        # print "option= " ,option, " list = ",list

    def variable_combo_box(self, options, default, msg, title = None, type = JOptionPane.QUESTION_MESSAGE):


        result = JOptionPane.showInputDialog(
            None,                                   # parentComponent
            msg,                                    # message text
            title,                                  # title
            type,                                   # messageType
            None,                                   # icon
            options,                                # selectionValues
            default                                 # initialSelectionValue
            )

        return result


    def displayMessage2(self, msg, title = ""):
        self.displayMessage(msg, "", True)
    def displayMessage1(self, msg, title = ""):
        self.displayMessage(msg, "", True)

    def displayMessage(self, msg, title = "", display = True):
        global display_message_flag

        if 'display_message_flag' not in globals():
            display_message_flag = True

        # if display_message_flag:
        if display:

            s = JOptionPane.showOptionDialog(None,
                    msg,
                    title,
                    JOptionPane.YES_NO_OPTION,
                    JOptionPane.PLAIN_MESSAGE,
                    None,
                    ["OK"],
                    None)
            if s == JOptionPane.CLOSED_OPTION:
                title = "choose"
                opt1 = "continue"
                opt2 = "stop system"
                msg = "you may wish to abort"
                s1 = self.customQuestionMessage2str(msg, title, opt1, opt2)
                if s1 == opt2:
                    #stop system
                    Mywindow2()
                    StopMaster().stop_all_threads()

                return s
            #JOptionPane.showMessageDialog(None, msg, 'Message', JOptionPane.WARNING_MESSAGE)
            return s
        #     print "display_message_flag ", display_message_flag
        # else:
        #     print "display_message_flag ", display_message_flag

    def customQuestionMessage(self, msg, title, opt1, opt2, opt3):
        self.CLOSED_OPTION = False
        options = [opt1, opt2, opt3]
        s = JOptionPane.showOptionDialog(None,
        msg,
        title,
        JOptionPane.YES_NO_CANCEL_OPTION,
        JOptionPane.QUESTION_MESSAGE,
        None,
        options,
        options[2])
        if s == JOptionPane.CLOSED_OPTION:
            self.CLOSED_OPTION = True
            return
        return s

    def customQuestionMessage3str(self, msg, title, opt1, opt2, opt3):
        self.CLOSED_OPTION = False
        options = [opt1, opt2, opt3]
        s = JOptionPane.showOptionDialog(None,
                                         msg,
                                         title,
                                         JOptionPane.YES_NO_CANCEL_OPTION,
                                         JOptionPane.QUESTION_MESSAGE,
                                         None,
                                         options,
                                         options[0])
        if s == JOptionPane.CLOSED_OPTION:
            self.CLOSED_OPTION = True
            return
        if s == JOptionPane.YES_OPTION:
            s1 = opt1
        elif s == JOptionPane.NO_OPTION:
            s1 = opt2
        else:
            s1 = opt3
        return s1

    def customQuestionMessage2(self, msg, title, opt1, opt2):
        self.CLOSED_OPTION = False
        options = [opt1, opt2]
        s = JOptionPane.showOptionDialog(None,
        msg,
        title,
        JOptionPane.YES_NO_OPTION,
        JOptionPane.QUESTION_MESSAGE,
        None,
        options,
        options[0])
        if s == JOptionPane.CLOSED_OPTION:
            self.CLOSED_OPTION = True
            return
        return s

    def customQuestionMessage2str(self, msg, title, opt1, opt2):
        self.CLOSED_OPTION = False
        options = [opt1, opt2]
        s = JOptionPane.showOptionDialog(None,
        msg,
        title,
        JOptionPane.YES_NO_OPTION,
        JOptionPane.QUESTION_MESSAGE,
        None,
        options,
        options[1])
        if s == JOptionPane.CLOSED_OPTION:
            self.CLOSED_OPTION = True
            return
        if s == JOptionPane.YES_OPTION:
            s1 = opt1
        else:
            s1 = opt2
        return s1

    def customMessage(self, msg, title, opt1):
        self.CLOSED_OPTION = False
        options = [opt1]
        s = JOptionPane.showOptionDialog(None,
        msg,
        title,
        JOptionPane.YES_OPTION,
        JOptionPane.PLAIN_MESSAGE,
        None,
        options,
        options[0])
        if s == JOptionPane.CLOSED_OPTION:
            self.CLOSED_OPTION = True
            return
        return s

    def input(self,msg, title, default_value):
        options = None
        x = JOptionPane.showInputDialog( None, msg,title, JOptionPane.QUESTION_MESSAGE, None, options, default_value);
        #x = JOptionPane.showInputDialog(None,msg)
        return x





class modifiableJComboBox:

    def __init__(self,list, msg):
        #list = self.get_all_roster_entries_with_speed_profile()
        jcb = JComboBox(list)
        jcb.setEditable(True)
        JOptionPane.showMessageDialog( None, jcb, msg, JOptionPane.QUESTION_MESSAGE)
        self.ans = str(jcb.getSelectedItem())

    def return_val(self):
        return self.ans



class StopMaster(jmri.jmrit.automat.AbstractAutomaton):

    def __init__(self):
        self.logLevel = 0
        if self.logLevel > 0: print 'Create Stop Thread'
        self.opd = OptionDialog()

    def setup(self):
        self.stop_master_sensor = sensors.getSensor("stopInglenookSensor")
        if self.stop_master_sensor is None:
            return False
        self.stop_master_sensor.setKnownState(INACTIVE)

        # self.start_scheduler = sensors.getSensor("startSchedulerSensor")
        # self.start_scheduler.setKnownState(INACTIVE)
        return True

    def handle(self):
        global timebase
        self.waitSensorActive(self.stop_master_sensor)
        #self.stop_master_sensor.setKnownState(INACTIVE)

        print "waited"
        msg = "stop or list threads"
        title = "Transits"
        opt1 = "stop"
        opt2 = "list threads"

        requested_action = self.opd.customQuestionMessage2str(msg, title, opt1, opt2)
        if self.opd.CLOSED_OPTION == True:
            self.stop_master_sensor.setKnownState(INACTIVE)
            #self.reset_start_sensor()
            return True
        if requested_action == opt1:
            #
            self.stop_all_threads()
            #self.stop_master_sensor.setKnownState(INACTIVE)
            self.reset_start_sensor()
            return False
        else:
            #self.reset_start_sensor()
            self.list_all_threads()
            #self.stop_master_sensor.setKnownState(INACTIVE)
            self.reset_start_sensor()
            return False

        #return True

    def reset_start_sensor(self):
        self.new_train_sensor = sensors.getSensor("startInglenookSensor")
        self.new_train_sensor.setKnownState(INACTIVE)

    def stop_all_threads(self):
        try:
            summary = jmri.jmrit.automat.AutomatSummary.instance()
            automatsList = java.util.concurrent.CopyOnWriteArrayList()
            for automat in summary.getAutomats():
                automatsList.add(automat)

            for automat in automatsList:
                automat.stop()
        except:
            pass
    def list_all_threads(self):
        summary = jmri.jmrit.automat.AutomatSummary.instance()
        automatsList = java.util.concurrent.CopyOnWriteArrayList()
        for automat in summary.getAutomats():
            automatsList.add(automat)

        for automat in automatsList:
            if automat.isRunning():
                print 'automatList "{}" thread running'.format(automat.getName())
            else:
                print 'automatList "{}" thread not running'.format(automat.getName())

    # def remove_listener(self):
    #     try:
    #         #stop the scheduler timebase listener
    #         if self.logLevel > 0: print "removing listener"
    #         timebase.removeMinuteChangeListener(TimeListener())
    #         return False
    #     except NameError:
    #         if self.logLevel > 0: print "Name error"
    #         return False
    #     else:
    #         return False
    #
    # def delete_active_transits(self):
    #
    #     DF = jmri.InstanceManager.getDefault(jmri.jmrit.dispatcher.DispatcherFrame)
    #     activeTrainsList = DF.getActiveTrainsList()
    #     for i in range(0, activeTrainsList.size()) :
    #         activeTrain = activeTrainsList.get(i)
    #         DF.terminateActiveTrain(activeTrain)

# End of class StopMaster

class OffActionMaster(jmri.jmrit.automat.AbstractAutomaton):

    button_sensors_to_watch = []
    def __init__(self):
        self.logLevel = 0

    def init(self):
        if self.logLevel > 0: print 'Create OffActionMaster Thread'
        self.get_run_buttons()
        self.get_route_dispatch_buttons()

        self.button_sensors_to_watch = self.run_stop_sensors
        if self.logLevel > 0: print "button to watch" , str(self.button_sensors_to_watch)
        #wait for one to go inactive
        button_sensors_to_watch_JavaList = java.util.Arrays.asList(self.button_sensors_to_watch)
        self.waitSensorState(button_sensors_to_watch_JavaList, INACTIVE)

        if self.logLevel > 0: print "button went inactive"
        sensor_that_went_inactive = [sensor for sensor in self.button_sensors_to_watch if sensor.getKnownState() == INACTIVE][0]
        if self.logLevel > 0: print "sensor_that_went_inactive" , sensor_that_went_inactive
        start_sensor = sensors.getSensor("startInglenookSensor")
        stop_sensor =  sensors.getSensor("stopInglenookSensor")
        if self.logLevel > 0: print "start_sensor" , start_sensor
        if self.logLevel > 0: print "stop_sensor" , stop_sensor
        if sensor_that_went_inactive in self.run_stop_sensors:
            if self.logLevel > 0: print "run stop sensor went inactive"

            if sensor_that_went_inactive == start_sensor:
                self.sensor_to_look_for = stop_sensor
                if self.logLevel > 0: print "start sensor went inactive"
                if self.logLevel > 0: print "setting stop sensor active"
                stop_sensor.setKnownState(ACTIVE)
                # self.waitMsec(5000)
                # if self.logLevel > 0: print "setting start sensor active"
                # start_sensor.setKnownState(ACTICE)
            elif sensor_that_went_inactive == stop_sensor:
                self.sensor_to_look_for = start_sensor
                if self.logLevel > 0: print "stop sensor went inactive"
                if self.logLevel > 0: print "setting start sensor active"
                start_sensor.setKnownState(ACTIVE)
                # self.waitMsec(5000)
                # start_sensor.setKnownState(ACTICE)
                pass#

        if self.logLevel > 0: print "finished OffActionMaster setup"

    def setup(self):
        if self.logLevel > 0: print "starting OffActionMaster setup"
        #get dictionary of buttons self.button_dict
        #self.get_route_dispatch_buttons()

        return True

    def handle(self):
        if self.logLevel > 0: print "started handle"
        #for pairs of buttons, if one goes off the other is set on
        #self.button_sensors_to_watch = self.run_sensor_to_look_for
        if self.logLevel > 0: print "button to watch" , str(self.button_sensors_to_watch)
        #wait for one to go active
        button_sensors_to_watch_JavaList = java.util.Arrays.asList(self.button_sensors_to_watch)
        self.waitSensorState(button_sensors_to_watch_JavaList, INACTIVE)
        #determine which one changed
        if self.logLevel > 0: print "sensor went inactive"
        sensor_that_went_inactive = [sensor for sensor in self.button_sensors_to_watch if sensor.getKnownState() == INACTIVE][0]

        if sensor_that_went_inactive in self.run_stop_sensors:
            if self.logLevel > 0: print "run stop sensor went inactive"
            start_sensor = sensors.getSensor("startInglenookSensor")
            stop_sensor =  sensors.getSensor("stopInglenookSensor")
            if sensor_that_went_inactive == start_sensor:
                self.sensor_to_look_for = stop_sensor
                if self.logLevel > 0: print "start sensor went inactive"
                if self.logLevel > 0: print "setting stop sensor active"
                stop_sensor.setKnownState(ACTIVE)
                # self.waitMsec(5000)
                # if self.logLevel > 0: print "setting start sensor active"
                # start_sensor.setKnownState(ACTICE)
            elif sensor_that_went_inactive == stop_sensor:
                self.sensor_to_look_for = start_sensor
                if self.logLevel > 0: print "stop sensor went inactive"
                if self.logLevel > 0: print "setting start sensor active"
                start_sensor.setKnownState(ACTIVE)

        if self.logLevel > 0: print "end handle"
        #self.waitMsec(20000)
        return False
    def get_route_dispatch_buttons(self):
        self.setup_route_or_run_dispatch_sensors = [sensors.getSensor(sensorName) for sensorName in ["setDispatchSensor","setRouteSensor","setStoppingDistanceSensor"]]
        #self.route_dispatch_states = [self.check_sensor_state(rd_sensor) for rd_sensor in self.setup_route_or_run_dispatch_sensors]
        pass

    def get_run_buttons(self):
        self.run_stop_sensors = [sensors.getSensor(sensorName) for sensorName in ["startInglenookSensor"]]



# class ResetButtonMaster(jmri.jmrit.automat.AbstractAutomaton):
#
#     # if a button is turned on, this routing turns it off
#     # another class will actually respond to the button and do something
#
#     # also monitors Setup Dispatch and Setup Route and also Run Route
#
#     button_sensors_to_watch = []
#     def __init__(self):
#         self.logLevel = 0
#
#     def init(self):
#         if self.logLevel > 0: print 'Create ResetButtonMaster Thread'
#         self.od = OptionDialog()
#
#     def setup(self):
#         if self.logLevel > 0: print "starting ResetButtonMaster setup"
#
#         #get dictionary of buttons self.button_dict
#         self.get_buttons()                      # responds to station buttons
#         self.get_route_dispatch_buttons()       #responds to "setDispatchSensor","setRouteSensor","setStoppingDistanceSensor"
#         self.get_route_run_button()             # responds ro run route button
#         #set all move_to buttons inactive
#         for sensor in self.button_sensors:
#             sensor.setKnownState(INACTIVE)
#
#         for sensor in self.setup_route_or_run_dispatch_sensors:
#             sensor.setKnownState(INACTIVE)
#
#         for sensor in self.route_run_sensor:
#             sensor.setKnownState(INACTIVE)
#
#
#         self.button_sensors_to_watch = self.route_run_sensor + self.button_sensors + self.setup_route_or_run_dispatch_sensors
#
#         if self.logLevel > 0: print "self.button_sensors_to_watch_init", [sensor.getUserName() for sensor in self.button_sensors_to_watch]
#
#         self.sensor_active = None
#         self.sensor_active_route_dispatch = None
#         self.sensor_active_run_dispatch = None
#         self.sensor_active_old = None
#         self.sensor_active_route_dispatch_old = None
#
#         if self.logLevel > 0: print "finished ResetButtonMaster setup"
#         return True
#
#     def handle(self):
#         #wait for a sensor to go active
#         button_sensors_to_watch_JavaList = java.util.Arrays.asList(self.button_sensors_to_watch)
#         self.waitSensorState(button_sensors_to_watch_JavaList, ACTIVE)
#
#         #determine which one changed
#         if self.logLevel > 0: print "self.button_sensors_to_watch",self.button_sensors_to_watch
#         sensor_active_all_array = [sensor for sensor in self.button_sensors_to_watch if sensor.getKnownState() == ACTIVE]
#
#         #reset button_sensors_to_watch
#         self.button_sensors_to_watch = self.route_run_sensor + self.button_sensors + self.setup_route_or_run_dispatch_sensors
#
#         # 1) modify button_sensors_to_watch so we don't keep triggering same senosr active
#         # 2) perform the correct action if a new button has been triggered
#         #    note we have to see whether a new sensor has been triggered by looking at old values
#
#         if self.logLevel > 0: print "sensor_active_all_array" , sensor_active_all_array
#         if self.logLevel > 0: print "self.sensor_active_route_dispatch_old" , self.sensor_active_route_dispatch_old
#         if self.logLevel > 0: print "self.sensor_active_route_dispatch" , self.sensor_active_route_dispatch
#         if self.logLevel > 0: print "self.sensor_active", self.sensor_active
#         if self.logLevel > 0: print "self.sensor_active_old", self.sensor_active_old
#
#         if self.sensor_active_route_dispatch_old != None:
#             self.button_sensors_to_watch.remove(self.sensor_active_route_dispatch_old)
#
#         for sensor in self.setup_route_or_run_dispatch_sensors:
#             if self.logLevel > 0: print "sensor in setup_route_or_run_dispatch_sensors", sensor.getUserName()
#             if sensor in sensor_active_all_array:
#                 if self.logLevel > 0: print "sensor in sensor_active_all_array", sensor.getUserName()
#                 sensor_active_all_array.remove(sensor)
#                 self.sensor_active_route_dispatch = sensor
#                 if self.sensor_active_route_dispatch != None and self.sensor_active_route_dispatch != self.sensor_active_route_dispatch_old:
#                     self.process_setup_route_or_run_dispatch_sensors(self.sensor_active_route_dispatch)
#                     self.sensor_active_route_dispatch_old = self.sensor_active_route_dispatch
#                     if self.logLevel > 0: print "removing ", self.sensor_active_route_dispatch_old
#
#         if len(sensor_active_all_array) > 0:
#             sensor_active_all = sensor_active_all_array[0]   # there should be only one or zero items in this array, and that not in self.setup_route_or_run_dispatch_sensors
#         else:
#             sensor_active_all = None
#
#         #the sensor can be in self.button_sensors or in self.route_run_sensor
#         if sensor_active_all in self.button_sensors:
#             self.sensor_active = sensor_active_all
#             if self.sensor_active != self.sensor_active_old :
#                 self.process_button_sensors(self.sensor_active)
#                 self.sensor_active_old = self.sensor_active
#             self.button_sensors_to_watch.remove(self.sensor_active)
#         elif sensor_active_all in self.route_run_sensor:
#             self.sensor_active_run_dispatch = sensor_active_all
#             self.process_run_route()
#         elif sensor_active_all in self.setup_route_or_run_dispatch_sensors:
#             if self.logLevel > 0: print "there is an error"  #we have eliminated this case already
#         else:
#             pass
#
#         return True
#
#
#
#     def process_button_sensors(self, sensor_changed):
#         [sensor.setKnownState(INACTIVE) for sensor in self.button_sensors if sensor != sensor_changed]
#
#     def  process_setup_route_or_run_dispatch_sensors(self, sensor_changed):
#         if self.logLevel > 0: print "sensor_changed", sensor_changed
#         if sensor_changed == sensors.getSensor("setDispatchSensor"):
#             sensors.getSensor("setRouteSensor").setKnownState(INACTIVE)
#             sensors.getSensor("setStoppingDistanceSensor").setKnownState(INACTIVE)
#             msg = "Press section buttons to set dispatch \nA train needs to be set up in a section first"
#             OptionDialog().displayMessage(msg)
#         elif sensor_changed == sensors.getSensor("setRouteSensor"):
#             sensors.getSensor("setStoppingDistanceSensor").setKnownState(INACTIVE)
#             sensors.getSensor("setDispatchSensor").setKnownState(INACTIVE)
#             msg = "Press section buttons to set route \nThe route may be used to schedule a train"
#             OptionDialog().displayMessage(msg)
#         elif sensor_changed == sensors.getSensor("setStoppingDistanceSensor"):
#             sensors.getSensor("setDispatchSensor").setKnownState(INACTIVE)
#             sensors.getSensor("setRouteSensor").setKnownState(INACTIVE)
#             msg = "Press station buttons to select a section in order to\nset stopping length for that section"
#             OptionDialog().displayMessage(msg)
#         else:
#             msg = "error"
#             OptionDialog().displayMessage(msg)
#
#         self.sensor_active_route_dispatch_old = None
#         self.button_sensors_to_watch = self.route_run_sensor + self.button_sensors + self.setup_route_or_run_dispatch_sensors
#
#
#     def process_run_route(self):
#         self.run_route()
#         sensors.getSensor("runRouteSensor").setKnownState(INACTIVE)
#
#     def get_buttons(self):
#         self.button_sensors = [self.get_button_sensor_given_block_name(station_block_name) for station_block_name in g.station_block_list]
#         self.button_sensor_states = [self.check_sensor_state(button_sensor) for button_sensor in self.button_sensors]
#         # for button_sensor in self.button_sensors:
#             # self.button_dict[button_sensor] = self.check_sensor_state(button_sensor)
#
#     def get_route_dispatch_buttons(self):
#         self.setup_route_or_run_dispatch_sensors = [sensors.getSensor(sensorName) for sensorName in ["setDispatchSensor","setRouteSensor","setStoppingDistanceSensor"]]
#         self.route_dispatch_states = [self.check_sensor_state(rd_sensor) for rd_sensor in self.setup_route_or_run_dispatch_sensors]
#
#     def get_route_run_button(self):
#         self.route_run_sensor = [sensors.getSensor(sensorName) for sensorName in ["runRouteSensor"]]
#
#     def check_sensor_state(self, sensor):
#         #if self.logLevel > 0: print("check_sensor_state",sensor)
#         if sensor == None :
#             #if self.logLevel > 0: print('Sensor in check_sensor_state is none')
#             return None
#         #sensor = sensors.getSensor(sensor_name)
#         if sensor is None:
#             OptionDialog().displayMessage('Sensor {} not found'.format( sensor_name))
#             return
#         currentState = True if sensor.getKnownState() == ACTIVE else False
#         #if self.logLevel > 0: print("check_sensor_state {}".format(currentState))
#         return currentState
#
#     def store_button_states(self):
#         self.button_sensor_states_old = self.button_sensor_states
#         if self.logLevel > 0: print "self.button_sensor_states_old",self.button_sensor_states_old
#         #self.button_dict_old = dict(self.button_dict)
#
#     def get_button_sensor_given_block_name(self, block_name):
#         button_sensor_name = "MoveTo"+block_name.replace(" ","_") +"_stored"
#         button_sensor = sensors.getSensor(button_sensor_name)
#         return button_sensor
#
#     def run_route(self):
#         # list_items = ("Run Route", "Cancel")
#         # title = "choose option"
#         # result = self.od.List(title, list_items)
#         # if self.od.CLOSED_OPTION == True:
#             # return
#         # if result == "Run Route":
#         RouteManager=jmri.InstanceManager.getDefault(jmri.jmrit.operations.routes.RouteManager)
#         list_items = RouteManager.getRoutesByNameList()
#         title = "choose route"
#         s = self.od.List(title, list_items)
#         if self.od.CLOSED_OPTION == True:
#             return
#         routeName = str(s)
#         if self.logLevel > 0: print "routeName", routeName
#         route = RouteManager.getRouteByName(routeName)
#
#         list_items = self.get_list_of_engines_to_move()
#                 # msg = "trains_to_choose" + str(trains_to_choose)
#         if list_items == []:
#             return
#         title = "what train do you want to move?"
#         engine = self.od.List(title, list_items)
#         if self.od.CLOSED_OPTION == True:
#             return
#         station_from = self.get_position_of_train(engine)
#
#         list_items = ["stop at end of route", "return to start position", "return to start position and repeat", "cancel"]
#         title = "What do you want to do"
#         option = self.od.List(title, list_items)
#         if self.od.CLOSED_OPTION == True:
#             return
#         repeat = False
#         dont_run_route = False
#         if option == "stop at end of route":
#             station_to = None
#             repeat = False
#         elif option == "return to start position":
#             station_to = station_from
#             repeat = False
#         elif option == "return to start position and repeat":
#             station_to = station_from
#             repeat = True
#         else:
#             dont_run_route = True
#         if repeat:
#             title = "repeat how many times?"
#             default_value = 3
#             msg = "repeat how many times"
#             no_repetitions = self.od.input(msg, title, default_value)
#         else:
#             no_repetitions = 0
#
#         if dont_run_route == False:
#             if self.logLevel > 0: print "station_from",    station_from, "station_to",station_to, "repeat",repeat
#             run_train = RunRoute(route, g.g_express, station_from, station_to, no_repetitions)
#             run_train.setName("running_route_" + routeName)
#             instanceList.append(run_train)
#             run_train.start()
#
#     def get_list_of_engines_to_move(self):
#         global trains_allocated
#         global trains_dispatched
#
#         #find what train we want to move
#         all_trains = self.get_all_roster_entries_with_speed_profile()
#         #trains to choose from are the allocated - dispatched
#         trains_to_choose = copy.copy(trains_allocated)
#         if self.logLevel > 0: print "trains_dispatchedx", trains_dispatched
#         if self.logLevel > 0: print "trains_allocated",trains_allocated
#         if self.logLevel > 0: print "trains_to_choose",trains_to_choose
#         if trains_dispatched != []:
#             for train in trains_dispatched:
#                 if self.logLevel > 0: print "removing" ,train
#                 trains_to_choose.remove(train)
#                 if self.logLevel > 0: print "trains_to_choose",trains_to_choose
#
#         # JOptionPane.showMessageDialog(None,msg)
#         if trains_to_choose == []:
#             str_trains_dispatched= (' '.join(trains_dispatched))
#             msg = "There are no trains available for dispatch\nTrains dispatched are:\n"+str_trains_dispatched+"\n"
#             title = "Cannot move train"
#             opt1 = "continue"
#             opt2 = "reset all allocations"
#             result = self.od.customQuestionMessage2str(msg, title, opt1, opt2)
#             if result == "reset all allocations":
#                 trains_dispatched = []
#         return trains_to_choose
#
#     def get_position_of_train(self, train_to_move):
#         ## Check the pressed button
#         for station_block_name in g.station_block_list:
#             if self.logLevel > 0: print "station_block_name", station_block_name
#
#             #get a True if the block block_value has the train name in it
#             block_value_state = self.check_train_in_block(station_block_name, train_to_move)
#             if self.logLevel > 0: print "block_value_state= ",block_value_state
#
#             #get a True if the block is occupied
#             block_occupied_state = self.check_sensor_state_given_block_name(station_block_name)
#             if self.logLevel > 0: print "block_occupied_state= ",block_occupied_state
#             if self.logLevel > 0: print ("station block name {} : {}". format(station_block_name, str(block_occupied_state)))
#
#             # # do not attempt to move to where you are
#             # button_pressed_in_occupied_station = (button_station_name == station_block_name)
#
#             #check if the block is occupied and has the required train in it
#             if block_value_state == True and block_occupied_state == True:
#                 # and button_pressed_in_occupied_station == False:
#                 return station_block_name
#         return None
#
#     def get_blockcontents(self, block_name):
#         block = blocks.getBlock(block_name)
#         value =  block.getValue()
#         return value
#
#     def check_train_in_block(self, block_name, train_name):
#         mem_val = self.get_blockcontents(block_name)
#         if train_name == mem_val:
#             return True
#         else:
#             return False
#
#     def check_sensor_state_given_block_name(self, station_block_name):
#         #if self.logLevel > 0: print("station block name {}".format(station_block_name))
#         layoutBlock = layoutblocks.getLayoutBlock(station_block_name)
#         station_sensor = layoutBlock.getOccupancySensor()
#         if station_sensor is None:
#             OptionDialog().displayMessage(' Sensor in block {} not found'.format(station_block_name))
#             return
#         currentState = True if station_sensor.getKnownState() == ACTIVE else False
#         return currentState
#
#     def get_all_roster_entries_with_speed_profile(self):
#         roster_entries_with_speed_profile = []
#         r = jmri.jmrit.roster.Roster.getDefault()
#         for roster_entry in jmri.jmrit.roster.Roster.getAllEntries(r):
#             if self.logLevel > 0: print "roster_entry.getSpeedProfile()",roster_entry,roster_entry.getSpeedProfile()
#             if roster_entry.getSpeedProfile() != None:
#                 roster_entries_with_speed_profile.append(roster_entry.getId())
#                 if self.logLevel > 0: print "roster_entry.getId()",roster_entry.getId()
#         return roster_entries_with_speed_profile
#
#
#
#
#     def set_mem_variable(self, block_name, train_name, block_occupancy):
#         if block_name != None:
#             #print "block_name", block_name
#             #print "self.check_train_in_block:",self.check_train_in_block(block_name, train_name) ,"xxxx"
#             if block_occupancy == True:
#                 #check and set the mem_name
#                 if self.check_train_in_block(block_name, train_name) == False:
#                     #print "setting train", train_name, "in block", block_name
#                     self.set_train_in_block(block_name, train_name)
#
#
#     def get_active_train(self, train_name):
#         DF = jmri.InstanceManager.getDefault(jmri.jmrit.dispatcher.DispatcherFrame)
#         java_active_trains_list = DF.getActiveTrainsList()
#         java_active_trains_Arraylist= java.util.ArrayList(java_active_trains_list)
#         #print "java_active_trains_Arraylist",java_active_trains_Arraylist
#         #print "train_name", train_name
#         for t in java_active_trains_Arraylist:
#             #print "activetrainname=",t.getActiveTrainName()
#             #print "train_name", train_name
#             #print "t.getActiveTrainName().count(train_name)", t.getActiveTrainName().count(train_name)
#             if t.getActiveTrainName().count(train_name) >0:     #check if train_name is contained in
#                 return t
#         return None
#
#     def get_occupied_blocks(self,active_train):
#         block_list = active_train.getBlockList()
#         section_list = active_train.getAllocatedSectionList()
#         start_block = active_train.getStartBlock()
#         end_block = active_train.getEndBlock()
#         seq_no = active_train.getStartBlockSectionSequenceNumber()
#         LastAllocatedSectionSeqNumber = active_train.getLastAllocatedSectionSeqNumber()
#         NextSectionToAllocate = active_train.getNextSectionToAllocate()
#         LastAllocatedSection = active_train.getLastAllocatedSection()
#         LastAllocatedSectionName = active_train.getLastAllocatedSectionName()
#         NextSectionToAllocateName = active_train.getNextSectionToAllocateName()
#         # print "block_list", block_list
#         # print "LastAllocatedSectionSeqNumber",LastAllocatedSectionSeqNumber
#         # print "section_list",section_list
#         # print "start block", start_block
#         # print "end_block", end_block
#         # print "getStartBlockSectionSequenceNumber", seq_no
#         # print "section_list", section_list
#         # print "NextSectionToAllocate", NextSectionToAllocate
#         # print "LastAllocatedSection", LastAllocatedSection
#         # print "LastAllocatedSectionName", LastAllocatedSectionName
#         # print "getNextSectionToAllocateName", NextSectionToAllocateName
#         return [block_list, start_block, end_block]
#
#     def check_train_in_block(self, block_name, train_name):
#         mem_val = self.get_blockcontents(block_name)
#         #print "mem_val", mem_val, "train_name", train_name
#         if train_name == mem_val:
#             #print "return true"
#             return True
#         else:
#             return False
#
#     def set_train_in_block(self, block_name, train_name):
#         self.set_blockcontents(block_name,train_name)
#
#     def get_block_position_of_train(self, train_name):
#             allocated_trains = self.get_allocated_trains()
#
#
#     def get_allocated_trains(self):
#         return trains_allocated
#
#     def get_non_allocated_trains(self):
#         all_trains = self.get_all_roster_entries_with_speed_profile()
#         non_allocated_trains = copy.copy(all_trains)
#         for train in trains_allocated:
#             if train in non_allocated_trains:
#                 non_allocated_trains.remove(train)
#         return non_allocated_trains
#
#     def get_all_roster_entries_with_speed_profile(self):
#         roster_entries_with_speed_profile = []
#         r = jmri.jmrit.roster.Roster.getDefault()
#         for roster_entry in jmri.jmrit.roster.Roster.getAllEntries(r):
#             if self.logLevel > 0: print "roster_entry.getSpeedProfile()",roster_entry,roster_entry.getSpeedProfile()
#             if roster_entry.getSpeedProfile() != None:
#                 roster_entries_with_speed_profile.append(roster_entry.getId())
#                 if self.logLevel > 0: print "roster_entry.getId()",roster_entry.getId()
#         return roster_entries_with_speed_profile
#
#     def get_blockcontents(self, block_name):
#         block = blocks.getBlock(block_name)
#         value =  block.getValue()
#         return value
#
#
#     def set_blockcontents(self, block_name, value):
#         block = blocks.getBlock(block_name)
#         value =  block.setValue(value)
#
#     def get_station_and_occupancy_and_block_value_of_train(self, train_to_move):
#         ## Check the pressed button
#         for station_block_name in g.station_block_list:
#             if self.logLevel > 0: print "station_block_name", station_block_name
#
#             #get a True if the block block_value has the train name in it
#             block_value_state = self.check_train_in_block(station_block_name, train_to_move)
#             block_occupancy_state = self.check_sensor_state_given_block_name(station_block_name)
#             if self.logLevel > 0: print "block_value_state1= ",block_value_state
#             # # do not attempt to move to where you are
#             # button_pressed_in_occupied_station = (button_station_name == station_block_name)
#
#             #check if the block is occupied and has the required train in it
#             if block_occupancy_state:
#                 # and button_pressed_in_occupied_station == False:
#                 return [station_block_name, block_value_state, block_occupancy_state]
#         return None
#
#     def get_position_of_train(self, train_to_move):
#         ## Check the pressed button
#         for station_block_name in g.station_block_list:
#             if self.logLevel > 0: print "station_block_name", station_block_name
#
#             #get a True if the block block_value has the train name in it
#             block_value_state = self.check_train_in_block(station_block_name, train_to_move)
#             if self.logLevel > 0: print "block_value_state= ",block_value_state
#
#             #get a True if the block is occupied
#             block_occupied_state = self.check_sensor_state_given_block_name(station_block_name)
#             if self.logLevel > 0: print "block_occupied_state= ",block_occupied_state
#             if self.logLevel > 0: print ("station block name {} : {}". format(station_block_name, str(block_occupied_state)))
#
#             # # do not attempt to move to where you are
#             # button_pressed_in_occupied_station = (button_station_name == station_block_name)
#
#             #check if the block is occupied and has the required train in it
#             if block_value_state == True and block_occupied_state == True:
#                 # and button_pressed_in_occupied_station == False:
#                 return station_block_name
#         return None
#
#     def check_sensor_state_given_block_name(self, station_block_name):
#         #if self.logLevel > 0: print("station block name {}".format(station_block_name))
#         layoutBlock = layoutblocks.getLayoutBlock(station_block_name)
#         station_sensor = layoutBlock.getOccupancySensor()
#         if station_sensor is None:
#             OptionDialog().displayMessage(' Sensor in block {} not found'.format(station_block_name))
#             return
#         currentState = True if station_sensor.getKnownState() == ACTIVE else False
#         return currentState

class RunInglenookMaster():

    def __init__(self):
        global g
        global le
        global indentno

        indentno = 0

        #my_path_to_jars = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/jars/jgrapht.jar')
        #import sys
        #sys.path.append(my_path_to_jars) # add the jar to your path
        #CreateGraph = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/CreateGraph.py')
        #exec(open (CreateGraph).read())

        # le = LabelledEdge
        # g = StationGraph()

        # new_train_master = NewTrainMaster()      #this used to respond to the setup train button
        # instanceList.append(new_train_master)
        # if new_train_master.setup():
        #     new_train_master.setName('New Train Master')
        #     new_train_master.start()

        # Inglenook_run2 = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/inglenook/inglenook_run2.py')
        # exec(open (Inglenook_run2).read())

        StartInglenook = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/inglenook/startInglenookSystem.py')
        exec(open (StartInglenook).read())

        # Inglenook = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/inglenook/inglenook.py')
        # exec(open (Inglenook).read())
        print "starting InglenookMaster"
        run_inglenook = InglenookMaster()                  #need this starts the system
        if run_inglenook.setup():
            print "run_inglenook_setup() returns True"
            run_inglenook.setName('Start Inglenook')
            run_inglenook.start()
            print "started StartInglenookMaster"
        else:
            print "run_inglenook_setup() returns False"

        stop_master = StopMaster()                  #need this stops the system
        if stop_master.setup():
            stop_master.setName('Stop Master')
            stop_master.start()

        off_action_master = OffActionMaster()
        instanceList.append(off_action_master)
        if off_action_master.setup():
            off_action_master.setName('Off-Action Master')
            off_action_master.start()
        else:
            if self.logLevel > 0: print("Off-Action Master not started")

        #set default values of buttons
        sensors.getSensor("justShowSortingInglenookSensor").setKnownState(INACTIVE)
        sensors.getSensor("simulateErrorsInglenookSensor").setKnownState(INACTIVE)
        sensors.getSensor("simulateInglenookSensor").setKnownState(INACTIVE)
        sensors.getSensor("simulateErrorsInglenookSensor").setKnownState(INACTIVE)
        sensors.getSensor("runRealTrainInglenookSensor").setKnownState(INACTIVE)




if __name__ == '__builtin__':
    pass
    RunInglenookMaster()
    # NewTrainMaster checksfor the new train in siding. Needs to inform what station we are in
    #DispatchMaster checks all button sensors

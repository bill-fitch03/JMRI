import jmri

import threading
import move_train_init as i
import move_train_helper as h
import move_train_call as ccc
import move_train_recovery_helper as r2
# import move_train_countActive as ca
import move_train_count as c
import move_train_recoverActive as ra
import move_train_recoverInactive as ri
import config as co
from threading import Thread

# New method of splitting files
# https://stackoverflow.com/questions/35059904/splitting-python-class-into-multiple-files

# The below list of methods are in Move_Train but have been moved to seperate files for housekeeping purposed

# unfortunately modules requiring use of jmri AbstractAutomaton tools need to remain in the main routine (such as sensors)

def add_methods(*methods):
    def decorator(Class):
        for method in methods:
            setattr(Class, method.__name__, method)
        return Class
    return decorator

@add_methods(i.myprint,i.myprint1,i.myprint2,i.indent,i.dedent)
@add_methods(r2.storeSensorFrom, r2.storeSensorTo, r2.storeSensor, r2.storeFunction, r2.storeCount, r2.storeTimeout)
@add_methods(ccc.decide_what_to_do_first, ccc.place_trucks_near_disconnect)
@add_methods(ccc.moveTrucksOneByOne)
# @add_methods(ccc.count_at_spur)
@add_methods(ccc.moveToDisconnectPosition, ccc.move_to_spur_operations, ccc.move_to_siding_operations, ccc.strip_0)
@add_methods(c.countTrucksInactive, c.countTrucksActive)
@add_methods(h.setPointsAndDirection, h.setBranch, h.setMidBranch, h.setSensor)
@add_methods(h.couple1, h.uncouple1)
@add_methods(h.swapRouteSameDirectionTravelling,h.swapRouteOppDirectionTravelling,h.sensorName,h.stateName)
@add_methods(h.noTrucksOnBranches, h.noTrucksOnBranch, h.moveDistance)
#@add_methods(r.returnToBranch)
# @add_methods(ca.moveToBranch, ca.countTrucksActive, ca.waitChangeSensorActive)
#@add_methods(ca.moveToBranch, ca.countTrucksActive)
#@add_methods(ci.countTrucksInactive, ci.waitChangeSensorInactive)

@add_methods(ri.alt_action_countTrucksInactive)
@add_methods(ra.alt_action_countTrucksActive2, ra.returnToBranch, ra.countTrucksAgain)

class Move_train2(jmri.jmrit.automat.AbstractAutomaton):

    # responds to the simulateInglenookSensor, and allows the Inglenook Siding Routine to start

    logLevel = 1
    tender = False
    indentno = 0

    #set up variables to use timeout decorator
    sensor_name = "sensor_stored"
    sensor_from_name = "sensor_from_stored"
    sensor_to_name = "sensor_to_stored"
    timeout_name = "timeout_stored"

    # myWindows = jmri.util.FileUtil.getExternalFilename('program:jython/ShuntingPuzzles/inglenook/myWindows.py')

    point3 = None
    #instanceList = []   # List of file based instances

    display_message_flag = False

    def __init__(self):
        self.spur_branch = 4 # count from `1
        # self.mid_branch = 5
        self.spurPeg = 3    # count from 0
        # self.midPeg = 4
        self.pegs = []

        self.stop_thread_sensor = sensors.getSensor("stopThreadSensor")
        self.stop_thread_sensor.setKnownState(INACTIVE)
        self.stop_thread = False

    def init(self):
        global gbl_simulate_sensor_wait_time
        global indentno
        global decide_what_to_do_instruction1, decide_what_to_do_instruction1a
        global decide_what_to_do_instruction2, decide_what_to_do_instruction2a
        print "setup"
        self.logLevel = 0
        if self.logLevel > 0: print 'Create Stop Thread'
        gbl_simulate_sensor_wait_time = 1000
        indentno = 0
        print "indentno", indentno
        self.dialogs = OptionDialog()
        decide_what_to_do_instruction1 = ""
        decide_what_to_do_instruction1a = ""
        decide_what_to_do_instruction2 = ""
        decide_what_to_do_instruction2a = ""



    def setup(self):
        print "start"
        test_sensor = sensors.getSensor("soundInglenookSensor")
        self.simulate_inglenook_sensor = test_sensor
        if test_sensor is None:
            print "returning False"
            return False
        test_sensor.setKnownState(INACTIVE)
        self.od = OptionDialog()
        print "returning True"
        return True

    def choose_action(self):
        title = ""
        msg = "simulate Inglenook"
        opt1 = "with simulated signals"
        opt2 = "with real signals"
        opt3 = "other actions"
        reply = self.od.customQuestionMessage2str(msg, title, opt1, opt2)
        if self.od.CLOSED_OPTION == True:
            return "cancel"
        if reply == opt1:
            return opt1
        elif reply == opt2:
            return opt2
        else:
            pass

    def handle(self):
        print ("handle")
        try:
            indentno
            print "handle` Move`_tran2 indentno set up", indentno
        except NameError:
            print "indentno not set up"

        self.indent()
        print "move_train handle (sets up sensors)"
        self.myprint("in Move_train init")
        global throttle
        #speeds
        # print "waiting for sensor"
        # mysensor = sensors("simulateSensor")
        # self.waitChangeSensorActive(sensor)
        # self.waitChangeSensorInactive(mysensor)

        self.stop = 0
        self.slow = 0.1
        self.vslow = 0.05
        self.uncouple = 0.15
        self.medium = 0.5
        self.couple = 0.3
        self.fast = 0.7

        self.smallDistance = "smallDistance"

        #sensor States
        self.sensorOn = 1
        self.sensorOff = 0

        self.initialmove = True
        self.myprint("Inside init(self)xx")

        sensorManager = jmri.InstanceManager.getDefault(jmri.SensorManager)
        turnoutManager = jmri.InstanceManager.getDefault(jmri.TurnoutManager)
        print ("setting up sensors")
        try:
            self.myprint ("trying to set up sensors")

            self.sensor1 = self.get_decoupling_sensor("#IS_spur_sensor#")
            self.myprint1 ("trying to set up sensors1", self.sensor1)

            self.sensor2 = self.get_decoupling_sensor("#IS_siding1_sensor#")
            self.myprint1 ("trying to set up sensors2", self.sensor2)

            self.sensor3 = self.get_decoupling_sensor("#IS_siding2_sensor#")
            self.myprint1 ("trying to set up sensors2", self.sensor3)

            self.sensor4 = self.get_decoupling_sensor("#IS_siding3_sensor#")"
            self.myprint1 ("trying to set up sensorsspur", self.sensor4)
            self.myprint1 ("sensore set up")
        except:
            self.myprint1 ("sensors not set!")
        self.myprint2("setting up points")
        self.myprint ("trying to set up points")
        self.point1 = turnoutManager.getTurnout("SP-T04")
        self.point2 = turnoutManager.getTurnout("SP-T03")
        self.point3 = turnoutManager.getTurnout("SP-T02")
        self.myprint ("self.point3" + str( self.point3.getUserName()))
        self.myprint1 ("points set up")

        try:
            self.myprint ("trying to set up points")
            self.point1 = turnoutManager.getTurnout("SP-T04")
            self.point2 = turnoutManager.getTurnout("SP-T03")
            self.point3 = turnoutManager.getTurnout("SP-T02")
            self.myprint ("self.point3" + str( self.point3.getUserName()))
            self.myprint1 ("points set up")
            self.myprint2("points set up")
        except:
            self.myprint1 ("points not set!")
            print ("points not set!")

        # get loco address. For long address change "False" to "True"
        # self.myprint("setting up throttle")
        # throttle = self.getThrottle(3, False)  # short address 3
        # self.myprint (throttle)
        # self.set_delay_if_not_simulation(1000)
        # self.setSpeed(self.stop)
        # self.set_delay_if_not_simulation(1000)
        # self.myprint1("throttle set up")
        # "setting up throttle")
        try:
            # print("setting up throttle2")
            # self.myprint1("setting up throttle")
            dccAddress = 3
            isLong = False
            throttle = self.getThrottle(dccAddress, isLong)  # short address 3
            # print("setting up throttle3")
            # self.myprint (throttle)
            self.set_delay_if_not_simulation(1000)
            self.waitMsec(1000)
            # print("setting up throttle4")
            self.setSpeed(self.stop)
            # print("setting up throttle5")
            self.set_delay_if_not_simulation(1000)
            self.waitMsec(1000)
            self.myprint1("throttle set up")
            # print("throttle set up")
        except:
            self.myprint1("throttle not set up")
            self.myprint2("throttle not set up")

        # sensor = sensors.getSensor("soundInglenookSensor")
        # self.waitSensorActive(sensor)

        self.myprint ("finished init")
        self.myprint(self.__dict__)
        self.myprint(dir())
        # self.dedent()
        # print("end")
        return False

    def get_decoupling_sensor(self, sensor_comment):
        for sensor in sensors.getNamedBeanSet():
            comment = sensor.getComment()
            if comment != None:
                if sensor_comment in comment:
                    return sensor
        return None


    def decide_what_to_do(self, screen, positions, position):
        global display_message_flag
        global decide_what_to_do_instruction
        self.indent()
        decide_what_to_do_instruction = "fred"
        self.positions = positions
        self.screen = screen         # for display_update
        self.position = position     # for display_update
        instructions = position

        # self.myprint(instructions)
        [instruction, noTrucksToMove, fromBranch, destBranch, pegs] = position


        if instruction == "move_trucks_one_by_one":

            display_message_flag = True
            self.display_message_flag = True

            if self.pegs == []:
                self.pegs = copy.deepcopy(pegs)  #initialise self.pegs
            else:
                pass # use self.pegs from previous step
            self.myprint1("self.pegs",self.pegs, "pegs", pegs)
            ListOfTrucksInBranches = [len(x) for x in self.pegs]

            # announce action
            self.notrucks = noTrucksToMove
            self.fromBranch = fromBranch
            self.destBranch = destBranch
            decide_what_to_do_instruction = "moveTrucksOneByOne" + str(noTrucksToMove) + " from " + str(fromBranch) + " to " + str(destBranch)
            print ("decide_what_to_do_instruction", decide_what_to_do_instruction)
            # self.update_displays(self.pegs)
            self.moveTrucksOneByOne(noTrucksToMove, fromBranch, destBranch, ListOfTrucksInBranches)

        elif instruction == "move_trucks":

            display_message_flag = True
            self.display_message_flag = True

            # announce action
            self.notrucks = noTrucksToMove
            self.fromBranch = fromBranch
            self.destBranch = destBranch
            if self.pegs == []:
                self.pegs = copy.deepcopy(pegs)  #initialise self.pegs
            else:
                pass # use self.pegs from previous step
            stage = "d what to do"
            decide_what_to_do_instruction = "moveTrucks" + str(noTrucksToMove) + " from " + str(fromBranch) + " to " + str(destBranch)
            # print ("decide_what_to_do_instruction", decide_what_to_do_instruction)
            # self.update_displays(self.pegs)
            self.moveTrucks(noTrucksToMove, fromBranch, destBranch, self.pegs)
        else:
            self.myprint("!!!!!!!!!unrecognised instruction " & instruction)
            pass
        self.dedent()
        return self.pegs

    def set_up_display_text(self, stage, deposit, originating_branch, destination_branch):
        global decide_what_to_do_instruction1
        global decide_what_to_do_instruction1a
        global decide_what_to_do_instruction2
        global decide_what_to_do_instruction2a
        msg = "curr: move " + str(stage) + str(deposit) + " trucks from " + str(originating_branch) + \
              " to " + str(destination_branch)
        msg2 = str(self.pegs)
        msg2 = msg2.replace("deque","").replace("[","").replace("]","")
        decide_what_to_do_instruction1 = decide_what_to_do_instruction2.replace("curr","prev")
        decide_what_to_do_instruction1a = decide_what_to_do_instruction2a
        decide_what_to_do_instruction2 = msg
        decide_what_to_do_instruction2a = msg2

    @print_name()
    def moveTrucks(self, numberTrucksToMove, fromBranch, destBranch, pegs):

        self.indent()
        numberTrucksToMove_old = self.numberTrucksToMove_previous
        stage = "one_move"
        if self.previousBranch != fromBranch:
            numberTrucksToMove1 = 0
            from_branch = self.previousBranch
            dest_branch = fromBranch
            self.set_up_display_text("stage1", numberTrucksToMove1, fromBranch, destBranch)
            self.moveTrucks2("stage1", from_branch, dest_branch, numberTrucksToMove1, numberTrucksToMove_old, self.pegs)
            numberTrucksToMove_old = numberTrucksToMove1
            stage = "stage2"

        # numberTrucksToMove = numberTrucksToMove_fromBranchToDestBranch
        self.set_up_display_text(stage, numberTrucksToMove, fromBranch, destBranch)
        self.moveTrucks2(stage, fromBranch, destBranch, numberTrucksToMove, numberTrucksToMove_old, self.pegs)

        self.previousBranch = destBranch
        self.numberTrucksToMove_previous = numberTrucksToMove

        self.dedent()

    @print_name()
    def moveTrucks2(self, stage, originating_branch, destination_branch, noTrucksToMove, noTrucksToMove_old, pegs):

        # move deposit trucks from originating_branch to destination_branch
        # the number of trucks 'deposited' in the last MoveTrucks2 is stored im deposit_old
        self.indent()

        # go to spur if origin is not the spur
        if originating_branch != self.spur_branch:     # start from a siding, move to spur
            sidingBranch = originating_branch
            self.move_to_spur_operations(sidingBranch, noTrucksToMove, noTrucksToMove_old)

        # go to siding if destination is a siding
        if destination_branch != self.spur_branch:     # start from spur, move to siding
            sidingBranch = destination_branch
            self.move_to_siding_operations(sidingBranch, noTrucksToMove)
        self.myprint2(self.pegs)
        self.dedent()
        pass

    def kill_everything(self):
        #this killes everything
        win = Mywindow()
        win.setVisible(1)
        #this prints out what it is killing
        win2 = Mywindow2()
        win2.setVisible(1)


    # def startFromBranch4(self, destBranch, pegs):
    #     self.indent()
    #     self.myprint("In startFromBranch4")
    #     self.noTrucksOnTrain =  self.noTrucksOnStack(pegs, 4)
    #     noTrucksToMove = 0
    #     fromBranch = 4
    #     destBranch = destBranch
    #     self.moveEngineToBranch(noTrucksOnTrain, noTrucksToMove, fromBranch, destBranch)
    #     connectTrucks(fromBranch)
    #     self.dedent()

        # @alternativeaction("alt_action_countTrucksActive2","sensor_stored")
        # @variableTimeout("timeout_stored")


        #@alternativeaction("alt_action_countTrucksInactive",sensor_name)
        #@timeout(3)

        #not used
    # def waitChangeSensor(self, sensor, required_sensor_state):
    #     global gbl_simulate_sensor_wait_time
    #     self.indent()
    #     self.myprint("in waitChangeSensor")
    #     #global config.throttle
    #     self.changeDirection()
    #     self.setSpeed(self.slow)
    #     while 1:
    #         self.myprint("about to waitChangeSensorInactive")
    #         simulate = sensors.getSensor("simulateInglenookSensor")
    #         if simulate.getKnownState() == ACTIVE:
    #             self.waitMsec(gbl_simulate_sensor_wait_time)
    #         else:
    #             self.waitChange([sensor])
    #         got_state = sensor.getKnownState()
    #         self.myprint( ">> moveBackToSensor " + self.stateName(got_state) );
    #         if required_sensor_state == self.sensorOn:
    #             self.myprint( ">> moveBackToSensor" + " sensor state on " + self.stateName(got_state) );
    #             if got_state == ACTIVE:
    #                 self.setSpeed(0)
    #                 #self.set_delay_if_not_simulation(1000)
    #                 self.dedent()
    #                 break
    #             else:
    #                 self.myprint( ">> moveBackToSensor" + " req_sensor_state on " + self.stateName(got_state) );
    #                 pass
    #         elif required_sensor_state == self.sensorOff:
    #             self.myprint( ">> moveBackToSensor" + " sensor state off" );
    #             if got_state == INACTIVE:
    #                 self.setSpeed(0)
    #                 #self.set_delay_if_not_simulation(1000)
    #                 self.dedent()
    #                 break
    #             else:
    #                 self.myprint( ">> moveBackToSensor" + " req_sensor_state off " + self.stateName(got_state) );
    #                 pass
    #         else:
    #             pass
    #     self.dedent()

        #not used
    def alt_action_countTrucksActive1(self,sensor):
        self.indent()
        self.myprint ("in alt_action_countTrucksActive1 ")
        #speak("in alt_action_countTrucksActive1")
        self.myprint ("end alt_action_countTrucksActive1 ")
        self.dedent()

        #not used
    def countTrucks(self, noTrucksToCount, sensor, state_to_use):
        self.indent() #state-to_use can be "ACTIVE" or "INACTIVE"
        self.myprint ("in countTrucks ")
        pass

        #can count 0 to n trucks on active
        #can count 1 to n trucks on inactive

        #check for invalid count
        if state_to_use == "INACTIVE" and noTrucksToCount == 0:
            self.myprint ("!!!!!!!!!!!!!state_to_use == 'INACTIVE' and noTrucksToCount == 0")

        # delay so that we are on a truck then count the number of off events
        self.myprint("counting " + str(noTrucksToCount) + " trucks on " + state_to_use)
        off_count = 0
        on_count = -1
        self.myprint("off_count is " + str(off_count))
        self.myprint("on_count is " + str(on_count))
        while 1:
            self.myprint("waiting change on sensor " + self.sensorName(sensor))
            self.waitChange([sensor])
            sensorstate = sensor.getKnownState()
            self.myprint(">>countTrucks: sensor state is " + self.stateName(sensorstate))
            if sensorstate == INACTIVE and state_to_use == self.stateName(sensorstate):
                self.myprint("off_count is @x " + str(off_count))
                off_count += 1
                self.myprint("off_count is @y " + str(off_count))
                if off_count == noTrucksToCount:
                    self.myprint("Bingo count is " + str(off_count))
                    self.setSpeed(self.stop)
                    self.dedent()
                    break
                else:
                    self.myprint ("off_count is @z " + str(off_count))
                    self.myprint(">>countTrucks: ignoring sensor @1, off_count is " + str(off_count) + " noTrucksToCount " + str(noTrucksToCount))
                    self.myprint(">>countTrucks: ignoring sensor @2, sensor state is " + self.stateName(sensorstate))
            elif sensorstate == ACTIVE and state_to_use == self.stateName(sensorstate):
                on_count+=1
                self.myprint(">>countTrucks: sensor on_count " + self.stateName(sensorstate) + " on_count = " + str(on_count))
                self.myprint("noTrucksToCount " + str(noTrucksToCount))
                if on_count == noTrucksToCount:
                    self.myprint("Bingo on_count is " + str(on_count))
                    self.setSpeed(self.stop)
                    self.dedent()
                    break
                else:
                    self.myprint(">>countTrucks: ignoring sensor @1a, on_count is " + str(on_count) + " noTrucksToCount " + str(noTrucksToCount))
                    self.myprint(">>countTrucks: ignoring sensor @2a, sensor state is " + self.stateName(sensorstate))
            else:
                self.myprint(">>countTrucks: ignoring sensor @1b, off_count is " + str(off_count) + " noTrucksToCount " + str(noTrucksToCount))
                self.myprint(">>countTrucks: ignoring sensor @2b, on_count is " + str(on_count))
                self.myprint(">>countTrucks: ignoring sensor @3b, sensor state is " + self.stateName(sensorstate))
        self.dedent()

        #**********************************************************************************
        # Routines that depend upon globals and cannot be moved to seperate file
        #**********************************************************************************
    def setSpeed(self, speed):
        #global throttle
        self.indent()
        self.myprint("in set speed: setting to " + str(speed))
        if sensors.getSensor("runRealTrainInglenookSensor").getKnownState() == ACTIVE:
            if throttle.getSpeedSetting() != speed:
                throttle.setSpeedSetting(speed)
                self.myprint("end set speed to " + str(speed))
            else:
                throttle.setSpeedSetting(speed)
                self.myprint("speed already at " + str(speed))

        self.dedent()

    def setSpeedSetDelay(self, speed, delay):
        #global throttle
        self.indent()
        self.myprint("in set speed: setting to " + str(speed))
        if sensors.getSensor("runRealTrainInglenookSensor").getKnownState() == ACTIVE:
            if throttle.getSpeedSetting() != speed:
                throttle.setSpeedSetting(speed)
                self.myprint("end set speed to " + str(speed) + "with delay " + str(delay))
                self.set_delay_if_not_simulation(delay)
            else:
                self.myprint("speed already at " + str(speed))

        self.dedent()

    def setPoints(self, fromBranch, toBranch):
        self.indent()
        self.myprint (">>in setPoints ")

        self.myprint("setting points fromBranch = " + str(fromBranch) + " toBranch = " + str(toBranch))
        self.myprint("get pointx CLOSED")
        self.myprint("self.point3", self.point3)
        self.myprint("self.point3.getState() before" + str(self.point3.getState()))
        self.point3.setState(CLOSED)
        self.myprint("self.point3.getState() after" + str(self.point3.getState()))
        if fromBranch == 4:
            if toBranch == 1:
                self.myprint("get point1 CLOSED")
                self.myprint("self.point1.getState() before" + str(self.point1.getState()))
                # if self.point1.getState() != CLOSED:
                # self.myprint("set point1 CLOSED")

                self.point1.setState(CLOSED)
                self.myprint("self.point1.getState() after" + str(self.point1.getState()))
            else:
                self.myprint("get point1 THROWN")
                self.myprint("self.point1.getState() before" + str(self.point1.getState()))
                # if self.point1.getState() != THROWN:
                # self.myprint("set point1 THROWN")
                self.point1.setState(THROWN)
                self.myprint("self.point1.getState() after" + str(self.point1.getState()))

            self.set_delay_if_not_simulation(3000)

            if toBranch == 3:
                self.myprint("get point2 CLOSED")
                # if self.point2.getState() != CLOSED:
                # self.myprint("set point2 CLOSED")
                self.point2.setState(CLOSED)
                self.set_delay_if_not_simulation(3000)
            elif toBranch == 2:
                self.myprint("get point2 THROWN")
                self.myprint("self.point2.getState() before" + str(self.point2.getState()))
                # if self.point2.getState() != THROWN:
                # self.myprint("set point2 THROWN")
                self.point2.setState(THROWN)
                self.myprint("self.point2.getState() after" + str(self.point2.getState()))
                self.set_delay_if_not_simulation(3000)
            else:
                self.myprint("do not set point2")


        else:
            if fromBranch == 1:
                self.myprint("get point1 CLOSED")
                self.myprint("self.point1.getState() before" + str(self.point1.getState()))
                # if self.point1.getState() != CLOSED:
                # self.myprint("set point1 CLOSED")
                self.point1.setState(CLOSED)
                self.myprint("self.point1.getState() after" + str(self.point1.getState()))
            else:
                self.myprint("get point1 THROWN")
                self.myprint("self.point1.getState() before" + str(self.point1.getState()))
                # if self.point1.getState() != THROWN:
                # self.myprint("set point1 THROWN")
                self.point1.setState(THROWN)
                self.myprint("self.point1.getState() after" + str(self.point1.getState()))

            self.set_delay_if_not_simulation(3000)

            if fromBranch == 3:
                self.myprint("get point2 CLOSED")
                self.myprint("self.point2.getState() before" + str(self.point2.getState()))
                # if self.point2.getState() != CLOSED:
                # self.myprint("set point2 CLOSED")
                self.myprint("self.point2.getState() before" + str(self.point2.getState()))
                self.point2.setState(CLOSED)
                self.myprint("self.point2.getState() after" + str(self.point2.getState()))
                self.set_delay_if_not_simulation(3000)
            elif fromBranch == 2:
                self.myprint("get point2 THROWN")
                self.myprint("self.point2.getState() before" + str(self.point2.getState()))
                # if self.point2.getState() != THROWN:
                # self.myprint("set point2 THROWN")
                self.point2.setState(THROWN)
                self.myprint("self.point2.getState() after" + str(self.point2.getState()))
                self.set_delay_if_not_simulation(3000)
            else:
                self.myprint("do not set point2")

        # self.myprint("end setting points: waiting 10 secs")
        # self.set_delay_if_not_simulation(10000)
        self.myprint("end setting points")
        self.dedent()
    @print_name()
    def setDirection(self, fromBranch, toBranch):
        global throttle
        self.indent()
        self.myprint1 ("in setDirection ")
        if toBranch != self.spur_branch:
            # set loco to forward
            self.myprint("Set Loco Forward")
            if sensors.getSensor("runRealTrainInglenookSensor").getKnownState() == ACTIVE:
                throttle.setIsForward(True)
            direction = "to_siding"
        else:
            # set loco to reverse
            self.myprint("Set Loco backward")
            if sensors.getSensor("runRealTrainInglenookSensor").getKnownState() == ACTIVE:
                throttle.setIsForward(False)
            direction = "to_spur"
        self.myprint1 ("end setDirection ", direction)
        self.dedent()
        return direction
    @print_name()
    def changeDirection(self):
        #global throttle
        self.indent()
        self.myprint ("in changeDirection ")
        #global throttle
        if throttle.getIsForward():
            if sensors.getSensor("runRealTrainInglenookSensor").getKnownState() == ACTIVE:
                throttle.setIsForward(False)
            self.myprint("Changed direction, reverse")
            direction = "forwards"
        else:
            if sensors.getSensor("runRealTrainInglenookSensor").getKnownState() == ACTIVE:
                throttle.setIsForward(True)
            self.myprint("Changed direction, forward")
            direction = "reverse"
        self.dedent()
        return direction

    @print_name()
    def waitChangeSensorActive(self, sensor):
        # self.indent()
        self.myprint("in waitChangeSensorActive" + " sensor " + self.sensorName(sensor))
        self.sensors_to_watch = [self.stop_thread_sensor, sensor]

        self.waitSensorActive(self.sensors_to_watch)
        sensor_changed = [sensor for sensor in self.button_sensors_to_watch if sensor.getKnownState() == ACTIVE][0]
        if sensor_changed == self.stop_thread_sensor:
            self.stop_thread = True
            # break
    @print_name()
    def waitChangeSensorInactive(self, sensor):
        # self.indent()
        self.myprint("in waitChangeSensorInactive" + " sensor " + self.sensorName(sensor))
        self.sensors_to_watch = [self.stop_thread_sensor, sensor]
        #waitChangeSensor(sensor,self.sensorOff)
        # while 1:
            #self.waitChange(self.sensors_to_watch)
        self.waitSensorInactive(self.sensors_to_watch)
        sensor_changed = [sensor for sensor in self.button_sensors_to_watch if sensor.getKnownState() == INACTIVE][0]
        if sensor_changed == self.stop_thread_sensor:
            self.stop_thread = True
        # break
            # got_state = sensor.getKnownState()
            # if got_state == INACTIVE:
            #     self.myprint("got_state inactive")
            #     # self.dedent()
            #     break

    def wait_sensor(self, sensorName, sensorState):
        sensor = sensors.getSensor(sensorName)
        if sensor is None:
            self.displayMessage('Sensor {} not found'.format(sensorName))
            return
        if sensorState == 'active':
            #if self.logLevel > 1: print ("wait_sensor active: sensorName {} sensorState {}",format(sensorName, sensorState))
            self.waitSensorActive(sensor)
        elif sensorState == 'inactive':
            self.waitSensorInactive(sensor)
        else:
            self.displayMessage('Sensor state, {}, is not valid'.format(sensorState))

    def mysound(self):
        self.myprint("bell")
        if sensors.getSensor("bellInglenookSensor").getKnownState() == ACTIVE:
            snd = jmri.jmrit.Sound("resources/sounds/Bell.wav")
            snd.play()
        self.myprint("bell end")

    # @print_name()
    def update_displays(self, pegs):
        #print "self.positions",  self.positions
        # position = next(self.positions)
        # print("!!!!!!!!!!!!!!!!! position", self.position)
        InglenookMaster().display_trucks_on_insert(self.pegs, self.screen)
        InglenookMaster().display_trucks_on_panel(self.pegs)

    def set_delay_if_not_simulation(self, msec):
        if sensors.getSensor("runRealTrainInglenookSensor").getKnownState() == ACTIVE:
            # seld.waitMsec(msec)
            pass

    def getBranchNo(self, truckNo):
        for branchno in range(1,5):
            if self.truckInSiding(truckNo, branchno):
                return branchno
        return 99

    def get_branch_from_sensor(self, sensor):
        sensor_name = sensor.getUserName().split("_")[-1]
        if sensor_name == "1" or  sensor_name == "2" or sensor_name == "3":
            return int(sensor_name)
        elif sensor_name == "spur":
            return 4
        elif sensor_name == "mid":
            return 99
        else:
            return 100
    def truckInSiding(self, truckNo, branchNo):
        return self.pegs[branchNo - 1].count(truckNo)>0

    # @print_name()
    # def countTrucksActive_wait1(self, sensor, direction, count):
    #     # going towards sidings, the number of trucks to pick up is 0
    #     global gbl_simulate_sensor_wait_time
    #     self.indent()
    #     simulate = sensors.getSensor("simulateInglenookSensor")
    #     if simulate.getKnownState() == ACTIVE:
    #         midPeg = self.setMidBranch(sensor)-1
    #         self.dialogs.displayMessage("countTrucksActive_wait1: engine: "+ str(count))
    #         #ensure the mimic panel updates
    #         self.myprint1("pegs", self.pegs)
    #         self.myprint1( "sensor.getUserName()", sensor.getUserName())
    #         if self.setBranch(sensor)==self.spur_branch:
    #             if direction == "forwards":
    #                 # we pop from spur  and push to mid to the left
    #                 self.myprint1("1 forwards we pop from spur and push to mid")
    #                 self.dialogs.displayMessage("1 we pop from spur and push to mid")
    #                 #self.myprint1("we pop from spur to the laft and push to deque 4")
    #                 self.pegs[midPeg].appendleft(self.pegs[self.spurPeg].pop())
    #             else:
    #                 # we pop from mid and push to spur
    #                 self.myprint1("2 we pop from mid and push to spur")
    #                 self.dialogs.displayMessage("2 we pop from mid and push to spur")
    #                 self.myprint1("we pop from smid to the laft and push to spur")
    #                 self.pegs[self.spurPeg].append(self.pegs[midPeg].popleft())
    #
    #         else:    #siding sensor
    #             sidingPeg = self.setBranch(sensor)-1       # the pegs start from 0
    #             midPeg = self.setMidBranch(sensor)-1
    #             # self.myprint1("# we pop from mid_branch and push to siding")
    #             if direction == "forwards":
    #                 self.myprint1("3 we pop from mid and push to siding (maybe we should not do this)")
    #                 self.dialogs.displayMessage("3 we pop from mid and push to siding (maybe we should not do this)")
    #                 # self.pegs[sidingPeg].append(self.pegs[self.midPeg].pop())    #comment out for now
    #                 # we just move the first truck to the coupling position
    #             else:
    #                 # we pop from mid and push to siding
    #                 self.myprint1("4 we pop from siding and push to mid")
    #                 self.dialogs.displayMessage("4 we pop from siding and push to mid")
    #                 self.myprint1("we pop from mid to the laft and push to spur")
    #                 self.pegs[midPeg].append(self.pegs[sidingPeg].pop())
    #
    #         self.update_displays(self.pegs)
    #         self.waitMsec(gbl_simulate_sensor_wait_time)    # make sure can see the update
    #     else:
    #         if self.setBranch(sensor)!=self.spur_branch:   # We don't count at the spur branch (though we could)
    #             self.myprint("actually waiting for sensor")
    #             self.waitChangeSensorActive(sensor)
    #     self.myprint("waited1")
    #     self.dedent()
    #
    #     # @alternativeaction("alt_action_countTrucksActive2","sensor_stored")
    #     # @variableTimeout("timeout_stored")
    # @print_name()
    # def countTrucksActive_wait2(self, sensor, direction, count):
    #     # going towards sidings
    #     global gbl_simulate_sensor_wait_time
    #     self.indent()
    #     simulate = sensors.getSensor("simulateInglenookSensor")
    #     if simulate.getKnownState() == ACTIVE:
    #         self.dialogs.displayMessage("countTrucksActive_wait2: truck count active: "+ str(count))
    #         #ensure the mimic panel updates
    #         self.myprint1("pegs", self.pegs)
    #         spur = 3
    #         mid = 4
    #         self.myprint1( "sensor.getUserName()", sensor.getUserName())
    #         if self.setBranch(sensor)==self.spur_branch:
    #             # we pop from stack 3 to the laft and push to deque 4
    #             self.myprint1("# we pop from mid to the laft and push to spur")
    #             self.dialogs.displayMessage("# we pop from mid to the laft and push to spur")
    #             self.pegs[spur].append(self.pegs[mid].popleft())
    #         else:
    #             self.dialogs.displayMessage("counting truck: active towards siding: sensor " + str(sensor.getUserName()))
    #             # we pop from deque 1 2 or 3 and push to mid deque
    #             self.myprint1("# we pop from deque 1 2 or 3 and push to spur")
    #             self.dialogs.displayMessage("# we pop from siding and push to mid")
    #             branch = self.setBranch(sensor)-1       # the pegs start from 0
    #             self.myprint1("sensor", sensor.getUserName(), "branch", branch)
    #             self.pegs[mid].append(self.pegs[branch].pop())
    #             self.myprint1("pegs after", self.pegs)
    #         self.update_displays(self.pegs)
    #         self.waitMsec(gbl_simulate_sensor_wait_time)    # make sure can see the update
    #     else:
    #         self.waitChangeSensorActive(sensor)
    #     self.myprint("waited2")
    #     self.dedent()

    @print_name()
    def simulate1(self):
        if (sensors.getSensor("simulateInglenookSensor").getKnownState() == ACTIVE or \
            sensors.getSensor("simulateErrorsInglenookSensor").getKnownState() == ACTIVE):
            return True
        else:
            return False

    @print_name()
    def really_doit_countTrucksInactive(self, sensor):
        do_it = (sensors.getSensor("runRealTrainInglenookSensor").getKnownState() == ACTIVE)
        if do_it:
            self.waitChangeSensorInactive(sensor)
            self.waitMsec(1000)


    @print_name()
    def really_doit_countTrucksActive(self, sensor):
        do_it = (sensors.getSensor("runRealTrainInglenookSensor").getKnownState() == ACTIVE)
        if do_it:
            self.waitChangeSensorActive(sensor)
            self.waitMsec(1000)

    @print_name()
    def simulate_countTrucksInactive(self, sidingBranch, sensor, direction, count, pegs):  #pegs just passed so they get printed out
        self.indent()
        simulate = self.simulate1()
        if simulate:
            #ensure the mimic panel updates
            self.myprint("pegs", self.pegs)
            spur = 3
            self.myprint1( "sensor.getUserName()", sensor.getUserName())
            my_branch = self.get_branch_from_sensor(sensor)
            self.dialogs.displayMessage("self.get_branch_from_sensor(sensor) " + str(my_branch) + " self.spur_branch " + str(self.spur_branch))
            if self.get_branch_from_sensor(sensor) == self.spur_branch:
                if direction == "to_spur":
                    # we pop from spur and push to  mid
                    midPeg = self.setMidBranch(sidingBranch) - 1
                    self.dialogs.displayMessage("pop from spur and push to  mid ")
                    self.myprint2("we pop from mid and push to spur")
                    self.myprint1("self.pegs before",self.pegs)
                    if pegs[self.spurPeg] == 0:
                        #error
                        self.myprint2("error: self.pegs before",self.pegs)
                        exit()
                    else:
                        self.pegs[spur].append(self.pegs[midPeg].popleft())
                else:
                    # we pop from mid from the left and push to  spur
                    # move_engine = True
                    midPeg = self.setMidBranch(sidingBranch) - 1
                    self.dialogs.displayMessage("pop from mid from the left and push to  spur ")
                    self.myprint2("we pop from spur and push to mid")
                    self.myprint1("self.pegs before",self.pegs)
                    self.pegs[midPeg].appendleft(self.pegs[spur].pop())
                self.myprint2("self.pegs after",self.pegs)
            else:
                if direction == "to_spur":
                    #we pop from branch and push to mid
                    # move_engine = False
                    midPeg = self.setMidBranch(sidingBranch) - 1
                    # print "midPeg" , midPeg
                    branchPeg = self.setBranch(sensor)-1       # the pegs start from 0
                    self.myprint1("pegs before", self.pegs)
                    self.dialogs.displayMessage("we pop from branch and push to mid")
                    self.myprint2("we pop from branch and push to mid")
                    self.pegs[midPeg].append(self.pegs[branchPeg].pop())
                    self.myprint1("pegs after", self.pegs)
                else:
                    # we pop from mid and push to stack 1 2 or 3
                    # move_engine = False
                    branchPeg = self.setBranch(sensor)-1       # the pegs start from 0
                    midPeg = self.setMidBranch(sidingBranch) - 1
                    self.dialogs.displayMessage("we pop from mid deque and push to branch")
                    self.myprint2("# we pop from mid and push to branch")
                    self.myprint1("self.pegs",self.pegs)
                    self.pegs[branchPeg].append(self.pegs[midPeg].pop())
                    self.myprint1("pegs after", self.pegs)
            self.update_displays(self.pegs)
            # self.waitMsec(gbl_simulate_sensor_wait_time)    # make sure can see the update
            if self.stop_thread_sensor.getKnownState() == ACTIVE:
                self.stop_thread == True
        self.dedent()

    @print_name()
    def simulate_countTrucksActive(self, sidingBranch, sensor, direction, count, pegs):  #pegs just passed so they get printed out
        self.indent()
        self.myprint2("simulate_countTrucksActive a")
        simulate = self.simulate1()
        self.myprint2("simulate_countTrucksActive a")
        if simulate:
            self.myprint2("simulate_countTrucksActive a")
            #ensure the mimic panel updates
            self.myprint("pegs", self.pegs)
            spur = 3
            self.myprint2( "sensor.getUserName()", sensor.getUserName())
            my_branch = self.get_branch_from_sensor(sensor)
            self.dialogs.displayMessage("self.get_branch_from_sensor(sensor) " + str(my_branch) + " self.spur_branch " + str(self.spur_branch))
            if self.get_branch_from_sensor(sensor) == self.spur_branch:
                if direction == "to_spur":
                    # we pop from spur and push to  mid
                    midPeg = self.setMidBranch(sidingBranch) - 1
                    self.dialogs.displayMessage("pop from spur and push to  mid ")
                    self.myprint2("we pop from mid and push to spur")
                    self.myprint1("self.pegs before",self.pegs)
                    if pegs[self.spurPeg] == 0:
                        #error
                        self.myprint2("error: self.pegs before",self.pegs)
                        exit()
                    else:
                        self.pegs[spur].append(self.pegs[midPeg].popleft())
                else:
                    # we pop from mid from the left and push to  spur
                    # move_engine = True
                    midPeg = self.setMidBranch(sidingBranch) - 1
                    self.dialogs.displayMessage("pop from mid from the left and push to  spur ")
                    self.myprint2("we pop from spur and push to mid")
                    self.myprint1("self.pegs before",self.pegs)
                    self.pegs[midPeg].appendleft(self.pegs[spur].pop())
                self.myprint2("self.pegs after",self.pegs)
            else:
                if direction == "to_spur":
                    #we pop from branch and push to mid
                    # move_engine = False
                    midPeg = self.setMidBranch(sidingBranch) - 1
                    # print "midPeg" , midPeg
                    branchPeg = self.setBranch(sensor)-1       # the pegs start from 0
                    self.myprint1("pegs before", self.pegs)
                    self.dialogs.displayMessage("we pop from branch and push to mid")
                    self.myprint2("we pop from branch and push to mid")
                    self.pegs[midPeg].append(self.pegs[branchPeg].pop())
                    self.myprint1("pegs after", self.pegs)
                else:
                    # we pop from mid and push to stack 1 2 or 3
                    # move_engine = False
                    branchPeg = self.setBranch(sensor)-1       # the pegs start from 0
                    midPeg = self.setMidBranch(sidingBranch) - 1
                    self.dialogs.displayMessage("we pop from mid deque and push to branch")
                    self.myprint2("# we pop from mid and push to branch")
                    self.myprint1("self.pegs",self.pegs)
                    self.pegs[branchPeg].append(self.pegs[midPeg].pop())
                    self.myprint1("pegs after", self.pegs)
            self.update_displays(self.pegs)
            # self.waitMsec(gbl_simulate_sensor_wait_time)    # make sure can see the update
        self.dedent()

        # # @print_name()
        # def is_there_a_truck(self):
        #     pass
        #
        # # @print_name()
        # def count_at_spur(self):
        #     direction = self.setDirection(sidingBranch, self.spur_branch)
        #     sensor = self.setSensor(self.spur_branch)
        #     self.countTrucksInactive(self.noTrucksOnTrain, sensor, direction, sidingBranch)  #counting all trucks on train
        #     self.setSpeed(self.stop)


    # 1) check for truck  (is_there_a_truck)
    #     stop_flag = False  # only checked when stop_sensor True
    #     stop_sensor = false
    #     if check for truck count = 1
    #         stop_thread_sensor True
    #         self.recover_flag = True
    #     if check_for_truck timed out
    #         self.recover_flag = False
    @print_name()                                                               # run first,  checks after function last
    @alternativeaction("alt_function", "sidingBranch", "noTrucksToMove")      # this is run 2nd, but stop flag is checked after timeout
    @variableTimeout("time_to_countInactive_one_truck")  # uses self.time_to_count_one_truck
    # @timeout(2000)
    def is_there_a_truck(self, sidingBranch, noTrucksToMove ):

        from java.util import Date

        start = Date().getTime()
        print ("setting direction")

        direction = self.setDirection(sidingBranch, self.spur_branch)
        print ("setting sensor", "time taken", Date().getTime() - start)
        sensor = self.setSensor(sidingBranch)

        self.myprint2("set sensor",  "time taken", Date().getTime() - start)

        noTrucksToCount = 1
        #if we are simulating an error, there will be one truck counted here i.e. simulate == True
        # and the routine will not time out
        self.myprint2("checking sensors is_there_a_truck")
        if sensors.getSensor("simulateErrorsInglenookSensor").getState() == ACTIVE:
            if self.index < 2:
                self.myprint2 ("simulating with errors")
                simulateOneTruck = True
                direction = self.setDirection(sidingBranch, self.spur_branch)
                self.display_pegs(self.pegs)
                self.countTrucksInactive(noTrucksToCount, sensor, direction, sidingBranch, simulateOneTruck)  #counting
                self.myprint2("********************* one truck went from siding to spur")
                print ("time taken a", Date().getTime() - start)
            else:
                print ("simulating with errors but success this time")
                simulateOneTruck = False
                # the routine needs to time out
                a_short_time = 3000  # enough to make it time out
                self.waitMsec(self.time_to_countInactive_one_truck)
                print ("time taken", Date().getTime() - start)
                print ("should have timed out")
                self.waitMsec(a_short_time)
                print ("time taken", Date().getTime() - start)
                print ("should have timed out")
        elif sensors.getSensor("simulateInglenookSensor").getState() == ACTIVE:
            print ("simulating without errors, the alt function should be called")
            simulateOneTruck = False
            # the routine needs to time out
            a_short_time = 3000  # enough to make it time out
            self.waitMsec(a_short_time)
            print ("time taken", Date().getTime() - start)
            print ("should have timed out")
            self.waitMsec(a_short_time)
            print ("time taken", Date().getTime() - start)
            print ("should have timed out")
            # the alt_function will be called
        elif sensors.getSensor("runRealTrainInglenookSensor").getState() == ACTIVE:
            self.myprint2 ("running real train")
            simulateOneTruck = True
            direction = self.setDirection(sidingBranch, self.spur_branch)
            self.display_pegs(self.pegs)
            self.countTrucksInactive(noTrucksToCount, sensor, direction, sidingBranch, simulateOneTruck)  #counting#

        # truck counted
        self.rectify_flag = True
        self.myprint2("********************** set rectify_flag", self.rectify_flag)
        self.stop_thread_sensor.setKnownState(ACTIVE)
        self.myprint2("set sensor",  "time taken", Date().getTime() - start)
        self.myprint2("is_there_a_truck end")

    @print_name()                                                               # run first,  checks after function last
    @alternativeaction("alt_function2", "sidingBranch", "noTrucksToCount", "simulate")      # this is run 2nd, but stop flag is checked after timeout
    @variableTimeout("time_to_countInactive_one_truck")  # uses self.time_to_count_one_truck
    # @timeout(2000)
    def count_at_siding__is_there_a_truck_error_if_none(self, sidingBranch, noTrucksToMove, time_to_countInactive_one_truck, simulate):

        from java.util import Date
        global place_trucks_near_disconnect_siding

        start = Date().getTime()
        print ("setting direction")

        direction = self.setDirection(sidingBranch, self.spur_branch)
        print ("setting sensor", "time taken", Date().getTime() - start)
        sensor = self.setSensor(sidingBranch)

        self.myprint2("set sensor",  "time taken", Date().getTime() - start)

        noTrucksToCount = noTrucksToMove
        #if we are simulating an error, there will be no truck counted here i.e. simulate == True
        # and the routine will not time out
        self.myprint2("checking sensors is_there_a_truck1")
        # self.dialogs.displayMessage1("in count_at_siding__is_there_a_truck_error_if_none"  + " self.index2 " +str(self.index2))
        if sensors.getSensor("simulateErrorsInglenookSensor").getState() == ACTIVE:
            if self.index2 < 2:
                midPeg = self.setMidBranch(sidingBranch) - 1
                self.dialogs.displayMessage1("added 9")
                print ("simulating with errors")
                simulateOneTruck = True
                # the routine needs to time out
                a_short_time = 3000  # enough to make it time out
                self.waitMsec(self.time_to_countInactive_one_truck)
                print ("time taken", Date().getTime() - start)
                print ("should have timed out")
                self.waitMsec(a_short_time)
                print ("time taken", Date().getTime() - start)
                print ("should have timed out")
                # now have to do recovery
            else:
                self.myprint2 ("simulating with errors but success this time")
                direction = self.setPointsAndDirection(sidingBranch, self.spur_branch)
                sensor = self.setSensor(sidingBranch)
                self.countTrucksActive(noTrucksToCount, sensor, direction, sidingBranch)  # counts from 0
                # self.set_delay_if_not_simulation(2000)
                print ("time taken aaaa", Date().getTime() - start)

        elif sensors.getSensor("simulateInglenookSensor").getState() == ACTIVE:
            self.myprint2 ("simulating with errors but success this time")
            direction = self.setPointsAndDirection(sidingBranch, self.spur_branch)
            sensor = self.setSensor(sidingBranch)
            self.countTrucksActive(noTrucksToCount, sensor, direction, sidingBranch)  # counts from 0
            self.set_delay_if_not_simulation(2000)
            print ("time taken a", Date().getTime() - start)
        elif sensors.getSensor("runRealTrainInglenookSensor").getState() == ACTIVE:
            self.myprint2 ("simulating with errors but success this time")
            direction = self.setPointsAndDirection(sidingBranch, self.spur_branch)
            sensor = self.setSensor(sidingBranch)
            self.countTrucksActive(noTrucksToCount, sensor, direction, sidingBranch)  # counts from 0
            self.set_delay_if_not_simulation(2000)
            print ("time taken a", Date().getTime() - start)
        # truck counted
        self.rectify_flag2 = False
        self.myprint2("********************** set rectify_flag2 False", self.rectify_flag2)
        self.stop_thread_sensor.setKnownState(ACTIVE)
        self.myprint2("set sensor",  "time taken", Date().getTime() - start)
        self.myprint2("count_at_siding__is_there_a_truck_error_if_none end")

    @print_name()
    def count_at_spur(self, sidingBranch, noTrucksToMove):
        # if stop_thread_sensor is set to inactive when counting, the routine stops   # check out countTrucksInactive to see how this works
        direction = self.setDirection(sidingBranch, self.spur_branch)
        sensor = self.setSensor(self.spur_branch)
        self.countTrucksInactive(self.noTrucksOnTrain, sensor, direction, sidingBranch)  #counting all trucks on train
        self.setSpeed(self.stop)

    @print_name()
    def count_at_siding(self, noTrucksToCount, sensor, direction, sidingBranch):
        operation = "PICKUP"
        direction = self.setPointsAndDirection(sidingBranch, self.spur_branch)
        sensor = self.setSensor(sidingBranch)
        self.countTrucksActive(noTrucksToCount, sensor, direction, sidingBranch)  # counts from 0     $$$$$$$$$$$$$changed$$$$$$$$$$$$$$
        self.set_delay_if_not_simulation(2000)

    def set_time_to_countInactive_one_truck(self):
        if sensors.getSensor("simulateErrorsInglenookSensor").getState() == ACTIVE:
            time_to_countInactive_one_truck = "8000"   # msec
        elif sensors.getSensor("simulateInglenookSensor").getState() == ACTIVE:
            time_to_countInactive_one_truck = "500"
        elif sensors.getSensor("runRealTrainInglenookSensor").getState() == ACTIVE:
            time_to_countInactive_one_truck = "5000"
        return time_to_countInactive_one_truck
    @print_name()
    def display_pegs(self, pegs):    #this is just to display the pegs using @print_name
        pass

    @print_name()
    def rectify_trucks_back_to_mid(self, sidingBranch):
        global repeat
        self.myprint2("hi")
        self.myprint2("in rectify_trucks_back_to_mid: a")
        direction = self.setDirection(self.spur_branch, sidingBranch)
        sensor = self.setSensor(self.spur_branch)
        noTrucksToCount = self.no_trucks_to_rectify
        self.myprint2("self.no_trucks_to_rectify", self.no_trucks_to_rectify)
        self.display_pegs(self.pegs)
        self.countTrucksInactive(noTrucksToCount, sensor, direction, sidingBranch)  #counting
        self.display_pegs(self.pegs)
        self.myprint2("in rectify_trucks_back_to_mid: ******************** one truck goes from mid to siding")
        self.couple1(sidingBranch)
        self.myprint2("in rectify_trucks_back_to_mid: end")
    @print_name()
    def rectify_trucks_back_to_siding(self, sidingBranch):
        self.myprint2("in rectify_trucks_back_to_siding: a")
        direction = self.setDirection(self.spur_branch, sidingBranch)
        sensor = self.setSensor(sidingBranch)
        noTrucksToCount = 1
        self.myprint2("in rectify_trucks_back_to_siding: b")
        self.display_pegs(self.pegs)
        self.countTrucksInactive(noTrucksToCount, sensor, direction, sidingBranch)  #counting
        self.display_pegs(self.pegs)
        self.myprint2("in rectify matters: ******************** one truck goes from mid to siding")
        self.couple1(sidingBranch)
        self.myprint2("in rectify_trucks_back_to_siding: end")

    def rectify_connect_up_again(self, sidingBranch):
        self.myprint2("in rectify_connect_up_again")
        # we need to reverse direction and connect up again
        direction = self.setDirection(self.spur_branch, sidingBranch)
        sensor = self.setSensor(sidingBranch)
        # might need to move a bit ectra here
        timeCouple = 450   #need to increase this every time repeat
        self.couple1(sidingBranch)
        # remove the spacer truck (9) so the engine is coupled
        midPeg = self.setMidBranch(sidingBranch) - 1
        self.pegs[midPeg].pop()
        self.update_displays(self.pegs)


    @print_name()
    def alt_function(self, sidingBranch, noTrucksToMove):
        self.myprint2 ("in alternative action setting stop thread sensor")
        self.dialogs.displayMessage1("in alt_function")
        # (a0) kill other count_at_spur thread
        self.stop_thread_sensor.setKnownState(INACTIVE)    # check out countTrucksInactive to see how this works

    @print_name()
    def alt_function2(self, sidingBranch, noTrucksToMove, simulate):
        self.myprint2 ("in alternative action setting stop thread sensor")
        self.dialogs.displayMessage1("in alt_function2")
        if simulate:
            # make the engine go away from the siding sensor without the rest of the trucks
            midPeg = self.setMidBranch(sidingBranch) - 1
            self.pegs[midPeg].append(9)
            self.update_displays(self.pegs)
        # (a0) kill other count_at_spur thread
        # self.stop_thread_sensor.setKnownState(INACTIVE)    # check out countTrucksInactive to see how this works
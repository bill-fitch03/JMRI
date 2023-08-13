    # @add_methods(ccc.decide_what_to_do_first, ccc.generate_first_instructions, ccc.decide_what_to_do)
# @add_methods(ccc.moveTrucksOneByOne, ccc.moveTrucksAllAtOnce, ccc.moveTrucks, ccc.moveEngineToBranch, ccc.moveToDisconnectPosition)

import java
import jmri
import copy
from timeout import alternativeaction, variableTimeout, print_name, timeout
from threading import Thread
import globals


@print_name()
def decide_what_to_do_first(self):
    print "calling decide_what_to_do_first in move_train_call"
    self.indent()
    # set up the trucks 5 in branch 3 and 3 in branch 2, and return to branch 4
    # self.noTrucksOnTrain = 0

    self.myprint("decide_what_to_do_first *")

    self.noTrucksOnTrain = 0
    self.previousBranch = self.spur_branch
    self.noTrucksToMoveFromPreviousStep = 0
    self.numberTrucksToMove_previous = 0

    self.myprint("self.noTrucksOnTrain:" + str(self.noTrucksOnTrain))
    self.myprint("self.previousBranch:" + str(self.previousBranch))
    # instruction_first = [generate_first_instructions]
    # self.noTrucksOnTrain = self.decide_what_to_do(instruction_first,self.noTrucksOnTrain)
    self.myprint("end decide_what_to_do_first")
    self.dedent()


# @print_name()
# def generate_first_instructions(self):
#     self.indent()
#     # the move trucks instruction is shown commented out, so we can see what the yield does
#     # moveTrucks(self, noTrucksOnTrain, noTruckstoMove, fromBranch, destBranch):
#
#     # we move from branch 4 to branch 3 depositing all 5 trucks
#     self.dedent()
#     pass


# Procedure
#
#     trucks on train yyzz (zz = x_old)
#     depositing zz  (x_old)
#     trucks on siding www
#     picking up xx
#         yyzz*www
#     move to left zz then to right xx
#     connect -zz + xx
#     trucks on train = yyzz - zz + xx
#
# on siding   move x to dest
#
# 0) move 0
#     b) move to siding
#         move x = 0
#         trucks on train y = 0
#         x_old = 0
#         y_old = 0
#
# 1) move x [init from dest]
#     a) move to spur
#         move 	x = 0
#         connect -x_old + x
#         trucks y = y_old - x_old + x
#     b) move to 'from' siding     (start here)
#         move 	x_old = x  (= 0 first)
#         trucks 	y_old = y  (= 0 first)
#
# 2) move to dest:  x trucks
#     a) move to spur
#         connect - x_old + x
#         move 	x
#         trucks 	y = y_old - x_old + x
#
#     b) move to dest siding
#         move 	x_old = x
#         trucks	y_old = y


    # DROPOFF
    # we do two threads
    # stop_thread_sensor = False
    # 1) check for truck  (is_there_a_truck_
    #     stop_flag = False  # only checked when stop_sensor True
    #     stop_sensor = false
    #     if check for truck count = 1
    #         stop_thread_sensor True
    #         rectify_flag = True
    #     if check_for_truck timed out
    #         rectify_flag = False
    #
    # 2) move to spur  (count_at_spur)
    #     check for stop_thread_sensor True while checkingh sensors
    #     self.stop_thread_flag set true in simulate
    #     self.stop_thread_flag is set if waiting for sensor (this is just the stop_thread_sensor flag
    #
    #     updates self.number_of_trucks_to_move_back
    #     if stop_thread_flag set True:
    #         stops prematurely to recover
    #
    # wait for above two threads to complete
    #
    # start below two threads if self.recover_flag set
    #
    # 3) recover_truck_to_siding if previous two have finished
    #     moves back  1 truck  (simulation)
    #
    # 3) recover_trucks_to_mid if previous two have finished
    #     moves back  self.number_of_trucks_to_move_back to mid
    #
    #
    # 4) alt_function
    #     if check_for_truck times out
    #         sets stop_sensor True
    #         sets stop_flag False

@print_name()
def move_to_spur_operations(self, sidingBranch, noTrucksToMove, noTrucksToMove_old):
    amountToMove = noTrucksToMove - noTrucksToMove_old     #

    self.time_to_countInactive_one_truck = self.set_time_to_countInactive_one_truck()    # need different times for simulation and real life

    # move to correct position and uncouple
    operation = self.moveToDisconnectPosition(self.noTrucksOnTrain, amountToMove, sidingBranch)
    self.myprint2("operation", operation)
    self.noTrucksOnTrain = self.noTrucksOnTrain + amountToMove
    # operation is "PICKUP" or "DROPOFF"
    self.uncouple1(sidingBranch, operation)

    if operation == "DROPOFF" or \
       operation == "PICKUP":     #error does not uncouple
        print "in operation", operation
        repeat = True
        self.index = 1
        while repeat:
            self.rectify_flag = False
            print "in repeat"
            self.dialogs.displayMessage1("In operation " + str(operation) + " in move_to_spur repeat")
            self.sidingBranch = sidingBranch                    # needed for alternate_function decorator: see is_there_a_truck
            self.noTrucksToMove = noTrucksToMove                # needed for alternate_function decorator: see is_there_a_truck
            t1 = Thread(target=self.is_there_a_truck, args=(sidingBranch, noTrucksToMove))   #sets rectify_flag if counts a truck
                                                                                            # and sets stop_thread_sensor
            t2 = Thread(target=self.count_at_spur, args=(sidingBranch, noTrucksToMove))

            t1.start()      # stop_thread_sensor and self.rectify_flag set here if trucks do not uncouple and counts a truck
            t2.start()      # stops prematurely if stop_thread_sensor set
            t1.join()
            self.myprint2("**************** t1 joined")
            t2.join()
            self.myprint2("**************** t2 joined", "self.rectify_flag", self.rectify_flag)
            if self.rectify_flag == True:
                t3 = Thread(target=self.rectify_trucks_back_to_siding, args=(sidingBranch,))
                t4 = Thread(target=self.rectify_trucks_back_to_mid, args=(sidingBranch,))
                t3.start()   # moves trucks back to siding
                t4.start()   # move trucks back to mid
                t3.join()
                self.myprint2("**************** t3 joined")
                t4.join()
                self.myprint2("**************** t4 joined")
                repeat = True
            else:
                self.myprint2("**************** repeat false")
                repeat = False
            self.index += 1
            self.myprint2("******************move_to_spur_operations: repeat", repeat)
    else:
        print "in operation PICKUP"
        repeat = True
        self.index = 1
        while repeat:
            print "in repeat"
            self.sidingBranch = sidingBranch                    # needed for alternate_function decorator: see is_there_a_truck
            self.noTrucksToMove = noTrucksToMove                # needed for alternate_function decorator: see is_there_a_truck
            t1 = Thread(target=self.is_there_a_truck, args=(sidingBranch, noTrucksToMove))   #sets rectify_flag if counts a truck
            # and sets stop_thread_sensor
            t2 = Thread(target=self.count_at_spur, args=(sidingBranch, noTrucksToMove))

            t1.start()      # stop_thread_sensor and self.rectify_flag set here if trucks do not uncouple and counts a truck
            t2.start()      # stops prematurely if stop_thread_sensor set
            t1.join()
            self.myprint2("**************** t1 joined")
            t2.join()

        self.count_at_spur(sidingBranch, noTrucksToMove)

@print_name()
def move_to_siding_operations(self, sidingBranch, noTrucksToMove):

    # the move operation will be done in the head operation
    # store variables which will be required
    # self.noTrucksToMoveFromPreviousStep = self.noTrucksToMove

    direction = self.setPointsAndDirection(self.spur_branch, sidingBranch)
    self.set_delay_if_not_simulation(5000)

    sensor = self.setSensor(self.spur_branch)
    self.countTrucksInactive(self.noTrucksOnTrain, sensor, direction, sidingBranch)  # leave the moving to the next movement

    sensor = self.setSensor(sidingBranch)     # a siding branch
    noTrucksToDetect = 0            #we are not moving trucks, we are only detecting the first one at the beginning of it.
    self.countTrucksInactive(noTrucksToDetect, sensor, direction, sidingBranch)  # leave the moving to the next movement




@print_name()
def moveToDisconnectPosition(self, noTrucksOnTrain, noTrucksToAdd, sidingBranch):

    self.indent()
    noTrucksToCount = abs(noTrucksToAdd)    #Trucks to add to train
    self.dialogs.displayMessage("moveToDisconnectPosition")
    if noTrucksToAdd >= 0:   # picking up trucks
        # operation = "PICKUP"
        # direction = self.setPointsAndDirection(sidingBranch, self.spur_branch)
        # sensor = self.setSensor(sidingBranch)
        # self.countTrucksActive(noTrucksToCount, sensor, direction, sidingBranch)  # counts from 0     $$$$$$$$$$$$$changed$$$$$$$$$$$$$$
        # self.set_delay_if_not_simulation(2000)
        operation = "PICKUP"

        print "in operation", operation
        repeat = True
        self.index2 = 1
        while repeat:
            self.rectify_flag2 = True
            print "in repeat"
            self.dialogs.displayMessage1("repeating moveToDisconnectPosition")
            self.sidingBranch = sidingBranch                    # needed for alternate_function decorator: see count_at_siding__is_there_a_truck_error_if_none
            self.noTrucksToCount = 1                             # needed for alternate_function decorator: see is_thecount_at_siding__is_there_a_truck_error_if_nonere_a_truck
            self.simulate = True

            # stage1 count 1 truck and time out if there is none (it is an error if there is none and we don't want to wait until the time for all the trucks before timing outy

            # t1 = Thread(target=self.count_at_siding__is_there_a_truck_error_if_none, args=(sidingBranch, noTrucksToCount))   #sets rectify_flag false if counts a truck
            # self.time_to_countActive_n_trucks = self.time_to_countInactive_one_truck * noTrucksToCount
            self.simulate = True
            self.count_at_siding__is_there_a_truck_error_if_none(sidingBranch, self.noTrucksToCount, self.time_to_countInactive_one_truck, self.simulate)    # sets rectify_flag false if counts a truck

            # # # and sets stop_thread_sensor
            # t2 = Thread(target=self.count_at_siding, args=(sidingBranch, noTrucksToCount))
            # #
            # t1.start()      # stop_thread_sensor and self.rectify_flag set here if trucks do not uncouple and counts a truck
            # t2.start()      # stops prematurely if stop_thread_sensor set
            # t1.join()
            # # self.myprint2("**************** t1 joined")
            # t2.join()
            # self.myprint2("**************** t2 joined", "self.rectify_flag", self.rectify_flag)
            #self.rectify_flag = False
            self.dialogs.displayMessage1("finished stage1 rectify_flag2" + str(self.rectify_flag2))
            if self.rectify_flag2 == True:
                self.dialogs.displayMessage1("rectify_flag2 " + str(self.rectify_flag2))
                self.rectify_connect_up_again(sidingBranch)
                # t3 = Thread(target=self.rectify_connect_up_again, args=(sidingBranch,))
                # # t4 = Thread(target=self.rectify_trucks_back_to_mid, args=(sidingBranch,))
                # t3.start()   # moves trucks back to siding
                # # t4.start()   # move trucks back to mid
                # t3.join()
                # # self.myprint2("**************** t3 joined")
                # # t4.join()
                # self.myprint2("**************** t4 joined")
                self.dialogs.displayMessage1("repeating")
                repeat = True
            else:

                self.noTrucksToCount = noTrucksToCount - 1  # we have already counted one
                self.dialogs.displayMessage2("don't need to rectify: counting " + str(self.noTrucksToCount) + " more trucks")
                direction = self.setPointsAndDirection(sidingBranch, self.spur_branch)
                sensor = self.setSensor(sidingBranch)
                self.countTrucksActive(self.noTrucksToCount, sensor, direction, sidingBranch)  # counts from 0
                self.dialogs.displayMessage1("done all trucks to disconnect not repeating")
                repeat = False
            self.index2 += 1
            self.myprint2("******************move_to_spur_operations: repeat", repeat,"index2", self.index2)
            self.dialogs.displayMessage2("finished repeat = " + str(repeat) + " index2 " + str(self.index2))

    elif noTrucksToAdd < 0: # dropping off trucks
        operation = "DROPOFF"
        print "in operation", operation
        if noTrucksToCount > noTrucksOnTrain:
            self.myprint("!!!!>>moveToDisconnectTrucks: dropping off trucks: error not enough trucks")
            crash_here   # does not exist so crashes
        self.myprint2("sidingBranch00", sidingBranch)
        direction = self.setPointsAndDirection(self.spur_branch, sidingBranch)
        self.myprint2("sidingBranch0", sidingBranch)
        sensor = self.setSensor(sidingBranch)
        self.myprint2("sidingBranch1", sidingBranch)
        self.countTrucksActive(noTrucksToCount, sensor, direction, sidingBranch)  # counts from 0
        self.myprint2("sidingBranch2", sidingBranch)
        self.set_delay_if_not_simulation(2000)
        operation = "DROPOFF"
    else:  # noTrucksToAdd == 0:
        operation = "PICKUP"
        pass
    self.myprint("end moveToDisconnectPosition ")
    self.dedent()
    return operation

# @print_name()
# def moveEngineToBranch(self, fromBranch, toBranch, trucksToMove):
#     self.indent()
#     self.myprint("In moveEngineToBranch")
#     # set direction
#     direction = self.setPointsAndDirection(fromBranch, toBranch)
#     self.setPoints(fromBranch, toBranch)
#     self.set_delay_if_not_simulation(2000)
#     # set Speed
#     self.setSpeed(self.slow)
#     # set sensor
#     sensor = self.setSensor(toBranch)
#
#     # this is wrong
#     noTrucksToCount = trucksToMove
#
#     # wait for sensor to trigger
#     self.myprint1("countTrucksInactive2", sensor)
#     self.countTrucksInActive(noTrucksToCount, sensor, direction, fromBranch, destBranch,)
#     self.setSpeed(self.stop)
#     self.set_delay_if_not_simulation(1000)
#
#     # go on for a bit
#     self.setSpeed(self.slow)
#     self.set_delay_if_not_simulation(500)
#     self.setSpeed(self.stop)
#
#     # uncouple
#     self.uncouple1()
#
#     self.myprint("end moveEngineToBranch ")
#     self.dedent()


@print_name()
def moveTrucksOneByOne(self, noTrucksToMove, fromBranch, destBranch, ListOfTrucksInBranches):
    self.indent()

    if self.spur_branch not in [fromBranch, destBranch]:
        noTrucksToMoveInOneGo = 1
        noOfRepetitions = noTrucksToMove
    else: # all can be done in one journey
        noTrucksToMoveInOneGo = noTrucksToMove
        noOfRepetitions = 1
    for i in range(noOfRepetitions):
        self.myprint2(">>>>>movetrucksonebyone  truck", i)
        self.dialogs.displayMessage(">>>>>movetrucksonebyone  truck" + str(i))

        ListOfTrucksInBranches = [len(x) for x in self.pegs]
        self.moveTrucks(noTrucksToMoveInOneGo, fromBranch, destBranch, self.pegs)

        ListOfTrucksInBranches = [len(x) for x in self.pegs]
        self.myprint("ListOfTrucksInBranches after", ListOfTrucksInBranches)
    self.dedent()

# moveTrucks emulates the following code in inglenook, however in addition to that code we must
# check whether we are at the correct branch before popping

# for i in range(0, noTrucks):
# if fromBranch != self.mainLine:
# pop from fromBranch push to mainLine
# if destBranch != 4:
# pop from fromBranch push to mainLine

# we do this with the following pseudocode
# if previousBranch != fromBranch
# move to fromBranch. We take the current number of trucks on train
# do this in 2 steps
# if previousBranch != mainLine
# move from previousBranch to mainLine
# if frombranch != mainLine
# move from mainLine to fromBranch
# repeat for each truck in trucksToMove
# if frombranch != mainLine
# take 1 truck from frombranch to mainLine
# if destBranch != mainLine
# take 1 truck from mainLine to destBranch
# deposit 1 truck at destBranch

def place_trucks_near_disconnect(self, branch):
    if branch != self.spur_branch:
        self.place_trucks_near_disconnect_siding = True
    self.update_displays(self.pegs)




# def setSensor(self, branch):
#     sensorManager = jmri.InstanceManager.getDefault(jmri.SensorManager)
#     if branch == self.spur_branch:
#         sensor = sensorManager.getSensor("Decoupling_spur")
#     elif branch == self.mid_branch:
#         sensor = None
#     elif branch == 1:
#         sensor = sensorManager.getSensor("Decoupling_1")
#     elif branch == 2:
#         sensor = sensorManager.getSensor("Decoupling_2")
#     elif branch == 3:
#         sensor = sensorManager.getSensor("Decoupling_3")
#     else:
#         pass
#     return sensor

def strip_0(self, pegs):
    list1 = []
    # print("*************")
    print("strip_0 pegs: " , pegs)
    for deque in pegs:
        list = [item for item in deque if item>0]
        list1 .append(list)
    print("strip_0 list1: " , list1)
    print("*************")
    return list1

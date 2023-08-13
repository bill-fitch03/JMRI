import jmri

class StartInglenookMaster(jmri.jmrit.automat.AbstractAutomaton):

    # responds to the simulateInglenookSensor, and allows the Inglenook Siding Routine to start

    logLevel = 0
    indentno = 0
    #instanceList = []   # List of file based instances

    def init(self):
        self.logLevel = 0
        if self.logLevel > 0: print 'Create Stop Thread'

    def setup(self):
        simulateInglenookSensor = "simulateInglenookSensor"
        self.simulate_inglenook_sensor = sensors.getSensor(simulateInglenookSensor)
        if self.simulate_inglenook_sensor is None:
            return False
        self.simulate_inglenook_sensor.setKnownState(INACTIVE)
        self.dialogs = OptionDialog()
        return True

    def handle(self):

        #this repeats
        # wait for a sensor requesting to check for new train
        self.dialogs.displayMessage("click Simulate Ingleook System to test")
        if self.logLevel > 0: print ("wait for a sensor requesting to check for new train")

        self.get_inglenook_run_or_simulate_buttons = [sensors.getSensor(sensorName) for sensorName in \
                ["justShowSortingInglenookSensor", "simulateInglenookSensor", \
                 "simulateErrorsInglenookSensor", "runRealTrainInglenookSensor"]]

        self.waitSensorActive(self.get_inglenook_run_or_simulate_buttons)
        # for sensor in self.get_inglenook_run_or_simulate_buttons:
        #     sensor.setKnownState(INACTIVE)
        run_inglenook = InglenookMaster()                  #need this starts the system
        if run_inglenook.setup():
            run_inglenook.setName('Run Inglenook')
            print "start InglenookMaster"
            run_inglenook.start()
        return False

    # def createAndShowGUI(self, super):
    #     createandshowGUI(self,super)

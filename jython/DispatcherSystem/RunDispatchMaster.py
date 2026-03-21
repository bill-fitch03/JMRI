import jmri
import os

RunDispatch = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/RunDispatch.py')
exec(open(RunDispatch).read())

FileResetButtonMaster = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/ResetButtonMaster.py')
exec(open(FileResetButtonMaster).read())

StopDispatcherSystem = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/StopDispatcherSystem.py')
exec(open(FileResetButtonMaster).read())

# FileMoveTrain has to go before CreateScheduler
FileMoveTrain = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/MoveTrain.py')
exec(open(FileMoveTrain).read())

CreateScheduler = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/Scheduler.py')
exec(open(CreateScheduler).read())

CreateSchedulerPanel = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/SchedulerPanel.py')
exec(open(CreateSchedulerPanel).read())

CreateSimulation = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/Simulation.py')
exec(open(CreateSimulation).read())

CreatePlatformPanel = jmri.util.FileUtil.getExternalFilename('program:jython/DispatcherSystem/PlatformPanel.py')
exec(open(CreatePlatformPanel).read())

global instanceList

instanceList = []
# Global dictionary to store references to the PositionableLabels
# This will be built dynamically when RunDispatchMaster starts.
direction_labels_map = {}

class BlockChangeListener(PropertyChangeListener):
    def __init__(self, block, label_map_ref):
        # print "blockChangeListener"
        self.block = block
        self.label_map_ref = label_map_ref # Reference to the global direction_labels_map
        self.logLevel = 1

    def propertyChange(self, event):
        if event.propertyName == "value": # Block value changes (train name)
            print "block value change"
            block_name = self.block.getUserName()
            print "block_name", block_name, "block", self.block
            layoutBlocks = jmri.InstanceManager.getDefault(jmri.jmrit.display.layoutEditor.LayoutBlockManager)
            current_block = layoutBlocks.getLayoutBlock(block_name)
            train_name = event.newValue # Get the new train name from the block value

            if block_name not in self.label_map_ref:
                if self.logLevel > 0: print "BlockChangeListener: No direction label found for block", block_name
                return

            label_to_update = self.label_map_ref[block_name]

            if train_name and train_name != "none" and train_name != "":
                # Check if the train is in the global 'trains' dictionary
                # This is crucial for getting the correct direction ('forward'/'reverse')
                if train_name in trains: # 'trains' global from MoveTrain.py
                    # if "direction" in trains[train_name]:
                    train = trains[train_name]
                    print "train" , train
                    if "direction" in train:
                        train_direction = train["direction"]
                        label_text = "FWD" if train_direction == "forward" else "REV"
                        edge = train["edge"]
                        # if "previous_edge" in trains[train_name]:
                        #     previous_edge = trains[train_name]["previous_edge"]
                        # else:
                        #     previous_edge = edge
                        #     # print "previous_edge set to edge"
                        # previous_travel_direction = self.get_travel_direction(previous_edge)
                        print "edge", edge
                        travel_direction = self.get_travel_direction(edge, block_name)
                        # if previous_travel_direction != travel_direction:
                        #     travel_direction = previous_travel_direction
                        #     print "set travel direction to previous"
                        print "travel_direction =", travel_direction
                        # label_text = label_text + " " + travel_direction
                        label_text = travel_direction + " " + label_text
                        # print "asdfg"
                        if self.logLevel > 0: print "BlockChangeListener: Block {} occupied by {}. Direction: {}".format(block_name, train_name, train_direction)
                    else:
                        label_text = train_name # Display the train name itself
                else:
                    # Train not yet known to MoveTrain.py's 'trains' dict, or it's a temporary value
                    label_text = train_name # Display the train name itself
                    if self.logLevel > 0: print "BlockChangeListener: Block {} occupied by unknown train {}. Displaying name.".format(block_name, train_name)
            else:
                # Block value is empty, clear the label
                label_text = ""
                if self.logLevel > 0: print "BlockChangeListener: Block {} is now empty. Clearing label.".format(block_name)

            # Update the label text on the EDT
            def setTextOnLabel():
                label_to_update.setText(label_text)
                print "setting text to" , label_text
                if label_to_update.getWidth() != 110:
                    print "setting size to 110"
                    label_to_update.setSize(110, label_to_update.getPreferredSize().height)
            jmri.util.ThreadingUtil.runOnGUI(setTextOnLabel)

    def get_travel_direction(self, edge, current_block_name):

        layoutBlocks = jmri.InstanceManager.getDefault(jmri.jmrit.display.layoutEditor.LayoutBlockManager)

        next_layout_block_name = self.next_block_in_path(edge)
        print "next_layout_block_name", next_layout_block_name
        if next_layout_block_name != "unknown":
            next_layout_block = layoutBlocks.getLayoutBlock(next_layout_block_name)
        else:
            next_layout_block = None

        penultimate_block_name = edge.getItem("penultimate_block_name")
        print "penultimate_block_name", penultimate_block_name, "current_block_name", current_block_name
        if penultimate_block_name != "":

            penultimate_block = layoutBlocks.getLayoutBlock(penultimate_block_name)
            # print "c"
            last_block_name = edge.getItem("last_block_name")
            print "last_block_name", last_block_name
            if last_block_name != "":
                last_block = layoutBlocks.getLayoutBlock(last_block_name)
                if current_block_name != "":
                    current_block = layoutBlocks.getLayoutBlock(current_block_name)
                    # print "d"
                    if next_layout_block_name == "unknown":
                        travel_direction = int(penultimate_block.getNeighbourDirection(last_block))
                        print "getting travel direction penultimate_block" , penultimate_block_name, "last_block", last_block_name
                    else:
                        print "getting travel direction current_block" , current_block_name, "last_block", last_block_name
                        travel_direction = current_block.getNeighbourDirection(next_layout_block)
                        print "travel_direction", travel_direction
                        travel_direction = int(travel_direction)
                    print "travel_direction", travel_direction
        else:
            travel_direction = "unknown"
            print "travel_direction", travel_direction
        # print "e"

        directionName = ""
        if travel_direction == jmri.Path.EAST:
            directionName = u"\u2192"+"E"
        elif travel_direction == jmri.Path.WEST:
            directionName = u"\u2190"+"W"
        elif travel_direction == jmri.Path.NORTH:
            directionName = u"\u2191"+"N"
        elif travel_direction == jmri.Path.SOUTH:
            directionName = u"\u2193"+"S"
        elif travel_direction == jmri.Path.NORTH_EAST:
            directionName = u"\u2197"+"NE"
        elif travel_direction == jmri.Path.NORTH_WEST:
            directionName = u"\u2196"+"NW"
        elif travel_direction == jmri.Path.SOUTH_EAST:
            directionName = u"\u2198"+"SE"
        elif travel_direction == jmri.Path.SOUTH_WEST:
            directionName = u"\u2199"+"SW"
        else:
            directionName = "unknown"
        print "directions E" , jmri.Path.EAST
        print "directions W" , jmri.Path.WEST
        print "directions N" , jmri.Path.NORTH
        print "directions S" , jmri.Path.SOUTH
        print "directions NE" , jmri.Path.NORTH_EAST
        print "directions NW" , jmri.Path.NORTH_WEST
        print "directions SE" , jmri.Path.SOUTH_EAST
        print "directions SW" , jmri.Path.SOUTH_WEST
        return directionName

    def next_block_in_path(self, edge):
        print "next_block_in_path"
        layout_block_list = edge.getItem("path")
        print "layout_block_list", layout_block_list
        current_block_name = self.block.getUserName()
        layoutBlocks = jmri.InstanceManager.getDefault(jmri.jmrit.display.layoutEditor.LayoutBlockManager)
        current_layout_block = layoutBlocks.getLayoutBlock(current_block_name)
        print "current_layout_block", current_layout_block, current_block_name
        current_block_index = layout_block_list.index(current_layout_block)
        print "current_block_index", current_block_index
        if current_block_index + 1 > len(layout_block_list) - 1:
            return "unknown"
        next_layout_block = layout_block_list.get(current_block_index + 1)
        print "next_layout_block", next_layout_block, next_layout_block.getUserName()
        return next_layout_block.getUserName()
        # try:
        #     print "next_block_in_path"
        #     layout_block_list = edge.getItem("path")
        #     print "layout_block_list", layout_block_list
        #     current_block_index = layout_block_list.index(current_block_name)
        #     print "current_block_index", current_block_index
        #     next_layout_block = layout_block_list.index[current_block_index + 1]
        #     print "next_layout_block", next_layout_block
        #     return next_layout_block.getUserName()
        # except:
        #     return ""




class RunDispatcherMaster(jmri.jmrit.automat.AbstractAutomaton ):

    def __init__(self):
        global g
        global le
        global glb_reset_all_trains

        self.logLevel = 0
        g = StationGraph()

        new_train_master = NewTrainMaster()
        instanceList.append(new_train_master)
        if new_train_master.setup():
            new_train_master.setName('New Train Master')
            new_train_master.start()

        stop_master = StopMaster()
        if stop_master.setup():
            stop_master.setName('Stop Master')
            stop_master.start()

        reset_button_master = ResetButtonMaster()
        instanceList.append(reset_button_master)
        if reset_button_master.setup():
            pass
            reset_button_master.setName('Reset Button Master')
            reset_button_master.start()

        dispatch_master = DispatchMaster()
        instanceList.append(dispatch_master)
        if dispatch_master.setup():
            dispatch_master.setName('Dispatch Master')
            dispatch_master.start()

        simulation_master = SimulationMaster()
        instanceList.append(simulation_master)
        if simulation_master.setup():
            simulation_master.setName('Simulation Master')
            simulation_master.start()

        global scheduler_master      #global so cas be referenced before killing threads
        scheduler_master = SchedulerMaster()
        instanceList.append(scheduler_master)

        if scheduler_master.setup():
            scheduler_master.setName('Scheduler Master')
            scheduler_master.start()

        monitorTrack_master = MonitorTrackMaster()
        instanceList.append(monitorTrack_master)
        if monitorTrack_master.setup():
            monitorTrack_master.setName('Monitor Track Master')
            monitorTrack_master.start()

        off_action_master = OffActionMaster()
        instanceList.append(off_action_master)
        if off_action_master.setup():
            off_action_master.setName('Off-Action Master')
            off_action_master.start()
        else:
            if self.logLevel > 0: print("Off-Action Master not started")

        # ensure the memory label contents are wiped out if we are starting from scratch

        if "glb_reset_all_trains" not in globals():
            glb_reset_all_trains = True     # first time round delete all memory variables

        # print "glb_reset_all_trains", glb_reset_all_trains

        #set default values of buttons
        sensors.getSensor("Express").setKnownState(INACTIVE)
        sensors.getSensor("simulateSensor").setKnownState(INACTIVE)
        sensors.getSensor("setDispatchSensor").setKnownState(ACTIVE)
        sensors.getSensor("stopMasterSensor").setKnownState(INACTIVE)
        sensors.getSensor("modifyMasterSensor").setKnownState(INACTIVE)
        sensors.getSensor("checkRouteSensor").setKnownState(INACTIVE)
        sensors.getSensor("checkRouteSensor").setKnownState(ACTIVE)
        sensors.getSensor("soundSensor").setKnownState(INACTIVE)
        sensors.getSensor("stopAtStopSensor").setKnownState(ACTIVE)
        sensors.getSensor("editRoutesSensor").setKnownState(INACTIVE)
        sensors.getSensor("viewScheduledSensor").setKnownState(INACTIVE)
        sensors.getSensor("showClockSensor").setKnownState(INACTIVE)
        sensors.getSensor("timetableSensor").setKnownState(INACTIVE)
        sensors.getSensor("departureTimeSensor").setKnownState(INACTIVE)
        sensors.getSensor("helpSensor").setKnownState(INACTIVE)
        global stored_simulate
        if 'stored_simulate' in globals():
            if stored_simulate == ACTIVE:
                sensors.getSensor("simulateSensor").setKnownState(ACTIVE)

        self.waitMsec(2000)   #wait for panel to load, it may have train values
        if glb_reset_all_trains == True:
            # print "removing train values"
            StopMaster().remove_train_values()
            # StopMaster().remove_all_trains_from_trains_allocated()

        self.update_operations_routes_and_locations()
        self.block_listeners = {} # To store listeners for later removal
        self.setup_direction_labels_and_listeners()


    def setup_direction_labels_and_listeners(self):
        self.logLevel = 0
        editorManager = jmri.InstanceManager.getDefault(jmri.jmrit.display.EditorManager)
        for editor in editorManager.getAll():
            if isinstance(editor, jmri.jmrit.display.layoutEditor.LayoutEditor) and editor.getTitle() != 'Dispatcher System':
                # Build the direction_labels_map from existing PositionableLabels on the panel
                # This assumes CreateIcons.py has already run and the panel was saved.
                for item in editor.getContents():
                    if isinstance(item, jmri.jmrit.display.PositionableLabel):
                        if self.logLevel > 0: print "name", item.getId()
                    if isinstance(item, jmri.jmrit.display.PositionableLabel) and item.getId() and item.getId().startswith("PL_DIRECTION_"):
                        block_name = item.getId().replace("PL_DIRECTION_", "").replace("_", " ")
                        direction_labels_map[block_name] = item
                        if self.logLevel > 0: print "RunDispatchMaster: Found existing direction label for block:", block_name

                if not direction_labels_map:
                    if self.logLevel > 0: print "RunDispatchMaster: No direction labels found on the panel. Did CreateIcons.py run and was the panel saved?"
                    return

                # Now, add listeners to the Blocks
                for block in blocks.getNamedBeanSet():
                    block_name = block.getUserName()
                    if block_name:
                        # Construct the expected label name
                        expected_label_name = "PL_DIRECTION_" + block_name.replace(" ", "_")

                        # Find this label in the editor contents
                        found_label = None
                        for item in editor.getContents():
                            if isinstance(item, jmri.jmrit.display.PositionableLabel):
                                # print ("item", item)
                                if item.getId() is not None:
                                    if self.logLevel > 0: print("item.getId()", item.getId())
                            if isinstance(item, jmri.jmrit.display.PositionableLabel) and item.getId() == expected_label_name:
                                found_label = item
                                break

                        if found_label:
                            direction_labels_map[block_name] = found_label
                            listener = BlockChangeListener(block, direction_labels_map)
                            block.addPropertyChangeListener("value", listener)
                            self.block_listeners[block_name] = listener

        self.logLevel = 0

    def dispose(self):
        # Remove listeners when RunDispatchMaster is stopped
        for block_name, listener in self.block_listeners.items():
            layoutBlock = jmri.InstanceManager.getDefault(jmri.jmrit.display.layoutEditor.LayoutBlockManager).getLayoutBlock(block_name)
            if layoutBlock and layoutBlock.getBlock():
                layoutBlock.getBlock().removePropertyChangeListener("value", listener)
                if self.logLevel > 0: print "RunDispatchMaster: Removed listener from block:", block_name
        super().dispose()

    def update_operations_routes_and_locations(self):
        # operations is used by dispatcher system
        # when a new route is created
        # and the route contains a station or action it is added to operations>locations
        # If we are using two config files one for simulation and one for real running they get out of sync
        # To allow us to use operations to get a list of all stations and actions we update them here

        self.update_operations_locations()
        self.update_operations_actions()

    def update_operations_locations(self):

        LocationManager=jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        for station_name in self.get_list_of_stopping_points():
            if LocationManager.getLocationByName(station_name) is None:
                LocationManager.newLocation(station_name)
                print "added", station_name

    def update_operations_actions(self):

        LocationManager=jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        for action in self.get_list_of_actions():
            # print "action", action
            if LocationManager.getLocationByName(action) is None:
                LocationManager.newLocation(action)
                # print "added", action


    # ***********************************************************
    # gets the list of stopping points (stations, sidings etc.)
    # ***********************************************************
    def get_list_of_stopping_points(self):
        stopping_points_set = set()

        # First, get stopping points from block comments
        for block in blocks.getNamedBeanSet():
            comment = block.getComment()
            if comment != None:
                if "stop" in comment.lower():
                    stopping_points_set.add(block.getUserName())

        # Second, automatically add blocks associated with LayoutTurntables
        editorManager = jmri.InstanceManager.getDefault(jmri.jmrit.display.EditorManager)
        for editor in editorManager.getAll():
            if isinstance(editor, jmri.jmrit.display.layoutEditor.LayoutEditor):
                # The returned object is a Java Set, which needs to be converted to a list for safe iteration in Jython
                for turntable in list(editor.getLayoutTurntables()):
                    layout_block = turntable.getLayoutBlock()
                    if layout_block is not None and layout_block.getUserName() is not None:
                        stopping_points_set.add(layout_block.getUserName())

        return sorted(list(stopping_points_set))


    def action_directory_in_DispatcherSystem(self):
        path = jmri.util.FileUtil.getScriptsPath() + "DispatcherSystem" + java.io.File.separator + "actions"
        if not os.path.exists(path):
            os.makedirs(path)
        return path + java.io.File.separator

    def action_directory(self):
        path = jmri.util.FileUtil.getUserFilesPath() + "dispatcher" + java.io.File.separator + "actions"
        if not os.path.exists(path):
            os.makedirs(path)
        return path + java.io.File.separator

    def get_list_of_actions(self):
        directory1 = self.action_directory_in_DispatcherSystem()
        files = os.listdir(directory1)
        # print "files in dispatcher system action directory", files

        python_files = [str(os.path.basename(f)) for f in files if f.endswith(".py")]
        # print "directory1", directory1, "python_files", python_files

        directory = self.action_directory()
        files = os.listdir(directory)
        python_files2 = [str(os.path.basename(f)) for f in files if f.endswith(".py")]

        python_files.extend(python_files2)
        return python_files

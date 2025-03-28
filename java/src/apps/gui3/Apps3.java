package apps.gui3;

import apps.*;
import apps.gui3.tabbedpreferences.TabbedPreferencesAction;
import apps.swing.AboutDialog;

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;

import java.awt.*;
import java.awt.event.AWTEventListener;
import java.awt.event.KeyEvent;
import java.io.*;
import java.util.EventObject;

import javax.swing.*;

import jmri.InstanceManager;
import jmri.jmrit.logixng.LogixNG_Manager;
import jmri.profile.*;
import jmri.util.*;
import jmri.util.swing.JmriJOptionPane;

/**
 * Base class for GUI3 JMRI applications.
 * <p>
 * This is a complete re-implementation of the apps.Apps support for JMRI
 * applications.
 * <p>
 * Each using application provides its own main() method.
 * <p>
 * There are a large number of missing features marked with TODO in comments
 * including code from the earlier implementation.
 *
 * @author Bob Jacobsen Copyright 2009, 2010
 */
public abstract class Apps3 extends AppsBase {

    /**
     * Initial actions before frame is created, invoked in the applications
     * main() routine.
     * <ul>
     * <li> Operations from {@link AppsBase#preInit(String)}
     * <li> Initialize the console support
     * </ul>
     *
     * @param applicationName application name
     */
    static public void preInit(String applicationName) {
        AppsBase.preInit(applicationName);

        // Initialise system console
        // Put this here rather than in apps.AppsBase as this is only relevant
        // for GUI applications - non-gui apps will use STDOUT & STDERR
        SystemConsole.getInstance();

        splash(true);

        setButtonSpace();

    }

    /**
     * Create and initialize the application object.
     * <p>
     * Expects initialization from preInit() to already be done.
     *
     * @param applicationName application name
     * @param configFileDef   default configuration file name
     * @param args            command line arguments set at application launch
     */
    public Apps3(String applicationName, String configFileDef, String[] args) {
        // pre-GUI work
        super(applicationName, configFileDef, args);

        // create GUI
        if (SystemType.isMacOSX()) {
            initMacOSXMenus();
        }
        if ( (((!configOK) || (!configDeferredLoadOK)) && (!preferenceFileExists)) || wizardLaunchCheck() ) {
            launchFirstTimeStartupWizard();
            return;
        }
        createAndDisplayFrame();
    }

    /**
     * To be overridden by applications that need to make
     * additional checks as to whether the first time wizard
     * should be launched.
     * @return true to force the wizard to be launched
     */
    protected boolean wizardLaunchCheck() {
        return false;
    }
    
    public void launchFirstTimeStartupWizard() {
        FirstTimeStartUpWizardAction prefsAction = new FirstTimeStartUpWizardAction("Start Up Wizard");
        prefsAction.setApp(this);
        prefsAction.actionPerformed(null);
    }
    
    /**
     * For compatability with adding in buttons to the toolbar using the
     * existing createbuttonmodel
     */
    @SuppressFBWarnings(value = "ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD",
            justification = "only one application at a time")
    protected static void setButtonSpace() {
        _buttonSpace = new JPanel();
        _buttonSpace.setLayout(new FlowLayout(FlowLayout.LEFT));
    }

    /**
     * Provide access to a place where applications can expect the configuration
     * code to build run-time buttons.
     *
     * @see apps.startup.CreateButtonModelFactory
     * @return null if no such space exists
     */
    static public JComponent buttonSpace() {
        return _buttonSpace;
    }
    static JComponent _buttonSpace = null;

    protected JmriJFrame mainFrame;

    abstract protected void createMainFrame();

    public void createAndDisplayFrame() {
        createMainFrame();

        //A Shutdown manager handles the quiting of the application
        mainFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
        displayMainFrame(mainFrame.getMaximumSize());
    }

    /**
     * Set a toolbar to be initially floating. This doesn't quite work right.
     *
     * @param toolBar the toolbar to float
     */
    protected void setFloating(JToolBar toolBar) {
        //((javax.swing.plaf.basic.BasicToolBarUI) toolBar.getUI()).setFloatingLocation(100,100);
        ((javax.swing.plaf.basic.BasicToolBarUI) toolBar.getUI()).setFloating(true, new Point(500, 500));
    }

    protected void displayMainFrame(Dimension d) {
        mainFrame.setSize(d);
        mainFrame.setVisible(true);
    }

    /**
     * Final actions before releasing control of app to user
     */
    @Override
    protected void start() {
        // TODO: splash(false);
        super.start();
        splash(false);
    }

    static protected void splash(boolean show) {
        splash(show, false);
    }

    static SplashWindow sp = null;
    static AWTEventListener debugListener = null;
    static boolean debugFired = false;
    static boolean debugmsg = false;

    static protected void splash(boolean show, boolean debug) {
        if (debugListener == null && debug) {
            // set a global listener for debug options
            debugFired = false;
            debugListener = new AWTEventListener() {

                @Override
                @SuppressFBWarnings(value = "ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD", justification = "debugmsg write is semi-global")
                public void eventDispatched(AWTEvent e) {
                    if (!debugFired) {
                        /*We set the debugmsg flag on the first instance of the user pressing any button
                         and the if the debugFired hasn't been set, this allows us to ensure that we don't
                         miss the user pressing F8, while we are checking*/
                        debugmsg = true;
                        if (e.getID() == KeyEvent.KEY_PRESSED && e instanceof KeyEvent && ((KeyEvent) e).getKeyCode() == 119) {     // F8
                            startupDebug();
                        } else if (e.getID() == KeyEvent.KEY_PRESSED && e instanceof KeyEvent && ((KeyEvent) e).getKeyCode() == 120) {  // F9
                            InstanceManager.getDefault(LogixNG_Manager.class).startLogixNGsOnLoad(false);
                        } else {
                            debugmsg = false;
                        }
                    }
                }
            };
            Toolkit.getDefaultToolkit().addAWTEventListener(debugListener,
                    AWTEvent.KEY_EVENT_MASK);
        }

        // bring up splash window for startup
        if (sp == null) {
            sp = new SplashWindow((debug) ? splashDebugMsg() : null);
        }
        sp.setVisible(show);
        if (!show) {
            sp.dispose();
            Toolkit.getDefaultToolkit().removeAWTEventListener(debugListener);
            debugListener = null;
            sp = null;
        }
    }

    static protected JPanel splashDebugMsg() {
        JLabel panelLabelDisableLogix = new JLabel(Bundle.getMessage("PressF8ToDebug"));
        panelLabelDisableLogix.setFont(panelLabelDisableLogix.getFont().deriveFont(9f));
        JLabel panelLabelDisableLogixNG = new JLabel(Bundle.getMessage("PressF9ToDisableLogixNG"));
        panelLabelDisableLogixNG.setFont(panelLabelDisableLogix.getFont().deriveFont(9f));
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.PAGE_AXIS));
        panel.add(panelLabelDisableLogix);
        panel.add(panelLabelDisableLogixNG);
        return panel;
    }

    static protected void startupDebug() {
        debugFired = true;
        debugmsg = true;

        debugmsg = false;
    }

    protected void initMacOSXMenus() {
        apps.plaf.macosx.Application macApp = apps.plaf.macosx.Application.getApplication();
        macApp.setAboutHandler((EventObject eo) -> {
            new AboutDialog(null, true).setVisible(true);
        });
        macApp.setPreferencesHandler((EventObject eo) -> {
            new TabbedPreferencesAction(Bundle.getMessage("MenuItemPreferences")).actionPerformed();
        });
        macApp.setQuitHandler((EventObject eo) -> handleQuit());
    }

    /**
     * Configure the {@link jmri.profile.Profile} to use for this application.
     * <p>
     * Overrides super() method so dialogs can be displayed.
     */
    @Override
    protected void configureProfile() {
        String profileFilename;
        FileUtil.createDirectory(FileUtil.getPreferencesPath());
        // Needs to be declared final as we might need to
        // refer to this on the Swing thread
        File profileFile;
        profileFilename = getConfigFileName().replaceFirst(".xml", ".properties");
        // decide whether name is absolute or relative
        if (!new File(profileFilename).isAbsolute()) {
            // must be relative, but we want it to
            // be relative to the preferences directory
            profileFile = new File(FileUtil.getPreferencesPath() + profileFilename);
        } else {
            profileFile = new File(profileFilename);
        }

        ProfileManager.getDefault().setConfigFile(profileFile);
        // See if the profile to use has been specified on the command line as
        // a system property org.jmri.profile as a profile id.
        if (System.getProperties().containsKey(ProfileManager.SYSTEM_PROPERTY)) {
            ProfileManager.getDefault().setActiveProfile(System.getProperty(ProfileManager.SYSTEM_PROPERTY));
        }
        // @see jmri.profile.ProfileManager#migrateToProfiles Javadoc for conditions handled here
        if (!profileFile.exists()) { // no profile config for this app
            log.trace("profileFile {} doesn't exist", profileFile);
            try {
                if (ProfileManager.getDefault().migrateToProfiles(getConfigFileName())) { // migration or first use
                    // notify user of change only if migration occurred
                    // TODO: a real migration message
                    JmriJOptionPane.showMessageDialog(sp,
                            Bundle.getMessage("ConfigMigratedToProfile"),
                            jmri.Application.getApplicationName(),
                            JmriJOptionPane.INFORMATION_MESSAGE);
                }
            } catch (IOException | IllegalArgumentException ex) {
                JmriJOptionPane.showMessageDialog(sp,
                        ex.getLocalizedMessage(),
                        jmri.Application.getApplicationName(),
                        JmriJOptionPane.ERROR_MESSAGE);
                log.error("Exception: ", ex);
            }
        }
        try {
            ProfileManagerDialog.getStartingProfile(sp);
            // Manually setting the configFilename property since calling
            // Apps.setConfigFilename() does not reset the system property
            System.setProperty("org.jmri.Apps.configFilename", Profile.CONFIG_FILENAME);
            Profile profile = ProfileManager.getDefault().getActiveProfile();
            if (profile != null) {
                log.info("Starting with profile {}", profile.getId());
            } else {
                log.info("Starting without a profile");
            }

            // rapid language set; must follow up later with full setting as part of preferences
            jmri.util.gui.GuiLafPreferencesManager.setLocaleMinimally(profile);
        } catch (IOException ex) {
            log.info("Profiles not configurable. Using fallback per-application configuration. Error: {}", ex.getMessage());
        }
    }

    @Override
    protected void setAndLoadPreferenceFile() {
        File sharedConfig = null;
        try {
            sharedConfig = FileUtil.getFile(FileUtil.PROFILE + Profile.SHARED_CONFIG);
            if (!sharedConfig.canRead()) {
                sharedConfig = null;
            }
        } catch (FileNotFoundException ex) {
            // ignore - this only means that sharedConfig does not exist.
        }
        super.setAndLoadPreferenceFile();
        if (sharedConfig == null && configOK == true && configDeferredLoadOK == true) {
            // this was logged in the super method
            String name = ProfileManager.getDefault().getActiveProfileName();
            if (!GraphicsEnvironment.isHeadless()) {
                JmriJOptionPane.showMessageDialog(sp,
                        Bundle.getMessage("SingleConfigMigratedToSharedConfig", name),
                        jmri.Application.getApplicationName(),
                        JmriJOptionPane.INFORMATION_MESSAGE);
            }
        }
    }

    private final static org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(Apps3.class);

}

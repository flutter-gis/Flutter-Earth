import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Particles 2.15 // Added for particle effects
import "./" // For ThemeProvider singleton registration

ApplicationWindow {
    id: appWindow
    visible: true
    width: 1200 // Increased default width
    height: 800 // Increased default height
    title: ThemeProvider.getCatchphrase("app_title", "Flutter Earth")
    color: ThemeProvider.getColor("background", "#FFFFFF") // Main background

    // Set window icon from theme
    // This needs to be done carefully, possibly from Python side if QRC path isn't direct.
    // For now, we assume ThemeProvider.paths.window_icon is a valid source.
    // Consider that ApplicationWindow.icon.source is not directly available.
    // One way is to use a helper C++ class or set it via backend.
    // Let's assume backend can set window icon.
    // Component.onCompleted: {
    //     backend.setWindowIcon(ThemeProvider.paths.window_icon);
    // }


    TopBar {
        id: topBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        z: 2
    }
    SideBar {
        id: sidebar
        anchors.top: topBar.bottom
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        z: 2
        onHomeClicked: mainContent.currentView = "HomeView"
        onMapClicked: mainContent.currentView = "MapView"
        onDownloadClicked: mainContent.currentView = "DownloadView"
        onProgressClicked: mainContent.currentView = "ProgressView"
        onSatelliteInfoClicked: mainContent.currentView = "SatelliteInfoView" // New
        onIndexAnalysisClicked: mainContent.currentView = "IndexAnalysisView" // New
        onVectorDownloadClicked: mainContent.currentView = "VectorDownloadView" // New
        onDataViewerClicked: mainContent.currentView = "DataViewerView"       // New
        onSettingsClicked: mainContent.currentView = "SettingsView"
        onAboutClicked: mainContent.currentView = "AboutView"
    }
    MainContent {
        id: mainContent
        anchors.top: topBar.bottom
        anchors.left: sidebar.right
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        z: 1
    }

    // --- Thematic Particle Effects ---
    ParticleSystem {
        id: magicSparklesSystem
        anchors.fill: parent
        visible: ThemeProvider.metadata.name === "Twilight Sparkle" && ThemeProvider.options.enable_animated_background
        z: 0 // Behind other content but above window background color

        ImageParticle {
            id: sparklePainter
            system: magicSparklesSystem
            source: "qrc:/assets/particles/sparkle.png" // Placeholder image
            color: ThemeProvider.getColor("accent", "#f8c5f8") // Use theme accent for sparkles
            colorVariation: 0.3
            alpha: 0 // Start invisible, fade in/out controlled by affectors
            entryEffect: ImageParticle.Fade
        }

        Emitter {
            id: sparkleEmitter
            system: magicSparklesSystem
            emitRate: 10 // Emit 10 particles per second
            lifeSpan: 2000 // Particles live for 2 seconds
            lifeSpanVariation: 500
            size: 8
            sizeVariation: 4
            velocity: PointDirection { x: 0; y: -20; xVariation: 10; yVariation: 10 } // Drift upwards slowly
            acceleration: PointDirection { y: 5 } // Slight downward pull for realism
            width: parent.width
            height: parent.height
        }

        Affector { // Fade in and out
            system: magicSparklesSystem
            once: false
            property real fadeInDuration: 500
            property real fadeOutDuration: 500
            property real stableDuration: 1000

            onAffected: (particle, dt) => {
                if (particle.lifeLeft < fadeOutDuration) {
                    particle.alpha = particle.lifeLeft / fadeOutDuration;
                } else if (particle.age < fadeInDuration) {
                    particle.alpha = particle.age / fadeInDuration;
                } else {
                    particle.alpha = 1.0;
                }
            }
        }
         Wander { // Gentle random movement
            system: magicSparklesSystem
            xVariance: 20
            yVariance: 20
            pace: 100 // Slower pace for gentle drift
        }
    }
    // --- End Thematic Particle Effects ---

    AuthDialog {
        id: authDialog
        visible: false
        onHelpRequested: helpPopup.open()
        onCredentialsEntered: function(keyFile, projectId) {
            backend.setAuthCredentials(keyFile, projectId)
            authDialog.visible = false
        }
    }
    HelpPopup { id: helpPopup }
    Component.onCompleted: {
        // Connect to the auth_missing signal from backend
        if (backend) {
            backend.auth_missing.connect(function() { 
                console.log("Authentication missing - showing dialog")
                authDialog.visible = true 
            })
            
            // Check if authentication is missing immediately
            if (!backend.isGeeInitialized()) {
                console.log("GEE not initialized - showing auth dialog immediately")
                authDialog.visible = true
            }
        }
    }
    Connections {
        target: backend
        function onThemeChanged(themeName, themeData) {
            ThemeProvider.updateThemeData();
            console.log("ThemeProvider: Theme changed to", themeName);
        }
    }
} 
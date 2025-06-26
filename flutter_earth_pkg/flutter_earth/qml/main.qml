import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Particles 2.15 // Added for particle effects
import QtQuick.Window 2.15
import QtQuick.Layouts 1.15
import "./" // For ThemeProvider singleton registration

ApplicationWindow {
    id: appWindow
    visible: true
    width: 1200
    height: 800
    title: ThemeProvider.getCatchphrase("app_title", "Flutter Earth")
    color: ThemeProvider.getColor("background", "#f0f0f0")

    // Current view to show in the main area
    property string currentView: "welcome"
    property string connectionStatus: "offline"
    property string statusBarColor: ThemeProvider.getColor("widget_bg", "#f0f0f0")
    property string statusBarText: "Initializing..."

    // Splash screen overlay
    SplashScreen {
        id: splashScreen
        anchors.fill: parent
        z: 10000
    }

    // Thematic Particle Effects (if any)
    ParticleSystem {
        id: magicSparklesSystem
        anchors.fill: parent
        visible: ThemeProvider.metadata.name === "Twilight Sparkle" && ThemeProvider.options.enable_animated_background
        z: 0

        ImageParticle {
            id: sparklePainter
            system: magicSparklesSystem
            source: "qrc:/assets/particles/sparkle.png"
            color: ThemeProvider.getColor("accent", "#f8c5f8")
            colorVariation: 0.3
            alpha: 0
            entryEffect: ImageParticle.Fade
        }

        Emitter {
            id: sparkleEmitter
            system: magicSparklesSystem
            emitRate: 10
            lifeSpan: 2000
            lifeSpanVariation: 500
            size: 8
            sizeVariation: 4
            velocity: PointDirection { x: 0; y: -20; xVariation: 10; yVariation: 10 }
            acceleration: PointDirection { y: 5 }
            width: parent.width
            height: parent.height
        }

        Affector {
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

        Wander {
            system: magicSparklesSystem
            xVariance: 20
            yVariance: 20
            pace: 100
        }
    }

    // Sidebar/tool bar
    SideBar {
        id: sidebar
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 240
        visible: true
        z: 3
        onHomeClicked: appWindow.currentView = "welcome"
        onMapClicked: appWindow.currentView = "map" // Placeholder, not used
        onDownloadClicked: appWindow.currentView = "download" // Placeholder, not used
        onProgressClicked: appWindow.currentView = "progress" // Placeholder, not used
        // onSatelliteInfoClicked: appWindow.currentView = "satelliteInfo" // Temporarily disabled
        onIndexAnalysisClicked: appWindow.currentView = "indexAnalysis"
        onVectorDownloadClicked: appWindow.currentView = "vectorDownload"
        onDataViewerClicked: appWindow.currentView = "dataViewer"
        onSettingsClicked: appWindow.currentView = "settings"
        onAboutClicked: appWindow.currentView = "about"
    }

    // TopBar - positioned above the main area
    TopBar {
        id: topBar
        anchors.top: parent.top
        anchors.left: sidebar.right
        anchors.right: parent.right
        z: 2
    }

    // Central main area - adjusted to account for TopBar
    Rectangle {
        id: mainArea
        anchors.top: topBar.bottom
        anchors.bottom: parent.bottom
        anchors.left: sidebar.right
        anchors.right: parent.right
        color: "transparent"
        z: 1
        Loader {
            id: mainLoader
            anchors.fill: parent
            sourceComponent: {
                if (appWindow.currentView === "settings") return settingsComponent;
                if (appWindow.currentView === "about") return aboutComponent;
                // if (appWindow.currentView === "satelliteInfo") return satelliteInfoComponent; // Temporarily disabled
                if (appWindow.currentView === "indexAnalysis") return indexAnalysisComponent;
                if (appWindow.currentView === "vectorDownload") return vectorDownloadComponent;
                if (appWindow.currentView === "dataViewer") return dataViewerComponent;
                if (appWindow.currentView === "download") return downloadComponent;
                // Add more as needed
                return welcomeComponent;
            }
        }
        // Welcome message component
        Component {
            id: welcomeComponent
            Rectangle {
                color: "transparent"
                anchors.fill: parent
                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 24
                    Image {
                        source: "qrc:/earth_logo.png"
                        width: 160; height: 160
                        fillMode: Image.PreserveAspectFit
                    }
                    Text {
                        text: ThemeProvider.getCatchphrase("app_title", "Welcome to Flutter Earth!")
                        font.pixelSize: 36
                        font.bold: true
                        color: ThemeProvider.getColor("primary", "#333")
                        horizontalAlignment: Text.AlignHCenter
                    }
                    Text {
                        text: "Select a tool from the sidebar to get started."
                        font.pixelSize: 20
                        color: ThemeProvider.getColor("text_subtle", "#666")
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }
        }
        // Settings component
        Component { id: settingsComponent; SettingsView { anchors.fill: parent } }
        Component { id: aboutComponent; AboutView { anchors.fill: parent } }
        // Component { id: satelliteInfoComponent; SatelliteInfoView { anchors.fill: parent } } // Temporarily disabled
        Component { id: indexAnalysisComponent; IndexAnalysisView { anchors.fill: parent } }
        Component { id: vectorDownloadComponent; VectorDownloadView { anchors.fill: parent } }
        Component { id: dataViewerComponent; DataViewerView { anchors.fill: parent } }
        Component { id: downloadComponent; DownloadView { anchors.fill: parent } }
    }

    // Auth dialog/modal logic remains as before
    AuthDialog {
        id: authDialog
        visible: false // Only show when authentication is missing
        onHelpRequested: helpPopup.open()
        onCredentialsEntered: function(keyFile, projectId) {
            backend.setAuthCredentials(keyFile, projectId)
            authDialog.visible = false
        }
    }

    Connections {
        target: backend
        function onAuth_missing() {
            console.log("AuthDialog signal received"); // DEBUG
            authDialog.visible = true
        }
    }

    HelpPopup { id: helpPopup }

    // Status bar at the bottom for connection status
    Rectangle {
        id: statusBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 28
        color: statusBarColor
        border.color: ThemeProvider.getColor("widget_border", "#e0e0e0")
        border.width: 1
        z: 10
        RowLayout {
            anchors.fill: parent
            anchors.margins: 8
            spacing: 12
            Item { Layout.fillWidth: true }
            Text {
                id: connectionStatusText
                text: "Status: " + statusBarText
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                font.bold: true
                color: connectionStatus === "online" ? ThemeProvider.getColor("success", "#388e3c") : ThemeProvider.getColor("error", "#b71c1c")
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    // Listen for theme changes and update ThemeProvider on the fly
    Connections {
        target: backend
        function onThemeChanged(themeName, themeData) {
            ThemeProvider.updateThemeData();
            console.log("ThemeProvider: Theme changed to", themeName);
        }
    }

    Connections {
        target: backend
        function onAuthSaved(message) {
            console.log("Auth saved message: " + message); // DEBUG
            savedPopup.text = message;
            savedPopup.open();
        }
    }

    Connections {
        target: backend
        function onConnectionStatusChanged(status) {
            connectionStatus = status;
            if (status === "online") {
                statusBarColor = ThemeProvider.getColor("success", "#d4ffd4");
                statusBarText = "Online";
            } else {
                statusBarColor = ThemeProvider.getColor("error", "#ffd4d4");
                statusBarText = "Offline";
            }
        }
    }

    Popup {
        id: savedPopup
        width: 300
        height: 60
        modal: false
        focus: false
        x: (parent ? parent.width : Screen.width) / 2 - width / 2
        y: 60
        property string text: ""
        background: Rectangle {
            color: ThemeProvider.getColor("notification_success_bg", ThemeProvider.getColor("accent", "#e0ffe0"))
            border.color: ThemeProvider.getColor("notification_success_border", ThemeProvider.getColor("accent", "#00cc00"))
            radius: 8
        }
        Column {
            anchors.centerIn: parent
            Text {
                text: savedPopup.text
                color: ThemeProvider.getColor("notification_success_text", ThemeProvider.getColor("text", "#222"))
                font.pixelSize: 18
            }
        }
        onOpened: {
            Qt.callLater(function() { savedPopup.close(); }, 2000);
        }
    }
} 
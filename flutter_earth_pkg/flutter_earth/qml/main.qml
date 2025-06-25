import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Particles 2.15 // Added for particle effects
import QtQuick.Window 2.15
import QtQuick.Layouts 1.15
import "./" // For ThemeProvider singleton registration

ApplicationWindow {
    id: appWindow
    visible: true
    width: 1400 // Increased default width for advanced features
    height: 900 // Increased default height for advanced features
    title: ThemeProvider.getCatchphrase("app_title", "Flutter Earth")
    color: ThemeProvider.getColor("background", "#FFFFFF") // Main background

    // Advanced GIS state
    property var advancedGISState: ({})
    property bool zenMode: false
    property var dockedPanels: ({})
    property var floatingPanels: ({})
    property string currentDisplayMode: "advancedMap" // "advancedMap" or "otherView"

    // Global search component
    GlobalSearch {
        id: globalSearch
        onOpenSettingsRequested: {
            console.log("GlobalSearch requested to open settings.")
            mainContent.currentView = "SettingsView.qml"
            appWindow.currentDisplayMode = "otherView"
            globalSearch.hide()
        }
        onOpenAddLayerDialogRequested: {
            console.log("GlobalSearch requested to open Add Layer dialog/panel.")
            // Placeholder: Actual mechanism to open 'Add Layer' UI would go here.
            // This might involve making a specific panel visible, or calling a backend function
            // that prepares data for an 'Add Layer' dialog.
            // For now, just logging and hiding search.
            // Example: if there's an AddLayerPanel.qml that can be loaded or made visible:
            // if (addLayerPanelLoader.source !== "AddLayerPanel.qml") addLayerPanelLoader.source = "AddLayerPanel.qml"
            // addLayerPanel.visible = true // or addLayerPanel.open()
            globalSearch.hide()
        }
    }

    // Keyboard shortcuts
    Shortcut {
        sequence: "Ctrl+Shift+P"
        onActivated: globalSearch.show()
    }

    Shortcut {
        sequence: "F11"
        onActivated: toggleZenMode()
    }

    Shortcut {
        sequence: "Ctrl+Shift+S"
        onActivated: saveWorkspaceDialog.open()
    }

    Shortcut {
        sequence: "Ctrl+Shift+L"
        onActivated: loadWorkspaceDialog.open()
    }

    // Main layout with dockable panels
    SplitView {
        id: mainSplitView
        anchors.fill: parent
        orientation: Qt.Horizontal
        // visible: !zenMode // Original
        visible: appWindow.currentDisplayMode === "advancedMap" && !zenMode

        // Left dock area
        SplitView {
            orientation: Qt.Vertical
            SplitView.minimumWidth: 200
            SplitView.maximumWidth: 400

            // Layer list panel
            Rectangle {
                id: layerListPanel
                SplitView.minimumHeight: 200
                SplitView.preferredHeight: 300
                // visible: (dockedPanels.layer_list && dockedPanels.layer_list.visible) || true // Original
                visible: dockedPanels.hasOwnProperty("layer_list") && dockedPanels.layer_list.visible
                
                color: ThemeProvider.getColor("widget_bg")
                border.color: ThemeProvider.getColor("widget_border")
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Panel header
                    Rectangle {
                        Layout.fillWidth: true
                        height: 30
                        color: ThemeProvider.getColor("primary")

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 5

                            Text {
                                text: qsTr("Layers")
                                color: ThemeProvider.getColor("text_on_primary")
                                font.family: ThemeProvider.getFont("body").family
                                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                                font.bold: true
                            }

                            Item { Layout.fillWidth: true }

                            Button {
                                text: "⛶"
                                width: 20
                                height: 20
                                onClicked: undockPanel("layer_list")
                            }
                        }
                    }

                    // Layer list content
                    Loader {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        source: "LayerListPanel.qml"
                    }
                }
            }

            // Toolbox panel
            Rectangle {
                id: toolboxPanel
                SplitView.minimumHeight: 150
                SplitView.preferredHeight: 250
                // visible: (dockedPanels.toolbox && dockedPanels.toolbox.visible) || true // Original
                visible: dockedPanels.hasOwnProperty("toolbox") && dockedPanels.toolbox.visible
                
                color: ThemeProvider.getColor("widget_bg")
                border.color: ThemeProvider.getColor("widget_border")
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Panel header
                    Rectangle {
                        Layout.fillWidth: true
                        height: 30
                        color: ThemeProvider.getColor("primary")

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 5

                            Text {
                                text: qsTr("Tools")
                                color: ThemeProvider.getColor("text_on_primary")
                                font.family: ThemeProvider.getFont("body").family
                                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                                font.bold: true
                            }

                            Item { Layout.fillWidth: true }

                            Button {
                                text: "⛶"
                                width: 20
                                height: 20
                                onClicked: undockPanel("toolbox")
                            }
                        }
                    }

                    // Toolbox content
                    Loader {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        source: "ToolboxPanel.qml"
                    }
                }
            }
        }

        // Center map area
        SplitView {
            orientation: Qt.Vertical
            SplitView.minimumWidth: 400

            // Top bar with search and controls
            TopBar {
                id: topBar
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                z: 2

                // Add global search button
                Button {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.margins: 10
                    text: "🔍"
                    ToolTip.visible: hovered
                    ToolTip.text: "Global Search (Ctrl+Shift+P)"
                    
                    onClicked: globalSearch.show()
                }
            }

            // Main map area
            AdvancedMapView {
                id: advancedMapView
                Layout.fillWidth: true
                Layout.fillHeight: true
                z: 1
            }
        }

        // Right dock area
        SplitView {
            orientation: Qt.Vertical
            SplitView.minimumWidth: 200
            SplitView.maximumWidth: 400

            // Bookmarks panel
            Rectangle {
                id: bookmarksPanel
                SplitView.minimumHeight: 150
                SplitView.preferredHeight: 200
                // visible: (dockedPanels.bookmarks && dockedPanels.bookmarks.visible) || true // Original
                visible: dockedPanels.hasOwnProperty("bookmarks") && dockedPanels.bookmarks.visible
                
                color: ThemeProvider.getColor("widget_bg")
                border.color: ThemeProvider.getColor("widget_border")
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Panel header
                    Rectangle {
                        Layout.fillWidth: true
                        height: 30
                        color: ThemeProvider.getColor("primary")

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 5

                            Text {
                                text: qsTr("Bookmarks")
                                color: ThemeProvider.getColor("text_on_primary")
                                font.family: ThemeProvider.getFont("body").family
                                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                                font.bold: true
                            }

                            Item { Layout.fillWidth: true }

                            Button {
                                text: "⛶"
                                width: 20
                                height: 20
                                onClicked: undockPanel("bookmarks")
                            }
                        }
                    }

                    // Bookmarks content
                    Loader {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        source: "BookmarksPanel.qml"
                    }
                }
            }

            // Attribute table panel
            Rectangle {
                id: attributeTablePanel
                SplitView.minimumHeight: 150
                SplitView.preferredHeight: 200
                // visible: (dockedPanels.attribute_table && dockedPanels.attribute_table.visible) || false // Original
                visible: dockedPanels.hasOwnProperty("attribute_table") && dockedPanels.attribute_table.visible
                
                color: ThemeProvider.getColor("widget_bg")
                border.color: ThemeProvider.getColor("widget_border")
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Panel header
                    Rectangle {
                        Layout.fillWidth: true
                        height: 30
                        color: ThemeProvider.getColor("primary")

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 5

                            Text {
                                text: qsTr("Attribute Table")
                                color: ThemeProvider.getColor("text_on_primary")
                                font.family: ThemeProvider.getFont("body").family
                                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                                font.bold: true
                            }

                            Item { Layout.fillWidth: true }

                            Button {
                                text: "⛶"
                                width: 20
                                height: 20
                                onClicked: undockPanel("attribute_table")
                            }
                        }
                    }

                    // Attribute table content
                    Loader {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        source: "AttributeTablePanel.qml"
                    }
                }
            }
        }
    }

    // Zen mode - full screen map
    AdvancedMapView {
        id: zenMapView
        anchors.fill: parent
        visible: zenMode
        z: 1
    }

    // Bottom status bar
    Rectangle {
        id: statusBar
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 25
        visible: !zenMode
        color: ThemeProvider.getColor("widget_bg")
        border.color: ThemeProvider.getColor("widget_border")
        border.width: 1

        RowLayout {
            anchors.fill: parent
            anchors.margins: 5
            spacing: 10

            // Coordinate display
            Text {
                id: coordinateDisplay
                text: "Lat: 0.000, Lon: 0.000"
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: 10
                color: ThemeProvider.getColor("text")
            }

            // Scale bar
            Text {
                id: scaleBar
                text: "Scale: 1:1000"
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: 10
                color: ThemeProvider.getColor("text")
            }

            Item { Layout.fillWidth: true }

            // Workspace controls
            Button {
                text: "Save Layout"
                onClicked: saveWorkspaceDialog.open()
            }

            Button {
                text: "Load Layout"
                onClicked: loadWorkspaceDialog.open()
            }

            Button {
                text: zenMode ? "Exit Zen" : "Zen Mode"
                onClicked: toggleZenMode()
            }
        }
    }

    // Side bar (simplified for advanced mode)
    SideBar {
        id: sidebar
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: statusBar.top
        width: 50
        visible: !zenMode
        z: 3
        onHomeClicked: {
            mainContent.currentView = "HomeView.qml"
            appWindow.currentDisplayMode = "otherView"
        }
        onMapClicked: {
            // mainContent.currentView = "MapView.qml" // MapView is part of AdvancedMapView in this context
            appWindow.currentDisplayMode = "advancedMap"
        }
        onDownloadClicked: {
            mainContent.currentView = "DownloadView.qml"
            appWindow.currentDisplayMode = "otherView"
        }
        onProgressClicked: {
            mainContent.currentView = "ProgressView.qml"
            appWindow.currentDisplayMode = "otherView"
        }
        onSatelliteInfoClicked: {
            mainContent.currentView = "SatelliteInfoView.qml"
            appWindow.currentDisplayMode = "otherView"
        }
        onIndexAnalysisClicked: {
            mainContent.currentView = "IndexAnalysisView.qml"
            appWindow.currentDisplayMode = "otherView"
        }
        onVectorDownloadClicked: {
            mainContent.currentView = "VectorDownloadView.qml"
            appWindow.currentDisplayMode = "otherView"
        }
        onDataViewerClicked: {
            mainContent.currentView = "DataViewerView.qml"
            appWindow.currentDisplayMode = "otherView"
        }
        onSettingsClicked: {
            mainContent.currentView = "SettingsView.qml"
            appWindow.currentDisplayMode = "otherView"
        }
        onAboutClicked: {
            mainContent.currentView = "AboutView.qml"
            appWindow.currentDisplayMode = "otherView"
        }
    }

    // Main content area (for non-map views)
    MainContent {
        id: mainContent
        // visible: false // Hidden in advanced mode, shown for other views // Original
        visible: appWindow.currentDisplayMode === "otherView" && !zenMode
        z: 1 // Ensure it's above zenMapView if active and currentDisplayMode changes
    }

    // --- Thematic Particle Effects ---
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

    // Dialogs
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

    // Workspace dialogs
    Dialog {
        id: saveWorkspaceDialog
        title: "Save Workspace Layout"
        width: 400
        height: 200
        modal: true

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            Label {
                text: "Layout Name:"
            }

            TextField {
                id: workspaceNameField
                Layout.fillWidth: true
                placeholderText: "Enter layout name"
            }

            Label {
                text: "Description:"
            }

            TextField {
                id: workspaceDescField
                Layout.fillWidth: true
                placeholderText: "Enter description"
            }

            RowLayout {
                Layout.fillWidth: true

                Item { Layout.fillWidth: true }

                Button {
                    text: "Save"
                    onClicked: {
                        backend.saveWorkspaceLayout(workspaceNameField.text, workspaceDescField.text)
                        saveWorkspaceDialog.close()
                    }
                }

                Button {
                    text: "Cancel"
                    onClicked: saveWorkspaceDialog.close()
                }
            }
        }
    }

    Dialog {
        id: loadWorkspaceDialog
        title: "Load Workspace Layout"
        width: 400
        height: 300
        modal: true

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            Label {
                text: "Select Layout:"
            }

            ListView {
                id: workspaceList
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: backend.getWorkspaceLayouts()

                delegate: Rectangle {
                    width: workspaceList.width
                    height: 60
                    color: index === workspaceList.currentIndex ? ThemeProvider.getColor("list_selected_bg") : ThemeProvider.getColor("list_bg")
                    border.color: ThemeProvider.getColor("widget_border")
                    border.width: 1
                    radius: 4

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 5

                        Text {
                            text: modelData.name
                            font.family: ThemeProvider.getFont("body").family
                            font.pixelSize: ThemeProvider.getFont("body").pixelSize
                            font.bold: true
                            color: ThemeProvider.getColor("text")
                        }

                        Text {
                            text: modelData.description
                            font.family: ThemeProvider.getFont("body").family
                            font.pixelSize: 10
                            color: ThemeProvider.getColor("text_subtle")
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            workspaceList.currentIndex = index
                        }
                        onDoubleClicked: {
                            backend.loadWorkspaceLayout(modelData.name)
                            loadWorkspaceDialog.close()
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true

                Item { Layout.fillWidth: true }

                Button {
                    text: "Load"
                    onClicked: {
                        if (workspaceList.currentIndex >= 0) {
                            var layout = backend.getWorkspaceLayouts()[workspaceList.currentIndex]
                            backend.loadWorkspaceLayout(layout.name)
                        }
                        loadWorkspaceDialog.close()
                    }
                }

                Button {
                    text: "Cancel"
                    onClicked: loadWorkspaceDialog.close()
                }
            }
        }
    }

    // Functions
    function toggleZenMode() {
        zenMode = !zenMode
        backend.toggleZenMode()
    }

    function undockPanel(panelType) {
        // Create floating panel
        var component = Qt.createComponent("DockablePanel.qml")
        if (component.status === Component.Ready) {
            var floatingPanel = component.createObject(appWindow, {
                "panelType": panelType
            })
            floatingPanel.showPanel()
        }
    }

    function updateAdvancedGISState() {
        advancedGISState = backend.getAdvancedGISState()
        zenMode = advancedGISState.zen_mode || false
        
        // Update panel visibility
        var panels = advancedGISState.panels || []
        dockedPanels = {}
        for (var i = 0; i < panels.length; i++) {
            var panel = panels[i]
            if (panel.docked && panel.visible) {
                dockedPanels[panel.panel_type] = panel
            }
        }
    }

    Component.onCompleted: {
        // Connect to the auth_missing signal from backend
        if (backend) {
            if (backend.auth_missing && backend.auth_missing.connect) {
                backend.auth_missing.connect(function() { 
                    console.log("Authentication missing - showing dialog")
                    authDialog.visible = true 
                })
            }
            // Check if authentication is missing immediately
            if (!backend.isGeeInitialized()) {
                console.log("GEE not initialized - showing auth dialog immediately")
                authDialog.visible = true
            }
            // Load advanced GIS state
            updateAdvancedGISState()
            // Connect to advanced GIS signals
            if (backend.onWorkspaceLayoutChanged && backend.onWorkspaceLayoutChanged.connect) {
                backend.onWorkspaceLayoutChanged.connect(function(layoutName) {
                    updateAdvancedGISState()
                })
            }
            if (backend.onPanelStateChanged && backend.onPanelStateChanged.connect) {
                backend.onPanelStateChanged.connect(function(panelType, state) {
                    updateAdvancedGISState()
                })
            }
        }
    }

    // Move Connections object here, outside of Component.onCompleted
    Connections {
        target: backend
        function onThemeChanged(themeName, themeData) {
            ThemeProvider.updateThemeData();
            console.log("ThemeProvider: Theme changed to", themeName);
        }
    }
} 
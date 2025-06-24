import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Fusion 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1600
    height: 900
    title: windowTitle
    color: windowBg

    // --- Palette ---
    property color windowBg: "#121212"
    property color sidebarBg: "#1E1E1E"
    property color contentBg: "#2A2A2A"
    property color contentBgLight: "#333333"
    property color primaryColor: "#4CAF50" // Green accent
    property color primaryColorHover: "#66BB6A"
    property color textColor: "#E0E0E0"
    property color secondaryTextColor: "#BDBDBD"
    property color borderColor: "#424242"
    property color errorColor: "#EF5350"
    
    // --- Properties ---
    property string windowTitle: "Flutter Earth"
    property string statusMessage: "Ready"
    property real overallProgress: 0.3
    property real monthlyProgress: 0.7
    property var currentTaskId: null

    // --- Reusable Components ---
    component StyledButton: Button {
        background: Rectangle {
            color: parent.hovered ? primaryColorHover : primaryColor
            radius: 6
            border.color: parent.hovered ? primaryColor : "transparent"
            border.width: 1
        }
        contentItem: Text {
            text: parent.text
            font: parent.font
            color: "#FFFFFF"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }

    component TabButton: Button {
        property bool active: false
        background: Rectangle {
            color: "transparent"
            Rectangle {
                width: parent.width
                height: 2
                color: active ? primaryColor : "transparent"
                anchors.bottom: parent.bottom
            }
        }
        contentItem: Text {
            text: parent.text
            font.pointSize: 10
            font.weight: active ? Font.Bold : Font.Normal
            color: active ? textColor : secondaryTextColor
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            topPadding: 10
            bottomPadding: 10
        }
    }

    component StyledTextField: TextField {
        background: Rectangle {
            color: contentBgLight
            border.color: parent.activeFocus ? primaryColor : borderColor
            border.width: 1
            radius: 4
        }
        padding: 8
        placeholderTextColor: secondaryTextColor
    }

    component StyledComboBox: ComboBox {
        background: Rectangle {
            color: contentBgLight
            border.color: parent.activeFocus ? primaryColor : borderColor
            border.width: 1
            radius: 4
        }
        indicator: Rectangle {
            width: 20
            height: 20
            anchors.right: parent.right
            anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            color: "transparent"
            Rectangle {
                width: 8
                height: 8
                anchors.centerIn: parent
                color: textColor
                rotation: 45
                Rectangle {
                    width: 8
                    height: 2
                    anchors.centerIn: parent
                    color: contentBgLight
                }
            }
        }
    }

    component StyledSpinBox: SpinBox {
        background: Rectangle {
            color: contentBgLight
            border.color: parent.activeFocus ? primaryColor : borderColor
            border.width: 1
            radius: 4
        }
    }

    component StyledProgressBar: ProgressBar {
        background: Rectangle {
            color: contentBgLight
            radius: 4
        }
        contentItem: Rectangle {
            color: primaryColor
            radius: 4
        }
    }

    component Card: Rectangle {
        property alias title: titleLabel.text
        property alias content: contentLoader.sourceComponent

        color: contentBg
        radius: 8
        border.color: borderColor
        border.width: 1
        Layout.fillWidth: true

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 15
            spacing: 15

            Label {
                id: titleLabel
                color: textColor
                font.pointSize: 12
                font.weight: Font.Bold
                bottomPadding: 5
            }
            Loader { id: contentLoader }
        }
    }

    // --- Main Layout ---
    Rectangle {
        id: mainContainer
        anchors.fill: parent
        color: sidebarBg
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 0
            
            // Header
            Label {
                text: "Flutter Earth"
                color: textColor
                font.pointSize: 22
                font.weight: Font.DemiBold
                Layout.alignment: Qt.AlignHCenter
                topPadding: 20
                bottomPadding: 20
            }

            // Tab buttons
            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 40
                spacing: 0
                
                TabButton {
                    text: "DOWNLOAD"
                    Layout.fillWidth: true
                    active: swipeView.currentIndex === 0
                    onClicked: swipeView.currentIndex = 0
                }
                TabButton {
                    text: "SATELLITE INFO"
                    Layout.fillWidth: true
                    active: swipeView.currentIndex === 1
                    onClicked: swipeView.currentIndex = 1
                }
                TabButton {
                    text: "POST-PROCESSING"
                    Layout.fillWidth: true
                    active: swipeView.currentIndex === 2
                    onClicked: swipeView.currentIndex = 2
                }
            }
            
            // Content area
            SwipeView {
                id: swipeView
                anchors.fill: parent
                currentIndex: 0
                
                background: Rectangle {
                    color: sidebarBg
                }

                // --- Download Tab ---
                Flickable {
                    contentWidth: 1; contentHeight: 1
                    clip: true
                    anchors.fill: parent
                    
                    GridLayout {
                        id: downloadGrid
                        columns: 2
                        rows: 1
                        anchors.fill: parent
                        columnSpacing: 20
                        rowSpacing: 0
                        
                        // --- Left Column: Settings ---
                        Item {
                            GridLayout.column: 0
                            GridLayout.row: 0
                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 20
                                Card {
                                    title: "Area & Time Settings"
                                    content: ColumnLayout {
                                        spacing: 15
                                        
                                        Label { text: "Area of Interest (BBOX)"; color: secondaryTextColor }
                                        StyledTextField { 
                                            id: aoiInput; 
                                            placeholderText: "minLon, minLat, maxLon, maxLat"
                                        }
                                        RowLayout {
                                            spacing: 10
                                            StyledButton { 
                                                text: "Select from Map"
                                                onClicked: handleSelectFromMap()
                                            }
                                            StyledButton { 
                                                text: "Load SHP"
                                                onClicked: handleLoadShapefile()
                                            }
                                        }
                                        
                                        RowLayout {
                                            spacing: 10
                                            ColumnLayout {
                                                Label { text: "Start Date"; color: secondaryTextColor }
                                                StyledTextField { 
                                                    id: startDate; 
                                                    placeholderText: "YYYY-MM-DD"
                                                }
                                            }
                                            ColumnLayout {
                                                Label { text: "End Date"; color: secondaryTextColor }
                                                StyledTextField { 
                                                    id: endDate; 
                                                    placeholderText: "YYYY-MM-DD" 
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                Card {
                                    title: "Processing Settings"
                                    content: ColumnLayout {
                                        spacing: 15
                                        
                                        Label { text: "Satellite"; color: secondaryTextColor }
                                        StyledComboBox { 
                                            id: satelliteCombo
                                            model: ["Landsat 8", "Sentinel-2", "MODIS"]
                                        }
                                        
                                        Label { text: "Max Cloud Cover (%)"; color: secondaryTextColor }
                                        StyledSpinBox { 
                                            id: cloudCoverSpin
                                            from: 0; to: 100; value: 20
                                        }
                                    }
                                }
                                
                                Card {
                                    title: "Output Settings"
                                    content: ColumnLayout {
                                        spacing: 15
                                        Label { text: "Output Format"; color: secondaryTextColor }
                                        StyledComboBox { 
                                            id: outputFormatCombo
                                            model: ["GeoTIFF", "NetCDF", "JPEG"]
                                        }
                                        Label { text: "Output Directory"; color: secondaryTextColor }
                                        RowLayout{
                                            StyledTextField { 
                                                id: outputDir; 
                                                placeholderText: "Select a directory..."
                                            }
                                            StyledButton { 
                                                text: "Browse" 
                                                onClicked: handleBrowseOutput()
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // --- Right Column: Status & Logs ---
                        Item {
                            GridLayout.column: 1
                            GridLayout.row: 0
                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 20
                                Card {
                                    title: "Progress"
                                    content: ColumnLayout {
                                        spacing: 12
                                        
                                        Label { text: "Overall Progress"; color: secondaryTextColor }
                                        StyledProgressBar {
                                            id: overallProgressBar
                                            value: overallProgress
                                        }
                                        
                                        Label { text: "Monthly Progress"; color: secondaryTextColor }
                                        StyledProgressBar {
                                            id: monthlyProgressBar
                                            value: monthlyProgress
                                        }
                                    }
                                }
                                
                                Card {
                                    title: "Log Console"
                                    content: TextArea {
                                        id: logConsole
                                        anchors.fill: parent
                                        text: "Ready to start download..."
                                        readOnly: true
                                        color: secondaryTextColor
                                        background: Rectangle { 
                                            color: contentBgLight 
                                            border.color: borderColor
                                            border.width: 1
                                            radius: 4
                                        }
                                        padding: 8
                                        font.pointSize: 9
                                    }
                                }
                            }
                        }
                    }
                }

                // --- Satellite Info Tab ---
                Rectangle { 
                    color: sidebarBg; 
                    anchors.fill: parent
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 20
                        Label { 
                            text: "Satellite Info View"; 
                            color: textColor
                        }
                    }
                }
                
                // --- Post-Processing Tab ---
                Rectangle { 
                    color: sidebarBg; 
                    anchors.fill: parent
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 20
                        Label { 
                            text: "Post-Processing View"; 
                            color: textColor
                        }
                    }
                }
            } // End of SwipeView

             // --- Controls ---
            Rectangle {
                color: contentBg
                Layout.fillWidth: true
                Layout.preferredHeight: 70
                
                RowLayout {
                    width: Math.min(parent.width - 40, 700)
                    anchors.centerIn: parent
                    spacing: 15

                    StyledButton { 
                        text: "Start Download"; 
                        Layout.fillWidth: true; 
                        Layout.preferredHeight: 40 
                        onClicked: handleStartDownload()
                    }
                    StyledButton { 
                        text: "Cancel"; 
                        Layout.fillWidth: true; 
                        Layout.preferredHeight: 40; 
                        background: Rectangle { 
                            color: parent.hovered? Qt.darker(errorColor) : errorColor; 
                            radius: 4 
                        }
                        onClicked: handleCancelDownload()
                    }
                }
            }
        }
    }

    // --- Status bar ---
    footer: Rectangle {
        height: 30
        color: contentBg
        border.color: borderColor
        border.width: 1

        Label {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 15
            text: statusMessage
            color: secondaryTextColor
        }
    }

    // Embedded Dialog Components
    Dialog {
        id: appDialog
        property string dialogType: "info"
        property string dialogTitle: ""
        property string dialogText: ""
        title: dialogTitle
        standardButtons: Dialog.Ok
        modal: true
        visible: false
        onAccepted: visible = false
        
        background: Rectangle {
            color: contentBg
            border.color: borderColor
            border.width: 1
            radius: 8
        }
        
        contentItem: Column {
            spacing: 10
            Label {
                text: appDialog.dialogText
                color: appDialog.dialogType === "error" ? errorColor : appDialog.dialogType === "warning" ? "#ffaa00" : textColor
                wrapMode: Text.Wrap
            }
        }
        function openDialog(type, title, text) {
            dialogType = type; dialogTitle = title; dialogText = text; visible = true;
        }
    }
    
    Dialog {
        id: inputDialog
        property string dialogType: "text"
        property string dialogTitle: ""
        property string dialogLabel: ""
        property string defaultValue: ""
        
        title: dialogTitle
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        visible: false
        
        signal inputProvided(string value)
        
        background: Rectangle {
            color: contentBg
            border.color: borderColor
            border.width: 1
            radius: 8
        }
        
        contentItem: ColumnLayout {
            spacing: 10
            
            Label {
                text: inputDialog.dialogLabel
                color: textColor
            }
            
            StyledTextField {
                id: inputField
                text: inputDialog.defaultValue
                echoMode: inputDialog.dialogType === "password" ? TextInput.Password : TextInput.Normal
                inputMethodHints: inputDialog.dialogType === "number" ? Qt.ImhFormattedNumbersOnly : Qt.ImhNone
            }
        }
        
        onAccepted: {
            inputProvided(inputField.text)
        }
        
        function openDialog(type, title, label, defaultVal) {
            dialogType = type
            dialogTitle = title
            dialogLabel = label
            defaultValue = defaultVal || ""
            inputField.text = defaultValue
            visible = true
        }
    }

    // --- Event Handlers ---
    function handleSelectFromMap() {
        logConsole.append("Select from map clicked")
        flutterEarth.log_message("Select from map clicked")
    }
    
    function handleLoadShapefile() {
        logConsole.append("Load shapefile clicked")
        flutterEarth.show_file_dialog("open", "Select Shapefile")
    }
    
    function handleBrowseOutput() {
        logConsole.append("Browse output directory clicked")
        flutterEarth.show_file_dialog("directory", "Select Output Directory")
    }
    
    function handleStartDownload() {
        logConsole.append("Starting download...");
        // Validate inputs
        if (!aoiInput.text || !startDate.text || !endDate.text || !outputDir.text) {
            appDialog.openDialog("error", "Validation Error", "Please fill in all required fields");
            return;
        }
        // Parse bbox
        let bboxParts = aoiInput.text.split(',').map(part => parseFloat(part.trim()));
        if (bboxParts.length !== 4 || bboxParts.some(isNaN)) {
            appDialog.openDialog("error", "Invalid BBOX", "Please enter valid coordinates: minLon, minLat, maxLon, maxLat");
            return;
        }
        // Create parameters
        let params = {
            bbox: {
                min_lon: bboxParts[0],
                min_lat: bboxParts[1],
                max_lon: bboxParts[2],
                max_lat: bboxParts[3]
            },
            start_date: startDate.text,
            end_date: endDate.text,
            satellite_collections: [satelliteCombo.currentText],
            output_format: outputFormatCombo.currentText,
            max_cloud_cover: cloudCoverSpin.value,
            output_directory: outputDir.text
        };
        try {
            currentTaskId = flutterEarth.start_download(params);
            logConsole.append("Download started with task ID: " + currentTaskId);
            statusMessage = "Download started...";
        } catch (error) {
            logConsole.append("Error starting download: " + error);
            appDialog.openDialog("error", "Download Error", "Failed to start download: " + error);
        }
    }
    
    function handleCancelDownload() {
        logConsole.append("Cancelling download...");
        if (currentTaskId) {
            let result = flutterEarth.cancel_download(currentTaskId);
            logConsole.append("Cancel requested for task ID: " + currentTaskId + ", result: " + result);
            statusMessage = "Download cancelled.";
        } else {
            logConsole.append("No active download to cancel.");
            statusMessage = "No active download to cancel.";
        }
    }

    // Connections to Python bridge
    Connections {
        target: flutterEarth
        
        function onShowMessage(type, title, text) {
            appDialog.openDialog(type, title, text);
        }
        
        function onUpdateStatusBar(message) {
            statusMessage = message;
        }
        
        function onUpdateProgress(progressType, value) {
            if (progressType === "overall") {
                overallProgress = value;
            } else if (progressType === "monthly") {
                monthlyProgress = value;
            }
        }
        
        function onUpdateWindowTitle(title) {
            windowTitle = title;
        }
        
        function onShowInputDialog(dialogType, title, defaultValue) {
            inputDialog.openDialog(dialogType, title, "Enter value:", defaultValue);
        }
        
        function onFileDialogResult(dialogType, selectedPath) {
            if (dialogType === "directory") {
                outputDir.text = selectedPath
                logConsole.append("Output directory selected: " + selectedPath)
            } else if (dialogType === "open") {
                // Handle shapefile selection
                logConsole.append("Shapefile selected: " + selectedPath)
                // TODO: Parse shapefile and extract coordinates
            }
        }
        
        function onInputDialogResult(dialogType, result) {
            logConsole.append("Input dialog result: " + result)
            // Handle input dialog results as needed
        }
    }
}
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import Qt.labs.platform 1.1
import "./" // For ThemeProvider

Rectangle {
    id: downloadView
    color: ThemeProvider.getColor("background", "#e3f2fd")
    anchors.fill: parent

    // Download parameters (bind to backend or user input)
    property var allSettings: backend.getAllSettings()
    property string aoi: "" // You can wire this to a map selection
    property string startDate: allSettings.start_date || "2022-01-01"
    property string endDate: allSettings.end_date || "2022-01-31"
    property string sensor: allSettings.sensor_priority ? allSettings.sensor_priority[0] : "LANDSAT_9"
    property string outputDir: allSettings.output_dir
    property bool cloudMask: allSettings.cloud_mask
    property real maxCloudCover: allSettings.max_cloud_cover

    property int progressCurrent: 0
    property int progressTotal: 1
    property string downloadStatus: ""
    property string downloadLog: ""

    Connections {
        target: backend
        function onDownloadProgressUpdated(current, total) {
            progressCurrent = current;
            progressTotal = total;
            downloadStatus = "Downloading: " + current + " / " + total;
        }
        function onDownloadErrorOccurred(userMsg, logMsg) {
            messageDialog.text = userMsg + "\n" + logMsg;
            messageDialog.open();
            downloadStatus = "Error: " + userMsg;
        }
        function onConfigChanged(newConfig) {
            allSettings = newConfig;
            outputDir = allSettings.output_dir;
            cloudMask = allSettings.cloud_mask;
            maxCloudCover = allSettings.max_cloud_cover;
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20

        Text {
            text: ThemeProvider.getCatchphrase("view_DownloadView", "Download Data")
            font.family: ThemeProvider.getFont("title").family
            font.pixelSize: ThemeProvider.getFont("title").pixelSize
            font.bold: ThemeProvider.getFont("title").bold
            color: ThemeProvider.getColor("primary", "#1565c0")
        }

        // AOI (Area of Interest) - for now, manual entry; can be wired to MapView
        RowLayout {
            spacing: 10
            Text {
                text: qsTr("AOI:")
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor("text", "#000000")
            }
            TextField {
                id: aoiField
                text: aoi
                placeholderText: "[minLon, minLat, maxLon, maxLat] or GeoJSON"
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey, "#000000")
                background: Rectangle {
                    color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey, "#FFFFFF")
                    border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey, "#8A8886")
                    radius: ThemeProvider.getStyle("text_input").radius || 2
                }
                onEditingFinished: aoi = text
                Layout.fillWidth: true // Allow it to take space
            }
        }

        // Other options
        RowLayout {
            spacing: 10
            CheckBox {
                id: overwriteBox
                text: qsTr("Overwrite Existing Files")
                checked: allSettings.overwrite_existing || false
                onCheckedChanged: backend.setSetting("overwrite_existing", checked)
                font: ThemeProvider.getFont("body")
                indicator.width: 18
                indicator.height: 18
            }
            CheckBox {
                id: cleanupTilesBox
                text: qsTr("Cleanup Intermediate Tiles")
                checked: allSettings.cleanup_tiles !== undefined ? allSettings.cleanup_tiles : true
                onCheckedChanged: backend.setSetting("cleanup_tiles", checked)
                Layout.leftMargin: 20
                font: ThemeProvider.getFont("body")
                indicator.width: 18
                indicator.height: 18
            }
        }

        // Dates
        RowLayout {
            spacing: 10
            Text { text: qsTr("Start Date:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
            TextField {
                id: startDateField
                text: startDate
                onEditingFinished: startDate = text
                Layout.preferredWidth: 120
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
            }
            Text { text: qsTr("End Date:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
            TextField {
                id: endDateField
                text: endDate
                onEditingFinished: endDate = text
                Layout.preferredWidth: 120
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
            }
        }

        // Sensor selection
        RowLayout {
            spacing: 10
            Text { text: qsTr("Sensor:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
            ComboBox {
                id: sensorCombo
                model: backend.getAllSensors()
                currentIndex: backend.getAllSensors().indexOf(sensor)
                onCurrentIndexChanged: { if (currentIndex >= 0) sensor = model[currentIndex]; }
                font: ThemeProvider.getFont("body")
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                popup.background: Rectangle { color: ThemeProvider.getColor("list_bg"); border.color: ThemeProvider.getColor("widget_border") }
            }
        }

        // Output directory
        RowLayout {
            spacing: 10
            Text { text: qsTr("Output Dir:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text")}
            TextField {
                id: outputDirField
                text: outputDir
                onEditingFinished: { outputDir = text; backend.setSetting("output_dir", text); }
                Layout.fillWidth: true
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
            }
            Button {
                id: browseOutputDirButton
                text: qsTr("Browse...")
                onClicked: outputDirDialog.open()
                font: ThemeProvider.getFont("button")
                background: Rectangle {
                    color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                    radius: ThemeProvider.getStyle("button_default").radius
                    border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                }
                contentItem: Text { text: parent.text; color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }
        }

        FileDialog {
            id: outputDirDialog
            title: "Select Output Directory"
            onAccepted: {
                var selectedPath = file.toString().replace(/^(file:\/{2,3})/, "");
                if (Qt.platform.os === "windows" && selectedPath.startsWith("/")) {
                    selectedPath = selectedPath.substring(1);
                }
                outputDirField.text = selectedPath;
                outputDir = selectedPath;
                backend.setSetting("output_dir", selectedPath);
            }
        }

        // Cloud mask and max cloud cover
        RowLayout {
            spacing: 10
            CheckBox {
                id: cloudMaskBox
                text: qsTr("Cloud Mask")
                checked: cloudMask
                onCheckedChanged: { cloudMask = checked; backend.setSetting("cloud_mask", checked); }
                font: ThemeProvider.getFont("body")
                indicator.width: 18; indicator.height: 18
            }
            Text { text: qsTr("Max Cloud Cover:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); Layout.leftMargin: 20 }
            SpinBox {
                id: maxCloudSpin
                value: maxCloudCover
                from: 0; to: 100; stepSize: 1
                onValueChanged: { maxCloudCover = value; backend.setSetting("max_cloud_cover", value); }
                Layout.preferredWidth: 80
                font: ThemeProvider.getFont("body")
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
            }
        }

        // Resolution settings
        RowLayout {
            spacing: 10
            CheckBox {
                id: useBestResolutionBox
                text: qsTr("Use Highest Resolution")
                checked: allSettings.use_best_resolution !== undefined ? allSettings.use_best_resolution : true
                onCheckedChanged: { targetResolutionSpin.enabled = !checked; backend.setSetting("use_best_resolution", checked); }
                font: ThemeProvider.getFont("body")
                indicator.width: 18; indicator.height: 18
            }
            Text { text: qsTr("Target Res (m):"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); Layout.leftMargin: 20 }
            SpinBox {
                id: targetResolutionSpin
                enabled: !useBestResolutionBox.checked
                value: allSettings.target_resolution || 30
                from: 1; to: 1000; stepSize: 1
                onValueChanged: { backend.setSetting("target_resolution", value); }
                Layout.preferredWidth: 80
                font: ThemeProvider.getFont("body")
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
            }
        }

        // Tiling settings
        RowLayout {
            spacing: 10
            Text { text: qsTr("Tiling Method:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
            ComboBox {
                id: tilingMethodCombo
                model: ["degree", "pixel"]
                currentIndex: model.indexOf(allSettings.tiling_method || "degree")
                onCurrentIndexChanged: {
                    if (currentIndex >= 0) {
                        backend.setSetting("tiling_method", model[currentIndex]);
                        numSubsectionsSpin.enabled = (model[currentIndex] === "pixel");
                    }
                }
                font: ThemeProvider.getFont("body")
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                popup.background: Rectangle { color: ThemeProvider.getColor("list_bg"); border.color: ThemeProvider.getColor("widget_border") }
            }
            Text { text: qsTr("Num Subsections:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); Layout.leftMargin: 20 }
            SpinBox {
                id: numSubsectionsSpin
                enabled: tilingMethodCombo.currentText === "pixel"
                value: allSettings.num_subsections || 100
                from: 1; to: 1000; stepSize: 1
                onValueChanged: { backend.setSetting("num_subsections", value); }
                Layout.preferredWidth: 80
                font: ThemeProvider.getFont("body")
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
            }
        }

        // Download buttons
        RowLayout {
            spacing: 10
            Button {
                id: startDownloadButton
                text: qsTr("Start Download")
                font: ThemeProvider.getFont("button")
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.button_primary.backgroundColorKey, ThemeProvider.colors.accent); radius: ThemeProvider.getStyle("button_primary").radius; border.color: ThemeProvider.getColor(ThemeProvider.styles.button_primary.borderColorKey, ThemeProvider.colors.accent) }
                contentItem: Text { text: parent.text; color: ThemeProvider.getColor(ThemeProvider.styles.button_primary.textColorKey, "white"); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                onClicked: {
                    if (aoiField.text.trim() === "") { messageDialog.text = "Area of Interest (AOI) cannot be empty."; messageDialog.open(); return; }
                    if (outputDirField.text.trim() === "") { messageDialog.text = "Output Directory cannot be empty."; messageDialog.open(); return; }
                    backend.startDownloadWithParams({
                        area_of_interest: aoiField.text,
                        start_date: startDateField.text,
                        end_date: endDateField.text,
                        sensor_name: sensorCombo.currentText,
                        output_dir: outputDirField.text,
                        cloud_mask: cloudMaskBox.checked,
                        max_cloud_cover: maxCloudSpin.value,
                        use_best_resolution: useBestResolutionBox.checked,
                        target_resolution: targetResolutionSpin.value,
                        tiling_method: tilingMethodCombo.currentText,
                        num_subsections: numSubsectionsSpin.value,
                        overwrite_existing: overwriteBox.checked,
                        cleanup_tiles: cleanupTilesBox.checked
                    });
                    downloadStatus = "Download started...";
                }
            }
            Button {
                id: cancelDownloadButton
                text: qsTr("Cancel Download")
                font: ThemeProvider.getFont("button")
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey); radius: ThemeProvider.getStyle("button_default").radius; border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey) }
                contentItem: Text { text: parent.text; color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                onClicked: { backend.cancelDownload(); downloadStatus = "Download cancelled."; }
            }
        }

        // Progress bar and status
        ProgressBar {
            id: downloadProgressBar
            value: progressTotal > 0 ? progressCurrent / progressTotal : 0.0
            Layout.fillWidth: true // Changed from fixed width
            background: Rectangle { color: ThemeProvider.getColor("progressbar_bg"); radius: 3 }
            contentItem: Rectangle {
                color: ThemeProvider.getColor("progressbar_fg")
                implicitWidth: downloadProgressBar.visualPosition * downloadProgressBar.width
                implicitHeight: downloadProgressBar.height
                radius: 3
            }
        }
        Text {
            id: downloadStatusText
            text: downloadStatus
            font: ThemeProvider.getFont("body")
            color: ThemeProvider.getColor("text_subtle")
        }

        // Download log/status area
        Rectangle {
            Layout.fillWidth: true; Layout.preferredHeight: 100
            color: ThemeProvider.getColor("entry_bg")
            radius: ThemeProvider.getStyle("text_input").radius || 3
            border.color: ThemeProvider.getColor("widget_border")
            border.width: 1
            ScrollView { // Added ScrollView for long logs
                anchors.fill: parent
                anchors.margins: 5
                clip: true
                TextArea { // Changed from Text to TextArea for potential edit/copy
                    id: downloadLogArea
                    readOnly: true
                    text: downloadLog.length > 0 ? downloadLog : qsTr("Waiting for download...")
                    font: ThemeProvider.getFont("monospace")
                    color: ThemeProvider.getColor("text")
                    background: Rectangle { color: "transparent" } // TextArea has its own bg
                    wrapMode: TextEdit.WordWrap
                }
            }
        }
    }

    Dialog {
        id: messageDialog
        title: ThemeProvider.getCatchphrase("dialog_title_info", "Download Info")
        modal: true
        standardButtons: Dialog.Ok
        width: 500
        height: 300

        property string text: ""

        ScrollView {
            anchors.fill: parent
            anchors.margins: 10
            Text {
                text: messageDialog.text
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor("text")
                wrapMode: Text.WordWrap
            }
        }
    }
}
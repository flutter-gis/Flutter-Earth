import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: downloadView
    // color: "#e3f2fd" // Replaced by theme
    anchors.fill: parent
    color: mainContent.currentTheme.widget_bg // Use theme color

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
            text: qsTr("Download Data")
            font.pointSize: 22
            font.bold: true
            color: mainContent.currentTheme.primary // Theme color
        }

        // AOI (Area of Interest) - for now, manual entry; can be wired to MapView
        RowLayout {
            spacing: 10
            Text { text: qsTr("AOI:"); font.pointSize: 16; color: mainContent.currentTheme.text }
            TextField {
                id: aoiField
                text: aoi
                placeholderText: "[minLon, minLat, maxLon, maxLat]"
                onEditingFinished: aoi = text
                width: 250
                color: mainContent.currentTheme.entry_fg
                background: Rectangle { color: mainContent.currentTheme.entry_bg; border.color: mainContent.currentTheme.entry_border }
            }
        }

        // Dates
        RowLayout {
            spacing: 10
            Text { text: qsTr("Start Date:"); font.pointSize: 16; color: mainContent.currentTheme.text }
            TextField {
                id: startDateField
                text: startDate
                onEditingFinished: startDate = text
                width: 120
                color: mainContent.currentTheme.entry_fg
                background: Rectangle { color: mainContent.currentTheme.entry_bg; border.color: mainContent.currentTheme.entry_border }
            }
            Text { text: qsTr("End Date:"); font.pointSize: 16; color: mainContent.currentTheme.text }
            TextField {
                id: endDateField
                text: endDate
                onEditingFinished: endDate = text
                width: 120
                color: mainContent.currentTheme.entry_fg
                background: Rectangle { color: mainContent.currentTheme.entry_bg; border.color: mainContent.currentTheme.entry_border }
            }
        }

        // Sensor selection
        RowLayout {
            spacing: 10
            Text { text: qsTr("Sensor:"); font.pointSize: 16; color: mainContent.currentTheme.text }
            ComboBox {
                id: sensorCombo
                model: backend.getAllSensors()
                currentIndex: backend.getAllSensors().indexOf(sensor)
                onCurrentIndexChanged: {
                    if (currentIndex >= 0)
                        sensor = model[currentIndex];
                }
                // Basic theming for ComboBox
                // background: Rectangle { color: mainContent.currentTheme.entry_bg; border.color: mainContent.currentTheme.entry_border }
                // contentItem: Text { text: control.displayText; color: mainContent.currentTheme.entry_fg }
            }
        }

        // Output directory
        RowLayout {
            spacing: 10
            Text { text: qsTr("Output Dir:"); font.pointSize: 16; color: mainContent.currentTheme.text }
            TextField {
                id: outputDirField
                text: outputDir
                onEditingFinished: outputDir = text
                width: 250
                color: mainContent.currentTheme.entry_fg
                background: Rectangle { color: mainContent.currentTheme.entry_bg; border.color: mainContent.currentTheme.entry_border }
            }
        }

        // Cloud mask and max cloud cover
        RowLayout {
            spacing: 10
            CheckBox {
                id: cloudMaskBox
                checked: cloudMask
                onCheckedChanged: cloudMask = checked
                // indicator: Rectangle { color: control.checked ? mainContent.currentTheme.primary : mainContent.currentTheme.disabled }
            }
            Text { text: qsTr("Cloud Mask"); font.pointSize: 16; color: mainContent.currentTheme.text }
            Text { text: qsTr("Max Cloud Cover:"); font.pointSize: 16; color: mainContent.currentTheme.text }
            SpinBox {
                id: maxCloudSpin
                value: maxCloudCover
                from: 0; to: 100; stepSize: 1
                onValueChanged: maxCloudCover = value
                width: 80
                // Basic theming
                // background: Rectangle { color: mainContent.currentTheme.entry_bg; border.color: mainContent.currentTheme.entry_border }
                // contentItem: Text { text: control.textFromValue(control.value, control.locale); color: mainContent.currentTheme.entry_fg }
            }
        }

        // Download buttons
        RowLayout {
            spacing: 10
            Button {
                text: qsTr("Start Download")
                onClicked: {
                    backend.startDownloadWithParams({
                        area_of_interest: JSON.parse(aoiField.text),
                        start_date: startDateField.text,
                        end_date: endDateField.text,
                        sensor_name: sensorCombo.currentText,
                        output_dir: outputDirField.text,
                        cloud_mask: cloudMaskBox.checked,
                        max_cloud_cover: maxCloudSpin.value
                    });
                    downloadStatus = "Download started...";
                }
            }
            Button {
                text: qsTr("Cancel Download")
                onClicked: {
                    backend.cancelDownload();
                    downloadStatus = "Download cancelled.";
                }
            }
        }

        // Progress bar and status
        ProgressBar {
            value: progressTotal > 0 ? progressCurrent / progressTotal : 0.0
            width: 300
            background: Rectangle { color: mainContent.currentTheme.progressbar_bg }
            contentItem: Item {
                Rectangle {
                    width: progressBar.visualPosition * progressBar.width
                    height: progressBar.height
                    color: mainContent.currentTheme.progressbar_fg
                }
            }
        }
        Text {
            text: downloadStatus
            color: mainContent.currentTheme.text_subtle // Theme color
            font.pointSize: 14
        }

        // Download log/status area
        Rectangle { // Consider replacing with TextArea for scrollability
            width: 400; height: 100
            color: mainContent.currentTheme.entry_bg // Theme color
            radius: 8
            border.color: mainContent.currentTheme.entry_border // Theme color
            border.width: 1
            Text {
                anchors.fill: parent
                anchors.margins: 5
                text: downloadLog.length > 0 ? downloadLog : qsTr("Waiting for download...")
                color: mainContent.currentTheme.text // Theme color
                font.pointSize: 12 // Smaller font for log
                wrapMode: Text.WordWrap
            }
        }
    }

    MessageDialog {
        id: messageDialog
        title: qsTr("Download Info")
        text: ""
        visible: false
        // Consider theming MessageDialog if possible, though it's often platform-styled
        onAccepted: visible = false
    }
} 
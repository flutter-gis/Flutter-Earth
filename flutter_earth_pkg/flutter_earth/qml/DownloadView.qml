import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: downloadView
    color: "#e3f2fd"
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
            text: qsTr("Download Data")
            font.pointSize: 22
            font.bold: true
            color: "#1565c0"
        }

        // AOI (Area of Interest) - for now, manual entry; can be wired to MapView
        RowLayout {
            spacing: 10
            Text { text: qsTr("AOI:"); font.pointSize: 16 }
            TextField {
                id: aoiField
                text: aoi
                placeholderText: "[minLon, minLat, maxLon, maxLat]"
                onEditingFinished: aoi = text
                width: 250
            }
        }

        // Dates
        RowLayout {
            spacing: 10
            Text { text: qsTr("Start Date:"); font.pointSize: 16 }
            TextField {
                id: startDateField
                text: startDate
                onEditingFinished: startDate = text
                width: 120
            }
            Text { text: qsTr("End Date:"); font.pointSize: 16 }
            TextField {
                id: endDateField
                text: endDate
                onEditingFinished: endDate = text
                width: 120
            }
        }

        // Sensor selection
        RowLayout {
            spacing: 10
            Text { text: qsTr("Sensor:"); font.pointSize: 16 }
            ComboBox {
                id: sensorCombo
                model: backend.getAllSensors()
                currentIndex: backend.getAllSensors().indexOf(sensor)
                onCurrentIndexChanged: {
                    if (currentIndex >= 0)
                        sensor = model[currentIndex];
                }
            }
        }

        // Output directory
        RowLayout {
            spacing: 10
            Text { text: qsTr("Output Dir:"); font.pointSize: 16 }
            TextField {
                id: outputDirField
                text: outputDir
                onEditingFinished: outputDir = text
                width: 250
            }
        }

        // Cloud mask and max cloud cover
        RowLayout {
            spacing: 10
            CheckBox {
                id: cloudMaskBox
                checked: cloudMask
                onCheckedChanged: cloudMask = checked
            }
            Text { text: qsTr("Cloud Mask"); font.pointSize: 16 }
            Text { text: qsTr("Max Cloud Cover:"); font.pointSize: 16 }
            SpinBox {
                id: maxCloudSpin
                value: maxCloudCover
                from: 0; to: 100; stepSize: 1
                onValueChanged: maxCloudCover = value
                width: 80
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
        }
        Text {
            text: downloadStatus
            color: "#1565c0"
            font.pointSize: 14
        }

        // Download log/status area
        Rectangle {
            width: 400; height: 100
            color: "#bbdefb"
            radius: 8
            border.color: "#1565c0"
            border.width: 1
            Text {
                anchors.centerIn: parent
                text: downloadLog.length > 0 ? downloadLog : qsTr("Waiting for download...")
                color: "#1565c0"
                font.pointSize: 14
            }
        }
    }

    MessageDialog {
        id: messageDialog
        title: qsTr("Download Info")
        text: ""
        visible: false
        onAccepted: visible = false
    }
} 
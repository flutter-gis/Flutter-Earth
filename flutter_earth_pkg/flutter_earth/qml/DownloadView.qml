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

    ScrollView {
        anchors.fill: parent
        anchors.margins: 0
        clip: true
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOn
        ScrollBar.vertical.policy: ScrollBar.AlwaysOn
        
        ColumnLayout {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 40
            width: parent.width - 80
            spacing: 0
            
            GridLayout {
                id: mainGrid
                anchors.horizontalCenter: parent.horizontalCenter
                columns: 2
                rowSpacing: 20
                columnSpacing: 20
                width: parent.width
                
                // AOI (spans both columns)
                GroupBox {
                    Layout.columnSpan: 2
                    Layout.fillWidth: true
                    Layout.minimumWidth: 350
                    title: "Area of Interest"
                    font: ThemeProvider.getFont("body")
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 8
                        Text {
                            text: "Enter coordinates or GeoJSON:"
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
                            Layout.fillWidth: true
                            Layout.preferredHeight: 40
                        }
                    }
                }

                // Date Range
                GroupBox {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 350
                    title: "Date Range"
                    font: ThemeProvider.getFont("body")
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 8
                        RowLayout {
                            spacing: 12
                            ColumnLayout {
                                spacing: 4
                                Text { text: qsTr("Start Date:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                                TextField {
                                    id: startDateField
                                    text: startDate
                                    onEditingFinished: startDate = text
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 35
                                    font: ThemeProvider.getFont("body")
                                    color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                                    background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                                }
                            }
                            ColumnLayout {
                                spacing: 4
                                Text { text: qsTr("End Date:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                                TextField {
                                    id: endDateField
                                    text: endDate
                                    onEditingFinished: endDate = text
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 35
                                    font: ThemeProvider.getFont("body")
                                    color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                                    background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                                }
                            }
                        }
                    }
                }

                // Sensor
                GroupBox {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 350
                    title: "Sensor"
                    font: ThemeProvider.getFont("body")
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 8
                        Text { text: qsTr("Select Sensor:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); }
                        ComboBox {
                            id: sensorCombo
                            model: backend.getAllSensors()
                            currentIndex: backend.getAllSensors().indexOf(sensor)
                            onCurrentIndexChanged: { if (currentIndex >= 0) sensor = model[currentIndex]; }
                            font: ThemeProvider.getFont("body")
                            Layout.fillWidth: true
                            Layout.preferredHeight: 35
                            background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                            popup.background: Rectangle { color: ThemeProvider.getColor("list_bg"); border.color: ThemeProvider.getColor("widget_border") }
                        }
                    }
                }

                // Output Directory
                GroupBox {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 350
                    title: "Output Directory"
                    font: ThemeProvider.getFont("body")
                    RowLayout {
                        anchors.fill: parent
                        spacing: 12
                        TextField {
                            id: outputDirField
                            text: outputDir
                            onEditingFinished: { outputDir = text; backend.setSetting("output_dir", text); }
                            Layout.fillWidth: true
                            Layout.preferredHeight: 35
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                            background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                        }
                        Button {
                            id: browseOutputDirButton
                            text: qsTr("Browse...")
                            onClicked: outputDirDialog.open()
                            font: ThemeProvider.getFont("button")
                            Layout.preferredHeight: 35
                            Layout.preferredWidth: 100
                            background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey); radius: ThemeProvider.getStyle("button_default").radius; border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey) }
                            contentItem: Text { text: parent.text; color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        }
                    }
                }

                // Cloud Settings
                GroupBox {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 350
                    title: "Cloud Settings"
                    font: ThemeProvider.getFont("body")
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 12
                        CheckBox {
                            id: cloudMaskBox
                            text: qsTr("Apply Cloud Mask")
                            checked: cloudMask
                            onCheckedChanged: { cloudMask = Boolean(checked); backend.setSetting("cloud_mask", Boolean(checked)); }
                            font: ThemeProvider.getFont("body")
                            indicator.width: 18; indicator.height: 18
                        }
                        RowLayout {
                            spacing: 12
                            Text { text: qsTr("Max Cloud Cover (%):"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); }
                            SpinBox {
                                id: maxCloudSpin
                                value: maxCloudCover
                                from: 0; to: 100; stepSize: 1
                                onValueChanged: { maxCloudCover = Number(value); backend.setSetting("max_cloud_cover", Number(value)); }
                                Layout.fillWidth: true
                                Layout.preferredHeight: 35
                                font: ThemeProvider.getFont("body")
                                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                            }
                        }
                    }
                }

                // Resolution Settings
                GroupBox {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 350
                    title: "Resolution Settings"
                    font: ThemeProvider.getFont("body")
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 12
                        CheckBox {
                            id: useBestResolutionBox
                            text: qsTr("Use Highest Resolution")
                            checked: allSettings.use_best_resolution !== undefined ? allSettings.use_best_resolution : true
                            onCheckedChanged: { targetResolutionSpin.enabled = Boolean(!checked); backend.setSetting("use_best_resolution", Boolean(checked)); }
                            font: ThemeProvider.getFont("body")
                            indicator.width: 18; indicator.height: 18
                        }
                        RowLayout {
                            spacing: 12
                            Text { text: qsTr("Target Res (m):"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); }
                            SpinBox {
                                id: targetResolutionSpin
                                enabled: !useBestResolutionBox.checked
                                value: allSettings.target_resolution || 30
                                from: 1; to: 1000; stepSize: 1
                                onValueChanged: { backend.setSetting("target_resolution", Number(value)); }
                                Layout.fillWidth: true
                                Layout.preferredHeight: 35
                                font: ThemeProvider.getFont("body")
                                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                            }
                        }
                    }
                }

                // Tiling Settings
                GroupBox {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 350
                    title: "Tiling Settings"
                    font: ThemeProvider.getFont("body")
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 12
                        RowLayout {
                            spacing: 12
                            Text { text: qsTr("Method:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); }
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
                                Layout.fillWidth: true
                                Layout.preferredHeight: 35
                                font: ThemeProvider.getFont("body")
                                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                                popup.background: Rectangle { color: ThemeProvider.getColor("list_bg"); border.color: ThemeProvider.getColor("widget_border") }
                            }
                        }
                        RowLayout {
                            spacing: 12
                            Text { text: qsTr("Subsections:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); }
                            SpinBox {
                                id: numSubsectionsSpin
                                enabled: tilingMethodCombo.currentText === "pixel"
                                value: allSettings.num_subsections || 100
                                from: 1; to: 1000; stepSize: 1
                                onValueChanged: { backend.setSetting("num_subsections", Number(value)); }
                                Layout.fillWidth: true
                                Layout.preferredHeight: 35
                                font: ThemeProvider.getFont("body")
                                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                            }
                        }
                    }
                }

                // Processing Options
                GroupBox {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 350
                    title: "Processing Options"
                    font: ThemeProvider.getFont("body")
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 12
                        CheckBox {
                            id: overwriteBox
                            text: qsTr("Overwrite Existing Files")
                            checked: allSettings.overwrite_existing || false
                            onCheckedChanged: backend.setSetting("overwrite_existing", Boolean(checked))
                            font: ThemeProvider.getFont("body")
                            indicator.width: 18
                            indicator.height: 18
                        }
                        CheckBox {
                            id: cleanupTilesBox
                            text: qsTr("Cleanup Intermediate Tiles")
                            checked: allSettings.cleanup_tiles !== undefined ? allSettings.cleanup_tiles : true
                            onCheckedChanged: backend.setSetting("cleanup_tiles", Boolean(checked))
                            font: ThemeProvider.getFont("body")
                            indicator.width: 18
                            indicator.height: 18
                        }
                    }
                }

                // Download Controls (spans both columns)
                GroupBox {
                    Layout.columnSpan: 2
                    Layout.fillWidth: true
                    Layout.minimumWidth: 350
                    title: "Download Controls"
                    font: ThemeProvider.getFont("body")
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 12
                        RowLayout {
                            spacing: 16
                            Button {
                                id: startDownloadButton
                                text: qsTr("Start Download")
                                font: ThemeProvider.getFont("button")
                                Layout.preferredHeight: 40
                                Layout.preferredWidth: 150
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
                                Layout.preferredHeight: 40
                                Layout.preferredWidth: 150
                                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey); radius: ThemeProvider.getStyle("button_default").radius; border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey) }
                                contentItem: Text { text: parent.text; color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                onClicked: { backend.cancelDownload(); downloadStatus = "Download cancelled."; }
                            }
                            Item { Layout.fillWidth: true }
                        }
                        ColumnLayout {
                            spacing: 8
                            ProgressBar {
                                id: downloadProgressBar
                                value: progressTotal > 0 ? progressCurrent / progressTotal : 0.0
                                Layout.fillWidth: true
                                Layout.preferredHeight: 20
                                background: Rectangle { color: ThemeProvider.getColor("progressbar_bg"); radius: 3 }
                                contentItem: Rectangle { color: ThemeProvider.getColor("progressbar_fg"); implicitWidth: downloadProgressBar.visualPosition * downloadProgressBar.width; implicitHeight: downloadProgressBar.height; radius: 3 }
                            }
                            Text { id: downloadStatusText; text: downloadStatus; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text_subtle") }
                        }
                    }
                }

                // Download log/status area (spans both columns)
                GroupBox {
                    Layout.columnSpan: 2
                    Layout.fillWidth: true
                    Layout.minimumWidth: 350
                    title: "Download Log"
                    font: ThemeProvider.getFont("body")
                    Layout.preferredHeight: 150
                    ScrollView {
                        anchors.fill: parent
                        clip: true
                        TextArea {
                            id: downloadLogArea
                            readOnly: true
                            text: downloadLog.length > 0 ? downloadLog : qsTr("Waiting for download...")
                            font: ThemeProvider.getFont("monospace")
                            color: ThemeProvider.getColor("text")
                            background: Rectangle { color: ThemeProvider.getColor("entry_bg"); border.color: ThemeProvider.getColor("widget_border"); border.width: 1; radius: ThemeProvider.getStyle("text_input").radius || 3 }
                            wrapMode: TextEdit.WordWrap
                        }
                    }
                }
            }
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

    MessageDialog {
        id: messageDialog
        title: ThemeProvider.getCatchphrase("dialog_title_info", "Download Info")
        text: messageDialog.text
    }
}
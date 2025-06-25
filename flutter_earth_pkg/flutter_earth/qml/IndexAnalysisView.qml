import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1
import "./" // For ThemeProvider
import Qt5Compat.GraphicalEffects

Rectangle {
    id: indexAnalysisView
    color: ThemeProvider.getColor("background", "white")
    anchors.fill: parent

    property var selectedFiles: []
    property var availableIndices: backend.getAvailableIndices()
    property var selectedIndices: []
    property string outputDir: backend.getSetting("output_dir") || ""
    property bool analysisRunning: false

    ScrollView {
        anchors.fill: parent
        anchors.margins: 20
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 20

            Label {
                text: ThemeProvider.getCatchphrase("view_IndexAnalysisView", "Index Analysis")
                font: ThemeProvider.getFont("title")
                color: ThemeProvider.getColor("primary")
                Layout.alignment: Qt.AlignHCenter
            }

            // Input Raster Selection
            GroupBox {
                title: "Input Raster Files"
                Layout.fillWidth: true
                font: ThemeProvider.getFont("body")

                ColumnLayout {
                    width: parent.width
                    spacing: 10

                    RowLayout {
                        Button {
                            text: "Add Raster Files..."
                            onClicked: rasterFileDialog.open()
                            font: ThemeProvider.getFont("button")
                            background: Rectangle {
                                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                                radius: ThemeProvider.getStyle("button_default").radius
                                border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                            }
                            contentItem: Text {
                                text: parent.text
                                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                        Button {
                            text: "Clear All"
                            onClicked: selectedFiles = []
                            enabled: selectedFiles.length > 0
                            font: ThemeProvider.getFont("button")
                            background: Rectangle {
                                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                                radius: ThemeProvider.getStyle("button_default").radius
                                border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                            }
                            contentItem: Text {
                                text: parent.text
                                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }

                    // File list
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 100
                        color: ThemeProvider.getColor("entry_bg")
                        border.color: ThemeProvider.getColor("widget_border")
                        radius: ThemeProvider.getStyle("text_input").radius || 3

                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 5
                            clip: true

                            ListView {
                                model: selectedFiles
                                delegate: RowLayout {
                                    width: parent.width
                                    Text {
                                        text: modelData
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text")
                                        Layout.fillWidth: true
                                    }
                                    Button {
                                        text: "Remove"
                                        onClicked: {
                                            var newFiles = selectedFiles.slice()
                                            newFiles.splice(index, 1)
                                            selectedFiles = newFiles
                                        }
                                        font: ThemeProvider.getFont("button")
                                        background: Rectangle {
                                            color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                                            radius: ThemeProvider.getStyle("button_default").radius
                                            border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                                        }
                                        contentItem: Text {
                                            text: parent.text
                                            color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Index Selection
            GroupBox {
                title: "Select Indices to Calculate"
                Layout.fillWidth: true
                font: ThemeProvider.getFont("body")

                ColumnLayout {
                    width: parent.width
                    spacing: 10

                    Repeater {
                        model: availableIndices // Iterate over the array of index objects
                        delegate: CheckBox {
                            // Use modelData.name (e.g., "NDVI") and modelData.full_name
                            text: modelData.name + (modelData.full_name ? " - " + modelData.full_name : "")
                            checked: selectedIndices.includes(modelData.name) // Check against the index name
                            onCheckedChanged: {
                                if (checked && !selectedIndices.includes(modelData.name)) {
                                    selectedIndices.push(modelData.name) // Store the index name
                                } else if (!checked) {
                                    var newSelectedIndices = selectedIndices.filter(i => i !== modelData.name)
                                    selectedIndices = newSelectedIndices
                                }
                                console.log("Selected indices:", JSON.stringify(selectedIndices))
                            }
                            font: ThemeProvider.getFont("body")
                            indicator.width: 18
                            indicator.height: 18
                        }
                    }
                }
            }

            // Band Mapping (simplified - assumes standard band order)
            GroupBox {
                title: "Band Mapping (Standard Order)"
                Layout.fillWidth: true
                font: ThemeProvider.getFont("body")

                ColumnLayout {
                    width: parent.width
                    spacing: 10

                    Text {
                        text: "For Landsat: Band 1=Blue, Band 2=Green, Band 3=Red, Band 4=NIR, Band 5=SWIR1, Band 6=SWIR2"
                        font: ThemeProvider.getFont("body")
                        color: ThemeProvider.getColor("text_subtle")
                        wrapMode: Text.WordWrap
                    }
                    Text {
                        text: "For Sentinel-2: Band 2=Blue, Band 3=Green, Band 4=Red, Band 8=NIR, Band 11=SWIR1, Band 12=SWIR2"
                        font: ThemeProvider.getFont("body")
                        color: ThemeProvider.getColor("text_subtle")
                        wrapMode: Text.WordWrap
                    }
                }
            }

            // Output Settings
            GroupBox {
                title: "Output Settings"
                Layout.fillWidth: true
                font: ThemeProvider.getFont("body")

                ColumnLayout {
                    width: parent.width
                    spacing: 10

                    RowLayout {
                        Text {
                            text: "Output Directory:"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                        }
                        TextField {
                            id: outputDirField
                            text: outputDir
                            onEditingFinished: outputDir = text
                            Layout.fillWidth: true
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                            background: Rectangle {
                                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey)
                                border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey)
                                radius: ThemeProvider.getStyle("text_input").radius
                            }
                        }
                        Button {
                            text: "Browse..."
                            onClicked: outputDirDialog.open()
                            font: ThemeProvider.getFont("button")
                            background: Rectangle {
                                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                                radius: ThemeProvider.getStyle("button_default").radius
                                border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                            }
                            contentItem: Text {
                                text: parent.text
                                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }
            }

            // Analysis Button
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter

                Button {
                    text: analysisRunning ? "Analysis Running..." : "Start Index Analysis"
                    enabled: selectedFiles.length > 0 && selectedIndices.length > 0 && outputDir !== "" && !analysisRunning
                    onClicked: startAnalysis()
                    font: ThemeProvider.getFont("button")
                    background: Rectangle {
                        color: enabled ? ThemeProvider.getColor(ThemeProvider.styles.button_primary.backgroundColorKey, ThemeProvider.colors.accent) : ThemeProvider.getColor("disabled")
                        radius: ThemeProvider.getStyle("button_primary").radius
                        border.color: enabled ? ThemeProvider.getColor(ThemeProvider.styles.button_primary.borderColorKey, ThemeProvider.colors.accent) : ThemeProvider.getColor("disabled")
                    }
                    contentItem: Text {
                        text: parent.text
                        color: enabled ? ThemeProvider.getColor(ThemeProvider.styles.button_primary.textColorKey, "white") : ThemeProvider.getColor("text_disabled")
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }

            // Status
            Text {
                id: statusText
                text: ""
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor("text_subtle")
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }

    // File dialogs
    FileDialog {
        id: rasterFileDialog
        title: "Select Raster Files"
        nameFilters: ["GeoTIFF files (*.tif *.tiff)", "All files (*)"]
        fileMode: FileDialog.OpenFiles
        onAccepted: {
            var newFiles = selectedFiles.slice()
            for (var i = 0; i < files.length; i++) {
                var filePath = files[i].toString().replace(/^(file:\/{2,3})/, "")
                if (Qt.platform.os === "windows" && filePath.startsWith("/")) {
                    filePath = filePath.substring(1)
                }
                if (!newFiles.includes(filePath)) {
                    newFiles.push(filePath)
                }
            }
            selectedFiles = newFiles
        }
    }

    FileDialog {
        id: outputDirDialog
        title: "Select Output Directory"
        folder: StandardPaths.standardLocations(StandardPaths.DocumentsLocation)[0]
        onAccepted: {
            var selectedPath = file.toString().replace(/^(file:\/{2,3})/, "")
            if (Qt.platform.os === "windows" && selectedPath.startsWith("/")) {
                selectedPath = selectedPath.substring(1)
            }
            outputDirField.text = selectedPath
            outputDir = selectedPath
        }
    }

    // Functions
    function startAnalysis() {
        if (selectedFiles.length === 0 || selectedIndices.length === 0 || outputDir === "") {
            statusText.text = "Please select files, indices, and output directory"
            return
        }

        analysisRunning = true
        statusText.text = "Starting analysis..."

        // Standard band mapping (simplified)
        var bandMap = {
            'red': 3,    // Band 3 for most sensors
            'nir': 4,    // Band 4 for most sensors
            'blue': 1,   // Band 1 for most sensors
            'green': 2,  // Band 2 for most sensors
            'swir1': 5,  // Band 5 for most sensors
            'swir2': 6   // Band 6 for most sensors
        }

        // Process each index
        for (var i = 0; i < selectedIndices.length; i++) {
            var indexType = selectedIndices[i]
            statusText.text = "Processing " + indexType + "..."
            
            var success = backend.startIndexAnalysis(selectedFiles, outputDir, indexType, bandMap)
            if (!success) {
                statusText.text = "Error processing " + indexType
                analysisRunning = false
                return
            }
        }

        statusText.text = "Analysis completed successfully!"
        analysisRunning = false
    }
}

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1
import "./" // For ThemeProvider singleton
import Qt5Compat.GraphicalEffects

Rectangle {
    id: vectorDownloadView
    color: ThemeProvider.getColor("background", "white")
    anchors.fill: parent

    property var dataSources: backend.getVectorDataSources()
    property var outputFormats: backend.getVectorOutputFormats()
    property string selectedDataSource: "Overpass API (OSM)"
    property string selectedOutputFormat: "GeoJSON"
    property string aoi: ""
    property string query: ""
    property string outputDir: backend.getSetting("output_dir") || ""
    property bool downloadRunning: false

    ScrollView {
        anchors.fill: parent
        anchors.margins: 20
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 20

        Label {
            text: ThemeProvider.getCatchphrase("view_VectorDownloadView", "Vector Data Download")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
        }

            // Data Source Selection
        GroupBox {
            title: "Data Source"
            Layout.fillWidth: true
                font: ThemeProvider.getFont("body")

            ColumnLayout {
                    width: parent.width
                    spacing: 10

                ComboBox {
                        id: dataSourceCombo
                        model: dataSources
                        textRole: "name"
                        currentIndex: 0
                        onCurrentIndexChanged: {
                            if (currentIndex >= 0) {
                                selectedDataSource = model[currentIndex].name
                                updateQueryPlaceholder()
                            }
                        }
                        font: ThemeProvider.getFont("body")
                        background: Rectangle {
                            color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey)
                            border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey)
                            radius: ThemeProvider.getStyle("text_input").radius
                        }
                        popup.background: Rectangle {
                            color: ThemeProvider.getColor("list_bg")
                            border.color: ThemeProvider.getColor("widget_border")
                        }
                    }

                    Text {
                        id: dataSourceDescription
                        text: dataSources[0] ? dataSources[0].description : ""
                        font: ThemeProvider.getFont("body")
                        color: ThemeProvider.getColor("text_subtle")
                        wrapMode: Text.WordWrap
                    }
                }
            }

            // Query Input
            GroupBox {
                title: "Query"
                Layout.fillWidth: true
                font: ThemeProvider.getFont("body")

                ColumnLayout {
                    width: parent.width
                    spacing: 10

                    TextArea {
                        id: queryArea
                        text: query
                        onTextChanged: query = text
                        placeholderText: "Enter Overpass query or URL..."
                        Layout.fillWidth: true
                        Layout.preferredHeight: 100
                        font: ThemeProvider.getFont("body")
                        color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                        background: Rectangle {
                            color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey)
                            border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey)
                            radius: ThemeProvider.getStyle("text_input").radius
                        }
                        wrapMode: TextEdit.Wrap
                    }

                    RowLayout {
                        Button {
                            text: "Load Example Query"
                            onClicked: loadExampleQuery()
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
                            text: "Clear Query"
                            onClicked: queryArea.text = ""
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

            // Area of Interest
        GroupBox {
            title: "Area of Interest (Optional)"
            Layout.fillWidth: true
                font: ThemeProvider.getFont("body")

            ColumnLayout {
                    width: parent.width
                    spacing: 10

                    RowLayout {
                        TextField {
                            id: aoiField
                            text: aoi
                            onEditingFinished: aoi = text
                            placeholderText: "minLon,minLat,maxLon,maxLat or GeoJSON Polygon"
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
                            text: "Select on Map"
                            onClicked: {
                                // This would integrate with MapView
                                var currentAOI = backend.getCurrentAOI()
                                if (currentAOI.length > 0) {
                                    aoiField.text = JSON.stringify(currentAOI)
                                    aoi = aoiField.text
                                }
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

                    Text {
                        text: "Leave empty to download data for the entire world (not recommended for large queries)"
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

                    RowLayout {
                        Text {
                            text: "Output Format:"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                        }
                ComboBox {
                            id: outputFormatCombo
                            model: outputFormats
                            currentIndex: 0
                            onCurrentIndexChanged: {
                                if (currentIndex >= 0) {
                                    selectedOutputFormat = model[currentIndex]
                                }
                            }
                            font: ThemeProvider.getFont("body")
                            background: Rectangle {
                                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey)
                                border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey)
                                radius: ThemeProvider.getStyle("text_input").radius
                            }
                            popup.background: Rectangle {
                                color: ThemeProvider.getColor("list_bg")
                                border.color: ThemeProvider.getColor("widget_border")
                            }
                        }
                    }
                }
            }

            // Download Button
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter

                Button {
                    text: downloadRunning ? "Downloading..." : "Start Vector Download"
                    enabled: query !== "" && outputDir !== "" && !downloadRunning
                    onClicked: startVectorDownload()
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
        id: outputDirDialog
        title: "Select Output Directory"
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
    function updateQueryPlaceholder() {
        if (selectedDataSource === "Overpass API (OSM)") {
            queryArea.placeholderText = "Enter Overpass QL query (e.g., [out:json]; node[\"amenity\"=\"school\"]({{bbox}}); out;)"
        } else if (selectedDataSource === "WFS") {
            queryArea.placeholderText = "Enter WFS service URL"
        } else if (selectedDataSource === "GeoJSON URL") {
            queryArea.placeholderText = "Enter direct GeoJSON file URL"
        }
    }

    function loadExampleQuery() {
        if (selectedDataSource === "Overpass API (OSM)") {
            queryArea.text = '[out:json];\nnode["amenity"="school"]({{bbox}});\nout;'
        } else if (selectedDataSource === "WFS") {
            queryArea.text = 'https://example.com/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=namespace:layer&outputFormat=application/json'
        } else if (selectedDataSource === "GeoJSON URL") {
            queryArea.text = 'https://example.com/data.geojson'
        }
    }

    function startVectorDownload() {
        if (query === "" || outputDir === "") {
            statusText.text = "Please enter a query and select output directory"
            return
        }

        downloadRunning = true
        statusText.text = "Starting vector download..."

        // Parse AOI if provided
        var aoiList = []
        if (aoi !== "") {
            try {
                if (aoi.startsWith("[")) {
                    aoiList = JSON.parse(aoi)
                } else {
                    aoiList = aoi.split(",").map(function(x) { return parseFloat(x.trim()) })
                }
            } catch (e) {
                statusText.text = "Invalid AOI format"
                downloadRunning = false
                return
            }
        }

        // Generate output filename
        var timestamp = new Date().toISOString().replace(/[:.]/g, "-")
        var outputPath = outputDir + "/vector_data_" + timestamp + "." + selectedOutputFormat.toLowerCase()

        var success = backend.startVectorDownload(aoiList, query, outputPath, selectedOutputFormat)
        if (success) {
            statusText.text = "Vector download completed successfully!"
        } else {
            statusText.text = "Vector download failed"
        }
        downloadRunning = false
    }

    Component.onCompleted: {
        updateQueryPlaceholder()
    }
}

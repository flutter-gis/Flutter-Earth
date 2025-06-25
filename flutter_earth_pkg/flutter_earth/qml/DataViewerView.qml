import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1
import "./" // For ThemeProvider
import Qt5Compat.GraphicalEffects

Rectangle {
    id: dataViewerView
    color: ThemeProvider.getColor("background", "white")
    anchors.fill: parent

    property var loadedRasterData: ({})
    property var loadedVectorData: ({})
    property string currentRasterFile: ""
    property string currentVectorFile: ""

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        Label {
            text: ThemeProvider.getCatchphrase("view_DataViewerView", "Data Viewer")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
        }

        // Data Loading Controls
        GroupBox {
            title: "Load Data"
            Layout.fillWidth: true
            font: ThemeProvider.getFont("body")

            RowLayout {
                Button {
                    text: "Load Raster..."
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
                    text: "Load Vector..."
                    onClicked: vectorFileDialog.open()
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
                    onClicked: {
                        loadedRasterData = {}
                        loadedVectorData = {}
                        currentRasterFile = ""
                        currentVectorFile = ""
                    }
                    enabled: currentRasterFile !== "" || currentVectorFile !== ""
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

        // Data Display Area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            border.color: ThemeProvider.getColor("widget_border")
            border.width: 1
            radius: ThemeProvider.getStyle("text_input").radius || 3
            color: ThemeProvider.getColor("entry_bg")

            ScrollView {
                anchors.fill: parent
                anchors.margins: 10
                clip: true

                ColumnLayout {
                    width: parent.width
                    spacing: 15

                    // Raster Data Information
                    GroupBox {
                        title: "Raster Data"
                        visible: currentRasterFile !== ""
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        ColumnLayout {
                            width: parent.width
                            spacing: 8

                            Text {
                                text: "File: " + currentRasterFile
                                font: ThemeProvider.getFont("body")
                                color: ThemeProvider.getColor("text")
                                wrapMode: Text.WordWrap
                            }

                            GridLayout {
                                columns: 2
                                columnSpacing: 20
                                rowSpacing: 5

                                Text { text: "Dimensions:"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                                Text { text: loadedRasterData.width ? loadedRasterData.width + " x " + loadedRasterData.height : "N/A"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }

                                Text { text: "Bands:"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                                Text { text: loadedRasterData.bands || "N/A"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }

                                Text { text: "CRS:"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                                Text { text: loadedRasterData.crs || "N/A"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); wrapMode: Text.WordWrap }

                                Text { text: "Data Type:"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                                Text { text: loadedRasterData.dtype || "N/A"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }

                                Text { text: "No Data Value:"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                                Text { text: loadedRasterData.nodata !== undefined ? loadedRasterData.nodata : "N/A"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                            }

                            // Bounds information
                            Text {
                                text: "Bounds: " + (loadedRasterData.bounds ? 
                                    "(" + loadedRasterData.bounds.left.toFixed(4) + ", " + 
                                    loadedRasterData.bounds.bottom.toFixed(4) + ") to (" + 
                                    loadedRasterData.bounds.right.toFixed(4) + ", " + 
                                    loadedRasterData.bounds.top.toFixed(4) + ")" : "N/A")
                                font: ThemeProvider.getFont("body")
                                color: ThemeProvider.getColor("text")
                                wrapMode: Text.WordWrap
                            }
                        }
                    }

                    // Vector Data Information
                    GroupBox {
                        title: "Vector Data"
                        visible: currentVectorFile !== ""
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        ColumnLayout {
                            width: parent.width
                            spacing: 8

                            Text {
                                text: "File: " + currentVectorFile
                                font: ThemeProvider.getFont("body")
                                color: ThemeProvider.getColor("text")
                                wrapMode: Text.WordWrap
                            }

                            GridLayout {
                                columns: 2
                                columnSpacing: 20
                                rowSpacing: 5

                                Text { text: "Features:"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                                Text { text: loadedVectorData.feature_count || "N/A"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }

                                Text { text: "Geometry Types:"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                                Text { text: loadedVectorData.geometry_types ? loadedVectorData.geometry_types.join(", ") : "N/A"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }

                                Text { text: "CRS:"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                                Text { text: loadedVectorData.crs || "N/A"; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); wrapMode: Text.WordWrap }
                            }

                            // Bounds information
                            Text {
                                text: "Bounds: " + (loadedVectorData.bounds ? 
                                    "(" + loadedVectorData.bounds[0].toFixed(4) + ", " + 
                                    loadedVectorData.bounds[1].toFixed(4) + ") to (" + 
                                    loadedVectorData.bounds[2].toFixed(4) + ", " + 
                                    loadedVectorData.bounds[3].toFixed(4) + ")" : "N/A")
                                font: ThemeProvider.getFont("body")
                                color: ThemeProvider.getColor("text")
                                wrapMode: Text.WordWrap
                            }

                            // Attribute columns
                            Text {
                                text: "Attributes: " + (loadedVectorData.columns ? loadedVectorData.columns.join(", ") : "N/A")
                                font: ThemeProvider.getFont("body")
                                color: ThemeProvider.getColor("text")
                                wrapMode: Text.WordWrap
                            }
                        }
                    }

                    // No data loaded message
                    Text {
                        text: "No data loaded. Use the buttons above to load raster or vector files."
                        visible: currentRasterFile === "" && currentVectorFile === ""
                        font: ThemeProvider.getFont("body")
                        color: ThemeProvider.getColor("text_subtle")
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }
        }
    }

    // File dialogs
    FileDialog {
        id: rasterFileDialog
        title: "Select Raster File"
        nameFilters: ["GeoTIFF files (*.tif *.tiff)", "All files (*)"]
        fileMode: FileDialog.OpenFile
        onAccepted: {
            var filePath = file.toString().replace(/^(file:\/{2,3})/, "")
            if (Qt.platform.os === "windows" && filePath.startsWith("/")) {
                filePath = filePath.substring(1)
            }
            currentRasterFile = filePath
            loadedRasterData = backend.loadRasterData(filePath)
        }
    }

    FileDialog {
        id: vectorFileDialog
        title: "Select Vector File"
        nameFilters: ["Vector files (*.geojson *.shp *.kml *.kmz)", "All files (*)"]
        fileMode: FileDialog.OpenFile
        onAccepted: {
            var filePath = file.toString().replace(/^(file:\/{2,3})/, "")
            if (Qt.platform.os === "windows" && filePath.startsWith("/")) {
                filePath = filePath.substring(1)
            }
            currentVectorFile = filePath
            loadedVectorData = backend.loadVectorData(filePath)
        }
    }
}

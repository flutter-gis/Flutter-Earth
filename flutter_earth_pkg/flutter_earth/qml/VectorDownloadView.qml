import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." // For ThemeProvider

Rectangle { // Changed from Item to Rectangle
    id: vectorDownloadView
    color: ThemeProvider.getColor("background", "white")
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10

        Label {
            text: ThemeProvider.getCatchphrase("view_VectorDownloadView", "Vector Data Download")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            text: "Functionality to download vector data (e.g., from Overpass API, WFS) will be implemented here."
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        // Placeholder for data source
        GroupBox {
            title: "Data Source"
            Layout.fillWidth: true
            ColumnLayout {
                ComboBox {
                    model: ["Overpass API (OSM)", "WFS", "GeoJSON URL"]
                }
                TextField { placeholderText: "Source URL or Overpass Query..."}
            }
        }

        // Placeholder for AOI
        GroupBox {
            title: "Area of Interest (Optional)"
            Layout.fillWidth: true
            ColumnLayout {
                TextField { placeholderText: "minLon,minLat,maxLon,maxLat or GeoJSON Polygon"}
                Button { text: "Select on Map" }
            }
        }

        // Placeholder for output settings
        GroupBox {
            title: "Output Settings"
            Layout.fillWidth: true
            ColumnLayout {
                TextField { placeholderText: "Output directory..." }
                Button { text: "Browse..." }
                ComboBox {
                    model: ["GeoJSON", "Shapefile", "KML"]
                    textRole: "" // Added to avoid potential warning if model items are not strings
                }
            }
        }

        Button {
            text: "Start Vector Download"
            Layout.alignment: Qt.AlignRight
            // onClicked: backend.startVectorDownload(...)
        }
    }
}

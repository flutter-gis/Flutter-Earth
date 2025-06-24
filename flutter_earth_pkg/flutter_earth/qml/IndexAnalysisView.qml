import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." // For ThemeProvider

Rectangle { // Changed from Item to Rectangle for background color
    id: indexAnalysisView
    color: ThemeProvider.getColor("background", "white")
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10

        Label {
            text: ThemeProvider.getCatchphrase("view_IndexAnalysisView", "Index Analysis")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            text: "Functionality to perform vegetation and other index analyses will be implemented here."
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        // Placeholder for input raster selection
        GroupBox {
            title: "Input Rasters"
            Layout.fillWidth: true
            ColumnLayout {
                Label { text: "Select input raster files..." }
                Button { text: "Add Raster(s)" }
            }
        }

        // Placeholder for index selection
        GroupBox {
            title: "Select Indices"
            Layout.fillWidth: true
            ColumnLayout {
                CheckBox { text: "NDVI" }
                CheckBox { text: "NDWI" }
                CheckBox { text: "SAVI" }
            }
        }

        // Placeholder for output settings
        GroupBox {
            title: "Output Settings"
            Layout.fillWidth: true
            ColumnLayout {
                TextField { placeholderText: "Output directory..." }
                Button { text: "Browse..." }
            }
        }

        Button {
            text: "Start Index Analysis"
            Layout.alignment: Qt.AlignRight
            // onClicked: backend.startIndexAnalysis(...)
        }
    }
}

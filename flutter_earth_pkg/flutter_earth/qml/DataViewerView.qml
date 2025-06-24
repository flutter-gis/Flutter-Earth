import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." // For ThemeProvider

Rectangle { // Changed from Item to Rectangle
    id: dataViewerView
    color: ThemeProvider.getColor("background", "white")
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10

        Label {
            text: ThemeProvider.getCatchphrase("view_DataViewerView", "Data Viewer")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            text: "Functionality to view raster and vector data will be implemented here. This might involve Matplotlib integration or a QML-native canvas."
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        // Placeholder for data loading controls
        GroupBox {
            title: "Load Data"
            Layout.fillWidth: true
            RowLayout {
                Button { text: "Load Raster..." }
                Button { text: "Load Vector..." }
            }
        }

        // Placeholder for the map/plot display area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            border.color: "gray"
            color: "lightgray"
            Label {
                text: "Data Display Area"
                anchors.centerIn: parent
            }
        }

        // Placeholder for layer controls or info
        GroupBox {
            title: "Layer Information"
            Layout.fillWidth: true
            Label { text: "Details about loaded layers..." }
        }
    }
}

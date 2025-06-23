import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." as App

Rectangle {
    id: sideBar
    width: 60
    color: App.Style.panelBackground
    Layout.fillHeight: true

    signal processingClicked()
    signal satelliteInfoClicked()
    signal vectorImportClicked()
    signal postProcessingClicked()
    signal appSettingsClicked()

    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        anchors.topMargin: 10

        // --- Navigation Buttons ---
        Button {
            text: "⚙️"
            font.pixelSize: 24
            Layout.alignment: Qt.AlignHCenter
            onClicked: sideBar.processingClicked()
            ToolTip.text: "Processing Settings"
            ToolTip.visible: parent.hovered
            background: Rectangle { color: "transparent" }
            contentItem: Text {
                text: parent.text
                color: App.Style.text
            }
        }

        Button {
            text: "🛰️"
            font.pixelSize: 24
            Layout.alignment: Qt.AlignHCenter
            onClicked: sideBar.satelliteInfoClicked()
            ToolTip.text: "Satellite Information"
            ToolTip.visible: parent.hovered
            background: Rectangle { color: "transparent" }
            contentItem: Text {
                text: parent.text
                color: App.Style.text
            }
        }

        Button {
            text: "🗺️"
            font.pixelSize: 24
            Layout.alignment: Qt.AlignHCenter
            onClicked: sideBar.vectorImportClicked()
            ToolTip.text: "Vector Import"
            ToolTip.visible: parent.hovered
            background: Rectangle { color: "transparent" }
            contentItem: Text {
                text: parent.text
                color: App.Style.text
            }
        }

        Button {
            text: "📊"
            font.pixelSize: 24
            Layout.alignment: Qt.AlignHCenter
            onClicked: sideBar.postProcessingClicked()
            ToolTip.text: "Post-Processing"
            ToolTip.visible: parent.hovered
            background: Rectangle { color: "transparent" }
            contentItem: Text {
                text: parent.text
                color: App.Style.text
            }
        }

        // Spacer
        Item { Layout.fillHeight: true }

        // --- App Settings Button ---
        Button {
            text: "🔧"
            font.pixelSize: 24
            Layout.alignment: Qt.AlignHCenter
            ToolTip.text: "Application Settings"
            ToolTip.visible: parent.hovered
            onClicked: sideBar.appSettingsClicked()
            background: Rectangle { color: "transparent" }
            contentItem: Text {
                text: parent.text
                color: App.Style.text
            }
        }
    }
} 
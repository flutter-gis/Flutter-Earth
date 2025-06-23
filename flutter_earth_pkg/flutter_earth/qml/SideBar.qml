import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: sidebar
    color: "#fce4ec"
    width: 160
    anchors.top: parent.top
    anchors.bottom: parent.bottom
    anchors.left: parent.left
    z: 2

    signal homeClicked()
    signal mapClicked()
    signal downloadClicked()
    signal progressClicked()
    signal settingsClicked()
    signal aboutClicked()

    Column {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20
        Repeater {
            model: [
                { label: qsTr("Home"), signal: "homeClicked" },
                { label: qsTr("Map"), signal: "mapClicked" },
                { label: qsTr("Download"), signal: "downloadClicked" },
                { label: qsTr("Progress"), signal: "progressClicked" },
                { label: qsTr("Settings"), signal: "settingsClicked" },
                { label: qsTr("About"), signal: "aboutClicked" }
            ]
            delegate: Rectangle {
                width: parent.width
                height: 48
                radius: 12
                property bool pressed: false
                property bool hovered: false
                color: pressed ? "#f06292" : hovered ? "#f8bbd0" : "white"
                border.color: "#e91e63"
                border.width: 2
                scale: pressed ? 1.13 : hovered ? 1.07 : 1.0
                Behavior on scale { NumberAnimation { duration: 160; easing.type: Easing.OutElastic } }
                Behavior on color { ColorAnimation { duration: 120 } }
                Rectangle {
                    anchors.fill: parent
                    color: "#e91e63"
                    opacity: pressed ? 0.12 : hovered ? 0.07 : 0
                    radius: 12
                    z: 1
                    Behavior on opacity { NumberAnimation { duration: 120 } }
                }
                Text {
                    anchors.centerIn: parent
                    text: modelData.label
                    font.pointSize: 16
                    font.bold: true
                    color: "#880e4f"
                    z: 2
                }
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onPressed: parent.pressed = true
                    onReleased: {
                        parent.pressed = false
                        sidebar[modelData.signal]()
                    }
                    onCanceled: parent.pressed = false
                    onEntered: parent.hovered = true
                    onExited: parent.hovered = false
                }
            }
        }
    }
} 
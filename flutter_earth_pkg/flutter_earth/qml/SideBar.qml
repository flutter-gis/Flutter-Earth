import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: sidebar
    // color: "#fce4ec" // Replaced by theme
    width: 160
    anchors.top: parent.top
    anchors.bottom: parent.bottom
    anchors.left: parent.left
    z: 2

    property color bgColor: "lightgrey"
    property color itemDefaultColor: "white"
    property color itemHoverColor: "lightsteelblue"
    property color itemPressColor: "steelblue"
    property color itemBorderColor: "grey"
    property color itemTextColor: "black"

    color: bgColor

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
                { label: qsTr("Home"), signalName: "homeClicked" },      // Changed 'signal' to 'signalName' for clarity
                { label: qsTr("Map"), signalName: "mapClicked" },
                { label: qsTr("Download"), signalName: "downloadClicked" },
                { label: qsTr("Progress"), signalName: "progressClicked" },
                { label: qsTr("Settings"), signalName: "settingsClicked" },
                { label: qsTr("About"), signalName: "aboutClicked" }
            ]
            delegate: Rectangle {
                width: parent.width
                height: 48
                radius: 12
                property bool pressed: false
                property bool hovered: false

                color: pressed ? sidebar.itemPressColor : hovered ? sidebar.itemHoverColor : sidebar.itemDefaultColor
                border.color: sidebar.itemBorderColor
                border.width: 1 // Reduced border width for a cleaner look

                scale: pressed ? 1.05 : hovered ? 1.02 : 1.0 // Subtle scale
                Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.InOutQuad } }
                Behavior on color { ColorAnimation { duration: 90 } }

                // Removed inner rectangle for opacity, relying on direct color change

                Text {
                    anchors.centerIn: parent
                    text: modelData.label
                    font.pointSize: 16
                    font.bold: true
                    color: sidebar.itemTextColor
                    z: 2
                }
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onPressed: parent.pressed = true
                    onReleased: {
                        parent.pressed = false
                        sidebar[modelData.signalName]() // Corrected to use signalName
                    }
                    onCanceled: parent.pressed = false
                    onEntered: parent.hovered = true
                    onExited: parent.hovered = false
                }
            }
        }
    }
} 
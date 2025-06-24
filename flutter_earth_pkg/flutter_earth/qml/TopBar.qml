import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: topBar
    // color: "#f8bbd0" // Replaced by theme
    height: 50
    // width: parent.width // Implicit from anchors
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    z: 2

    property color barColor: "pink" // Default, will be overridden by main.qml
    property color textColor: "black" // Default, will be overridden by main.qml

    color: barColor // Use the property

    Row {
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 20 // Add some margin
        spacing: 20
        Text {
            text: qsTr("Flutter Earth")
            font.bold: true
            font.pointSize: 18
            color: textColor // Use the property
        }
    }
} 
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: topBar
    color: "#f8bbd0"
    height: 50
    width: parent.width
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    z: 2

    Row {
        anchors.verticalCenter: parent.verticalCenter
        spacing: 20
        Text {
            text: qsTr("Flutter Earth")
            font.bold: true
            font.pointSize: 18
            color: "#880e4f"
        }
    }
} 
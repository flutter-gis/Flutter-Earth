import QtQuick 2.15
import QtQuick.Controls 2.15
import "." // Assuming ThemeProvider.qml is in the same directory

Rectangle {
    id: topBar
    color: ThemeProvider.getColor("primary", "#f8bbd0") // Use theme's primary color
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
            text: qsTr("Flutter Earth") // Could be replaced by ThemeProvider.catchphrases.app_title later
            font.family: ThemeProvider.getFont("title").family
            font.pixelSize: ThemeProvider.getFont("title").pixelSize
            font.bold: ThemeProvider.getFont("title").bold
            color: ThemeProvider.getColor("text_on_primary", "#FFFFFF") // Assuming a text_on_primary color
            anchors.leftMargin: 10
        }
    }
} 
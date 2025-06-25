import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt5Compat.GraphicalEffects
import "./" // For ThemeProvider singleton

Rectangle {
    id: topBar
    color: ThemeProvider.getColor("primary", "#f8bbd0")
    height: 54
    width: parent.width
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    z: 2
    radius: 0
    layer.enabled: true
    layer.effect: DropShadow {
        color: ThemeProvider.getColor("primary"); radius: 10; samples: 16; x: 0; y: 2; spread: 0.08
    }
    Row {
        anchors.verticalCenter: parent.verticalCenter
        spacing: 20
        Text {
            text: ThemeProvider.getCatchphrase("app_title", "Flutter Earth")
            font.family: ThemeProvider.getFont("title").family
            font.pixelSize: ThemeProvider.getFont("title").pixelSize + 2
            font.bold: ThemeProvider.getFont("title").bold
            color: ThemeProvider.getColor("text_on_primary", "#FFFFFF")
            anchors.leftMargin: 18
        }
    }
} 
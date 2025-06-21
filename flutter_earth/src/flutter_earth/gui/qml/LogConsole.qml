import QtQuick 2.15
import QtQuick.Controls 2.15

GroupBox {
    id: logConsole
    title: "Log Console"
    Layout.fillWidth: true
    TextArea {
        id: logTextArea
        readOnly: true
        wrapMode: TextArea.Wrap
        text: "[Logs will appear here]"
        color: "#fff"
        background: Rectangle { color: "#222" }
        font.pixelSize: 12
        height: 100
        anchors.left: parent.left
        anchors.right: parent.right
    }
} 
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

GroupBox {
    id: controlsGroup
    title: "Processing Controls"
    Layout.fillWidth: true
    RowLayout {
        spacing: 10
        Button { text: "Start" }
        Button { text: "Cancel" }
        Button { text: "Verify" }
    }
} 
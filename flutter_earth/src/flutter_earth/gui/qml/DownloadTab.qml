import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: downloadTab
    anchors.fill: parent
    
    ScrollView {
        anchors.fill: parent
        ColumnLayout {
            width: parent.width
            spacing: 20
            anchors.margins: 20
            AreaTimeGroup {}
            ProcessingGroup {}
            OutputGroup {}
            ControlsGroup {}
            LogConsole {}
        }
    }
} 
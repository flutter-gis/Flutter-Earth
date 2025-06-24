import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: downloadTab
    anchors.fill: parent
    
    ScrollView {
        anchors.fill: parent
        GridLayout {
            id: mainGrid
            columns: 2
            rowSpacing: 20
            columnSpacing: 20
            anchors.margins: 20
            width: parent.width

            // Top row
            AreaTimeGroup {
                Layout.row: 0
                Layout.column: 0
                Layout.fillWidth: true
            }
            ProcessingGroup {
                Layout.row: 0
                Layout.column: 1
                Layout.fillWidth: true
            }

            // Second row
            OutputGroup {
                Layout.row: 1
                Layout.column: 0
                Layout.fillWidth: true
            }
            ControlsGroup {
                Layout.row: 1
                Layout.column: 1
                Layout.fillWidth: true
            }

            // LogConsole spans both columns at the bottom
            LogConsole {
                Layout.row: 2
                Layout.column: 0
                Layout.columnSpan: 2
                Layout.fillWidth: true
            }
        }
    }
} 
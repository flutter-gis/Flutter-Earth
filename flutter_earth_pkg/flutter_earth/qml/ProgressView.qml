import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: progressView
    color: "#e8f5e9"
    anchors.fill: parent
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 30
        Text {
            text: qsTr("Download Progress")
            font.pointSize: 22
            font.bold: true
            color: "#388e3c"
        }
        ProgressBar {
            value: backend && backend.progress_tracker ? backend.progress_tracker.getProgress() : 0.0
            width: 300
        }
        BusyIndicator {
            running: true
            width: 48; height: 48
        }
        Text {
            text: backend && backend.progress_tracker ? backend.progress_tracker.getStatus() : qsTr("No active downloads.")
            font.pointSize: 14
            color: "#388e3c"
        }
    }
} 
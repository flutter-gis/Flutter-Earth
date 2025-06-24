import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." // For ThemeProvider

Rectangle {
    id: progressView
    color: ThemeProvider.getColor("background", "#e8f5e9")
    anchors.fill: parent

    // Properties to hold progress data from backend
    // These should be updated via signals from AppBackend for real-time updates
    property real currentProgress: backend.getProgress ? backend.getProgress() : 0.0
    property string currentStatus: backend.getStatus ? backend.getStatus() : ThemeProvider.getCatchphrase("status_no_active_downloads", "No active downloads.")
    property bool isBusy: currentProgress > 0 && currentProgress < 1.0 // Example logic for busy

    Connections {
        target: backend
        function onDownloadProgressUpdated(current, total) {
            currentProgress = total > 0 ? current / total : 0.0;
            // currentStatus can be updated here too if backend provides more detailed status messages
        }
        // function onDownloadStatusChanged(newStatus) { currentStatus = newStatus; }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 30
        Text {
            text: ThemeProvider.getCatchphrase("view_ProgressView", "Download Progress")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary", "#388e3c")
        }
        ProgressBar {
            id: mainProgressBar
            value: currentProgress
            Layout.fillWidth: true
            Layout.preferredWidth: 300 // Max width for centering
            background: Rectangle { color: ThemeProvider.getColor("progressbar_bg"); radius: 3 }
            contentItem: Rectangle {
                color: ThemeProvider.getColor("progressbar_fg")
                implicitWidth: mainProgressBar.visualPosition * mainProgressBar.width
                implicitHeight: mainProgressBar.height
                radius: 3
            }
        }
        BusyIndicator {
            running: isBusy
            // Style BusyIndicator if needed, e.g., using custom delegate or by tinting
        }
        Text {
            text: currentStatus
            font: ThemeProvider.getFont("body")
            color: ThemeProvider.getColor("text_subtle", "#388e3c")
        }
    }
} 
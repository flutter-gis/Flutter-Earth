import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: progressView
    // color: "#e8f5e9" // Replaced by theme
    anchors.fill: parent
    color: mainContent.currentTheme.widget_bg // Use theme color

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 30
        Text {
            text: qsTr("Download Progress")
            font.pointSize: 22
            font.bold: true
            color: mainContent.currentTheme.primary // Theme color
        }
        ProgressBar {
            id: progressBar
            value: backend ? backend.getProgress().progress : 0.0
            width: 300
            background: Rectangle { color: mainContent.currentTheme.progressbar_bg }
            contentItem: Item {
                Rectangle {
                    width: progressBar.visualPosition * progressBar.width
                    height: progressBar.height
                    color: mainContent.currentTheme.progressbar_fg
                }
            }
        }
        BusyIndicator {
            id: busyIndicator
            running: backend ? backend.getProgress().status === 'running' : false
            width: 48; height: 48
            // Consider theming BusyIndicator if default is not good
        }
        Text {
            id: statusText
            text: backend ? backend.getProgressStatusText() : qsTr("No active downloads.")
            font.pointSize: 14
            color: mainContent.currentTheme.text_subtle // Theme color
            wrapMode: Text.WordWrap
            width: parent.width - 20 // Ensure text wraps within layout
        }
        Button {
            text: qsTr("Refresh Progress")
            onClicked: {
                var progressData = backend.getProgress();
                progressBar.value = progressData.progress;
                statusText.text = backend.getProgressStatusText();
                busyIndicator.running = progressData.status === 'running';
            }
        }
    }
} 
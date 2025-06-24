import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.settings 1.0

Rectangle {
    id: settingsView
    // color: "#f3e5f5" // Replaced by theme
    anchors.fill: parent
    color: mainContent.currentTheme.widget_bg // Use theme color

    property var allSettings: backend.getAllSettings()

    // React to config/setting changes
    Connections {
        target: backend
        function onConfigChanged(newConfig) {
            allSettings = newConfig;
            themeCombo.currentIndex = backend.getAvailableThemes().indexOf(allSettings.theme);
            outputDirField.text = allSettings.output_dir;
        }
        function onSettingChanged(key, value) {
            if (key === "theme") {
                themeCombo.currentIndex = backend.getAvailableThemes().indexOf(value);
            }
            if (key === "output_dir") {
                outputDirField.text = value;
            }
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 30

        Text {
            text: qsTr("Settings")
            font.pointSize: 22
            font.bold: true
            color: mainContent.currentTheme.primary // Theme color
        }

        // Theme selection
        RowLayout {
            spacing: 10
            Text { text: qsTr("Theme:"); font.pointSize: 16; color: mainContent.currentTheme.text }
            ComboBox {
                id: themeCombo
                model: backend.getAvailableThemes()
                currentIndex: backend.getAvailableThemes().indexOf(allSettings.theme)
                onCurrentIndexChanged: {
                    if (currentIndex >= 0)
                        backend.setSetting("theme", model[currentIndex]);
                }
                // Basic theming
            }
        }

        // Output directory
        RowLayout {
            spacing: 10
            Text { text: qsTr("Output Directory:"); font.pointSize: 16; color: mainContent.currentTheme.text }
            TextField {
                id: outputDirField
                text: allSettings.output_dir
                onEditingFinished: {
                    backend.setSetting("output_dir", text);
                }
                width: 300
                color: mainContent.currentTheme.entry_fg
                background: Rectangle { color: mainContent.currentTheme.entry_bg; border.color: mainContent.currentTheme.entry_border }
            }
        }

        // Reload settings from disk
        Button {
            text: qsTr("Reload Settings")
            onClicked: backend.reloadConfig()
        }

        // Clear cache and logs
        Button {
            text: qsTr("Clear Cache and Logs")
            onClicked: {
                if (backend && backend.clearCacheAndLogs) {
                    backend.clearCacheAndLogs();
                    clearDialog.text = qsTr("All cache and log files have been cleared.");
                    clearDialog.open();
                }
            }
        }
        MessageDialog {
            id: clearDialog
            title: qsTr("Cleanup Complete")
            text: ""
            visible: false
            onAccepted: visible = false
        }
    }
} 
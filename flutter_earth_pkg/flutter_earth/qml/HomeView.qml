import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: homeView
    // color: "#fff3e0" // Replaced by theme
    anchors.fill: parent
    color: mainContent.currentTheme.widget_bg // Use theme color

    property string userName: backend.getSetting ? backend.getSetting("user_name") || "" : ""

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 30

        Text {
            text: userName ? (qsTr("Welcome, ") + userName + "!") : qsTr("Welcome to Flutter Earth!")
            font.pointSize: 28
            font.bold: true
            color: mainContent.currentTheme.primary // Use theme color
            opacity: 0.0
            SequentialAnimation on opacity {
                NumberAnimation { to: 1.0; duration: 1200; easing.type: Easing.OutCubic }
            }
        }
        Text {
            text: qsTr("Status: ") + (backend && backend.isGeeInitialized() ? qsTr("Earth Engine Ready") : qsTr("Earth Engine Not Authenticated"))
            font.pointSize: 16
            color: backend && backend.isGeeInitialized() ? mainContent.currentTheme.success : mainContent.currentTheme.error // Use theme colors
        }
        RowLayout {
            spacing: 20
            Button {
                text: qsTr("Go to Map")
                onClicked: mainContent.currentView = "MapView"
                // Basic theming for buttons, can be expanded with custom components
                // background: Rectangle { color: mainContent.currentTheme.button_bg }
                // contentItem: Text { text: control.text; color: mainContent.currentTheme.button_fg }
            }
            Button {
                text: qsTr("Download Data")
                onClicked: mainContent.currentView = "DownloadView"
            }
            Button {
                text: qsTr("Settings")
                onClicked: mainContent.currentView = "SettingsView"
            }
        }
    }
} 
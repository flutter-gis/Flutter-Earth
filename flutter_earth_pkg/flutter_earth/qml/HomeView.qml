import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: homeView
    color: "#fff3e0"
    anchors.fill: parent

    property string userName: backend.getSetting ? backend.getSetting("user_name") || "" : ""

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 30

        Text {
            text: userName ? (qsTr("Welcome, ") + userName + "!") : qsTr("Welcome to Flutter Earth!")
            font.pointSize: 28
            font.bold: true
            color: "#e65100"
            opacity: 0.0
            SequentialAnimation on opacity {
                NumberAnimation { to: 1.0; duration: 1200; easing.type: Easing.OutCubic }
            }
        }
        Text {
            text: qsTr("Status: ") + (backend && backend.isGeeInitialized() ? qsTr("Earth Engine Ready") : qsTr("Earth Engine Not Authenticated"))
            font.pointSize: 16
            color: backend && backend.isGeeInitialized() ? "#388e3c" : "#b71c1c"
        }
        RowLayout {
            spacing: 20
            Button {
                text: qsTr("Go to Map")
                onClicked: mainContent.currentView = "MapView"
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
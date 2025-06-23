import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 1000
    height: 700
    title: "Flutter Earth"
    color: "pink"

    TopBar {
        id: topBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        z: 2
    }
    Sidebar {
        id: sidebar
        anchors.top: topBar.bottom
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        z: 2
        onHomeClicked: mainContent.currentView = "HomeView"
        onMapClicked: mainContent.currentView = "MapView"
        onDownloadClicked: mainContent.currentView = "DownloadView"
        onProgressClicked: mainContent.currentView = "ProgressView"
        onSettingsClicked: mainContent.currentView = "SettingsView"
        onAboutClicked: mainContent.currentView = "AboutView"
    }
    MainContent {
        id: mainContent
        anchors.top: topBar.bottom
        anchors.left: sidebar.right
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        z: 1
    }
} 
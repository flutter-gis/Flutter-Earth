import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: mainContent
    property string currentView: "HomeView"
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.bottom: parent.bottom
    anchors.margins: 0
    z: 0

    // Centralized view loader for navigation
    Loader {
        id: viewLoader
        anchors.fill: parent
        source: {
            if (mainContent.currentView === "HomeView") return "HomeView.qml"
            if (mainContent.currentView === "MapView") return "MapView.qml"
            if (mainContent.currentView === "DownloadView") return "DownloadView.qml"
            if (mainContent.currentView === "ProgressView") return "ProgressView.qml"
            if (mainContent.currentView === "SettingsView") return "SettingsView.qml"
            if (mainContent.currentView === "AboutView") return "AboutView.qml"
            // Add more views here as needed
            return "HomeView.qml"
        }
    }
} 
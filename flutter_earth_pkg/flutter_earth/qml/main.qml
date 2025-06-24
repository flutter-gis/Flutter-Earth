import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 1000
    height: 700
    title: "Flutter Earth"
    // color: "pink" // To be replaced by theme

    property var themeColors: backend.getCurrentThemeColors()
    color: themeColors.background // Set window background from theme

    Connections {
        target: backend
        function onThemeChanged() {
            themeColors = backend.getCurrentThemeColors();
            // Force re-evaluation of bindings dependent on themeColors
            // This can be tricky; explicit updates in components might be needed
            // or ensuring components correctly re-bind.
            console.log("Theme changed in main.qml, new background: " + themeColors.background)
        }
    }

    TopBar {
        id: topBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        z: 2
        // Pass theme colors down or access them globally
        barColor: themeColors.secondary // Example: topBar has a barColor property
        textColor: themeColors.text
    }
    Sidebar {
        id: sidebar
        anchors.top: topBar.bottom
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        z: 2
        // Pass theme colors
        bgColor: themeColors.primary
        itemDefaultColor: themeColors.widget_bg
        itemHoverColor: themeColors.button_hover_bg
        itemPressColor: themeColors.accent
        itemBorderColor: themeColors.primary
        itemTextColor: themeColors.text

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
        // Views loaded here should also use themeColors
        // This could be done by passing themeColors to the Loader's item
        // or by having each view access a global theme object/properties.
        property var currentTheme: themeColors // Make theme available to loaded views
    }
} 
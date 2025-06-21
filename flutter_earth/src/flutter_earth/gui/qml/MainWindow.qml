import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Controls.impl 2.15
import QtQuick.Templates 2.15 as T

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1400
    height: 900
    title: "Flutter Earth"
    color: "#1e1e1e"
    Material.theme: Material.Dark

    // Menu bar
    menuBar: MenuBar {
        MenuBarItem { text: "File" }
        MenuBarItem { text: "Settings" }
        MenuBarItem { text: "Help" }
    }

    // Toolbar
    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            ToolButton { text: "Home" }
            ToolButton { text: "Download" }
            ToolButton { text: "Map" }
            ToolButton { text: "Theme" }
        }
    }

    // Main content
    RowLayout {
        anchors.fill: parent
        spacing: 0
        Sidebar { Layout.preferredWidth: 400; Layout.fillHeight: true }
        MapPanel { Layout.fillWidth: true; Layout.fillHeight: true }
    }

    // Status bar
    footer: Label {
        text: "Ready"
        padding: 10
    }
} 
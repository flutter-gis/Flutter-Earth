import QtQuick 2.15
import QtQuick.Controls 2.15
import "." // Assuming ThemeProvider.qml is in the same directory or an importable path

Rectangle {
    id: sidebar
    color: ThemeProvider.getColor("widget_bg", "#fce4ec") // Use theme color
    width: 180 // Slightly wider for icons + text
    anchors.top: parent.top
    anchors.bottom: parent.bottom
    anchors.left: parent.left
    z: 2

    signal homeClicked()
    signal mapClicked()
    signal downloadClicked()
    signal progressClicked()
    signal satelliteInfoClicked() // New
    signal indexAnalysisClicked() // New
    signal vectorDownloadClicked() // New
    signal dataViewerClicked()    // New
    signal settingsClicked()
    signal aboutClicked()

    Column {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15 // Adjusted spacing for more items
        Repeater {
            model: [
                { label: qsTr("Home"), signal: "homeClicked", icon: "🏠" },
                { label: qsTr("Map"), signal: "mapClicked", icon: "🗺️" },
                { label: qsTr("Download"), signal: "downloadClicked", icon: "📥" },
                { label: qsTr("Satellite Info"), signal: "satelliteInfoClicked", icon: "🛰️" }, // New
                { label: qsTr("Index Analysis"), signal: "indexAnalysisClicked", icon: "🌱" }, // New
                { label: qsTr("Vector Download"), signal: "vectorDownloadClicked", icon: "🌐" }, // New
                { label: qsTr("Data Viewer"), signal: "dataViewerClicked", icon: "📊" },       // New
                { label: qsTr("Progress"), signal: "progressClicked", icon: "🔄" },
                { label: qsTr("Settings"), signal: "settingsClicked", icon: "⚙️" },
                { label: qsTr("About"), signal: "aboutClicked", icon: "ℹ️" }
            ]
            delegate: Rectangle {
                width: parent.width
                height: 48
                radius: ThemeProvider.getStyle("button_default").radius || 8 // Use theme style
                property bool pressed: false
                property bool hovered: false

                // Get colors from ThemeProvider based on keys defined in theme config
                color: pressed ? ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_pressed_color, "#f06292")
                               : hovered ? ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_hover_color, "#f8bbd0")
                                         : ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_color, "white")
                border.color: ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_border_color, "#e91e63")
                border.width: ThemeProvider.getStyle("button_default").borderWidth || 2

                scale: pressed ? 1.13 : hovered ? 1.07 : 1.0
                Behavior on scale { NumberAnimation { duration: 160; easing.type: Easing.OutElastic } }
                Behavior on color { ColorAnimation { duration: 120 } }

                Rectangle { // Optional overlay for pressed/hover, if not handled by main color change
                    anchors.fill: parent
                    color: ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_border_color, "#e91e63") // Example usage
                    opacity: pressed ? 0.12 : hovered ? 0.07 : 0
                    radius: parent.radius
                    z: 1
                    visible: false // Can be enabled if direct color change isn't enough
                    Behavior on opacity { NumberAnimation { duration: 120 } }
                }

                Row {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    spacing: 8
                    Text {
                        id: iconText
                        text: modelData.icon
                        font.pixelSize: ThemeProvider.getFont("button").pixelSize + 2 // Slightly larger for icon
                        color: ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_text_color, "#880e4f")
                        z: 2
                    }
                    Text {
                        id: labelText
                        text: modelData.label
                        font.family: ThemeProvider.getFont("button").family
                        font.pixelSize: ThemeProvider.getFont("button").pixelSize
                        font.bold: ThemeProvider.getFont("button").bold
                        color: ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_text_color, "#880e4f")
                        z: 2
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onPressed: parent.pressed = true
                    onReleased: {
                        parent.pressed = false
                        sidebar[modelData.signal]()
                    }
                    onCanceled: parent.pressed = false
                    onEntered: parent.hovered = true
                    onExited: parent.hovered = false
                }
            }
        }
    }
} 
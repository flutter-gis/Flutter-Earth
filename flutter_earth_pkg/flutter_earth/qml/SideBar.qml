import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt5Compat.GraphicalEffects
import "./" // For ThemeProvider singleton

Rectangle {
    id: sidebar
    color: ThemeProvider.getColor("widget_bg", "#fce4ec")
    width: 180
    anchors.top: parent.top
    anchors.bottom: parent.bottom
    anchors.left: parent.left
    z: 2
    radius: 16
    layer.enabled: true
    layer.effect: DropShadow {
        color: ThemeProvider.getColor("primary"); radius: 16; samples: 16; x: 0; y: 2; spread: 0.10
    }

    signal homeClicked()
    signal mapClicked()
    signal downloadClicked()
    signal progressClicked()
    signal satelliteInfoClicked()
    signal indexAnalysisClicked()
    signal vectorDownloadClicked()
    signal dataViewerClicked()
    signal settingsClicked()
    signal aboutClicked()

    Column {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15
        Repeater {
            model: [
                { label: qsTr("Home"), signal: "homeClicked", icon: "🏠" },
                { label: qsTr("Map"), signal: "mapClicked", icon: "🗺️" },
                { label: qsTr("Download"), signal: "downloadClicked", icon: "📥" },
                { label: qsTr("Satellite Info"), signal: "satelliteInfoClicked", icon: "🛰️" },
                { label: qsTr("Index Analysis"), signal: "indexAnalysisClicked", icon: "🌱" },
                { label: qsTr("Vector Download"), signal: "vectorDownloadClicked", icon: "🌐" },
                { label: qsTr("Data Viewer"), signal: "dataViewerClicked", icon: "📊" },
                { label: qsTr("Progress"), signal: "progressClicked", icon: "🔄" },
                { label: qsTr("Settings"), signal: "settingsClicked", icon: "⚙️" },
                { label: qsTr("About"), signal: "aboutClicked", icon: "ℹ️" }
            ]
            delegate: Rectangle {
                width: parent.width
                height: 48
                radius: ThemeProvider.getStyle("button_default").radius || 8
                property bool pressed: false
                property bool hovered: false
                color: pressed ? ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_pressed_color, "#f06292")
                               : hovered ? ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_hover_color, "#f8bbd0")
                                         : ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_color, "white")
                border.color: ThemeProvider.getColor(ThemeProvider.styles.sidebar_button_border_color, "#e91e63")
                border.width: ThemeProvider.getStyle("button_default").borderWidth || 2
                scale: pressed ? 1.13 : hovered ? 1.07 : 1.0
                Behavior on scale { NumberAnimation { duration: 160; easing.type: Easing.OutElastic } }
                Behavior on color { ColorAnimation { duration: 120 } }
                layer.enabled: true
                layer.effect: DropShadow {
                    color: hovered ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("widget_border");
                    radius: hovered ? 12 : 8; samples: 16; x: 0; y: 2; spread: 0.08
                }
                Row {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    spacing: 8
                    Text {
                        id: iconText
                        text: modelData.icon
                        font.family: ThemeProvider.getFont("button").family
                        font.pixelSize: ThemeProvider.getFont("button").pixelSize + 2
                        font.bold: ThemeProvider.getFont("button").bold
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
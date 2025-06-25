import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import "." // For ThemeProvider

Rectangle {
    id: homeView
    color: ThemeProvider.getColor("background", "#fff3e0")
    anchors.fill: parent

    property string userName: backend.getSetting ? backend.getSetting("user_name") || "" : ""
    property string welcomeText: {
        var baseWelcome = ThemeProvider.getCatchphrase("view_HomeView_Welcome", "Welcome to Flutter Earth!");
        if (userName) {
            baseWelcome = ThemeProvider.getCatchphrase("view_HomeView_WelcomeUser", "Welcome, %1!").arg(userName);
        }
        return baseWelcome;
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 30

        Text {
            text: welcomeText
            font.family: ThemeProvider.getFont("title").family
            font.pixelSize: ThemeProvider.getFont("title").pixelSize + 10
            font.bold: ThemeProvider.getFont("title").bold
            color: ThemeProvider.getColor("accent", "#e65100")
            opacity: 0.0
            SequentialAnimation on opacity {
                NumberAnimation { to: 1.0; duration: 1200; easing.type: Easing.OutCubic }
            }
            layer.enabled: true
            layer.effect: DropShadow {
                color: ThemeProvider.getColor("primary"); radius: 12; samples: 16; x: 0; y: 2; spread: 0.10
            }
        }
        Text {
            text: qsTr("Status: ") + (backend && backend.isGeeInitialized() ? ThemeProvider.getCatchphrase("status_gee_ready", "Earth Engine Ready") : ThemeProvider.getCatchphrase("status_gee_not_ready","Earth Engine Not Authenticated"))
            font.family: ThemeProvider.getFont("body").family
            font.pixelSize: ThemeProvider.getFont("body").pixelSize + 2
            font.bold: true
            color: backend && backend.isGeeInitialized() ? ThemeProvider.getColor("success", "#388e3c") : ThemeProvider.getColor("error", "#b71c1c")
        }
        RowLayout {
            spacing: 24
            Repeater {
                model: [
                    { labelKey: "action_goto_map", view: "MapView", defaultText: "Go to Map" },
                    { labelKey: "action_goto_download", view: "DownloadView", defaultText: "Download Data" },
                    { labelKey: "action_goto_settings", view: "SettingsView", defaultText: "Settings" }
                ]
                delegate: Button {
                    text: ThemeProvider.getCatchphrase(modelData.labelKey, modelData.defaultText)
                    onClicked: mainContent.currentView = modelData.view
                    font.family: ThemeProvider.getFont("button").family
                    font.pixelSize: ThemeProvider.getFont("button").pixelSize
                    font.bold: ThemeProvider.getFont("button").bold
                    background: Rectangle {
                        color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey, "#DDDDDD")
                        radius: ThemeProvider.getStyle("button_default").radius
                        border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey, "#AAAAAA")
                        border.width: ThemeProvider.getStyle("button_default").borderWidth || 1
                        layer.enabled: true
                        layer.effect: DropShadow {
                            color: ThemeProvider.getColor("primary"); radius: 8; samples: 16; x: 0; y: 2; spread: 0.08
                        }
                    }
                    contentItem: Text {
                        text: parent.text
                        font.family: ThemeProvider.getFont("button").family
                        font.pixelSize: ThemeProvider.getFont("button").pixelSize
                        font.bold: ThemeProvider.getFont("button").bold
                        color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey, "#000000")
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }
    }
} 
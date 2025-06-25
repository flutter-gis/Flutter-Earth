import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import "." // For ThemeProvider

Rectangle {
    id: aboutView
    color: ThemeProvider.getColor("background", "#e0f2f1")
    anchors.fill: parent

    property string userName: backend.getSetting ? backend.getSetting("user_name") || "" : ""
    property bool namePrompted: false

    // Prompt for name on first startup
    Component.onCompleted: {
        if (!userName && !namePrompted) {
            nameDialog.open();
            namePrompted = true;
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 24

        Text {
            text: userName ? ThemeProvider.getCatchphrase("about_hello_user", "Hello %1!").arg(userName) : ThemeProvider.getCatchphrase("about_hello_generic", "Hello!")
            font.family: ThemeProvider.getFont("title").family
            font.pixelSize: ThemeProvider.getFont("title").pixelSize - 2
            font.bold: ThemeProvider.getFont("title").bold
            color: ThemeProvider.getColor("text", "#004d40")
            layer.enabled: true
            layer.effect: DropShadow {
                color: ThemeProvider.getColor("primary"); radius: 8; samples: 16; x: 0; y: 2; spread: 0.08
            }
        }
        Text {
            text: ThemeProvider.getCatchphrase("view_AboutView", "About Flutter Earth")
            font.family: ThemeProvider.getFont("title").family
            font.pixelSize: ThemeProvider.getFont("title").pixelSize
            font.bold: ThemeProvider.getFont("title").bold
            color: ThemeProvider.getColor("primary", "#004d40")
        }
        Text {
            text: qsTr("Version 1.0.0") // Version can be dynamic later
            font.family: ThemeProvider.getFont("body").family
            font.pixelSize: ThemeProvider.getFont("body").pixelSize
            color: ThemeProvider.getColor("text_subtle", "#00796b")
        }
        Text {
            text: ThemeProvider.getCatchphrase("about_developed_by", "Developed by Jakob Newman and contributors.")
            font.family: ThemeProvider.getFont("body").family
            font.pixelSize: ThemeProvider.getFont("body").pixelSize
            color: ThemeProvider.getColor("text_subtle", "#00796b")
        }
        Button {
            text: ThemeProvider.getCatchphrase("action_visit_website", "Visit Project Website")
            onClicked: Qt.openUrlExternally("https://github.com/jakobnewman/Flutter-Earth") // URL could also come from theme/config
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
        // Add a changelog section
        GroupBox {
            title: qsTr("Recent Changes (Changelog)")
            Layout.fillWidth: true
            Layout.preferredHeight: 180
            font: ThemeProvider.getFont("body")
            ScrollView {
                anchors.fill: parent
                clip: true
                TextArea {
                    readOnly: true
                    wrapMode: TextEdit.WordWrap
                    font: ThemeProvider.getFont("monospace")
                    text: backend.getChangelog ? backend.getChangelog() : "See CHANGELOG.md for details."
                }
            }
        }
    }

    Dialog { // Name input dialog
        id: nameDialog
        title: ThemeProvider.getCatchphrase("dialog_title_welcome", "Welcome!")
        modal: true
        standardButtons: Dialog.Ok
        visible: false
        background: Rectangle { color: ThemeProvider.getColor("widget_bg"); border.color: ThemeProvider.getColor("widget_border"); radius: 10 }
        contentItem: ColumnLayout {
            spacing: 10
            Text {
                text: ThemeProvider.getCatchphrase("prompt_enter_name", "Please enter your name:")
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                color: ThemeProvider.getColor("text")
            }
            TextField {
                id: nameField
                Layout.fillWidth: true
                placeholderText: ThemeProvider.getCatchphrase("placeholder_your_name", "Your name")
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
            }
        }
        // Ok button will use standard dialog styling, can be customized if needed
        onAccepted: {
            if (nameField.text.length > 0) {
                backend.setSetting("user_name", nameField.text);
                userName = nameField.text; // Update local property for immediate UI refresh
            }
        }
    }
} 
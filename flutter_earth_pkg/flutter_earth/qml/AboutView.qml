import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
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
        spacing: 20

        Text {
            text: userName ? ThemeProvider.getCatchphrase("about_hello_user", "Hello %1!").arg(userName) : ThemeProvider.getCatchphrase("about_hello_generic", "Hello!")
            font: ThemeProvider.getFont("title") // Using title font for emphasis
            font.pixelSize: ThemeProvider.getFont("title").pixelSize - 2 // Slightly smaller than main titles
            color: ThemeProvider.getColor("text", "#004d40")
        }
        Text {
            text: ThemeProvider.getCatchphrase("view_AboutView", "About Flutter Earth")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary", "#004d40")
        }
        Text {
            text: qsTr("Version 1.0.0") // Version can be dynamic later
            font: ThemeProvider.getFont("body")
            color: ThemeProvider.getColor("text_subtle", "#00796b")
        }
        Text {
            text: ThemeProvider.getCatchphrase("about_developed_by", "Developed by Jakob Newman and contributors.")
            font: ThemeProvider.getFont("body")
            color: ThemeProvider.getColor("text_subtle", "#00796b")
        }
        Button {
            text: ThemeProvider.getCatchphrase("action_visit_website", "Visit Project Website")
            onClicked: Qt.openUrlExternally("https://github.com/jakobnewman/Flutter-Earth") // URL could also come from theme/config
            font: ThemeProvider.getFont("button")
            background: Rectangle {
                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey, "#DDDDDD")
                radius: ThemeProvider.getStyle("button_default").radius
                border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey, "#AAAAAA")
                border.width: ThemeProvider.getStyle("button_default").borderWidth || 1
            }
            contentItem: Text {
                text: parent.text
                font: parent.font
                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey, "#000000")
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    Dialog { // Name input dialog
        id: nameDialog
        title: ThemeProvider.getCatchphrase("dialog_title_welcome", "Welcome!")
        modal: true
        standardButtons: Dialog.Ok
        visible: false
        background: Rectangle { color: ThemeProvider.getColor("widget_bg"); border.color: ThemeProvider.getColor("widget_border") }
        contentItem: ColumnLayout {
            spacing: 10
            Text {
                text: ThemeProvider.getCatchphrase("prompt_enter_name", "Please enter your name:")
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor("text")
            }
            TextField {
                id: nameField
                Layout.fillWidth: true
                placeholderText: ThemeProvider.getCatchphrase("placeholder_your_name", "Your name")
                font: ThemeProvider.getFont("body")
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
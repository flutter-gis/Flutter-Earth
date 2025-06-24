import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: aboutView
    // color: "#e0f2f1" // Replaced by theme
    anchors.fill: parent
    color: mainContent.currentTheme.widget_bg // Use theme color

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
            text: userName ? (qsTr("Hello ") + userName + "!") : qsTr("Hello!")
            font.pointSize: 20
            font.bold: true
            color: mainContent.currentTheme.primary // Theme color
        }
        Text {
            text: qsTr("About Flutter Earth")
            font.pointSize: 22
            font.bold: true
            color: mainContent.currentTheme.primary // Theme color
        }
        Text {
            text: qsTr("Version 1.0.0")
            font.pointSize: 14
            color: mainContent.currentTheme.text_subtle // Theme color
        }
        Text {
            text: qsTr("Developed by Jakob Newman and contributors.")
            font.pointSize: 14
            color: mainContent.currentTheme.text_subtle // Theme color
        }
        Button {
            text: qsTr("Visit Project Website")
            onClicked: Qt.openUrlExternally("https://github.com/jakobnewman/Flutter-Earth")
        }
    }

    Dialog {
        id: nameDialog
        title: qsTr("Welcome!")
        modal: true
        standardButtons: Dialog.Ok
        visible: false
        ColumnLayout {
            spacing: 10
            Text { text: qsTr("Please enter your name:") }
            TextField {
                id: nameField
                width: 200
                placeholderText: qsTr("Your name")
            }
        }
        onAccepted: {
            if (nameField.text.length > 0) {
                backend.setSetting("user_name", nameField.text);
                userName = nameField.text;
            }
        }
    }
} 
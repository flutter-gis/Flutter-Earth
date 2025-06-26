import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1
import "./" // For ThemeProvider singleton

Popup {
    id: authDialog
    modal: true
    focus: true
    width: 440
    height: 280
    x: (parent ? parent.width : Screen.width) / 2 - width / 2
    y: (parent ? parent.height : Screen.height) / 2 - height / 2
    property alias keyFile: keyFileField.text
    property alias projectId: projectIdField.text
    signal helpRequested()
    signal credentialsEntered(string keyFile, string projectId)
    background: Rectangle {
        color: ThemeProvider.getColor("widget_bg", "white")
        border.color: ThemeProvider.getColor("widget_border", "#cccccc")
        radius: 10
    }
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        Text { 
            text: "To use Earth Engine features, please upload your Google Cloud service account JSON key and enter your project ID."
            wrapMode: Text.WordWrap
            font: ThemeProvider.getFont("body")
            color: ThemeProvider.getColor("text")
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            Text { 
                text: "JSON Key File:"
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor("text")
            }
            TextField { 
                id: keyFileField
                Layout.fillWidth: true
                placeholderText: "Select your key file..."
                readOnly: true
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                background: Rectangle {
                    color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey)
                    border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey)
                    radius: ThemeProvider.getStyle("text_input").radius
                }
            }
            Button {
                text: "Browse..."
                onClicked: fileDialog.open()
                font: ThemeProvider.getFont("button")
                background: Rectangle {
                    color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                    radius: ThemeProvider.getStyle("button_default").radius
                    border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            Text { 
                text: "Project ID:"
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor("text")
            }
            TextField { 
                id: projectIdField
                Layout.fillWidth: true
                placeholderText: "your-gcp-project-id"
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                background: Rectangle {
                    color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey)
                    border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey)
                    radius: ThemeProvider.getStyle("text_input").radius
                }
            }
        }
        RowLayout {
            Layout.alignment: Qt.AlignRight
            spacing: 10
            Button { 
                text: "Help"; 
                onClicked: authDialog.helpRequested(); 
                font: ThemeProvider.getFont("button") 
            }
            Button { 
                text: ThemeProvider.getCatchphrase("auth_save", "Save Credentials")
                onClicked: {
                    if (keyFileField.text && projectIdField.text) {
                        authDialog.credentialsEntered(keyFileField.text, projectIdField.text)
                        authDialog.close()
                    }
                }
                font: ThemeProvider.getFont("button") 
            }
            Button { 
                text: "Cancel"; 
                onClicked: authDialog.close(); 
                font: ThemeProvider.getFont("button") 
            }
        }
        FileDialog {
            id: fileDialog
            title: "Select Service Account JSON Key"
            nameFilters: ["JSON files (*.json)"]
            onAccepted: {
                var filePath = file.toString().replace(/^(file:\/{2,3})/, "")
                if (Qt.platform.os === "windows" && filePath.startsWith("/")) {
                    filePath = filePath.substring(1)
                }
                keyFileField.text = filePath
            }
        }
    }

    onOpened: {
        if (backend && backend.getCredentials) {
            var creds = backend.getCredentials();
            if (creds && creds.project_id && creds.key_file) {
                keyFileField.text = creds.key_file;
                projectIdField.text = creds.project_id;
                // Don't auto-apply - let user decide whether to save or modify
            }
        }
    }
} 
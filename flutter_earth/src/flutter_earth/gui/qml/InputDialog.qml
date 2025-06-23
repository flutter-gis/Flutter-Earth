import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: inputDialog
    property string dialogType: "text"  // "text", "number", "password"
    property string dialogTitle: ""
    property string dialogLabel: ""
    property string defaultValue: ""
    
    title: dialogTitle
    standardButtons: Dialog.Ok | Dialog.Cancel
    modal: true
    visible: false
    
    signal inputProvided(string value)
    
    contentItem: ColumnLayout {
        spacing: 10
        
        Label {
            text: dialogLabel
            color: "#fff"
        }
        
        TextField {
            id: inputField
            text: defaultValue
            echoMode: dialogType === "password" ? TextInput.Password : TextInput.Normal
            inputMethodHints: dialogType === "number" ? Qt.ImhFormattedNumbersOnly : Qt.ImhNone
            Layout.fillWidth: true
            color: "#fff"
            background: Rectangle {
                color: "#2a2a2a"
                border.color: "#555"
            }
        }
    }
    
    onAccepted: {
        inputProvided(inputField.text)
    }
    
    function openDialog(type, title, label, defaultVal) {
        dialogType = type
        dialogTitle = title
        dialogLabel = label
        defaultValue = defaultVal || ""
        inputField.text = defaultValue
        visible = true
    }
} 
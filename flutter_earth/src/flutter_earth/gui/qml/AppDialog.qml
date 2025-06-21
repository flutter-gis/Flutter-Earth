import QtQuick 2.15
import QtQuick.Controls 2.15

Dialog {
    id: appDialog
    property string dialogType: "info"
    property string dialogTitle: ""
    property string dialogText: ""
    title: dialogTitle
    standardButtons: Dialog.Ok
    modal: true
    visible: false
    onAccepted: visible = false
    contentItem: Column {
        spacing: 10
        Label {
            text: dialogText
            color: dialogType === "error" ? "#ff5555" : dialogType === "warning" ? "#ffaa00" : "#fff"
            wrapMode: Text.Wrap
        }
    }
    function openDialog(type, title, text) {
        dialogType = type; dialogTitle = title; dialogText = text; visible = true;
    }
} 
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." as App

Dialog {
    id: mapDialog
    title: "Select Area of Interest on Map"
    width: parent.width * 0.8
    height: parent.height * 0.8
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel

    // Signal to emit the selected area
    signal areaSelected(var geometry)

    // TODO: Connect this to the MapView's drawing tools
    onAccepted: {
        // let selectedArea = mapView.getSelection()
        // areaSelected(selectedArea)
    }

    App.MapView {
        anchors.fill: parent
    }
} 
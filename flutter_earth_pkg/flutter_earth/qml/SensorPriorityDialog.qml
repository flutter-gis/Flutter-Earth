import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: dialog
    title: "Edit Sensor Priority"
    standardButtons: Dialog.Ok | Dialog.Cancel
    modal: true
    width: 400
    height: 500

    property var priorityModel: []
    property var allSensors: []
    property var availableSensors: []

    function updateAvailableSensors() {
        var currentSensors = new Set(priorityModel)
        availableSensors = allSensors.filter(function(sensor) {
            return !currentSensors.has(sensor)
        })
    }

    Component.onCompleted: {
        priorityModel = backend.get_sensor_priority()
        allSensors = backend.get_all_sensors()
        updateAvailableSensors()
    }

    onAccepted: {
        backend.set_sensor_priority(priorityModel)
    }

    ColumnLayout {
        anchors.fill: parent

        Label {
            text: "Arrange sensors in preferred order (top is highest priority)."
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        ListView {
            id: priorityView
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: priorityModel
            delegate: ItemDelegate {
                width: parent.width
                text: modelData
                
                RowLayout {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.rightMargin: 5
                    spacing: 5

                    Button {
                        text: "↑"
                        enabled: index > 0
                        onClicked: {
                            priorityModel.splice(index, 1, priorityModel.splice(index - 1, 1, modelData)[0])
                            priorityView.model = [] // Force model update
                            priorityView.model = priorityModel
                        }
                    }
                    Button {
                        text: "↓"
                        enabled: index < priorityModel.length - 1
                        onClicked: {
                            priorityModel.splice(index, 1, priorityModel.splice(index + 1, 1, modelData)[0])
                            priorityView.model = [] // Force model update
                            priorityView.model = priorityModel
                        }
                    }
                    Button {
                        text: "✕"
                        onClicked: {
                            priorityModel.splice(index, 1)
                            updateAvailableSensors()
                            priorityView.model = [] // Force model update
                            priorityView.model = priorityModel
                        }
                    }
                }
            }
        }

        RowLayout {
            id: addSensorRow
            Layout.fillWidth: true

            ComboBox {
                id: addSensorCombo
                Layout.fillWidth: true
                model: availableSensors
            }

            Button {
                text: "Add"
                enabled: addSensorCombo.currentIndex !== -1
                onClicked: {
                    priorityModel.push(addSensorCombo.currentText)
                    updateAvailableSensors()
                    priorityView.model = []
                    priorityView.model = priorityModel
                }
            }
        }
    }
} 
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." as App

Rectangle {
    id: controlPanel
    color: App.Style.widget_bg
    radius: 8

    // Add the new Map Selection Dialog
    MapSelectionDialog {
        id: mapDialog
        onAreaSelected: (geometry) => {
            // Update the AOI input with the new geometry
            aoiInput.text = JSON.stringify(geometry)
        }
    }

    Flickable {
        anchors.fill: parent
        contentWidth: availableWidth
        contentHeight: column.height
        clip: true

        ColumnLayout {
            id: column
            anchors.fill: parent
            anchors.margins: 20
            spacing: 20

            Label {
                text: "Settings"
                font.pixelSize: 24
                color: App.Style.text
                Layout.alignment: Qt.AlignHCenter
            }

            // Theme switcher
            /*
            Button {
                text: "Switch Theme"
                onClicked: {
                    App.Style.nextTheme()
                }
                background: Rectangle {
                    color: App.Style.secondaryButton
                    radius: 4
                }
                contentItem: Text {
                    text: parent.text
                    color: App.Style.text
                }
            }
            */

            // --- Area & Time ---
            GroupBox {
                title: "Area & Time"
                Layout.fillWidth: true

                ColumnLayout {
                    RowLayout {
                        Label { text: "AOI (bbox):"; color: App.Style.text }
                        TextField {
                            id: aoiInput
                            placeholderText: "minLon,minLat,maxLon,maxLat"
                            Layout.fillWidth: true
                            color: App.Style.entry_fg
                            placeholderTextColor: App.Style.text_subtle
                            background: Rectangle { color: App.Style.entry_bg; border.color: App.Style.primary; radius: 4 }
                        }
                    }
                    RowLayout {
                        Button {
                            text: "Select on Map"
                            onClicked: mapDialog.open()
                            background: Rectangle { color: App.Style.button_bg; radius: 4 }
                            contentItem: Text { text: parent.text; color: App.Style.button_fg }
                        }
                        Button {
                            text: "Import SHP"
                            background: Rectangle { color: App.Style.button_bg; radius: 4 }
                            contentItem: Text { text: parent.text; color: App.Style.button_fg }
                        }
                    }
                     RowLayout {
                        Label { text: "Start Date:"; color: App.Style.text }
                        TextField {
                            id: startDateInput
                            placeholderText: "YYYY-MM-DD"
                            color: App.Style.entry_fg
                            placeholderTextColor: App.Style.text_subtle
                            background: Rectangle { color: App.Style.entry_bg; border.color: App.Style.primary; radius: 4 }
                        }
                    }
                    RowLayout {
                        Label { text: "End Date:"; color: App.Style.text }
                        TextField {
                            id: endDateInput
                            placeholderText: "YYYY-MM-DD"
                            color: App.Style.entry_fg
                            placeholderTextColor: App.Style.text_subtle
                            background: Rectangle { color: App.Style.entry_bg; border.color: App.Style.primary; radius: 4 }
                        }
                    }
                }
            }

            // --- Processing & Sensor ---
            GroupBox {
                title: "Processing & Sensor"
                Layout.fillWidth: true

                ColumnLayout {
                    RowLayout {
                        Label { text: "Sensor Priority:"; color: App.Style.text }
                        
                        ListView {
                            id: sensorPriorityView
                            Layout.fillWidth: true
                            height: 75 // Adjust as needed, or use Layout.preferredHeight
                            model: backend ? backend.getSensorPriority() : []
                            clip: true
                            
                            delegate: ItemDelegate {
                                text: modelData
                                width: parent.width
                                color: App.Style.text
                                background: Rectangle {
                                    color: "transparent"
                                }
                            }
                        }

                        Button {
                            text: "Edit..."
                            background: Rectangle { color: App.Style.button_bg; radius: 4 }
                            contentItem: Text { text: parent.text; color: App.Style.button_fg }
                            onClicked: sensorPriorityDialog.open()
                        }
                    }
                    CheckBox {
                        id: cloudMaskCheck
                        text: "Apply Cloud Masking"
                        checked: true
                        contentItem: Text {
                            text: parent.text
                            color: App.Style.text
                        }
                    }
                    RowLayout {
                        Label { text: "Max Cloud Cover:"; color: App.Style.text }
                        SpinBox {
                            id: cloudCoverSpin
                            from: 0
                            to: 100
                            value: 20
                            stepSize: 5
                            background: Rectangle { color: "transparent" }
                            contentItem: Text {
                                text: parent.value
                                color: App.Style.text
                            }
                            up.indicator: Rectangle {
                                width: 16
                                height: 16
                                color: App.Style.button_bg
                                Text { text: "+"; anchors.centerIn: parent; color: App.Style.button_fg }
                            }
                            down.indicator: Rectangle {
                                width: 16
                                height: 16
                                color: App.Style.button_bg
                                Text { text: "-"; anchors.centerIn: parent; color: App.Style.button_fg }
                            }
                        }
                        Label { text: "%"; color: App.Style.text }
                    }
                }
            }

            // --- Output ---
            GroupBox {
                title: "Output"
                Layout.fillWidth: true

                ColumnLayout {
                    RowLayout {
                        Label { text: "Output Directory:"; color: App.Style.text }
                        TextField {
                            id: outputDirInput
                            placeholderText: "Select a directory..."
                            Layout.fillWidth: true
                            color: App.Style.entry_fg
                            placeholderTextColor: App.Style.text_subtle
                            background: Rectangle { color: App.Style.entry_bg; border.color: App.Style.primary; radius: 4 }
                        }
                        Button {
                            text: "Browse..."
                            background: Rectangle { color: App.Style.button_bg; radius: 4 }
                            contentItem: Text { text: parent.text; color: App.Style.button_fg }
                        }
                    }
                    CheckBox {
                        id: cleanupTilesCheck
                        text: "Cleanup temporary tile files"
                        checked: true
                        contentItem: Text {
                            text: parent.text
                            color: App.Style.text
                        }
                    }
                    CheckBox {
                        id: overwriteCheck
                        text: "Overwrite existing files"
                        checked: false
                        contentItem: Text {
                            text: parent.text
                            color: App.Style.text
                        }
                    }
                }
            }

            // Spacer to push controls to the bottom
            Item { Layout.fillHeight: true }

            // --- Controls ---
            RowLayout {
                Layout.fillWidth: true
                Button {
                    id: runButton
                    text: "Run"
                    Layout.fillWidth: true
                    highlighted: true
                    enabled: backend ? backend.isGeeInitialized() : false
                    onClicked: {
                        // Placeholder for the run logic
                        console.log("Run button clicked! Should start processing.")
                    }
                    background: Rectangle {
                        color: runButton.pressed ? Qt.darker(App.Style.primary, 1.2) : App.Style.primary
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: App.Style.button_fg
                        font.bold: true
                    }
                }
                Button {
                    id: cancelButton
                    text: "Cancel"
                    Layout.fillWidth: true
                    enabled: false
                    background: Rectangle {
                        color: App.Style.secondaryButton
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: App.Style.text
                    }
                }
            }
        }
    }

    SensorPriorityDialog {
        id: sensorPriorityDialog
    }

    Connections {
        target: backend
        function onSensorPriorityChanged() {
            sensorPriorityView.model = backend.get_sensor_priority()
        }
    }
} 
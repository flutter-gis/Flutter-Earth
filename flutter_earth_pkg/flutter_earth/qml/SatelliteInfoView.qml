import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." as App

Rectangle {
    id: root
    color: "transparent" // The background is handled by the view container

    property var currentSensor: null

    RowLayout {
        anchors.fill: parent
        spacing: 10

        // --- Left Panel: Satellite List ---
        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: 300
            Layout.maximumWidth: 400
            color: App.Style.panelBackground
            radius: 8

            ListView {
                id: categoryView
                anchors.fill: parent
                anchors.margins: 5
                model: satelliteData // From python context
                clip: true

                delegate: ColumnLayout {
                    width: categoryView.width

                    Label {
                        text: modelData.name // category name
                        font.pixelSize: 18
                        font.bold: true
                        color: App.Style.text
                        Layout.fillWidth: true
                        background: Rectangle {
                            color: Qt.darker(App.Style.panelBackground, 1.1)
                        }
                        padding: 5
                    }

                    ListView {
                        width: categoryView.width
                        height: children.length * 30 // Approximate height
                        model: modelData.sensors
                        delegate: ItemDelegate {
                            width: parent.width
                            height: 30
                            text: modelData.name // sensor name
                            onClicked: root.currentSensor = modelData
                            background: Rectangle {
                                color: "transparent"
                            }
                            contentItem: Text {
                                text: parent.text
                                color: App.Style.text
                                font.bold: mouseArea.containsMouse
                            }
                        }
                    }
                }
            }
        }

        // --- Right Panel: Details ---
        Rectangle {
            Layout.fillHeight: true
            Layout.fillWidth: true
            color: App.Style.panelBackground
            radius: 8

            Flickable {
                anchors.fill: parent
                contentWidth: availableWidth
                contentHeight: detailsColumn.height
                clip: true

                ColumnLayout {
                    id: detailsColumn
                    width: parent.width
                    anchors.margins: 15
                    spacing: 10

                    Label {
                        text: root.currentSensor ? root.currentSensor.name : "Select a Satellite"
                        font.pixelSize: 24
                        font.bold: true
                        color: App.Style.text
                    }

                    Label {
                        text: root.currentSensor ? root.currentSensor.description : ""
                        wrapMode: Text.WordWrap
                        color: App.Style.textLight
                    }

                    GridLayout {
                        columns: 2
                        visible: root.currentSensor != null
                        columnSpacing: 20
                        rowSpacing: 5

                        Label { text: "<b>Type:</b>"; color: App.Style.text }
                        Label { text: root.currentSensor ? root.currentSensor.type : ""; color: App.Style.textLight }

                        Label { text: "<b>Resolution:</b>"; color: App.Style.text }
                        Label { text: root.currentSensor ? root.currentSensor.resolution_nominal : ""; color: App.Style.textLight }

                        Label { text: "<b>Revisit Interval:</b>"; color: App.Style.text }
                        Label { text: root.currentSensor ? root.currentSensor.revisit_interval : ""; color: App.Style.textLight }
                    }

                    Label {
                        text: "<b>Common Uses:</b>"
                        visible: root.currentSensor != null
                        color: App.Style.text
                        topPadding: 10
                    }
                    Label {
                        text: root.currentSensor ? root.currentSensor.common_uses : ""
                        wrapMode: Text.WordWrap
                        color: App.Style.textLight
                    }

                    Label {
                        text: "<b>Use Categories:</b>"
                        visible: root.currentSensor != null && root.currentSensor.use_categories.length > 0
                        color: App.Style.text
                        topPadding: 10
                    }
                    Flow {
                        width: parent.width
                        spacing: 4
                        visible: root.currentSensor != null
                        Repeater {
                            model: root.currentSensor ? root.currentSensor.use_categories : []
                            delegate: Rectangle {
                                color: App.Style.secondaryButton
                                radius: 4
                                height: 24
                                width: tagText.width + 10
                                Text {
                                    id: tagText
                                    text: modelData
                                    anchors.centerIn: parent
                                    color: App.Style.text
                                }
                            }
                        }
                    }
                }
            }
        }
    }
} 
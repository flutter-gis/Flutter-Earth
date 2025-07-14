import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3

Dialog {
    id: detailsDialog
    title: "Dataset Details"
    width: 600
    height: 500
    modal: true
    standardButtons: Dialog.Close

    property var dataset: ({})

    onAccepted: close()
    onRejected: close()

    ScrollView {
        anchors.fill: parent
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 15

            // Header with title and thumbnail
            Rectangle {
                Layout.fillWidth: true
                height: 120
                color: "#f8f9fa"
                radius: 8

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 15

                    // Thumbnail
                    Rectangle {
                        Layout.preferredWidth: 90
                        Layout.preferredHeight: 90
                        color: "#ecf0f1"
                        radius: 4

                        Image {
                            anchors.fill: parent
                            source: dataset.thumbnail_path || ""
                            fillMode: Image.PreserveAspectCrop
                            visible: dataset.thumbnail_path
                        }

                        Text {
                            anchors.centerIn: parent
                            text: "No Image"
                            color: "#7f8c8d"
                            visible: !dataset.thumbnail_path
                        }
                    }

                    // Title and basic info
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 5

                        Text {
                            text: dataset.title || "Untitled Dataset"
                            font.pixelSize: 18
                            font.bold: true
                            color: "#2c3e50"
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            text: "Provider: " + (dataset.provider || "Unknown")
                            font.pixelSize: 12
                            color: "#7f8c8d"
                        }

                        // Tags
                        Flow {
                            spacing: 5

                            Repeater {
                                model: dataset.tags || []

                                Rectangle {
                                    color: "#3498db"
                                    radius: 12
                                    height: 24

                                    Text {
                                        anchors.centerIn: parent
                                        anchors.margins: 10
                                        text: modelData
                                        font.pixelSize: 11
                                        color: "white"
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Description
            GroupBox {
                Layout.fillWidth: true
                title: "Description"
                font.bold: true

                Text {
                    anchors.fill: parent
                    text: dataset.description || "No description available"
                    font.pixelSize: 14
                    color: "#2c3e50"
                    wrapMode: Text.WordWrap
                }
            }

            // Metadata
            GroupBox {
                Layout.fillWidth: true
                title: "Metadata"
                font.bold: true

                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    columnSpacing: 15
                    rowSpacing: 8

                    Repeater {
                        model: {
                            var metadata = dataset.metadata || {}
                            var keys = Object.keys(metadata)
                            var result = []
                            for (var i = 0; i < keys.length; i++) {
                                result.push({key: keys[i], value: metadata[keys[i]]})
                            }
                            return result
                        }

                        Text {
                            text: modelData.key + ":"
                            font.pixelSize: 12
                            font.bold: true
                            color: "#2c3e50"
                        }

                        Text {
                            text: modelData.value
                            font.pixelSize: 12
                            color: "#7f8c8d"
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }

            // URL
            GroupBox {
                Layout.fillWidth: true
                title: "Source URL"
                font.bold: true

                RowLayout {
                    anchors.fill: parent
                    spacing: 10

                    Text {
                        text: dataset.url || "No URL available"
                        font.pixelSize: 12
                        color: "#3498db"
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }

                    Button {
                        text: "Open"
                        enabled: dataset.url
                        onClicked: Qt.openUrlExternally(dataset.url)
                        background: Rectangle {
                            color: parent.enabled ? (parent.pressed ? "#3498db" : "#2980b9") : "#bdc3c7"
                            radius: 4
                        }
                        contentItem: Text {
                            text: parent.text
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }

            // Export options
            GroupBox {
                Layout.fillWidth: true
                title: "Export Options"
                font.bold: true

                RowLayout {
                    anchors.fill: parent
                    spacing: 10

                    Button {
                        text: "Export as JSON"
                        onClicked: exportAsJSON()
                        background: Rectangle {
                            color: parent.pressed ? "#27ae60" : "#2ecc71"
                            radius: 4
                        }
                        contentItem: Text {
                            text: parent.text
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Button {
                        text: "Copy to Clipboard"
                        onClicked: copyToClipboard()
                        background: Rectangle {
                            color: parent.pressed ? "#f39c12" : "#e67e22"
                            radius: 4
                        }
                        contentItem: Text {
                            text: parent.text
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Item { Layout.fillWidth: true }
                }
            }
        }
    }

    function exportAsJSON() {
        var jsonData = JSON.stringify(dataset, null, 2)
        var fileDialog = Qt.createComponent("FileDialog.qml")
        if (fileDialog.status === Component.Ready) {
            var dialog = fileDialog.createObject(detailsDialog, {
                "title": "Save JSON File",
                "nameFilters": ["JSON Files (*.json)"],
                "defaultSuffix": "json"
            })
            dialog.accepted.connect(function() {
                // In a real implementation, you would write the file here
                console.log("Exporting to: " + dialog.fileUrl)
            })
            dialog.open()
        }
    }

    function copyToClipboard() {
        var jsonData = JSON.stringify(dataset, null, 2)
        // In a real implementation, you would copy to clipboard here
        console.log("Copying to clipboard: " + jsonData.substring(0, 100) + "...")
    }
} 
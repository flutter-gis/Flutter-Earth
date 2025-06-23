import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." as App

Rectangle {
    id: root
    color: "transparent"

    property var availableIndices: backend ? Object.keys(backend.get_available_indices()) : []

    Flickable {
        anchors.fill: parent
        contentWidth: availableWidth
        contentHeight: column.height
        clip: true

        ColumnLayout {
            id: column
            width: parent.width
            anchors.margins: 10
            spacing: 15

            Label {
                text: "Post-Processing"
                font.pixelSize: 24
                color: App.Style.text
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: "This section will contain tools for post-processing downloaded imagery, such as calculating spectral indices."
                wrapMode: Text.WordWrap
                color: App.Style.text
                Layout.fillWidth: true
            }

            GroupBox {
                title: "Input & Index"
                Layout.fillWidth: true

                ColumnLayout {
                    RowLayout {
                        Label { text: "Input Raster File:"; color: App.Style.text }
                        TextField {
                            id: inputFileInput
                            placeholderText: "Select a GeoTIFF file..."
                            Layout.fillWidth: true
                            color: App.Style.inputFg
                            placeholderTextColor: App.Style.placeholderFg
                            background: Rectangle { color: App.Style.inputBg; border.color: App.Style.accent; radius: 4 }
                        }
                        Button {
                            text: "Browse..."
                            background: Rectangle { color: App.Style.secondaryButton; radius: 4 }
                            contentItem: Text { text: parent.text; color: App.Style.text }
                        }
                    }
                    Label { text: "Index to Calculate:"; color: App.Style.text }
                    ComboBox {
                        id: indexCombo
                        model: availableIndices
                        Layout.fillWidth: true
                        background: Rectangle { color: App.Style.inputBg; border.color: App.Style.accent; radius: 4 }
                    }
                }
            }

            GroupBox {
                title: "Output"
                Layout.fillWidth: true

                ColumnLayout {
                    RowLayout {
                        Label { text: "Output File:"; color: App.Style.text }
                        TextField {
                            id: outputFileInput
                            placeholderText: "Specify output file path..."
                            Layout.fillWidth: true
                            color: App.Style.inputFg
                            placeholderTextColor: App.Style.placeholderFg
                            background: Rectangle { color: App.Style.inputBg; border.color: App.Style.accent; radius: 4 }
                        }
                        Button {
                            text: "Browse..."
                            background: Rectangle { color: App.Style.secondaryButton; radius: 4 }
                            contentItem: Text { text: parent.text; color: App.Style.text }
                        }
                    }
                }
            }

            Item { Layout.fillHeight: true }

            Button {
                id: startButton
                text: "Start Processing"
                Layout.fillWidth: true
                highlighted: true
                onClicked: {
                    let params = {
                        inputFile: inputFileInput.text,
                        outputFile: outputFileInput.text,
                        index: indexCombo.currentText
                    };
                    backend.start_post_processing(JSON.stringify(params));
                }
                background: Rectangle {
                    color: startButton.pressed ? Qt.darker(App.Style.primaryButton, 1.2) : App.Style.primaryButton
                    radius: 4
                }
                contentItem: Text {
                    text: parent.text
                    color: App.Style.text
                    font.bold: true
                }
            }
        }
    }
} 
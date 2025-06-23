import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." as App

Rectangle {
    id: root
    color: "transparent"

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
                text: "Vector Data Import"
                font.pixelSize: 24
                color: App.Style.text
                Layout.alignment: Qt.AlignHCenter
            }

            GroupBox {
                title: "Data Source"
                Layout.fillWidth: true

                ColumnLayout {
                    Label { text: "Source (URL, File Path, or Overpass Query):"; color: App.Style.text }
                    TextField {
                        id: sourceInput
                        placeholderText: "e.g., https://.../data.geojson"
                        Layout.fillWidth: true
                        color: App.Style.inputFg
                        placeholderTextColor: App.Style.placeholderFg
                        background: Rectangle { color: App.Style.inputBg; border.color: App.Style.accent; radius: 4 }
                    }
                    Label { text: "Source Type:"; color: App.Style.text }
                    ComboBox {
                        id: sourceTypeCombo
                        model: ["URL", "Local File", "Overpass API Query"]
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
                        Label { text: "Output Directory:"; color: App.Style.text }
                        TextField {
                            id: outputDirInput
                            placeholderText: "Select a directory..."
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
                    Label { text: "Output Format:"; color: App.Style.text }
                    ComboBox {
                        id: outputFormatCombo
                        model: ["GeoJSON", "ESRI Shapefile", "KML"]
                        Layout.fillWidth: true
                        background: Rectangle { color: App.Style.inputBg; border.color: App.Style.accent; radius: 4 }
                    }
                }
            }
            
            Item { Layout.fillHeight: true }

            Button {
                id: startButton
                text: "Start Vector Download"
                Layout.fillWidth: true
                highlighted: true
                enabled: backend.isGeeInitialized()
                onClicked: {
                    let params = {
                        source: sourceInput.text,
                        sourceType: sourceTypeCombo.currentText,
                        outputDir: outputDirInput.text,
                        outputFormat: outputFormatCombo.currentText
                    };
                    backend.start_vector_import(JSON.stringify(params));
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
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." // For ThemeProvider

Rectangle { // Changed from Item to Rectangle
    id: satelliteInfoView
    color: ThemeProvider.getColor("background", "white")
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10

        Label {
            text: ThemeProvider.getCatchphrase("view_SatelliteInfoView", "Satellite Information")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            text: ThemeProvider.getCatchphrase("desc_SatelliteInfoView", "Detailed information about various satellites and their sensors will be displayed here.")
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            font: ThemeProvider.getFont("body")
            color: ThemeProvider.getColor("text_subtle")
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10

            // TreeView for satellite categories and sensors
            TreeView {
                id: satelliteTree
                Layout.fillWidth: true
                Layout.preferredWidth: parent.width * 0.4
                Layout.fillHeight: true
                clip: true
                model: backend.satelliteData // TODO: Wrap this in a proper QAbstractItemModel for full functionality

                background: Rectangle {
                    color: ThemeProvider.getColor("entry_bg")
                    border.color: ThemeProvider.getColor("widget_border")
                }

                delegate: TreeViewDelegate {
                    text: model.display
                    font: ThemeProvider.getFont("body")
                    // TODO: Indentation, expand/collapse icons styling
                    background: Rectangle {
                         color: model.selected ? ThemeProvider.getColor("list_selected_bg") : "transparent"
                    }
                    Label { // Using Label to easily set text color
                        text: parent.text
                        color: model.selected ? ThemeProvider.getColor("list_selected_fg") : ThemeProvider.getColor("list_fg")
                        elide: Text.ElideRight
                        leftPadding: 10 + parent.indentation // Manual indentation based on depth
                    }
                }

                TableViewColumn {
                    title: ThemeProvider.getCatchphrase("header_satellite_category", "Satellite / Category")
                    role: "name"
                    resizable: true
                    delegate: Text { // Styling for header text
                        text: title
                        font: ThemeProvider.getFont("button") // Using button font for header
                        font.bold: true
                        color: ThemeProvider.getColor("text")
                        elide: Text.ElideRight
                    }
                }
                TableViewColumn {
                    title: ThemeProvider.getCatchphrase("header_type", "Type")
                    role: "type"
                    resizable: true
                     delegate: Text { // Styling for header text
                        text: title
                        font: ThemeProvider.getFont("button")
                        font.bold: true
                        color: ThemeProvider.getColor("text")
                        elide: Text.ElideRight
                    }
                }
            }

            // Details display area
            TextArea {
                id: detailsDisplay
                Layout.fillWidth: true
                Layout.fillHeight: true
                readOnly: true
                placeholderText: ThemeProvider.getCatchphrase("placeholder_select_satellite", "Select a satellite to see details.")
                textFormat: TextArea.RichText
                font: ThemeProvider.getFont("body")
                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey, "black")
                background: Rectangle {
                    color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey, "white")
                    border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey, "gray")
                    radius: ThemeProvider.getStyle("text_input").radius || 2
                }

                // Example connection if satelliteTree selection changes
                // Connections {
                //     target: satelliteTree.selection
                //     function onCurrentIndexChanged() {
                //         var selectedNode = satelliteTree.model.get(satelliteTree.currentIndex)
                //         if (selectedNode && selectedNode.isSensor) { // isSensor is a hypothetical property
                //             detailsDisplay.text = backend.getSatelliteDetailsAsHtml(selectedNode.id)
                //         } else {
                //             detailsDisplay.text = "Select a sensor."
                //         }
                //     }
                // }
            }
        }
    }

    Component.onCompleted: {
        // Temporary: Populate detailsDisplay with some info about the satelliteData structure
        // This is for debugging until the TreeView model and delegate are fully functional.
        var data = backend.satelliteData; // This is an array of categories
        var tempDetails = "Satellite Categories and Sensors (Raw Structure):\n\n";
        if (data && data.length > 0) {
            for (var i = 0; i < data.length; i++) {
                tempDetails += "Category: " + data[i].name + "\n";
                if (data[i].sensors && data[i].sensors.length > 0) {
                    for (var j = 0; j < data[i].sensors.length; j++) {
                        tempDetails += "  - Sensor: " + data[i].sensors[j].id + " (" + data[i].sensors[j].type + ")\n";
                    }
                }
                tempDetails += "\n";
            }
        } else {
            tempDetails = "No satellite data available from backend or backend.satelliteData is not structured as expected.";
        }
        detailsDisplay.text = tempDetails;

        // Check if backend.satelliteData is suitable for TreeView
        // A proper model would be QAbstractItemModel based.
        // For now, this will likely not work as TreeView expects a model.
        // We will need to adapt or wrap backend.satelliteData.
        console.log("Satellite Data from backend for TreeView:", JSON.stringify(backend.satelliteData))
    }
}

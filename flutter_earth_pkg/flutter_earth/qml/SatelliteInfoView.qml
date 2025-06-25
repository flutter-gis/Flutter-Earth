import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "./" // For ThemeProvider

Rectangle {
    id: satelliteInfoView
    color: ThemeProvider.getColor("background", "white")
    anchors.fill: parent

    property var satelliteCategories: backend.getSatelliteCategories ? backend.getSatelliteCategories() : {}
    property string selectedSensor: ""

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        Label {
            text: ThemeProvider.getCatchphrase("view_SatelliteInfoView", "Satellite Information")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            text: "Browse available satellites and their capabilities. Learn about different sensors and their resolutions."
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            font: ThemeProvider.getFont("body")
            color: ThemeProvider.getColor("text_subtle")
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 20

            // Satellite Categories and Sensors List
            GroupBox {
                title: "Satellites & Sensors"
                Layout.fillWidth: true
                Layout.preferredWidth: parent.width * 0.4
                Layout.fillHeight: true
                font: ThemeProvider.getFont("body")

                ColumnLayout {
                    width: parent.width
                    spacing: 10

                    // Category Selection
                    ComboBox {
                        id: categoryCombo
                        model: Object.keys(satelliteCategories)
                        currentIndex: 0
                        onCurrentIndexChanged: {
                            if (currentIndex >= 0) {
                                var categoryName = model[currentIndex]
                                sensorList.model = satelliteCategories[categoryName] || []
                            }
                        }
                        font: ThemeProvider.getFont("body")
                        background: Rectangle {
                            color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey)
                            border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey)
                            radius: ThemeProvider.getStyle("text_input").radius
                        }
                        popup: Popup {
                            background: Rectangle {
                                color: ThemeProvider.getColor("list_bg")
                                border.color: ThemeProvider.getColor("widget_border")
                            }
                        }
                    }

                    // Sensor List
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: ThemeProvider.getColor("entry_bg")
                        border.color: ThemeProvider.getColor("widget_border")
                        radius: ThemeProvider.getStyle("text_input").radius || 3

                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 5
                            clip: true

                            ListView {
                                id: sensorList
                                model: []
                                delegate: Rectangle {
                                    width: parent.width
                                    height: 50
                                    color: ListView.isCurrentItem ? ThemeProvider.getColor("list_selected_bg") : (index % 2 === 0 ? ThemeProvider.getColor("entry_bg") : ThemeProvider.getColor("alternate_bg", ThemeProvider.getColor("entry_bg")))

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        spacing: 10

                                        Text {
                                            text: modelData.id || "Unknown Sensor"
                                            font: ThemeProvider.getFont("body")
                                            font.bold: true
                                            color: ThemeProvider.getColor("text")
                                            Layout.fillWidth: true
                                        }

                                        Text {
                                            text: modelData.type || "Unknown Type"
                                            font: ThemeProvider.getFont("body")
                                            font.pixelSize: ThemeProvider.getFont("body").pixelSize - 2
                                            color: ThemeProvider.getColor("text_subtle")
                                            Layout.fillWidth: true
                                        }

                                        Text {
                                            text: modelData.resolution ? modelData.resolution + "m" : "N/A"
                                            font: ThemeProvider.getFont("body")
                                            color: ThemeProvider.getColor("text_subtle")
                                        }
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            sensorList.currentIndex = index
                                            selectedSensor = modelData.id
                                            loadSensorDetails(modelData.id)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Sensor Details Display
            GroupBox {
                title: "Sensor Details"
                Layout.fillWidth: true
                Layout.fillHeight: true
                font: ThemeProvider.getFont("body")

                ScrollView {
                    anchors.fill: parent
                    clip: true

                    ColumnLayout {
                        width: parent.width
                        spacing: 15

                        // Sensor Overview
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 200
                            color: ThemeProvider.getColor("entry_bg")
                            border.color: ThemeProvider.getColor("widget_border")
                            radius: ThemeProvider.getStyle("text_input").radius || 3

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 15
                                spacing: 10

                                Text {
                                    id: sensorName
                                    text: "Select a sensor to view details"
                                    font: ThemeProvider.getFont("title")
                                    color: ThemeProvider.getColor("primary")
                                    Layout.fillWidth: true
                                    wrapMode: Text.WordWrap
                                }

                                GridLayout {
                                    columns: 2
                                    columnSpacing: 20
                                    rowSpacing: 8
                                    Layout.fillWidth: true

                                    Text { 
                                        id: typeLabel
                                        text: "Type:"
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text")
                                        font.bold: true 
                                    }
                                    Text { 
                                        id: typeValue
                                        text: ""
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text") 
                                    }

                                    Text { 
                                        id: resolutionLabel
                                        text: "Resolution:"
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text")
                                        font.bold: true 
                                    }
                                    Text { 
                                        id: resolutionValue
                                        text: ""
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text") 
                                    }

                                    Text { 
                                        id: bandsLabel
                                        text: "Bands:"
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text")
                                        font.bold: true 
                                    }
                                    Text { 
                                        id: bandsValue
                                        text: ""
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text")
                                        wrapMode: Text.WordWrap 
                                    }

                                    Text { 
                                        id: coverageLabel
                                        text: "Coverage:"
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text")
                                        font.bold: true 
                                    }
                                    Text { 
                                        id: coverageValue
                                        text: ""
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text") 
                                    }

                                    Text { 
                                        id: launchLabel
                                        text: "Launch Date:"
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text")
                                        font.bold: true 
                                    }
                                    Text { 
                                        id: launchValue
                                        text: ""
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text") 
                                    }

                                    Text { 
                                        id: statusLabel
                                        text: "Status:"
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text")
                                        font.bold: true 
                                    }
                                    Text { 
                                        id: statusValue
                                        text: ""
                                        font: ThemeProvider.getFont("body")
                                        color: ThemeProvider.getColor("text") 
                                    }
                                }
                            }
                        }

                        // Band Information
                        GroupBox {
                            title: "Band Information"
                            Layout.fillWidth: true
                            font: ThemeProvider.getFont("body")

                            ColumnLayout {
                                width: parent.width
                                spacing: 10

                                Repeater {
                                    id: bandRepeater
                                    model: []
                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 40
                                        color: index % 2 === 0 ? ThemeProvider.getColor("entry_bg") : ThemeProvider.getColor("alternate_bg", ThemeProvider.getColor("entry_bg"))
                                        radius: 3

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 10
                                            spacing: 15

                                            Text {
                                                text: "Band " + (index + 1)
                                                font: ThemeProvider.getFont("body")
                                                font.bold: true
                                                color: ThemeProvider.getColor("text")
                                                Layout.preferredWidth: 60
                                            }

                                            Text {
                                                text: modelData.name || "Unknown"
                                                font: ThemeProvider.getFont("body")
                                                color: ThemeProvider.getColor("text")
                                                Layout.fillWidth: true
                                            }

                                            Text {
                                                text: modelData.wavelength ? modelData.wavelength + " nm" : "N/A"
                                                font: ThemeProvider.getFont("body")
                                                color: ThemeProvider.getColor("text_subtle")
                                                Layout.preferredWidth: 100
                                            }

                                            Text {
                                                text: modelData.resolution ? modelData.resolution + "m" : "N/A"
                                                font: ThemeProvider.getFont("body")
                                                color: ThemeProvider.getColor("text_subtle")
                                                Layout.preferredWidth: 80
                                            }
                                        }
                                    }
                                }

                                Text {
                                    text: "No band information available"
                                    visible: bandRepeater.model.length === 0
                                    font: ThemeProvider.getFont("body")
                                    color: ThemeProvider.getColor("text_subtle")
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }

                        // Applications
                        GroupBox {
                            title: "Applications"
                            Layout.fillWidth: true
                            font: ThemeProvider.getFont("body")

                            Text {
                                id: applicationsText
                                text: "Select a sensor to see its applications"
                                font: ThemeProvider.getFont("body")
                                color: ThemeProvider.getColor("text")
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
            }
        }
    }

    // Functions
    function loadSensorDetails(sensorId) {
        var details = backend.getSatelliteDetails ? backend.getSatelliteDetails(sensorId) : {}
        
        // Update sensor overview
        sensorName.text = details.name || sensorId
        typeValue.text = details.type || "N/A"
        resolutionValue.text = details.resolution ? details.resolution + "m" : "N/A"
        bandsValue.text = details.bands ? details.bands.join(", ") : "N/A"
        coverageValue.text = details.coverage || "N/A"
        launchValue.text = details.launch_date || "N/A"
        statusValue.text = details.status || "N/A"

        // Update band information
        bandRepeater.model = details.band_info || []

        // Update applications
        applicationsText.text = details.applications || "No application information available"
    }

    Component.onCompleted: {
        // Initialize with first category if available
        if (Object.keys(satelliteCategories).length > 0) {
            categoryCombo.currentIndex = 0
        }
    }
}

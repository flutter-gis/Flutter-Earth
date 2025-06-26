import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "./" // For ThemeProvider

Rectangle {
    id: mapView
    color: ThemeProvider.getColor("background", "#fffde7")
    anchors.fill: parent

    property string mapType: "Street"
    property var mapTypes: [
        { label: "Street", value: "street" },
        { label: "Satellite", value: "satellite" },
        { label: "Terrain", value: "terrain" },
        { label: "Hybrid", value: "hybrid" },
        { label: "Night", value: "night" },
        { label: "Light", value: "light" }
    ]
    property var aoiCoords: [] // [minLon, minLat, maxLon, maxLat]
    property bool drawingAOI: false
    property var firstCorner: null
    property string viewId: ""
    property var mapCenter: [0, 0]
    property int zoomLevel: 10
    property real rotation: 0
    property real tilt: 0
    property bool isSynchronized: false

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        Text {
            text: qsTr("Interactive Map View")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
        }

        // Map placeholder with selectable type and AOI drawing
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            border.color: ThemeProvider.getColor("widget_border")
            border.width: 1
            radius: 3
            color: ThemeProvider.getColor("widget_bg")

            // Placeholder for map
            Rectangle {
                id: mapPlaceholder
                anchors.fill: parent
                anchors.margins: 5
                color: ThemeProvider.getColor("background")
                border.color: ThemeProvider.getColor("widget_border")
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "Map View\n(Interactive map will be implemented here)"
                    font: ThemeProvider.getFont("body")
                    color: ThemeProvider.getColor("text_subtle")
                    horizontalAlignment: Text.AlignHCenter
                }

                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton
                    onPressed: {
                        if (!drawingAOI) {
                            // Start AOI selection
                            firstCorner = Qt.point(mouse.x, mouse.y)
                            drawingAOI = true
                            aoiCoords = []
                        } else {
                            // Finish AOI selection
                            var secondCorner = Qt.point(mouse.x, mouse.y)
                            var minX = Math.min(firstCorner.x, secondCorner.x)
                            var maxX = Math.max(firstCorner.x, secondCorner.x)
                            var minY = Math.min(firstCorner.y, secondCorner.y)
                            var maxY = Math.max(firstCorner.y, secondCorner.y)
                            aoiCoords = [minX, minY, maxX, maxY]
                            drawingAOI = false
                        }
                    }
                }

                // AOI Rectangle overlay
                Rectangle {
                    id: aoiOverlay
                    visible: aoiCoords.length === 4
                    color: ThemeProvider.getColor("accent", "#0288d1")
                    opacity: 0.3
                    border.color: ThemeProvider.getColor("accent", "#0288d1")
                    border.width: 2
                    x: aoiCoords.length === 4 ? aoiCoords[0] : 0
                    y: aoiCoords.length === 4 ? aoiCoords[1] : 0
                    width: aoiCoords.length === 4 ? (aoiCoords[2] - aoiCoords[0]) : 0
                    height: aoiCoords.length === 4 ? (aoiCoords[3] - aoiCoords[1]) : 0
                }
            }
        }

        // Controls
        RowLayout {
            Layout.fillWidth: true
            spacing: 20

            // Map type selector
            RowLayout {
                spacing: 10
                Text { 
                    text: qsTr("Map Type:"); 
                    font: ThemeProvider.getFont("body"); 
                    color: ThemeProvider.getColor("text")
                }
                ComboBox {
                    id: mapTypeCombo
                    model: mapTypes
                    textRole: "label"
                    onCurrentIndexChanged: mapType = model[currentIndex].label
                    font: ThemeProvider.getFont("body")
                    background: Rectangle { 
                        color: ThemeProvider.getColor("entry_bg"); 
                        border.color: ThemeProvider.getColor("entry_border"); 
                        radius: 3
                    }
                    popup.background: Rectangle { 
                        color: ThemeProvider.getColor("list_bg"); 
                        border.color: ThemeProvider.getColor("widget_border") 
                    }
                }
            }

            // AOI Controls
            RowLayout {
                spacing: 10
                Button {
                    text: qsTr("Set AOI for Download")
                    enabled: aoiCoords.length === 4
                    onClicked: {
                        backend.setAOIFromMap(aoiCoords);
                        messageDialog.text = qsTr("AOI set for download:\n") + JSON.stringify(aoiCoords);
                        messageDialog.open();
                    }
                    font: ThemeProvider.getFont("button")
                    background: Rectangle { 
                        color: enabled ? ThemeProvider.getColor("accent") : ThemeProvider.getColor("disabled");
                        radius: 3;
                        border.color: enabled ? ThemeProvider.getColor("accent") : ThemeProvider.getColor("disabled")
                    }
                    contentItem: Text { 
                        text: parent.text; 
                        color: enabled ? "white" : ThemeProvider.getColor("text_disabled");
                        horizontalAlignment: Text.AlignHCenter;
                        verticalAlignment: Text.AlignVCenter
                    }
                }
                Button {
                    text: qsTr("Clear AOI")
                    enabled: aoiCoords.length === 4
                    onClicked: {
                        aoiCoords = [];
                        drawingAOI = false;
                    }
                    font: ThemeProvider.getFont("button")
                    background: Rectangle { 
                        color: ThemeProvider.getColor("button_bg");
                        radius: 3;
                        border.color: ThemeProvider.getColor("button_border")
                    }
                    contentItem: Text { 
                        text: parent.text; 
                        color: ThemeProvider.getColor("button_text");
                        horizontalAlignment: Text.AlignHCenter;
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }

        // Instructions
        Text {
            text: "Click and drag on the map to select an Area of Interest (AOI) for downloads. The selected area will be highlighted in blue."
            font: ThemeProvider.getFont("body")
            color: ThemeProvider.getColor("text_subtle")
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
    }

    Dialog {
        id: messageDialog
        title: qsTr("Map Info")
        modal: true
        standardButtons: Dialog.Ok
        width: 400
        height: 200

        property string text: ""

        Text {
            text: messageDialog.text
            font: ThemeProvider.getFont("body")
            color: ThemeProvider.getColor("text")
            wrapMode: Text.WordWrap
            anchors.fill: parent
        }
    }
} 
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtLocation 5.15
import QtPositioning 5.15
import "./" // For ThemeProvider

Rectangle {
    id: mapView
    color: ThemeProvider.getColor("background", "#fffde7")
    anchors.fill: parent

    property string mapType: "Street"
    property var mapTypes: [
        { label: "Street", value: Map.StreetMap },
        { label: "Satellite", value: Map.SatelliteMapDay },
        { label: "Terrain", value: Map.TerrainMap },
        { label: "Hybrid", value: Map.HybridMap },
        { label: "Night", value: Map.NightMap },
        { label: "Light", value: Map.LightMap }
    ]
    property var aoiCoords: [] // [minLon, minLat, maxLon, maxLat]
    property bool drawingAOI: false
    property var firstCorner: null

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

        // Map with selectable type and AOI drawing
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            border.color: ThemeProvider.getColor("widget_border")
            border.width: 1
            radius: ThemeProvider.getStyle("text_input").radius || 3

            Map {
                id: map
                anchors.fill: parent
                anchors.margins: 5
                plugin: Plugin { 
                    name: "osm"
                    PluginParameter {
                        name: "osm.useragent"
                        value: "Flutter Earth Application"
                    }
                }
                center: QtPositioning.coordinate(37.7749, -122.4194) // Default: San Francisco
                zoomLevel: 6
                activeMapType: mapTypes[mapTypeCombo.currentIndex].value

                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton
                    onPressed: {
                        if (!drawingAOI) {
                            // Start AOI selection
                            firstCorner = map.toCoordinate(Qt.point(mouse.x, mouse.y));
                            drawingAOI = true;
                            aoiCoords = [];
                        } else {
                            // Finish AOI selection
                            var secondCorner = map.toCoordinate(Qt.point(mouse.x, mouse.y));
                            var minLat = Math.min(firstCorner.latitude, secondCorner.latitude);
                            var maxLat = Math.max(firstCorner.latitude, secondCorner.latitude);
                            var minLon = Math.min(firstCorner.longitude, secondCorner.longitude);
                            var maxLon = Math.max(firstCorner.longitude, secondCorner.longitude);
                            aoiCoords = [minLon, minLat, maxLon, maxLat];
                            drawingAOI = false;
                        }
                    }
                }

                // AOI Rectangle overlay
                MapRectangle {
                    id: aoiOverlay
                    visible: aoiCoords.length === 4
                    color: ThemeProvider.getColor("accent", "#0288d1")
                    opacity: 0.3
                    border.color: ThemeProvider.getColor("accent", "#0288d1")
                    border.width: 2
                    topLeft: aoiCoords.length === 4 ? QtPositioning.coordinate(aoiCoords[1], aoiCoords[0]) : QtPositioning.coordinate(0,0)
                    bottomRight: aoiCoords.length === 4 ? QtPositioning.coordinate(aoiCoords[3], aoiCoords[2]) : QtPositioning.coordinate(0,0)
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
                        color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); 
                        border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); 
                        radius: ThemeProvider.getStyle("text_input").radius 
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
                        color: enabled ? ThemeProvider.getColor(ThemeProvider.styles.button_primary.backgroundColorKey, ThemeProvider.colors.accent) : ThemeProvider.getColor("disabled");
                        radius: ThemeProvider.getStyle("button_primary").radius;
                        border.color: enabled ? ThemeProvider.getColor(ThemeProvider.styles.button_primary.borderColorKey, ThemeProvider.colors.accent) : ThemeProvider.getColor("disabled")
                    }
                    contentItem: Text { 
                        text: parent.text; 
                        color: enabled ? ThemeProvider.getColor(ThemeProvider.styles.button_primary.textColorKey, "white") : ThemeProvider.getColor("text_disabled");
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
                        color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey);
                        radius: ThemeProvider.getStyle("button_default").radius;
                        border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                    }
                    contentItem: Text { 
                        text: parent.text; 
                        color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey);
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
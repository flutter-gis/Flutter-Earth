import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtLocation 5.15
import QtPositioning 5.15

Rectangle {
    id: mapView
    // color: "#fffde7" // Replaced by theme
    anchors.fill: parent
    color: mainContent.currentTheme.widget_bg // Use theme color

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
        anchors.centerIn: parent
        spacing: 20

        Text {
            text: qsTr("Map View")
            font.pointSize: 22
            font.bold: true
            color: mainContent.currentTheme.primary // Theme color
        }

        // Map with selectable type and AOI drawing
        Map {
            id: map
            Layout.fillWidth: true
            Layout.fillHeight: true // Make map take available vertical space in ColumnLayout
            Layout.minimumHeight: 300 // Ensure it has a reasonable minimum height
            plugin: Plugin { name: "osm" }
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
                color: Qt.rgba(mainContent.currentTheme.primary.r, mainContent.currentTheme.primary.g, mainContent.currentTheme.primary.b, 0.3) // Theme color with opacity
                border.color: mainContent.currentTheme.primary // Theme color
                border.width: 2
                topLeft: aoiCoords.length === 4 ? QtPositioning.coordinate(aoiCoords[1], aoiCoords[0]) : QtPositioning.coordinate(0,0)
                bottomRight: aoiCoords.length === 4 ? QtPositioning.coordinate(aoiCoords[3], aoiCoords[2]) : QtPositioning.coordinate(0,0)
            }
        }

        // Map type selector
        RowLayout {
            id: mapControlsRow // Added id for anchoring map
            spacing: 10
            Text { text: qsTr("Map Type:"); font.pointSize: 16; color: mainContent.currentTheme.text }
            ComboBox {
                id: mapTypeCombo
                model: mapTypes
                textRole: "label"
                onCurrentIndexChanged: mapType = model[currentIndex].label
                // Basic theming for ComboBox
            }
        }

        RowLayout {
            spacing: 10
            Button {
                text: qsTr("Set AOI for Download")
                enabled: aoiCoords.length === 4
                onClicked: {
                    backend.setSetting("area_of_interest", aoiCoords);
                    messageDialog.text = qsTr("AOI set for download:\n") + JSON.stringify(aoiCoords);
                    messageDialog.open();
                }
            }
            Button {
                text: qsTr("Clear AOI")
                enabled: aoiCoords.length === 4
                onClicked: {
                    aoiCoords = [];
                    drawingAOI = false;
                }
            }
        }
    }

    MessageDialog {
        id: messageDialog
        title: qsTr("Map Info")
        text: ""
        visible: false
        onAccepted: visible = false
    }
} 
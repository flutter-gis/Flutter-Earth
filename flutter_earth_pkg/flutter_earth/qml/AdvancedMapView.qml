// AdvancedMapView.qml is currently not used. All map tab and map view logic has been removed as per latest requirements.
// Only the sidebar and authentication dialog are shown in the application.

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import "./" // For MapView and ThemeProvider

Item {
    id: advancedMapView
    anchors.fill: parent
    
    property var mapViews: []
    property string activeTab: "main"
    property bool zenMode: false
    property int mapCounter: 1 // For unique map naming
    
    // Toolbar with Add Map button
    Row {
        id: mapToolbar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40
        spacing: 10
        padding: 10
        Rectangle {
            color: "transparent"
            width: 10; height: 1 // Spacer
        }
        Button {
            text: qsTr("Add Map")
            onClicked: {
                var newViewId = backend.createMapView("main", "Map " + (mapCounter + 1))
                mapCounter++
                var state = backend.getAdvancedGISState()
                mapViews = state.map_views || []
                activeTab = newViewId
            }
        }
    }
    
    // Tab bar for multiple map views
    TabBar {
        id: mapTabBar
        anchors.top: mapToolbar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40
        visible: !zenMode && mapViews.length > 0
        
        Repeater {
            model: mapViews
            
            TabButton {
                text: modelData.tab_title || "Map " + (index + 1)
                width: Math.max(100, implicitWidth)
                
                onClicked: {
                    activeTab = modelData.view_id
                    mapStack.currentIndex = index
                }
                // Optional: Add close button for non-main tabs
                visible: true
            }
        }
    }
    
    // Map stack for multiple views
    StackView {
        id: mapStack
        anchors.top: mapTabBar.visible ? mapTabBar.bottom : mapToolbar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        initialItem: MapView {
            id: mainMapView
        }
    }
    
    // Zen mode toggle button
    Button {
        id: zenModeButton
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 10
        width: 40
        height: 40
        text: zenMode ? "☐" : "⛶"
        visible: !zenMode || mapViews.length > 1
        
        background: Rectangle {
            color: ThemeProvider.getColor("button_bg")
            radius: 20
            border.color: ThemeProvider.getColor("button_border")
            border.width: 2
        }
        
        onClicked: {
            zenMode = !zenMode
            backend.toggleZenMode()
        }
    }
    
    // Synchronization controls
    Row {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.margins: 10
        spacing: 5
        visible: !zenMode && mapViews.length > 1
        
        Button {
            text: "Sync All"
            onClicked: {
                var viewIds = []
                for (var i = 0; i < mapViews.length; i++) {
                    viewIds.push(mapViews[i].view_id)
                }
                backend.synchronizeMapViews(viewIds)
            }
        }
        
        Button {
            text: "Unsync All"
            onClicked: {
                for (var i = 0; i < mapViews.length; i++) {
                    var state = mapViews[i]
                    state.synchronized = false
                    backend.setMapViewState(state.view_id, state)
                }
            }
        }
    }
    
    Component.onCompleted: {
        // On startup, do not show any map tabs
        mapViews = []
        activeTab = ""
        zenMode = false
        mapCounter = 0
        // Connect to backend signals as before
        if (backend.onMapViewStateChanged) {
            backend.onMapViewStateChanged.connect(function(viewId, newState) {
                for (var i = 0; i < mapViews.length; i++) {
                    if (mapViews[i].view_id === viewId) {
                        mapViews[i] = newState
                        mapViews = mapViews // Trigger update
                        break
                    }
                }
            })
        }
        if (backend.onWorkspaceLayoutChanged) {
            backend.onWorkspaceLayoutChanged.connect(function(layoutName) {
                var state = backend.getAdvancedGISState()
                mapViews = state.map_views ? state.map_views.filter(function(v) { return v.view_id.startsWith("map_"); }) : []
                activeTab = mapViews.length > 0 ? mapViews[0].view_id : ""
            })
        }
    }

    function clearTabsForZenMode() {
        mapViews = [];
        activeTab = "";
        mapCounter = 0;
    }
} 
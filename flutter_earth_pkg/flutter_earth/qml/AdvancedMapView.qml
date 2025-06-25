import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

Item {
    id: advancedMapView
    anchors.fill: parent
    
    property var mapViews: []
    property string activeTab: "main"
    property bool zenMode: false
    
    // Tab bar for multiple map views
    TabBar {
        id: mapTabBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40
        visible: !zenMode && mapViews.length > 1
        
        Repeater {
            model: mapViews
            
            TabButton {
                text: modelData.tab_title || "Map " + (index + 1)
                width: Math.max(100, implicitWidth)
                
                onClicked: {
                    activeTab = modelData.view_id
                    mapStack.currentIndex = index
                }
            }
        }
        
        // Add new map button
        TabButton {
            text: "+"
            width: 40
            
            onClicked: {
                var newViewId = backend.createMapView("main", "New Map")
                mapViews = backend.getAdvancedGISState().map_views
            }
        }
    }
    
    // Map stack for multiple views
    StackView {
        id: mapStack
        anchors.top: mapTabBar.visible ? mapTabBar.bottom : parent.top
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
        // Load initial state
        var state = backend.getAdvancedGISState()
        mapViews = state.map_views || []
        activeTab = state.current_layout || "main"
        zenMode = state.zen_mode || false
        
        // Connect to backend signals
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
                mapViews = state.map_views || []
                activeTab = state.current_layout || "main"
            })
        }
    }
} 
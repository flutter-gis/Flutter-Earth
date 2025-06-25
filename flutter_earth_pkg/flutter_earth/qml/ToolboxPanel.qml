import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: toolboxPanel
    anchors.fill: parent
    
    property string activeTool: ""
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 5
        
        // Tool search
        TextField {
            id: toolSearchField
            Layout.fillWidth: true
            placeholderText: "Search tools..."
            
            onTextChanged: filterTools()
        }
        
        // Tool categories
        TabBar {
            id: toolTabBar
            Layout.fillWidth: true
            
            TabButton {
                text: "Navigation"
            }
            
            TabButton {
                text: "Selection"
            }
            
            TabButton {
                text: "Measurement"
            }
            
            TabButton {
                text: "Analysis"
            }
            
            TabButton {
                text: "Drawing"
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
        
        // Tool content
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: toolTabBar.currentIndex
            
            // Navigation tools
            ScrollView {
                GridLayout {
                    columns: 2
                    rowSpacing: 5
                    columnSpacing: 5
                    
                    // Zoom tools
                    GroupBox {
                        title: "Zoom Tools"
                        Layout.fillWidth: true
                        Layout.columnSpan: 2
                        
                        GridLayout {
                            columns: 3
                            
                            Button {
                                text: "🔍+"
                                ToolTip.visible: hovered
                                ToolTip.text: "Zoom In"
                                Layout.fillWidth: true
                                
                                onClicked: activateTool("zoom_in")
                            }
                            
                            Button {
                                text: "🔍-"
                                ToolTip.visible: hovered
                                ToolTip.text: "Zoom Out"
                                Layout.fillWidth: true
                                
                                onClicked: activateTool("zoom_out")
                            }
                            
                            Button {
                                text: "🔍"
                                ToolTip.visible: hovered
                                ToolTip.text: "Zoom to Extent"
                                Layout.fillWidth: true
                                
                                onClicked: activateTool("zoom_extent")
                            }
                        }
                    }
                    
                    // Pan tool
                    Button {
                        text: "✋"
                        ToolTip.visible: hovered
                        ToolTip.text: "Pan"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "pan" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("pan")
                    }
                    
                    // Rotate tool
                    Button {
                        text: "🔄"
                        ToolTip.visible: hovered
                        ToolTip.text: "Rotate"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "rotate" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("rotate")
                    }
                    
                    // Go to coordinate
                    Button {
                        text: "📍"
                        ToolTip.visible: hovered
                        ToolTip.text: "Go to Coordinate"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: coordinateDialog.open()
                    }
                    
                    // Bookmark
                    Button {
                        text: "🔖"
                        ToolTip.visible: hovered
                        ToolTip.text: "Add Bookmark"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: bookmarkDialog.open()
                    }
                }
            }
            
            // Selection tools
            ScrollView {
                GridLayout {
                    columns: 2
                    rowSpacing: 5
                    columnSpacing: 5
                    
                    Button {
                        text: "👆"
                        ToolTip.visible: hovered
                        ToolTip.text: "Select by Point"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "select_point" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("select_point")
                    }
                    
                    Button {
                        text: "📦"
                        ToolTip.visible: hovered
                        ToolTip.text: "Select by Rectangle"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "select_rectangle" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("select_rectangle")
                    }
                    
                    Button {
                        text: "🔷"
                        ToolTip.visible: hovered
                        ToolTip.text: "Select by Polygon"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "select_polygon" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("select_polygon")
                    }
                    
                    Button {
                        text: "🔍"
                        ToolTip.visible: hovered
                        ToolTip.text: "Identify Features"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "identify" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("identify")
                    }
                    
                    Button {
                        text: "🧹"
                        ToolTip.visible: hovered
                        ToolTip.text: "Clear Selection"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: clearSelection()
                    }
                    
                    Button {
                        text: "📊"
                        ToolTip.visible: hovered
                        ToolTip.text: "Selection Statistics"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: showSelectionStats()
                    }
                }
            }
            
            // Measurement tools
            ScrollView {
                GridLayout {
                    columns: 2
                    rowSpacing: 5
                    columnSpacing: 5
                    
                    Button {
                        text: "📏"
                        ToolTip.visible: hovered
                        ToolTip.text: "Measure Distance"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "measure_distance" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("measure_distance")
                    }
                    
                    Button {
                        text: "📐"
                        ToolTip.visible: hovered
                        ToolTip.text: "Measure Area"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "measure_area" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("measure_area")
                    }
                    
                    Button {
                        text: "📐"
                        ToolTip.visible: hovered
                        ToolTip.text: "Measure Angle"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "measure_angle" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("measure_angle")
                    }
                    
                    Button {
                        text: "🎯"
                        ToolTip.visible: hovered
                        ToolTip.text: "Snap to Features"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "snap" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("snap")
                    }
                    
                    Button {
                        text: "📋"
                        ToolTip.visible: hovered
                        ToolTip.text: "Measurement History"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: showMeasurementHistory()
                    }
                    
                    Button {
                        text: "🧹"
                        ToolTip.visible: hovered
                        ToolTip.text: "Clear Measurements"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: clearMeasurements()
                    }
                }
            }
            
            // Analysis tools
            ScrollView {
                GridLayout {
                    columns: 2
                    rowSpacing: 5
                    columnSpacing: 5
                    
                    Button {
                        text: "📊"
                        ToolTip.visible: hovered
                        ToolTip.text: "Statistics"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: showStatistics()
                    }
                    
                    Button {
                        text: "🌡️"
                        ToolTip.visible: hovered
                        ToolTip.text: "Heatmap"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: createHeatmap()
                    }
                    
                    Button {
                        text: "📈"
                        ToolTip.visible: hovered
                        ToolTip.text: "Buffer Analysis"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: bufferAnalysis()
                    }
                    
                    Button {
                        text: "🔗"
                        ToolTip.visible: hovered
                        ToolTip.text: "Intersection"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: intersectionAnalysis()
                    }
                    
                    Button {
                        text: "🔄"
                        ToolTip.visible: hovered
                        ToolTip.text: "Swipe Tool"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "swipe" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("swipe")
                    }
                    
                    Button {
                        text: "🔍"
                        ToolTip.visible: hovered
                        ToolTip.text: "Magnifier"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "magnifier" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("magnifier")
                    }
                }
            }
            
            // Drawing tools
            ScrollView {
                GridLayout {
                    columns: 2
                    rowSpacing: 5
                    columnSpacing: 5
                    
                    Button {
                        text: "✏️"
                        ToolTip.visible: hovered
                        ToolTip.text: "Draw Point"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "draw_point" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("draw_point")
                    }
                    
                    Button {
                        text: "📏"
                        ToolTip.visible: hovered
                        ToolTip.text: "Draw Line"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "draw_line" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("draw_line")
                    }
                    
                    Button {
                        text: "🔷"
                        ToolTip.visible: hovered
                        ToolTip.text: "Draw Polygon"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "draw_polygon" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("draw_polygon")
                    }
                    
                    Button {
                        text: "⭕"
                        ToolTip.visible: hovered
                        ToolTip.text: "Draw Circle"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "draw_circle" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("draw_circle")
                    }
                    
                    Button {
                        text: "📝"
                        ToolTip.visible: hovered
                        ToolTip.text: "Add Text"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        background: Rectangle {
                            color: activeTool === "add_text" ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                            radius: 5
                        }
                        
                        onClicked: activateTool("add_text")
                    }
                    
                    Button {
                        text: "🧹"
                        ToolTip.visible: hovered
                        ToolTip.text: "Clear Drawings"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        
                        onClicked: clearDrawings()
                    }
                }
            }
        }
    }
    
    // Functions
    function activateTool(toolName) {
        activeTool = toolName
        backend.startMeasurement(toolName)
        console.log("Activated tool:", toolName)
    }
    
    function filterTools() {
        // Implementation for filtering tools
    }
    
    function clearSelection() {
        // Implementation for clearing selection
        console.log("Clear selection")
    }
    
    function showSelectionStats() {
        // Implementation for showing selection statistics
        console.log("Show selection statistics")
    }
    
    function showMeasurementHistory() {
        // Implementation for showing measurement history
        console.log("Show measurement history")
    }
    
    function clearMeasurements() {
        // Implementation for clearing measurements
        console.log("Clear measurements")
    }
    
    function showStatistics() {
        // Implementation for showing statistics
        console.log("Show statistics")
    }
    
    function createHeatmap() {
        // Implementation for creating heatmap
        console.log("Create heatmap")
    }
    
    function bufferAnalysis() {
        // Implementation for buffer analysis
        console.log("Buffer analysis")
    }
    
    function intersectionAnalysis() {
        // Implementation for intersection analysis
        console.log("Intersection analysis")
    }
    
    function clearDrawings() {
        // Implementation for clearing drawings
        console.log("Clear drawings")
    }
    
    // Dialogs
    Dialog {
        id: coordinateDialog
        title: "Go to Coordinate"
        width: 300
        height: 150
        modal: true
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 10
            
            Label {
                text: "Latitude:"
            }
            
            TextField {
                id: latField
                Layout.fillWidth: true
                placeholderText: "Enter latitude"
            }
            
            Label {
                text: "Longitude:"
            }
            
            TextField {
                id: lonField
                Layout.fillWidth: true
                placeholderText: "Enter longitude"
            }
            
            RowLayout {
                Layout.fillWidth: true
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Go"
                    onClicked: {
                        var lat = parseFloat(latField.text)
                        var lon = parseFloat(lonField.text)
                        if (!isNaN(lat) && !isNaN(lon)) {
                            // Implementation for going to coordinate
                            console.log("Go to coordinate:", lat, lon)
                        }
                        coordinateDialog.close()
                    }
                }
                
                Button {
                    text: "Cancel"
                    onClicked: coordinateDialog.close()
                }
            }
        }
    }
    
    Dialog {
        id: bookmarkDialog
        title: "Add Bookmark"
        width: 300
        height: 200
        modal: true
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 10
            
            Label {
                text: "Name:"
            }
            
            TextField {
                id: bookmarkNameField
                Layout.fillWidth: true
                placeholderText: "Enter bookmark name"
            }
            
            Label {
                text: "Description:"
            }
            
            TextField {
                id: bookmarkDescField
                Layout.fillWidth: true
                placeholderText: "Enter description"
            }
            
            RowLayout {
                Layout.fillWidth: true
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Add"
                    onClicked: {
                        var name = bookmarkNameField.text
                        var desc = bookmarkDescField.text
                        if (name) {
                            // Implementation for adding bookmark
                            console.log("Add bookmark:", name, desc)
                        }
                        bookmarkDialog.close()
                    }
                }
                
                Button {
                    text: "Cancel"
                    onClicked: bookmarkDialog.close()
                }
            }
        }
    }
}

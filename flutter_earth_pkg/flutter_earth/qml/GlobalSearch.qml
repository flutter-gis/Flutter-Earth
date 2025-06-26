import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

Window {
    id: globalSearch
    visible: false
    width: 600
    height: 400
    title: "Global Search & Command Palette"
    modality: Qt.NonModal
    flags: Qt.Window | Qt.FramelessWindowHint
    
    property var searchResults: []
    property string currentQuery: ""
    
    Rectangle {
        anchors.fill: parent
        color: ThemeProvider.getColor("widget_bg")
        border.color: ThemeProvider.getColor("widget_border")
        border.width: 2
        radius: 8
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 10
            
            // Search input
            TextField {
                id: searchInput
                Layout.fillWidth: true
                placeholderText: "Search layers, tools, bookmarks, or type commands..."
                text: currentQuery
                
                onTextChanged: {
                    currentQuery = text
                    performSearch()
                }
                
                onAccepted: {
                    if (searchResults.length > 0) {
                        executeResult(searchResults[0])
                    }
                }
                
                background: Rectangle {
                    color: ThemeProvider.getColor("entry_bg")
                    border.color: ThemeProvider.getColor("entry_border")
                    border.width: 1
                    radius: 5
                }
            }
            
            // Search results
            ListView {
                id: resultsList
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: searchResults
                spacing: 2
                
                delegate: Rectangle {
                    width: resultsList.width
                    height: 50
                    color: index === resultsList.currentIndex ? ThemeProvider.getColor("list_selected_bg") : ThemeProvider.getColor("list_bg")
                    border.color: ThemeProvider.getColor("widget_border")
                    border.width: 1
                    radius: 4
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 10
                        
                        // Result icon
                        Text {
                            text: getResultIcon(modelData.type)
                            font.pixelSize: 20
                            color: ThemeProvider.getColor("text")
                        }
                        
                        // Result content
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            
                            Text {
                                text: modelData.name || modelData.description
                                font.family: ThemeProvider.getFont("body").family
                                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                                font.bold: true
                                color: ThemeProvider.getColor("text")
                                elide: Text.ElideRight
                            }
                            
                            Text {
                                text: modelData.description || ""
                                font.family: ThemeProvider.getFont("body").family
                                font.pixelSize: 10
                                color: ThemeProvider.getColor("text_subtle")
                                elide: Text.ElideRight
                                visible: modelData.description
                            }
                        }
                        
                        // Keyboard shortcut hint
                        Text {
                            text: getKeyboardShortcut(modelData.type, modelData.name)
                            font.family: ThemeProvider.getFont("body").family
                            font.pixelSize: 10
                            color: ThemeProvider.getColor("text_subtle")
                            visible: getKeyboardShortcut(modelData.type, modelData.name) !== ""
                        }
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            resultsList.currentIndex = index
                            executeResult(modelData)
                        }
                    }
                }
                
                highlight: Rectangle {
                    color: ThemeProvider.getColor("list_selected_bg")
                    radius: 4
                }
            }
            
            // Status bar
            RowLayout {
                Layout.fillWidth: true
                height: 20
                
                Text {
                    text: searchResults.length + " results"
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: 10
                    color: ThemeProvider.getColor("text_subtle")
                }
                
                Item { Layout.fillWidth: true }
                
                Text {
                    text: "↑↓ Navigate • Enter Execute • Esc Close"
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: 10
                    color: ThemeProvider.getColor("text_subtle")
                }
            }
        }
    }
    
    // Functions
    function performSearch() {
        if (currentQuery.length < 2) {
            searchResults = []
            return
        }
        
        // Search using backend
        var results = backend.search(currentQuery)
        
        // Add command suggestions
        var commands = getCommandSuggestions(currentQuery)
        results = results.concat(commands)
        
        searchResults = results
    }
    
    function getCommandSuggestions(query) {
        var commands = []
        var queryLower = query.toLowerCase()
        
        // Tool commands
        var tools = ["zoom", "pan", "select", "measure", "identify", "swipe", "rotate", "tilt", "magnifier", "bookmark", "snap", "grid"]
        for (var i = 0; i < tools.length; i++) {
            if (tools[i].indexOf(queryLower) !== -1) {
                commands.push({
                    type: "command",
                    name: "Activate " + tools[i] + " tool",
                    description: "Switch to " + tools[i] + " tool",
                    action: "tool",
                    tool: tools[i]
                })
            }
        }
        
        // Layer commands
        if (queryLower.indexOf("layer") !== -1) {
            commands.push({
                type: "command",
                name: "Add Layer",
                description: "Open layer addition dialog",
                action: "add_layer"
            })
        }
        
        // View commands
        if (queryLower.indexOf("view") !== -1) {
            commands.push({
                type: "command",
                name: "New Map View",
                description: "Create a new map view",
                action: "new_map_view"
            })
        }
        
        // Settings commands
        if (queryLower.indexOf("setting") !== -1 || queryLower.indexOf("config") !== -1) {
            commands.push({
                type: "command",
                name: "Open Settings",
                description: "Open application settings",
                action: "open_settings"
            })
        }
        
        return commands
    }
    
    function executeResult(result) {
        switch (result.type) {
            case "layer":
                // Select and zoom to layer
                console.log("Execute layer:", result.id)
                break
                
            case "bookmark":
                // Go to bookmark
                console.log("Go to bookmark:", result.name)
                break
                
            case "tool":
                // Activate tool
                console.log("Activate tool:", result.name)
                break
                
            case "command":
                executeCommand(result.action, result)
                break
        }
        
        // Close search window
        globalSearch.close()
    }
    
    function executeCommand(action, data) {
        switch (action) {
            case "tool":
                backend.startMeasurement(data.tool)
                break
                
            case "add_layer":
                // Open layer addition dialog
                console.log("Open add layer dialog")
                break
                
            case "new_map_view":
                backend.createMapView("main", "New Map")
                break
                
            case "open_settings":
                // Open settings view
                console.log("Open settings")
                break
        }
    }
    
    function getResultIcon(type) {
        switch (type) {
            case "layer": return "🗺️"
            case "bookmark": return "🔖"
            case "tool": return "🔧"
            case "command": return "⚡"
            default: return "📄"
        }
    }
    
    function getKeyboardShortcut(type, name) {
        switch (type) {
            case "tool":
                switch (name) {
                    case "zoom": return "Ctrl+Z"
                    case "pan": return "Ctrl+P"
                    case "select": return "Ctrl+S"
                    case "measure": return "Ctrl+M"
                    default: return ""
                }
            default: return ""
        }
    }
    
    // Keyboard navigation
    Keys.onPressed: function(event) {
        switch (event.key) {
            case Qt.Key_Up:
                if (resultsList.currentIndex > 0) {
                    resultsList.currentIndex--
                }
                event.accepted = true
                break
                
            case Qt.Key_Down:
                if (resultsList.currentIndex < searchResults.length - 1) {
                    resultsList.currentIndex++
                }
                event.accepted = true
                break
                
            case Qt.Key_Return:
            case Qt.Key_Enter:
                if (searchResults.length > 0 && resultsList.currentIndex >= 0) {
                    executeResult(searchResults[resultsList.currentIndex])
                }
                event.accepted = true
                break
                
            case Qt.Key_Escape:
                globalSearch.close()
                event.accepted = true
                break
        }
    }
    
    // Show/hide functions
    function show() {
        visible = true
        searchInput.focus = true
        searchInput.selectAll()
        raise()
        requestActivate()
    }
    
    function hide() {
        visible = false
    }
    
    Component.onCompleted: {
        // Position window in center of main window
        var mainWindow = ApplicationWindow.window
        if (mainWindow) {
            x = mainWindow.x + mainWindow.width / 2 - width / 2
            y = mainWindow.y + mainWindow.height / 2 - height / 2
        }
    }
} 
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

Window {
    id: dockablePanel
    visible: false
    flags: Qt.Window | Qt.FramelessWindowHint
    modality: Qt.NonModal
    
    property string panelType: ""
    property bool docked: true
    property string dockPosition: "left"
    property int panelWidth: 250
    property int panelHeight: 400
    property int zOrder: 0
    
    // Panel content
    Rectangle {
        id: panelBackground
        anchors.fill: parent
        color: ThemeProvider.getColor("widget_bg")
        border.color: ThemeProvider.getColor("widget_border")
        border.width: 2
        radius: 8
        
        // Title bar
        Rectangle {
            id: titleBar
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 30
            color: ThemeProvider.getColor("primary")
            radius: 6
            
            Text {
                id: titleText
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: 8
                text: getPanelTitle(panelType)
                color: ThemeProvider.getColor("text_on_primary")
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                font.bold: true
            }
            
            // Control buttons
            Row {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: 5
                spacing: 5
                
                Button {
                    id: dockButton
                    width: 20
                    height: 20
                    text: docked ? "⛶" : "⊞"
                    
                    background: Rectangle {
                        color: "transparent"
                        border.color: ThemeProvider.getColor("text_on_primary")
                        border.width: 1
                        radius: 3
                    }
                    
                    onClicked: {
                        if (docked) {
                            undockPanel()
                        } else {
                            dockPanel()
                        }
                    }
                }
                
                Button {
                    id: closeButton
                    width: 20
                    height: 20
                    text: "×"
                    
                    background: Rectangle {
                        color: "transparent"
                        border.color: ThemeProvider.getColor("text_on_primary")
                        border.width: 1
                        radius: 3
                    }
                    
                    onClicked: {
                        hidePanel()
                    }
                }
            }
        }
        
        // Panel content area
        Item {
            id: contentArea
            anchors.top: titleBar.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 5
            
            // Load appropriate content based on panel type
            Loader {
                id: contentLoader
                anchors.fill: parent
                source: getPanelContent(panelType)
            }
        }
    }
    
    // Resize handles
    Rectangle {
        id: resizeHandle
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: 10
        height: 10
        color: ThemeProvider.getColor("accent")
        radius: 5
        visible: !docked
        
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.SizeFDiagCursor
            
            property point startPos
            property point startSize
            
            onPressed: {
                startPos = Qt.point(mouse.x, mouse.y)
                startSize = Qt.point(dockablePanel.width, dockablePanel.height)
            }
            
            onPositionChanged: {
                if (pressed) {
                    var deltaX = mouse.x - startPos.x
                    var deltaY = mouse.y - startPos.y
                    dockablePanel.width = Math.max(200, startSize.x + deltaX)
                    dockablePanel.height = Math.max(200, startSize.y + deltaY)
                }
            }
        }
    }
    
    // Functions
    function getPanelTitle(type) {
        switch (type) {
            case "layer_list": return "Layers"
            case "attribute_table": return "Attribute Table"
            case "toolbox": return "Tools"
            case "search": return "Search"
            case "bookmarks": return "Bookmarks"
            case "measurement": return "Measurements"
            case "time_slider": return "Time Slider"
            case "coordinate_display": return "Coordinates"
            case "scale_bar": return "Scale Bar"
            case "magnifier": return "Magnifier"
            case "notification_center": return "Notifications"
            case "task_manager": return "Tasks"
            case "help_panel": return "Help"
            case "style_manager": return "Styles"
            case "statistics": return "Statistics"
            default: return "Panel"
        }
    }
    
    function getPanelContent(type) {
        switch (type) {
            case "layer_list": return "LayerListPanel.qml"
            case "attribute_table": return "AttributeTablePanel.qml"
            case "toolbox": return "ToolboxPanel.qml"
            case "search": return "GlobalSearch.qml"
            case "bookmarks": return "BookmarksPanel.qml"
            case "measurement": return "" // TODO: Create MeasurementPanel.qml
            case "time_slider": return "" // TODO: Create TimeSliderPanel.qml
            case "coordinate_display": return "" // TODO: Create CoordinateDisplayPanel.qml
            case "scale_bar": return "" // TODO: Create ScaleBarPanel.qml
            case "magnifier": return "" // TODO: Create MagnifierPanel.qml
            case "notification_center": return "" // TODO: Create NotificationCenterPanel.qml
            case "task_manager": return "" // TODO: Create TaskManagerPanel.qml
            case "help_panel": return "HelpPopup.qml"
            case "style_manager": return "" // TODO: Create StyleManagerPanel.qml
            case "statistics": return "" // TODO: Create StatisticsPanel.qml
            default: return ""
        }
    }
    
    function showPanel() {
        visible = true
        raise()
        requestActivate()
    }
    
    function hidePanel() {
        visible = false
    }
    
    function undockPanel() {
        docked = false
        dockPosition = "floating"
        
        // Position the floating window
        var mainWindow = ApplicationWindow.window
        if (mainWindow) {
            x = mainWindow.x + mainWindow.width / 2 - width / 2
            y = mainWindow.y + mainWindow.height / 2 - height / 2
        }
        
        // Update backend
        var state = {
            docked: false,
            position: "floating",
            position_coords: [x, y],
            size: [width, height]
        }
        backend.setPanelState(panelType, state)
    }
    
    function dockPanel() {
        docked = true
        dockPosition = "left" // Default position
        
        // Update backend
        var state = {
            docked: true,
            position: dockPosition,
            size: [width, height]
        }
        backend.setPanelState(panelType, state)
        
        // Hide floating window
        hidePanel()
    }
    
    function updateState(newState) {
        docked = newState.docked || false
        dockPosition = newState.position || "left"
        panelWidth = newState.size ? newState.size[0] : 250
        panelHeight = newState.size ? newState.size[1] : 400
        zOrder = newState.z_order || 0
        
        if (!docked) {
            width = panelWidth
            height = panelHeight
            if (newState.position_coords) {
                x = newState.position_coords[0]
                y = newState.position_coords[1]
            }
        }
    }
    
    Component.onCompleted: {
        // Set initial size
        width = panelWidth
        height = panelHeight
    }
} 
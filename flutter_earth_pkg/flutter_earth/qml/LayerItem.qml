import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: layerItem
    anchors.fill: parent
    
    property var layerData: null
    property bool selected: false
    
    signal visibilityChanged(bool visible)
    signal opacityChanged(real opacity)
    signal layerSelected(string layerId)
    signal layerRemoved(string layerId)
    signal layerIsolated(string layerId)
    signal layerZoomed(string layerId)
    
    color: selected ? ThemeProvider.getColor("list_selected_bg") : ThemeProvider.getColor("list_bg")
    border.color: ThemeProvider.getColor("widget_border")
    border.width: 1
    radius: 4
    
    MouseArea {
        anchors.fill: parent
        
        onClicked: {
            selected = !selected
            layerSelected(layerData.layer_id)
        }
        
        onDoubleClicked: {
            // Zoom to layer
            layerZoomed(layerData.layer_id)
        }
        
        onPressAndHold: {
            contextMenu.popup()
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 5
        spacing: 2
        
        // Layer header
        RowLayout {
            Layout.fillWidth: true
            height: 20
            
            // Visibility toggle
            CheckBox {
                id: visibilityCheckBox
                checked: layerData ? layerData.visible : false
                
                onCheckedChanged: {
                    if (layerData) {
                        visibilityChanged(checked)
                    }
                }
            }
            
            // Layer icon
            Rectangle {
                width: 16
                height: 16
                color: getLayerColor(layerData ? layerData.type : "")
                radius: 2
            }
            
            // Layer name
            Text {
                id: layerNameText
                text: layerData ? layerData.name : ""
                Layout.fillWidth: true
                elide: Text.ElideRight
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                color: ThemeProvider.getColor("text")
            }
            
            // Expand/collapse button for groups
            Button {
                id: expandButton
                width: 16
                height: 16
                text: layerData && layerData.group ? "▼" : ""
                visible: layerData && layerData.group
                
                background: Rectangle {
                    color: "transparent"
                }
                
                onClicked: {
                    if (layerData) {
                        layerData.expanded = !layerData.expanded
                    }
                }
            }
        }
        
        // Opacity slider
        RowLayout {
            Layout.fillWidth: true
            height: 20
            visible: layerData && layerData.visible
            
            Text {
                text: "Opacity:"
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: 10
                color: ThemeProvider.getColor("text_subtle")
            }
            
            Slider {
                id: opacitySlider
                Layout.fillWidth: true
                from: 0.0
                to: 1.0
                value: layerData ? layerData.opacity : 1.0
                stepSize: 0.1
                
                onValueChanged: {
                    if (layerData) {
                        opacityChanged(value)
                    }
                }
            }
            
            Text {
                text: Math.round(opacitySlider.value * 100) + "%"
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: 10
                color: ThemeProvider.getColor("text_subtle")
            }
        }
        
        // Layer info
        RowLayout {
            Layout.fillWidth: true
            height: 15
            visible: layerData
            
            Text {
                text: layerData ? layerData.type.toUpperCase() : ""
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: 8
                color: ThemeProvider.getColor("text_subtle")
            }
            
            Item { Layout.fillWidth: true }
            
            Text {
                text: layerData && layerData.group ? "Group: " + layerData.group : ""
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: 8
                color: ThemeProvider.getColor("text_subtle")
                visible: layerData && layerData.group
            }
        }
    }
    
    // Context menu
    Menu {
        id: contextMenu
        
        MenuItem {
            text: "Zoom to Layer"
            onTriggered: layerZoomed(layerData.layer_id)
        }
        
        MenuItem {
            text: "Isolate Layer"
            onTriggered: layerIsolated(layerData.layer_id)
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Properties"
            onTriggered: showLayerProperties()
        }
        
        MenuItem {
            text: "Style"
            onTriggered: showLayerStyle()
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Remove Layer"
            onTriggered: layerRemoved(layerData.layer_id)
        }
    }
    
    // Functions
    function getLayerColor(type) {
        switch (type) {
            case "raster": return "#4CAF50"
            case "vector": return "#2196F3"
            case "wms": return "#FF9800"
            case "wfs": return "#9C27B0"
            default: return "#757575"
        }
    }
    
    function showLayerProperties() {
        // Implementation for showing layer properties
        console.log("Show properties for layer:", layerData.layer_id)
    }
    
    function showLayerStyle() {
        // Implementation for showing layer style editor
        console.log("Show style for layer:", layerData.layer_id)
    }
    
    // Update layer data
    onLayerDataChanged: {
        if (layerData) {
            visibilityCheckBox.checked = layerData.visible
            opacitySlider.value = layerData.opacity
        }
    }
} 
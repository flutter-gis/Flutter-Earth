import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1

Item {
    id: layerListPanel
    anchors.fill: parent
    
    property var layers: []
    property string searchFilter: ""
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 5
        
        // Search and filter bar
        Rectangle {
            Layout.fillWidth: true
            height: 40
            color: ThemeProvider.getColor("entry_bg")
            border.color: ThemeProvider.getColor("entry_border")
            border.width: 1
            radius: 5
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                
                TextField {
                    id: searchField
                    Layout.fillWidth: true
                    placeholderText: "Search layers..."
                    text: searchFilter
                    
                    onTextChanged: {
                        searchFilter = text
                        filterLayers()
                    }
                    
                    background: Rectangle {
                        color: "transparent"
                    }
                }
                
                Button {
                    text: "☰"
                    width: 30
                    height: 30
                    
                    onClicked: layerMenu.open()
                    
                    Menu {
                        id: layerMenu
                        
                        MenuItem {
                            text: "Group Selected"
                            onTriggered: groupSelectedLayers()
                        }
                        
                        MenuItem {
                            text: "Ungroup Selected"
                            onTriggered: ungroupSelectedLayers()
                        }
                        
                        MenuSeparator {}
                        
                        MenuItem {
                            text: "Select All"
                            onTriggered: selectAllLayers()
                        }
                        
                        MenuItem {
                            text: "Deselect All"
                            onTriggered: deselectAllLayers()
                        }
                        
                        MenuSeparator {}
                        
                        MenuItem {
                            text: "Remove Selected"
                            onTriggered: removeSelectedLayers()
                        }
                    }
                }
            }
        }
        
        // Layer list
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            ListView {
                id: layerListView
                model: filteredLayers
                spacing: 2
                
                delegate: LayerItem {
                    layerData: modelData
                    width: layerListView.width
                    height: 60
                    
                    onVisibilityChanged: {
                        backend.updateLayerVisibility(layerData.layer_id, visible)
                    }
                    
                    onOpacityChanged: {
                        backend.updateLayerOpacity(layerData.layer_id, opacity)
                    }
                    
                    onLayerSelected: {
                        selectLayer(layerData.layer_id)
                    }
                    
                    onLayerRemoved: {
                        backend.removeLayer(layerData.layer_id)
                    }
                    
                    onLayerIsolated: {
                        backend.isolateLayer(layerData.layer_id)
                    }
                    
                    onLayerZoomed: {
                        zoomToLayer(layerData.layer_id)
                    }
                }
            }
        }
        
        // Layer controls
        RowLayout {
            Layout.fillWidth: true
            height: 40
            spacing: 5
            
            Button {
                text: "Add Layer"
                Layout.fillWidth: true
                
                onClicked: addLayerDialog.open()
            }
            
            Button {
                text: "Clear"
                Layout.preferredWidth: 60
                
                onClicked: clearAllLayers()
            }
        }
    }
    
    // Computed property for filtered layers
    property var filteredLayers: {
        if (searchFilter === "") {
            return layers
        }
        
        var filtered = []
        for (var i = 0; i < layers.length; i++) {
            var layer = layers[i]
            if (layer.name.toLowerCase().indexOf(searchFilter.toLowerCase()) !== -1) {
                filtered.push(layer)
            }
        }
        return filtered
    }
    
    // Functions
    function filterLayers() {
        // Trigger recomputation of filteredLayers
        filteredLayers = filteredLayers
    }
    
    function selectLayer(layerId) {
        // Implementation for selecting a layer
        console.log("Selected layer:", layerId)
    }
    
    function zoomToLayer(layerId) {
        // Implementation for zooming to layer extent
        console.log("Zoom to layer:", layerId)
    }
    
    function groupSelectedLayers() {
        var selectedLayers = getSelectedLayers()
        if (selectedLayers.length > 0) {
            var groupName = "Group " + (Math.floor(Math.random() * 1000))
            backend.groupLayers(selectedLayers, groupName)
        }
    }
    
    function ungroupSelectedLayers() {
        var selectedLayers = getSelectedLayers()
        for (var i = 0; i < selectedLayers.length; i++) {
            backend.groupLayers([selectedLayers[i]], "")
        }
    }
    
    function selectAllLayers() {
        // Implementation for selecting all layers
    }
    
    function deselectAllLayers() {
        // Implementation for deselecting all layers
    }
    
    function removeSelectedLayers() {
        var selectedLayers = getSelectedLayers()
        for (var i = 0; i < selectedLayers.length; i++) {
            backend.removeLayer(selectedLayers[i])
        }
    }
    
    function getSelectedLayers() {
        // Implementation to get selected layer IDs
        return []
    }
    
    function clearAllLayers() {
        for (var i = 0; i < layers.length; i++) {
            backend.removeLayer(layers[i].layer_id)
        }
    }
    
    // Add layer dialog
    Dialog {
        id: addLayerDialog
        title: "Add Layer"
        width: 400
        height: 300
        modal: true
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 10
            
            Label {
                text: "Layer Type:"
            }
            
            ComboBox {
                id: layerTypeCombo
                Layout.fillWidth: true
                model: ["Raster", "Vector", "WMS", "WFS"]
            }
            
            Label {
                text: "Source:"
            }
            
            TextField {
                id: layerSourceField
                Layout.fillWidth: true
                placeholderText: "Enter file path or URL"
            }
            
            Label {
                text: "Name:"
            }
            
            TextField {
                id: layerNameField
                Layout.fillWidth: true
                placeholderText: "Enter layer name"
            }
            
            RowLayout {
                Layout.fillWidth: true
                
                Button {
                    text: "Browse"
                    onClicked: fileDialog.open()
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Add"
                    onClicked: {
                        var layerInfo = {
                            name: layerNameField.text,
                            source: layerSourceField.text,
                            type: layerTypeCombo.currentText.toLowerCase()
                        }
                        backend.addLayer(layerInfo)
                        addLayerDialog.close()
                    }
                }
                
                Button {
                    text: "Cancel"
                    onClicked: addLayerDialog.close()
                }
            }
        }
    }
    
    // File dialog
    // FileDialog {
    FileDialog {
        id: fileDialog
        title: "Select Layer File"
        nameFilters: ["All Files (*)", "Raster Files (*.tif *.tiff *.jpg *.png)", "Vector Files (*.shp *.geojson *.kml)"]
        
        onAccepted: {
            layerSourceField.text = fileDialog.fileUrl.toString()
        }
    }
    
    Component.onCompleted: {
        // Load initial layers
        var state = backend.getAdvancedGISState()
        layers = state.layers
        
        // Connect to backend signals
        backend.onLayerStateChanged.connect(function(layerId, newState) {
            for (var i = 0; i < layers.length; i++) {
                if (layers[i].layer_id === layerId) {
                    layers[i] = newState
                    layers = layers // Trigger update
                    break
                }
            }
        })
    }
} 
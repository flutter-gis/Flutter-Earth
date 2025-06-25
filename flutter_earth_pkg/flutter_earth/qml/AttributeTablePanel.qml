import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.2

Rectangle {
    id: attributeTablePanel
    color: ThemeProvider.getColor("widget_bg")
    
    property var currentLayer: null
    property var tableData: []
    property var selectedRows: []
    property bool isEditing: false
    property var columnSettings: ({})
    
    // Column management
    property var visibleColumns: []
    property var columnOrder: []
    property var columnWidths: ({})
    
    // Filtering and search
    property string searchText: ""
    property var activeFilters: ({})
    property var filterOptions: ({})
    
    // Statistics
    property var columnStatistics: ({})
    property bool showStatistics: false
    
    // Conditional formatting
    property var conditionalFormats: ({})
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 5
        
        // Header with controls
        Rectangle {
            Layout.fillWidth: true
            height: 40
            color: ThemeProvider.getColor("primary")
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                spacing: 10
                
                // Layer selector
                ComboBox {
                    id: layerSelector
                    Layout.preferredWidth: 150
                    model: backend.getAllLayers()
                    textRole: "name"
                    onCurrentIndexChanged: {
                        if (currentIndex >= 0) {
                            currentLayer = model[currentIndex]
                            loadTableData()
                        }
                    }
                }
                
                // Search bar
                TextField {
                    id: searchField
                    Layout.fillWidth: true
                    placeholderText: "Search attributes..."
                    onTextChanged: {
                        searchText = text
                        applyFilters()
                    }
                }
                
                // Filter button
                Button {
                    text: "🔍"
                    tooltip: "Advanced Filter"
                    onClicked: filterDialog.open()
                }
                
                // Column management
                Button {
                    text: "📊"
                    tooltip: "Column Settings"
                    onClicked: columnSettingsDialog.open()
                }
                
                // Statistics toggle
                Button {
                    text: showStatistics ? "📈" : "📉"
                    tooltip: "Toggle Statistics"
                    onClicked: showStatistics = !showStatistics
                }
                
                // Edit mode toggle
                Button {
                    text: isEditing ? "💾" : "✏️"
                    tooltip: isEditing ? "Save Changes" : "Edit Mode"
                    onClicked: toggleEditMode()
                }
            }
        }
        
        // Statistics panel
        Rectangle {
            Layout.fillWidth: true
            height: showStatistics ? 80 : 0
            visible: showStatistics
            color: ThemeProvider.getColor("widget_bg")
            border.color: ThemeProvider.getColor("widget_border")
            border.width: 1
            
            ScrollView {
                anchors.fill: parent
                anchors.margins: 5
                
                RowLayout {
                    spacing: 20
                    
                    Repeater {
                        model: visibleColumns
                        
                        ColumnLayout {
                            spacing: 2
                            
                            Text {
                                text: modelData
                                font.family: ThemeProvider.getFont("body").family
                                font.pixelSize: 10
                                font.bold: true
                                color: ThemeProvider.getColor("text")
                            }
                            
                            Text {
                                text: getColumnStatistic(modelData)
                                font.family: ThemeProvider.getFont("body").family
                                font.pixelSize: 9
                                color: ThemeProvider.getColor("text_subtle")
                            }
                        }
                    }
                }
            }
        }
        
        // Table content
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: ThemeProvider.getColor("widget_bg")
            border.color: ThemeProvider.getColor("widget_border")
            border.width: 1
            
            Text {
                anchors.centerIn: parent
                text: "Attribute table will be displayed here"
                color: ThemeProvider.getColor("text_subtle")
            }
        }
        
        // Status bar
        Rectangle {
            Layout.fillWidth: true
            height: 20
            color: ThemeProvider.getColor("widget_bg")
            border.color: ThemeProvider.getColor("widget_border")
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                
                Text {
                    text: `Rows: ${tableData.length} | Selected: ${selectedRows.length}`
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: 9
                    color: ThemeProvider.getColor("text_subtle")
                }
                
                Item { Layout.fillWidth: true }
                
                Text {
                    text: isEditing ? "Editing Mode" : "View Mode"
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: 9
                    color: ThemeProvider.getColor("text_subtle")
                }
            }
        }
    }
    
    // Advanced Filter Dialog
    Dialog {
        id: filterDialog
        title: "Advanced Filter"
        width: 500
        height: 400
        modal: true
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 10
            
            // Filter conditions
            ListView {
                id: filterListView
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: Object.keys(activeFilters)
                
                delegate: Rectangle {
                    width: filterListView.width
                    height: 60
                    color: ThemeProvider.getColor("widget_bg")
                    border.color: ThemeProvider.getColor("widget_border")
                    border.width: 1
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 5
                        spacing: 10
                        
                        ComboBox {
                            Layout.preferredWidth: 120
                            model: visibleColumns
                            currentIndex: visibleColumns.indexOf(modelData)
                        }
                        
                        ComboBox {
                            Layout.preferredWidth: 80
                            model: ["equals", "contains", "greater than", "less than", "between"]
                        }
                        
                        TextField {
                            Layout.fillWidth: true
                            placeholderText: "Value"
                        }
                        
                        Button {
                            text: "✕"
                            onClicked: removeFilter(modelData)
                        }
                    }
                }
            }
            
            RowLayout {
                Layout.fillWidth: true
                
                Button {
                    text: "Add Filter"
                    onClicked: addFilter()
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Apply"
                    onClicked: {
                        applyFilters()
                        filterDialog.close()
                    }
                }
                
                Button {
                    text: "Cancel"
                    onClicked: filterDialog.close()
                }
            }
        }
    }
    
    // Column Settings Dialog
    Dialog {
        id: columnSettingsDialog
        title: "Column Settings"
        width: 400
        height: 300
        modal: true
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 10
            
            // Column visibility
            GroupBox {
                title: "Column Visibility"
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                ScrollView {
                    anchors.fill: parent
                    
                    ColumnLayout {
                        spacing: 5
                        
                        Repeater {
                            model: Object.keys(columnSettings)
                            
                            CheckBox {
                                text: modelData
                                checked: visibleColumns.includes(modelData)
                                onCheckedChanged: {
                                    if (checked) {
                                        visibleColumns.push(modelData)
                                    } else {
                                        visibleColumns = visibleColumns.filter(function(col) { return col !== modelData })
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            RowLayout {
                Layout.fillWidth: true
                
                Button {
                    text: "Reset to Default"
                    onClicked: resetColumnSettings()
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "OK"
                    onClicked: columnSettingsDialog.close()
                }
            }
        }
    }
    
    // Functions
    function loadTableData() {
        if (!currentLayer) return
        // Load attribute data from the layer
        console.log("Loading table data for layer:", currentLayer.name)
    }
    
    function getCellValue(rowIndex, columnName) {
        if (rowIndex < 0 || rowIndex >= tableData.length) return ""
        return tableData[rowIndex][columnName] || ""
    }
    
    function getCellColor(rowIndex, columnName) {
        var value = getCellValue(rowIndex, columnName)
        var format = conditionalFormats[columnName]
        
        if (format) {
            // Apply conditional formatting
            if (format.type === "range") {
                var numValue = parseFloat(value)
                if (!isNaN(numValue)) {
                    if (numValue >= format.min && numValue <= format.max) {
                        return format.color
                    }
                }
            } else if (format.type === "text") {
                if (value.includes(format.text)) {
                    return format.color
                }
            }
        }
        
        return ThemeProvider.getColor("text")
    }
    
    function calculateStatistics() {
        columnStatistics = {}
        
        for (var i = 0; i < visibleColumns.length; i++) {
            var col = visibleColumns[i]
            var values = []
            
            for (var j = 0; j < tableData.length; j++) {
                var value = tableData[j][col]
                if (value !== null && value !== undefined && value !== "") {
                    values.push(value)
                }
            }
            
            if (values.length > 0) {
                var numericValues = values.filter(function(v) { return !isNaN(parseFloat(v)) })
                
                if (numericValues.length > 0) {
                    var sum = numericValues.reduce(function(a, b) { return a + parseFloat(b) }, 0)
                    var avg = sum / numericValues.length
                    var min = Math.min(...numericValues.map(function(v) { return parseFloat(v) }))
                    var max = Math.max(...numericValues.map(function(v) { return parseFloat(v) }))
                    
                    columnStatistics[col] = {
                        count: values.length,
                        numeric: numericValues.length,
                        average: avg.toFixed(2),
                        min: min.toFixed(2),
                        max: max.toFixed(2)
                    }
                } else {
                    columnStatistics[col] = {
                        count: values.length,
                        unique: [...new Set(values)].length
                    }
                }
            }
        }
    }
    
    function getColumnStatistic(columnName) {
        var stats = columnStatistics[columnName]
        if (!stats) return "No data"
        
        if (stats.numeric) {
            return `Avg: ${stats.average} | Min: ${stats.min} | Max: ${stats.max}`
        } else {
            return `Count: ${stats.count} | Unique: ${stats.unique}`
        }
    }
    
    function applyFilters() {
        // Apply search and filter conditions
        var filteredData = tableData.filter(function(row) {
            // Search text filter
            if (searchText) {
                var found = false
                for (var col in row) {
                    if (row[col].toString().toLowerCase().includes(searchText.toLowerCase())) {
                        found = true
                        break
                    }
                }
                if (!found) return false
            }
            
            // Advanced filters
            for (var filterCol in activeFilters) {
                var filter = activeFilters[filterCol]
                var value = row[filterCol]
                
                if (filter.operator === "equals" && value !== filter.value) return false
                if (filter.operator === "contains" && !value.toString().includes(filter.value)) return false
                if (filter.operator === "greater than" && parseFloat(value) <= parseFloat(filter.value)) return false
                if (filter.operator === "less than" && parseFloat(value) >= parseFloat(filter.value)) return false
            }
            
            return true
        })
        
        tableListView.model = filteredData
    }
    
    function addFilter() {
        // Add a new filter condition
        var newFilter = {
            column: visibleColumns[0],
            operator: "equals",
            value: ""
        }
        activeFilters[newFilter.column] = newFilter
    }
    
    function removeFilter(columnName) {
        delete activeFilters[columnName]
    }
    
    function selectAllRows() {
        selectedRows = []
        for (var i = 0; i < tableData.length; i++) {
            selectedRows.push(i)
        }
    }
    
    function clearSelection() {
        selectedRows = []
    }
    
    function toggleEditMode() {
        isEditing = !isEditing
        if (!isEditing) {
            saveChanges()
        }
    }
    
    function saveChanges() {
        if (currentLayer) {
            console.log("Saving changes for layer:", currentLayer.name)
        }
    }
    
    function resetColumnSettings() {
        visibleColumns = Object.keys(columnSettings)
        columnWidths = {}
        for (var i = 0; i < visibleColumns.length; i++) {
            columnWidths[visibleColumns[i]] = 100
        }
    }
    
    function startCellEdit(rowIndex, mouseX) {
        // Start editing a specific cell
        // This would open an inline editor
    }
    
    Component.onCompleted: {
        if (backend.getAllLayers().length > 0) {
            layerSelector.currentIndex = 0
        }
    }
} 
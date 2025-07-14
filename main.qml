import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Dialogs 1.3

Window {
    id: mainWindow
    visible: true
    width: 1200
    height: 800
    title: "Earth Engine Catalog Web Crawler - QML Interface"
    color: "#f5f5f5"

    // Properties for data management
    property var datasets: []
    property var filteredDatasets: []
    property string searchText: ""
    property var selectedFilters: []
    property bool isCrawling: false
    property int progressValue: 0
    property string statusText: "Ready. Select an HTML file to begin."

    // File dialog
    FileDialog {
        id: fileDialog
        title: "Select HTML File"
        nameFilters: ["HTML Files (*.html *.htm)", "All Files (*)"]
        onAccepted: {
            filePathInput.text = fileDialog.fileUrl.toString().replace("file:///", "")
            startCrawlButton.enabled = true
            logMessage("Selected file: " + filePathInput.text)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        // Header
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: "#2c3e50"
            radius: 8

            Text {
                anchors.centerIn: parent
                text: "Earth Engine Catalog Web Crawler"
                font.pixelSize: 24
                font.bold: true
                color: "white"
            }
        }

        // File Selection Section
        GroupBox {
            Layout.fillWidth: true
            title: "HTML File Selection"
            font.bold: true

            RowLayout {
                anchors.fill: parent
                spacing: 10

                TextField {
                    id: filePathInput
                    Layout.fillWidth: true
                    placeholderText: "Select local HTML file to crawl..."
                    readOnly: true
                    background: Rectangle {
                        border.color: "#bdc3c7"
                        border.width: 1
                        radius: 4
                    }
                }

                Button {
                    text: "Browse"
                    onClicked: fileDialog.open()
                    background: Rectangle {
                        color: parent.pressed ? "#3498db" : "#2980b9"
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }

        // Options Section
        GroupBox {
            Layout.fillWidth: true
            title: "Crawling Options"
            font.bold: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 8

                CheckBox {
                    id: downloadThumbsCheck
                    text: "Download thumbnails"
                    checked: true
                }

                CheckBox {
                    id: extractDetailsCheck
                    text: "Extract detailed information"
                    checked: true
                }

                CheckBox {
                    id: saveIndividualCheck
                    text: "Save as individual JSON files"
                    checked: true
                }
            }
        }

        // Search and Filters Section
        GroupBox {
            Layout.fillWidth: true
            title: "Search & Filters"
            font.bold: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                // Search Bar
                TextField {
                    id: searchInput
                    Layout.fillWidth: true
                    placeholderText: "Search datasets..."
                    onTextChanged: {
                        searchText = text
                        filterDatasets()
                    }
                    background: Rectangle {
                        border.color: "#bdc3c7"
                        border.width: 1
                        radius: 4
                    }
                }

                // Filter Chips
                Flow {
                    Layout.fillWidth: true
                    spacing: 8

                    Button {
                        text: "All"
                        checkable: true
                        checked: true
                        onClicked: {
                            if (checked) {
                                selectedFilters = []
                                filterDatasets()
                            }
                        }
                        background: Rectangle {
                            color: parent.checked ? "#27ae60" : "#ecf0f1"
                            radius: 15
                        }
                        contentItem: Text {
                            text: parent.text
                            color: parent.checked ? "white" : "#2c3e50"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Button {
                        text: "Satellite"
                        checkable: true
                        onClicked: toggleFilter("Satellite")
                        background: Rectangle {
                            color: parent.checked ? "#3498db" : "#ecf0f1"
                            radius: 15
                        }
                        contentItem: Text {
                            text: parent.text
                            color: parent.checked ? "white" : "#2c3e50"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Button {
                        text: "Climate"
                        checkable: true
                        onClicked: toggleFilter("Climate")
                        background: Rectangle {
                            color: parent.checked ? "#e74c3c" : "#ecf0f1"
                            radius: 15
                        }
                        contentItem: Text {
                            text: parent.text
                            color: parent.checked ? "white" : "#2c3e50"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Button {
                        text: "Land Cover"
                        checkable: true
                        onClicked: toggleFilter("Land Cover")
                        background: Rectangle {
                            color: parent.checked ? "#f39c12" : "#ecf0f1"
                            radius: 15
                        }
                        contentItem: Text {
                            text: parent.text
                            color: parent.checked ? "white" : "#2c3e50"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Button {
                        text: "Hydrology"
                        checkable: true
                        onClicked: toggleFilter("Hydrology")
                        background: Rectangle {
                            color: parent.checked ? "#9b59b6" : "#ecf0f1"
                            radius: 15
                        }
                        contentItem: Text {
                            text: parent.text
                            color: parent.checked ? "white" : "#2c3e50"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }
        }

        // Status and Progress
        GroupBox {
            Layout.fillWidth: true
            title: "Status"
            font.bold: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                Text {
                    id: statusLabel
                    text: statusText
                    font.pixelSize: 14
                    color: "#2c3e50"
                }

                ProgressBar {
                    id: progressBar
                    Layout.fillWidth: true
                    value: progressValue / 100
                    visible: isCrawling
                    background: Rectangle {
                        color: "#ecf0f1"
                        radius: 4
                    }
                    contentItem: Rectangle {
                        color: "#27ae60"
                        radius: 4
                        width: progressBar.width * progressBar.value
                    }
                }

                Text {
                    text: isCrawling ? progressValue + "%" : ""
                    font.pixelSize: 12
                    color: "#7f8c8d"
                    visible: isCrawling
                }
            }
        }

        // Advanced Feature Status Bar
        RowLayout {
            Layout.fillWidth: true
            spacing: 20
            Rectangle { color: "transparent"; width: 10; height: 1 }
            Text { id: spacyStatus; text: "spaCy: ?"; color: "#34495e"; font.bold: true }
            Text { id: bertStatus; text: "BERT: ?"; color: "#34495e"; font.bold: true }
            Text { id: geoStatus; text: "Geospatial: ?"; color: "#34495e"; font.bold: true }
            Text { id: dashboardStatus; text: "Dashboard: ?"; color: "#34495e"; font.bold: true }
            Text { id: configStatus; text: "Config: ?"; color: "#34495e"; font.bold: true }
            Item { Layout.fillWidth: true }
            Button {
                text: "Open Dashboard"
                onClicked: crawlerBackend.openDashboard()
            }
            Button {
                text: "Edit Config"
                onClicked: crawlerBackend.editConfig()
            }
        }

        // Control Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                id: startCrawlButton
                text: "Start Crawling"
                enabled: false
                onClicked: startCrawling()
                background: Rectangle {
                    color: parent.enabled ? (parent.pressed ? "#27ae60" : "#2ecc71") : "#bdc3c7"
                    radius: 4
                }
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }

            Button {
                id: stopCrawlButton
                text: "Stop"
                enabled: false
                onClicked: stopCrawling()
                background: Rectangle {
                    color: parent.enabled ? (parent.pressed ? "#e74c3c" : "#e67e22") : "#bdc3c7"
                    radius: 4
                }
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }

            Button {
                text: "Clear Console"
                onClicked: consoleOutput.clear()
                background: Rectangle {
                    color: parent.pressed ? "#95a5a6" : "#7f8c8d"
                    radius: 4
                }
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "Results: " + filteredDatasets.length + " datasets"
                font.pixelSize: 12
                color: "#7f8c8d"
            }
        }

        // Results & Multi-Tab Console
        GroupBox {
            Layout.fillWidth: true
            Layout.fillHeight: true
            title: "Results & Console"
            font.bold: true
            TabBar {
                id: tabBar
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                TabButton { text: "Datasets (" + filteredDatasets.length + ")" }
                TabButton { text: "Console" }
                TabButton { text: "ML Log" }
                TabButton { text: "Validation Log" }
                TabButton { text: "Error Log" }
            }
            StackLayout {
                anchors.top: tabBar.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.topMargin: 10
                currentIndex: tabBar.currentIndex
                // Datasets Tab
                ScrollView {
                    clip: true

                    ListView {
                        id: datasetsListView
                        model: filteredDatasets
                        spacing: 10

                        delegate: Rectangle {
                            width: datasetsListView.width
                            height: datasetCard.height
                            color: "transparent"

                            Rectangle {
                                id: datasetCard
                                width: parent.width
                                height: Math.max(120, contentLayout.height + 20)
                                color: "white"
                                radius: 8
                                border.color: "#ecf0f1"
                                border.width: 1

                                RowLayout {
                                    id: contentLayout
                                    anchors.fill: parent
                                    anchors.margins: 15
                                    spacing: 15

                                    // Thumbnail
                                    Rectangle {
                                        Layout.preferredWidth: 80
                                        Layout.preferredHeight: 80
                                        color: "#ecf0f1"
                                        radius: 4

                                        Image {
                                            anchors.fill: parent
                                            source: modelData.thumbnail_path || ""
                                            fillMode: Image.PreserveAspectCrop
                                            visible: modelData.thumbnail_path
                                        }

                                        Text {
                                            anchors.centerIn: parent
                                            text: "No Image"
                                            color: "#7f8c8d"
                                            visible: !modelData.thumbnail_path
                                        }
                                    }

                                    // Content
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        spacing: 5

                                        Text {
                                            text: modelData.title || "Untitled Dataset"
                                            font.pixelSize: 16
                                            font.bold: true
                                            color: "#2c3e50"
                                            wrapMode: Text.WordWrap
                                        }

                                        Text {
                                            text: modelData.description || "No description available"
                                            font.pixelSize: 12
                                            color: "#7f8c8d"
                                            wrapMode: Text.WordWrap
                                            maximumLineCount: 2
                                            elide: Text.ElideRight
                                        }

                                        // Tags
                                        Flow {
                                            spacing: 5

                                            Repeater {
                                                model: modelData.tags || []

                                                Rectangle {
                                                    color: "#3498db"
                                                    radius: 10
                                                    height: 20

                                                    Text {
                                                        anchors.centerIn: parent
                                                        anchors.margins: 8
                                                        text: modelData
                                                        font.pixelSize: 10
                                                        color: "white"
                                                    }
                                                }
                                            }
                                        }

                                        Text {
                                            text: "Provider: " + (modelData.provider || "Unknown")
                                            font.pixelSize: 10
                                            color: "#95a5a6"
                                        }
                                    }

                                    // Actions
                                    ColumnLayout {
                                        spacing: 5

                                        Button {
                                            text: "View"
                                            onClicked: Qt.openUrlExternally(modelData.url)
                                            background: Rectangle {
                                                color: parent.pressed ? "#3498db" : "#2980b9"
                                                radius: 4
                                            }
                                            contentItem: Text {
                                                text: parent.text
                                                color: "white"
                                                horizontalAlignment: Text.AlignHCenter
                                                verticalAlignment: Text.AlignVCenter
                                            }
                                        }

                                        Button {
                                            text: "Details"
                                            onClicked: showDatasetDetails(modelData)
                                            background: Rectangle {
                                                color: parent.pressed ? "#27ae60" : "#2ecc71"
                                                radius: 4
                                            }
                                            contentItem: Text {
                                                text: parent.text
                                                color: "white"
                                                horizontalAlignment: Text.AlignHCenter
                                                verticalAlignment: Text.AlignVCenter
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                // Console Tab
                ScrollView {
                    clip: true

                    TextArea {
                        id: consoleOutput
                        readOnly: true
                        wrapMode: TextArea.Wrap
                        font.family: "Consolas"
                        font.pixelSize: 12
                        background: Rectangle {
                            color: "#2c3e50"
                        }
                        color: "#ecf0f1"
                    }
                }
                // ML Log Tab
                ScrollView {
                    clip: true
                    TextArea {
                        id: mlLogOutput
                        readOnly: true
                        wrapMode: TextArea.Wrap
                        font.family: "Consolas"
                        font.pixelSize: 12
                        background: Rectangle {
                            color: "#2c3e50"
                        }
                        color: "#ecf0f1"
                    }
                }
                // Validation Log Tab
                ScrollView {
                    clip: true
                    TextArea {
                        id: validationLogOutput
                        readOnly: true
                        wrapMode: TextArea.Wrap
                        font.family: "Consolas"
                        font.pixelSize: 12
                        background: Rectangle {
                            color: "#2c3e50"
                        }
                        color: "#ecf0f1"
                    }
                }
                // Error Log Tab
                ScrollView {
                    clip: true
                    TextArea {
                        id: errorLogOutput
                        readOnly: true
                        wrapMode: TextArea.Wrap
                        font.family: "Consolas"
                        font.pixelSize: 12
                        background: Rectangle {
                            color: "#2c3e50"
                        }
                        color: "#e74c3c"
                    }
                }
            }
        }
    }

    // Functions
    function logMessage(message) {
        var timestamp = new Date().toLocaleTimeString()
        consoleOutput.append("[" + timestamp + "] " + message)
    }

    function toggleFilter(filterName) {
        var index = selectedFilters.indexOf(filterName)
        if (index > -1) {
            selectedFilters.splice(index, 1)
        } else {
            selectedFilters.push(filterName)
        }
        filterDatasets()
    }

    function filterDatasets() {
        filteredDatasets = datasets.filter(function(dataset) {
            // Search filter
            if (searchText && !dataset.title.toLowerCase().includes(searchText.toLowerCase()) && 
                !dataset.description.toLowerCase().includes(searchText.toLowerCase())) {
                return false
            }

            // Category filters
            if (selectedFilters.length > 0) {
                var hasMatchingTag = false
                for (var i = 0; i < selectedFilters.length; i++) {
                    if (dataset.tags && dataset.tags.some(function(tag) {
                        return tag.toLowerCase().includes(selectedFilters[i].toLowerCase())
                    })) {
                        hasMatchingTag = true
                        break
                    }
                }
                if (!hasMatchingTag) return false
            }

            return true
        })
    }

    function startCrawling() {
        isCrawling = true
        progressValue = 0
        statusText = "Crawling..."
        startCrawlButton.enabled = false
        stopCrawlButton.enabled = true
        logMessage("Starting crawl of: " + filePathInput.text)
        
        // Simulate crawling process (replace with actual backend integration)
        crawlingTimer.start()
    }

    function stopCrawling() {
        isCrawling = false
        statusText = "Crawling stopped"
        startCrawlButton.enabled = true
        stopCrawlButton.enabled = false
        crawlingTimer.stop()
        logMessage("Crawling stopped by user")
    }

    function showDatasetDetails(dataset) {
        // Create and show details dialog
        var detailsDialog = Qt.createComponent("DatasetDetailsDialog.qml")
        if (detailsDialog.status === Component.Ready) {
            var dialog = detailsDialog.createObject(mainWindow, {
                "dataset": dataset
            })
            dialog.open()
        }
    }

    // Timer for simulating crawling progress
    Timer {
        id: crawlingTimer
        interval: 100
        repeat: true
        onTriggered: {
            if (progressValue < 100) {
                progressValue += 1
                logMessage("Processing dataset " + progressValue + "...")
            } else {
                crawlingTimer.stop()
                isCrawling = false
                statusText = "Crawling complete!"
                startCrawlButton.enabled = true
                stopCrawlButton.enabled = false
                logMessage("Crawling complete! Processed datasets.")
                
                // Add sample data for demonstration
                datasets = [
                    {
                        title: "Landsat 8 Surface Reflectance",
                        description: "Landsat 8 Surface Reflectance (SR) data are available in Earth Engine as a collection of scenes.",
                        thumbnail_path: "",
                        url: "https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2",
                        tags: ["Satellite", "Landsat", "Surface Reflectance"],
                        provider: "USGS",
                        metadata: {
                            "Spatial Resolution": "30m",
                            "Temporal Coverage": "2013-present"
                        }
                    },
                    {
                        title: "MODIS Terra Surface Reflectance",
                        description: "MODIS Terra Surface Reflectance 8-Day Global 500m",
                        thumbnail_path: "",
                        url: "https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MOD09A1",
                        tags: ["Satellite", "MODIS", "Surface Reflectance"],
                        provider: "NASA",
                        metadata: {
                            "Spatial Resolution": "500m",
                            "Temporal Coverage": "2000-present"
                        }
                    }
                ]
                filterDatasets()
            }
        }
    }

    // Connections to backend signals for status and logs
    Connections {
        target: crawlerBackend
        onSpacyStatusChanged: spacyStatus.text = "spaCy: " + (arguments[0] ? "✔" : "✖")
        onBertStatusChanged: bertStatus.text = "BERT: " + (arguments[0] ? "✔" : "✖")
        onGeoStatusChanged: geoStatus.text = "Geospatial: " + (arguments[0] ? "✔" : "✖")
        onDashboardStatusChanged: dashboardStatus.text = "Dashboard: " + (arguments[0] ? "✔" : "✖")
        onConfigStatusChanged: configStatus.text = "Config: " + (arguments[0] ? "✔" : "✖")
        onMlLog: mlLogOutput.append(arguments[0])
        onValidationLog: validationLogOutput.append(arguments[0])
        onErrorLog: errorLogOutput.append(arguments[0])
    }
} 
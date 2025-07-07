import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    color: "#f9f9f9"
    anchors.fill: parent
    
    // Properties for crawler state
    property int crawlerProgress: 0
    property string crawlerStatus: "idle"
    property string crawlerMessage: "Ready to start crawler"
    property int satellitesFound: 0
    property int datasetsFound: 0
    
    // Connect to backend signals
    Connections {
        target: backend
        
        function onCrawlerProgressChanged(percentage, message) {
            crawlerProgress = percentage
            crawlerMessage = message
            if (percentage > 0) {
                crawlerStatus = "running"
            } else if (percentage === 100) {
                crawlerStatus = "completed"
            }
        }
        
        function onCrawlerStatusChanged(status, message) {
            crawlerStatus = status
            crawlerMessage = message
            if (status === "completed" || status === "stopped") {
                crawlerProgress = 0
            }
        }
        
        function onConsoleOutput(message) {
            consoleOutput.text += message + "\n"
            // Auto-scroll to bottom
            consoleOutput.cursorPosition = consoleOutput.text.length
        }
        
        function onSatelliteCountChanged(count) {
            satellitesFound = count
        }
        
        function onDatasetCountChanged(count) {
            datasetsFound = count
        }
    }
    
    Flickable {
        anchors.fill: parent
        contentWidth: Math.max(parent.width, 1100)
        contentHeight: column.implicitHeight + 60
        clip: true
        
        ColumnLayout {
            id: column
            width: Math.min(parent.width, 1100)
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 32
            anchors.top: parent.top
            anchors.topMargin: 32
            
            // Header
            Label {
                text: "Satellites & Crawler"
                font.pixelSize: 36
                color: "#2c3e50"
                font.bold: true
                Layout.alignment: Qt.AlignLeft
            }
            
            Label {
                text: "Manage satellite data crawling and view real-time progress."
                font.pixelSize: 18
                color: "#34495e"
                wrapMode: Text.WordWrap
                Layout.alignment: Qt.AlignLeft
            }
            
            // Controls Row
            RowLayout {
                Layout.fillWidth: true
                spacing: 24
                anchors.leftMargin: 0
                anchors.rightMargin: 0
                Button {
                    text: "🚀 Start Crawler"
                    enabled: crawlerStatus !== "running"
                    onClicked: backend.start_crawler()
                    Layout.preferredWidth: 200
                    font.pixelSize: 20
                    font.bold: true
                    background: Rectangle {
                        color: parent.pressed ? "#2980b9" : (parent.enabled ? "#3498db" : "#bdc3c7")
                        radius: 12
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#ffffff"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 20
                        font.bold: true
                    }
                }
                Button {
                    text: "⏸️ Pause Crawler"
                    enabled: crawlerStatus === "running"
                    onClicked: backend.stop_crawler()
                    Layout.preferredWidth: 200
                    font.pixelSize: 20
                    font.bold: true
                    background: Rectangle {
                        color: parent.pressed ? "#f39c12" : (parent.enabled ? "#f39c12" : "#bdc3c7")
                        radius: 12
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#ffffff"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 20
                        font.bold: true
                    }
                }
                Button {
                    text: "⏹️ Stop Crawler"
                    enabled: crawlerStatus === "running"
                    onClicked: backend.stop_crawler()
                    Layout.preferredWidth: 200
                    font.pixelSize: 20
                    font.bold: true
                    background: Rectangle {
                        color: parent.pressed ? "#c0392b" : (parent.enabled ? "#e74c3c" : "#bdc3c7")
                        radius: 12
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#ffffff"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 20
                        font.bold: true
                    }
                }
            }
            
            // Console Output Card
            Rectangle {
                color: "#fff"
                radius: 16
                border.color: "#e0e0e0"
                border.width: 1
                Layout.fillWidth: true
                Layout.preferredHeight: 260
                anchors.horizontalCenter: parent.horizontalCenter
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 32
                    spacing: 12
                    RowLayout {
                        Label {
                            text: "📝 Console Output"
                            font.pixelSize: 28
                            color: "#223"
                            font.bold: true
                        }
                        Item { Layout.fillWidth: true }
                        Button {
                            text: "🗑️ Clear"
                            onClicked: consoleOutput.text = ""
                            background: Rectangle {
                                color: parent.pressed ? "#c0392b" : "#e74c3c"
                                radius: 8
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#fff"
                                font.pixelSize: 16
                                font.bold: true
                            }
                        }
                    }
                    TextArea {
                        id: consoleOutput
                        readOnly: true
                        color: "#2c3e50"
                        font.family: "Consolas, Monaco, monospace"
                        font.pixelSize: 16
                        background: Rectangle {
                            color: "#f8f9fa"
                            radius: 8
                            border.color: "#e9ecef"
                            border.width: 1
                        }
                        padding: 16
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        wrapMode: TextEdit.Wrap
                        Component.onCompleted: {
                            text = "Console ready. Start the crawler to see real-time output.\n"
                        }
                    }
                }
            }
            
            // Satellites Table Card
            Rectangle {
                color: "#fff"
                radius: 16
                border.color: "#e0e0e0"
                border.width: 1
                Layout.fillWidth: true
                Layout.preferredHeight: 420
                anchors.horizontalCenter: parent.horizontalCenter
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 32
                    spacing: 12
                    RowLayout {
                        Label {
                            text: "🛰️ Satellites Data"
                            font.pixelSize: 28
                            color: "#223"
                            font.bold: true
                        }
                        Item { Layout.fillWidth: true }
                        Label {
                            text: "Total: " + (typeof satelliteModel.count === 'number' ? satelliteModel.count : 0)
                            font.pixelSize: 18
                            color: "#7f8c8d"
                        }
                    }
                    // Table Header
                    Rectangle {
                        color: "#f8f9fa"
                        radius: 8
                        height: 48
                        Layout.fillWidth: true
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 0
                            Label { text: "Satellite Name"; font.bold: true; font.pixelSize: 16; Layout.preferredWidth: 220; color: "#2c3e50"; }
                            Label { text: "Description"; font.bold: true; font.pixelSize: 16; Layout.preferredWidth: 340; color: "#2c3e50"; }
                            Label { text: "Datasets"; font.bold: true; font.pixelSize: 16; Layout.preferredWidth: 100; color: "#2c3e50"; horizontalAlignment: Text.AlignHCenter }
                            Label { text: "Status"; font.bold: true; font.pixelSize: 16; Layout.preferredWidth: 100; color: "#2c3e50"; horizontalAlignment: Text.AlignHCenter }
                            Label { text: "Actions"; font.bold: true; font.pixelSize: 16; Layout.preferredWidth: 100; color: "#2c3e50"; horizontalAlignment: Text.AlignHCenter }
                        }
                    }
                    // Table Content
                    ListView {
                        id: satelliteListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: satelliteModel
                        spacing: 0
                        clip: true
                        delegate: Rectangle {
                            width: parent.width
                            height: 56
                            color: index % 2 === 0 ? "#fff" : "#f8f9fa"
                            radius: 0
                            border.color: "#e9ecef"
                            border.width: 1
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 0
                                Label {
                                    text: model.name || "Unknown Satellite"
                                    font.pixelSize: 15
                                    color: "#2c3e50"
                                    font.bold: true
                                    Layout.preferredWidth: 220
                                    elide: Text.ElideRight
                                }
                                Label {
                                    text: model.description || "No description available"
                                    font.pixelSize: 14
                                    color: "#7f8c8d"
                                    Layout.preferredWidth: 340
                                    elide: Text.ElideRight
                                    maximumLineCount: 2
                                }
                                Label {
                                    text: model.datasets_count || 0
                                    font.pixelSize: 14
                                    color: "#27ae60"
                                    font.bold: true
                                    Layout.preferredWidth: 100
                                    horizontalAlignment: Text.AlignHCenter
                                }
                                Label {
                                    text: model.status || "Unknown"
                                    font.pixelSize: 14
                                    color: "#7f8c8d"
                                    Layout.preferredWidth: 100
                                    horizontalAlignment: Text.AlignHCenter
                                }
                                Button {
                                    text: "🔍 Details"
                                    onClicked: {
                                        consoleOutput.text += "Viewing details for: " + model.name + "\n"
                                    }
                                    background: Rectangle {
                                        color: parent.pressed ? "#2980b9" : "#3498db"
                                        radius: 6
                                    }
                                    contentItem: Text {
                                        text: parent.text
                                        color: "#fff"
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                        font.pixelSize: 13
                                        font.bold: true
                                    }
                                    Layout.preferredWidth: 100
                                }
                            }
                        }
                    }
                }
            }
        }
    }
} 
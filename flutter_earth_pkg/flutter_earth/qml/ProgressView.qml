import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import "./" // For ThemeProvider

Rectangle {
    id: progressView
    color: ThemeProvider.getColor("background", "#e8f5e9")
    anchors.fill: parent

    // Properties to hold progress data from backend
    // These should be updated via signals from AppBackend for real-time updates
    property real currentProgress: backend.getProgress ? backend.getProgress() : 0.0
    property string currentStatus: backend.getDownloadStatus ? backend.getDownloadStatus() : "No active downloads"
    property bool isBusy: currentProgress > 0 && currentProgress < 1.0
    property var downloadHistory: backend.getDownloadHistory ? backend.getDownloadHistory() : []

    Connections {
        target: backend
        function onDownloadProgressUpdated(current, total) {
            currentProgress = total > 0 ? current / total : 0.0
        }
        function onDownloadErrorOccurred(userMsg, logMsg) {
            currentStatus = "Error: " + userMsg
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        Label {
            text: ThemeProvider.getCatchphrase("view_ProgressView", "Progress & Management")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
        }

        // Current Download Status
        GroupBox {
            title: "Current Download Status"
            Layout.fillWidth: true
            font: ThemeProvider.getFont("body")

            ColumnLayout {
                width: parent.width
                spacing: 15

                // Progress Bar
                ProgressBar {
                    id: progressBar
                    value: currentProgress
                    Layout.fillWidth: true
                    visible: isBusy
                    background: Rectangle {
                        color: ThemeProvider.getColor("progressbar_bg")
                        radius: 3
                    }
            contentItem: Rectangle {
                color: ThemeProvider.getColor("progressbar_fg")
                        implicitWidth: progressBar.visualPosition * progressBar.width
                        implicitHeight: progressBar.height
                radius: 3
            }
        }

                // Status Text
                Text {
                    id: statusText
                    text: currentStatus
                    font: ThemeProvider.getFont("body")
                    color: ThemeProvider.getColor("text")
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }

                // Control Buttons
                RowLayout {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter

                    Button {
                        text: "Cancel Download"
                        enabled: isBusy
                        onClicked: {
                            backend.cancelDownload()
                            currentStatus = "Download cancelled"
                        }
                        font: ThemeProvider.getFont("button")
                        background: Rectangle {
                            color: enabled ? ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey) : ThemeProvider.getColor("disabled")
                            radius: ThemeProvider.getStyle("button_default").radius
                            border.color: enabled ? ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey) : ThemeProvider.getColor("disabled")
                        }
                        contentItem: Text {
                            text: parent.text
                            color: enabled ? ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey) : ThemeProvider.getColor("text_disabled")
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Button {
                        text: "Clear Cache & Logs"
                        onClicked: {
                            backend.clearCacheAndLogs()
                            currentStatus = "Cache and logs cleared"
                        }
                        font: ThemeProvider.getFont("button")
                        background: Rectangle {
                            color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                            radius: ThemeProvider.getStyle("button_default").radius
                            border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                        }
                        contentItem: Text {
                            text: parent.text
                            color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Button {
                        text: "Reload Settings"
                        onClicked: {
                            backend.reloadConfig()
                            currentStatus = "Settings reloaded"
                        }
                        font: ThemeProvider.getFont("button")
                        background: Rectangle {
                            color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                            radius: ThemeProvider.getStyle("button_default").radius
                            border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                        }
                        contentItem: Text {
                            text: parent.text
                            color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Button {
                        text: "Clear History"
                        onClicked: {
                            backend.clearDownloadHistory()
                            downloadHistory = []
                            currentStatus = "Download history cleared"
                        }
                        font: ThemeProvider.getFont("button")
                        background: Rectangle {
                            color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                            radius: ThemeProvider.getStyle("button_default").radius
                            border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                        }
                        contentItem: Text {
                            text: parent.text
                            color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }
        }

        // Download History
        GroupBox {
            title: "Download History"
            Layout.fillWidth: true
            Layout.fillHeight: true
            font: ThemeProvider.getFont("body")

            ColumnLayout {
                width: parent.width
                spacing: 10

                // History List
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: ThemeProvider.getColor("entry_bg")
                    border.color: ThemeProvider.getColor("widget_border")
                    radius: ThemeProvider.getStyle("text_input").radius || 3

                    ScrollView {
                        anchors.fill: parent
                        anchors.margins: 5
                        clip: true

                        ListView {
                            model: downloadHistory
                            delegate: Rectangle {
                                width: parent.width
                                height: 60
                                color: index % 2 === 0 ? ThemeProvider.getColor("entry_bg") : ThemeProvider.getColor("alternate_bg", ThemeProvider.getColor("entry_bg"))

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 10

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 2

                                        Text {
                                            text: modelData.name || "Download " + (index + 1)
                                            font: ThemeProvider.getFont("body")
                                            font.bold: true
                                            color: ThemeProvider.getColor("text")
                                        }

                                        Text {
                                            text: modelData.date || "Unknown date"
                                            font: ThemeProvider.getFont("body")
                                            font.pixelSize: ThemeProvider.getFont("body").pixelSize - 2
                                            color: ThemeProvider.getColor("text_subtle")
                                        }

                                        Text {
                                            text: modelData.status || "Unknown status"
                                            font: ThemeProvider.getFont("body")
                                            font.pixelSize: ThemeProvider.getFont("body").pixelSize - 2
                                            color: modelData.status === "Completed" ? ThemeProvider.getColor("success") : 
                                                   modelData.status === "Failed" ? ThemeProvider.getColor("error") : 
                                                   ThemeProvider.getColor("text_subtle")
                                        }
                                    }

                                    Button {
                                        text: "View Details"
                                        enabled: modelData.details !== undefined
                                        onClicked: {
                                            // Show details dialog
                                            detailsDialog.text = JSON.stringify(modelData.details, null, 2)
                                            detailsDialog.open()
                                        }
                                        font: ThemeProvider.getFont("button")
                                        background: Rectangle {
                                            color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                                            radius: ThemeProvider.getStyle("button_default").radius
                                            border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                                        }
                                        contentItem: Text {
                                            text: parent.text
                                            color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // No history message
                Text {
                    text: "No download history available"
                    visible: downloadHistory.length === 0
                    font: ThemeProvider.getFont("body")
                    color: ThemeProvider.getColor("text_subtle")
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
    }

    // Details Dialog
    Dialog {
        id: detailsDialog
        title: "Download Details"
        modal: true
        standardButtons: Dialog.Ok
        width: 600
        height: 400

        property string text: ""

        ScrollView {
            anchors.fill: parent
            TextArea {
                text: detailsDialog.text
                readOnly: true
                font: ThemeProvider.getFont("monospace")
                wrapMode: TextEdit.Wrap
            }
        }
    }
} 
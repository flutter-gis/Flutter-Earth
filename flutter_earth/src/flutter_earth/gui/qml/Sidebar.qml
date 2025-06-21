import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick 2.15

Item {
    id: sidebar
    width: 400
    height: parent.height

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Tab buttons
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            spacing: 0

            Button {
                text: "Download"
                Layout.fillWidth: true
                Layout.fillHeight: true
                onClicked: swipeView.currentIndex = 0
                background: Rectangle {
                    color: swipeView.currentIndex === 0 ? "#3a3a3a" : "#2a2a2a"
                }
            }
            Button {
                text: "Satellite Info"
                Layout.fillWidth: true
                Layout.fillHeight: true
                onClicked: swipeView.currentIndex = 1
                background: Rectangle {
                    color: swipeView.currentIndex === 1 ? "#3a3a3a" : "#2a2a2a"
                }
            }
            Button {
                text: "Post-Processing"
                Layout.fillWidth: true
                Layout.fillHeight: true
                onClicked: swipeView.currentIndex = 2
                background: Rectangle {
                    color: swipeView.currentIndex === 2 ? "#3a3a3a" : "#2a2a2a"
                }
            }
            Button {
                text: "Index Analysis"
                Layout.fillWidth: true
                Layout.fillHeight: true
                onClicked: swipeView.currentIndex = 3
                background: Rectangle {
                    color: swipeView.currentIndex === 3 ? "#3a3a3a" : "#2a2a2a"
                }
            }
            Button {
                text: "Vector Download"
                Layout.fillWidth: true
                Layout.fillHeight: true
                onClicked: swipeView.currentIndex = 4
                background: Rectangle {
                    color: swipeView.currentIndex === 4 ? "#3a3a3a" : "#2a2a2a"
                }
            }
            Button {
                text: "Data Viewer"
                Layout.fillWidth: true
                Layout.fillHeight: true
                onClicked: swipeView.currentIndex = 5
                background: Rectangle {
                    color: swipeView.currentIndex === 5 ? "#3a3a3a" : "#2a2a2a"
                }
            }
        }

        // Content area
        SwipeView {
            id: swipeView
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: 0

            DownloadTab {}
            SatelliteInfoTab {}
            PostProcessingTab {}
            IndexAnalysisTab {}
            VectorDownloadTab {}
            DataViewerTab {}
        }
    }
} 
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." as App

ApplicationWindow {
    id: root
    visible: true
    width: 1400
    height: 850
    title: "Flutter Earth - QML Edition"
    color: App.Style.background

    Item {
        id: content
        anchors.fill: parent
        
        // --- Main Layout ---
        RowLayout {
            anchors.fill: parent
            spacing: 0 // No space between sidebar and main content

            // --- Sidebar for Navigation ---
            App.SideBar {
                id: sideBar
                onProcessingClicked: viewStack.currentIndex = 0
                onSatelliteInfoClicked: viewStack.currentIndex = 1
                onVectorImportClicked: viewStack.currentIndex = 2
                onPostProcessingClicked: viewStack.currentIndex = 3
                onAppSettingsClicked: viewStack.currentIndex = 4
            }

            // --- View Stack ---
            StackLayout {
                id: viewStack
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: 0

                App.ControlPanel {
                    id: controlPanelView
                }

                App.SatelliteInfoView {
                    id: satelliteInfoView
                }
                
                App.VectorImportView {
                    id: vectorImportView
                }

                App.PostProcessingView {
                    id: postProcessingView
                }

                App.SettingsView {
                    id: settingsView
                }
            }
        }
    }
    
    Component.onCompleted: {
        console.log("Flutter Earth QML loaded.")
        if (backend) {
            console.log("AppBackend connected successfully.")
            // You can call backend functions here to initialize the UI if needed
            // For example, to log the current theme:
            var themeColors = backend.getCurrentThemeColors()
            console.log("Current theme loaded: " + themeColors.primary)
        }
    }
} 
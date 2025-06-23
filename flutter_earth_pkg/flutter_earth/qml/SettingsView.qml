import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "." as App

Rectangle {
    id: root
    color: "transparent"

    Flickable {
        anchors.fill: parent
        contentWidth: availableWidth
        contentHeight: column.height
        clip: true

        ColumnLayout {
            id: column
            width: parent.width
            anchors.margins: 20
            spacing: 20

            Label {
                text: "Application Settings"
                font.pixelSize: 24
                color: App.Style.text
            }

            GroupBox {
                title: "Appearance"
                Layout.fillWidth: true
                
                RowLayout {
                    Label {
                        text: "Theme"
                        color: App.Style.text
                    }
                    ComboBox {
                        id: themeComboBox
                        Layout.fillWidth: true
                        
                        // Populate the model from the backend
                        model: backend ? backend.getAvailableThemes() : []
                        
                        onActivated: {
                            // When the user selects a theme, call the backend
                            if(backend) {
                                backend.setTheme(currentText)
                            }
                        }

                        Component.onCompleted: {
                            if (backend) {
                                var currentThemeName = backend.getCurrentThemeName()
                                var initialIndex = model.indexOf(currentThemeName)
                                if (initialIndex !== -1) {
                                    currentIndex = initialIndex
                                }
                            }
                        }
                    }
                }
            }
        }
    }
} 
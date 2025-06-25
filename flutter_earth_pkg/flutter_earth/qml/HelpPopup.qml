import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import "./" // For ThemeProvider

Dialog {
    id: helpPopup
    title: ThemeProvider.getCatchphrase("dialog_title_help", "Help & Documentation")
    modal: true
    standardButtons: Dialog.Close
    width: 800
    height: 600
    visible: false

    background: Rectangle {
        color: ThemeProvider.getColor("widget_bg")
        border.color: ThemeProvider.getColor("widget_border")
        radius: ThemeProvider.getStyle("dialog").radius || 8
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        // Help Navigation
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: "Getting Started"
                onClicked: helpStack.currentIndex = 0
                font: ThemeProvider.getFont("button")
                background: Rectangle {
                    color: helpStack.currentIndex === 0 ? ThemeProvider.getColor("primary") : ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                    radius: ThemeProvider.getStyle("button_default").radius
                    border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                }
            }

            Button {
                text: "Download Guide"
                onClicked: helpStack.currentIndex = 1
                font: ThemeProvider.getFont("button")
                background: Rectangle {
                    color: helpStack.currentIndex === 1 ? ThemeProvider.getColor("primary") : ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                    radius: ThemeProvider.getStyle("button_default").radius
                    border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                }
            }

            Button {
                text: "Analysis Tools"
                onClicked: helpStack.currentIndex = 2
                font: ThemeProvider.getFont("button")
                background: Rectangle {
                    color: helpStack.currentIndex === 2 ? ThemeProvider.getColor("primary") : ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                    radius: ThemeProvider.getStyle("button_default").radius
                    border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                }
            }

            Button {
                text: "FAQ"
                onClicked: helpStack.currentIndex = 3
                font: ThemeProvider.getFont("button")
                background: Rectangle {
                    color: helpStack.currentIndex === 3 ? ThemeProvider.getColor("primary") : ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                    radius: ThemeProvider.getStyle("button_default").radius
                    border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                }
            }
        }

        // Help Content Stack
        StackLayout {
            id: helpStack
            Layout.fillWidth: true
            Layout.fillHeight: true

            // Getting Started
            ScrollView {
                clip: true
                ColumnLayout {
                    width: parent.width
                    spacing: 15

                    Text {
                        text: "Welcome to Flutter Earth!"
                        font: ThemeProvider.getFont("title")
                        color: ThemeProvider.getColor("primary")
                        Layout.fillWidth: true
                    }

                    Text {
                        text: "Flutter Earth is a powerful tool for downloading and analyzing satellite imagery using Google Earth Engine. Here's how to get started:"
                        font: ThemeProvider.getFont("body")
                        color: ThemeProvider.getColor("text")
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }

                    GroupBox {
                        title: "1. Authentication"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "• You'll need a Google Earth Engine account\n• Set up authentication in the Settings view\n• Provide your GCP project ID and service account key"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }

                    GroupBox {
                        title: "2. Download Satellite Data"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "• Go to the Download view\n• Select your area of interest\n• Choose satellite sensor and date range\n• Configure processing options\n• Start the download"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }

                    GroupBox {
                        title: "3. Analyze Your Data"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "• Use the Index Analysis view for vegetation indices\n• View your data in the Data Viewer\n• Export results in various formats"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }

            // Download Guide
            ScrollView {
                clip: true
                ColumnLayout {
                    width: parent.width
                    spacing: 15

                    Text {
                        text: "Download Guide"
                        font: ThemeProvider.getFont("title")
                        color: ThemeProvider.getColor("primary")
                        Layout.fillWidth: true
                    }

                    GroupBox {
                        title: "Area of Interest (AOI)"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "You can specify your AOI in several formats:\n\n• Bounding Box: [minLon, minLat, maxLon, maxLat]\n• GeoJSON Polygon: Paste a valid GeoJSON\n• Use the Map view to draw and select areas"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }

                    GroupBox {
                        title: "Satellite Sensors"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "Available sensors:\n\n• Landsat 8/9: 30m resolution, good for land monitoring\n• Sentinel-2: 10m resolution, excellent for agriculture\n• Sentinel-1: Radar data, works in all weather\n• MODIS: 250m resolution, good for large areas\n• VIIRS: 375m resolution, environmental monitoring"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }

                    GroupBox {
                        title: "Processing Options"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "• Cloud Mask: Automatically remove cloudy pixels\n• Max Cloud Cover: Set maximum allowed cloud coverage\n• Resolution: Choose output resolution\n• Tiling: Split large areas into manageable tiles\n• Output Format: GeoTIFF, JPEG, or PNG"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }

            // Analysis Tools
            ScrollView {
                clip: true
                ColumnLayout {
                    width: parent.width
                    spacing: 15

                    Text {
                        text: "Analysis Tools"
                        font: ThemeProvider.getFont("title")
                        color: ThemeProvider.getColor("primary")
                        Layout.fillWidth: true
                    }

                    GroupBox {
                        title: "Vegetation Indices"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "Available indices:\n\n• NDVI: Normalized Difference Vegetation Index\n• EVI: Enhanced Vegetation Index\n• SAVI: Soil Adjusted Vegetation Index\n• NDWI: Normalized Difference Water Index\n• NDMI: Normalized Difference Moisture Index\n• NBR: Normalized Burn Ratio\n• NDSI: Normalized Difference Snow Index\n• NDBI: Normalized Difference Built-up Index"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }

                    GroupBox {
                        title: "Data Viewer"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "The Data Viewer allows you to:\n\n• Load and preview raster and vector data\n• View metadata and statistics\n• Export data in various formats\n• Generate basic visualizations"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }

                    GroupBox {
                        title: "Vector Data Download"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "Download vector data from:\n\n• OpenStreetMap Overpass API\n• WFS (Web Feature Service) endpoints\n• Direct GeoJSON URLs\n• Custom queries and filters"
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }

            // FAQ
            ScrollView {
                clip: true
                ColumnLayout {
                    width: parent.width
                    spacing: 15

                    Text {
                        text: "Frequently Asked Questions"
                        font: ThemeProvider.getFont("title")
                        color: ThemeProvider.getColor("primary")
                        Layout.fillWidth: true
                    }

                    GroupBox {
                        title: "Q: How do I set up Google Earth Engine authentication?"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "A: Go to Settings → Authentication. You'll need a Google Cloud Project ID and a service account key file. Follow the Google Earth Engine setup guide for detailed instructions."
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }

                    GroupBox {
                        title: "Q: Why is my download taking so long?"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "A: Download time depends on area size, resolution, and date range. Large areas or high-resolution data take longer. Use the Progress view to monitor status."
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }

                    GroupBox {
                        title: "Q: What file formats are supported?"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "A: Raster: GeoTIFF, JPEG, PNG. Vector: GeoJSON, Shapefile, KML. The Data Viewer supports most common geospatial formats."
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }

                    GroupBox {
                        title: "Q: How do I choose the right satellite sensor?"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "A: Use the Satellite Info view to compare sensors. Consider resolution, revisit time, and spectral bands for your specific application."
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }

                    GroupBox {
                        title: "Q: Can I use this without Google Earth Engine?"
                        Layout.fillWidth: true
                        font: ThemeProvider.getFont("body")

                        Text {
                            text: "A: Limited functionality is available without GEE authentication. You can view data, use the map, and access some analysis tools."
                            font: ThemeProvider.getFont("body")
                            color: ThemeProvider.getColor("text")
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }
    }
} 
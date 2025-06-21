import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

GroupBox {
    id: processingGroup
    title: "Processing & Sensor Settings"
    Layout.fillWidth: true
    ColumnLayout {
        spacing: 10
        RowLayout {
            spacing: 10
            Label { text: "Sensor:"; color: "#fff" }
            ComboBox { id: sensorCombo; model: ["LANDSAT_8", "LANDSAT_9", "SENTINEL_2"] }
        }
        RowLayout {
            spacing: 10
            CheckBox { text: "Cloud Mask" }
            CheckBox { text: "Best Resolution" }
        }
    }
} 
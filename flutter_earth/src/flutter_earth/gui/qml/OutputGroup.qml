import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

GroupBox {
    id: outputGroup
    title: "Output Settings"
    Layout.fillWidth: true
    ColumnLayout {
        spacing: 10
        RowLayout {
            spacing: 10
            Label { text: "Output Dir:"; color: "#fff" }
            TextField { id: outputDir; placeholderText: "./output"; width: 200 }
            Button { text: "Browse" }
        }
        RowLayout {
            spacing: 10
            Label { text: "Format:"; color: "#fff" }
            ComboBox { id: formatCombo; model: ["GeoTIFF", "JPEG", "PNG"] }
        }
    }
} 
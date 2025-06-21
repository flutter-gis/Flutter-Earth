import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

GroupBox {
    id: areaTimeGroup
    title: "Area & Time Settings"
    Layout.fillWidth: true
    ColumnLayout {
        spacing: 10
        // AOI input
        RowLayout {
            spacing: 10
            Label { text: "AOI (BBOX):"; color: "#fff" }
            TextField { id: aoiInput; placeholderText: "minLon,minLat,maxLon,maxLat"; width: 200 }
            Button { text: "🗺️ Map" }
            Button { text: "📂 SHP" }
        }
        // Date inputs
        RowLayout {
            spacing: 10
            Label { text: "Start Date:"; color: "#fff" }
            TextField { id: startDate; placeholderText: "YYYY-MM-DD"; width: 120 }
            Label { text: "End Date:"; color: "#fff" }
            TextField { id: endDate; placeholderText: "YYYY-MM-DD"; width: 120 }
        }
    }
} 
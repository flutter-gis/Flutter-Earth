import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt5Compat.GraphicalEffects
import "./" // For ThemeProvider singleton

Rectangle {
    id: topBar
    color: ThemeProvider.getColor("primary", "#f8bbd0")
    height: 80
    width: parent.width
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    z: 2
    radius: 0
    layer.enabled: true
    layer.effect: DropShadow {
        color: ThemeProvider.getColor("primary"); radius: 10; samples: 16; x: 0; y: 2; spread: 0.08
    }
    
    // Add subtle background pattern
    Rectangle {
        anchors.fill: parent
        color: "transparent"
        opacity: 0.1
        
        Canvas {
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.strokeStyle = ThemeProvider.getColor("text_on_primary", "#FFFFFF");
                ctx.lineWidth = 1;
                
                // Draw subtle diagonal lines
                for (var i = 0; i < width; i += 20) {
                    ctx.beginPath();
                    ctx.moveTo(i, 0);
                    ctx.lineTo(i + 20, height);
                    ctx.stroke();
                }
            }
        }
    }
    
    Row {
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 25
        spacing: 20
        Text {
            text: ThemeProvider.getCatchphrase("app_title", "Flutter Earth")
            font.family: ThemeProvider.getFont("title").family
            font.pixelSize: ThemeProvider.getFont("title").pixelSize + 4
            font.bold: ThemeProvider.getFont("title").bold
            color: ThemeProvider.getColor("text_on_primary", "#FFFFFF")
            layer.enabled: true
            layer.effect: DropShadow {
                color: "#000000"
                radius: 2
                samples: 4
                x: 1
                y: 1
                spread: 0.1
            }
        }
        
        // Add a subtle separator
        Rectangle {
            width: 2
            height: 40
            color: ThemeProvider.getColor("text_on_primary", "#FFFFFF")
            opacity: 0.3
            anchors.verticalCenter: parent.verticalCenter
        }
        
        // Add version or status text
        Text {
            text: "v1.0.0 - Ready"
            font.family: ThemeProvider.getFont("body").family
            font.pixelSize: ThemeProvider.getFont("body").pixelSize - 2
            color: ThemeProvider.getColor("text_on_primary", "#FFFFFF")
            opacity: 0.8
            anchors.verticalCenter: parent.verticalCenter
        }
    }
} 
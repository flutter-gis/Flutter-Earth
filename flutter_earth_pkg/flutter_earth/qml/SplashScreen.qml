import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "./" // For ThemeProvider

Rectangle {
    id: splashScreen
    anchors.fill: parent
    color: ThemeProvider.getColor("background", "#222")
    z: 1000
    visible: true

    property string themeName: ThemeProvider.getCurrentThemeName ? ThemeProvider.getCurrentThemeName() : "Default"
    property string splashMessage: getSplashMessage(themeName)
    property string splashImage: getSplashImage(themeName)

    // Fade out after 2.5 seconds
    SequentialAnimation on opacity {
        running: visible
        NumberAnimation { from: 1; to: 1; duration: 1200 }
        NumberAnimation { from: 1; to: 0; duration: 800 }
        onStopped: splashScreen.visible = false
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 30
        Image {
            source: splashImage
            width: 180; height: 180
            fillMode: Image.PreserveAspectFit
            visible: splashImage !== ""
        }
        Text {
            text: splashMessage
            font.pixelSize: 32
            font.bold: true
            color: ThemeProvider.getColor("primary", "#fff")
            horizontalAlignment: Text.AlignHCenter
        }
    }

    function getSplashMessage(theme) {
        if (theme === "Princess Luna") return "Welcome to Luna's Lunar Mapper!";
        if (theme === "Default (Dark)") return "Welcome to Flutter Earth";
        if (theme === "Zombie") return "Braaaains... Loading...";
        if (theme === "Princess Celestia") return "Celestial Mapping Awaits!";
        return "Loading...";
    }
    function getSplashImage(theme) {
        if (theme === "Princess Luna") return "qrc:/luna_moon.png";
        if (theme === "Zombie") return "qrc:/zombie_hand.png";
        if (theme === "Princess Celestia") return "qrc:/celestia_sun.png";
        return "qrc:/earth_logo.png";
    }
} 
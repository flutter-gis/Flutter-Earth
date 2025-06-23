import QtQuick 2.15
import QtQuick.Controls 2.15
import QtWebEngine 1.10
import "." as App

Rectangle {
    id: mapView
    color: App.Style.widget_bg
    radius: 8

    WebEngineView {
        id: webEngineView
        anchors.fill: parent

        Component.onCompleted: {
            if (backend) {
                webEngineView.url = backend.getMapUrl()
            }
        }
    }
} 
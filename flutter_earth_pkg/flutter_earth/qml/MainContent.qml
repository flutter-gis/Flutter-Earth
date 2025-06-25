import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: mainContent
    property string currentView: "HomeView.qml" // Default to a .qml file
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.bottom: parent.bottom
    anchors.margins: 0
    z: 0

    // Centralized view loader for navigation
    Loader {
        id: viewLoader
        anchors.fill: parent
        source: mainContent.currentView // currentView now holds the direct .qml filename

        // Fallback if currentView is empty or invalid, though ideally SideBar always sets a valid one.
        // Consider adding an onError handler for the Loader if necessary.
        // Default view can be set by initializing mainContent.currentView to "HomeView.qml"
        Component.onCompleted: {
            if (!mainContent.currentView) {
                mainContent.currentView = "HomeView.qml";
            }
        }
    }
} 
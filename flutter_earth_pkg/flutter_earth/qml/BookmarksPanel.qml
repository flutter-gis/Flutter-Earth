import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: bookmarksPanel
    anchors.fill: parent
    
    property var bookmarks: []
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 5
        
        // Search bar
        TextField {
            id: bookmarkSearchField
            Layout.fillWidth: true
            placeholderText: "Search bookmarks..."
            
            onTextChanged: filterBookmarks()
        }
        
        // Bookmarks list
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            ListView {
                id: bookmarksList
                model: filteredBookmarks
                spacing: 2
                
                delegate: Rectangle {
                    width: bookmarksList.width
                    height: 70
                    color: ThemeProvider.getColor("list_bg")
                    border.color: ThemeProvider.getColor("widget_border")
                    border.width: 1
                    radius: 4
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 2
                        
                        RowLayout {
                            Layout.fillWidth: true
                            
                            Text {
                                text: modelData.name
                                font.family: ThemeProvider.getFont("body").family
                                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                                font.bold: true
                                color: ThemeProvider.getColor("text")
                                Layout.fillWidth: true
                            }
                            
                            Button {
                                text: "📍"
                                width: 30
                                height: 30
                                onClicked: goToBookmark(modelData)
                            }
                            
                            Button {
                                text: "🗑️"
                                width: 30
                                height: 30
                                onClicked: removeBookmark(modelData.name)
                            }
                        }
                        
                        Text {
                            text: modelData.description
                            font.family: ThemeProvider.getFont("body").family
                            font.pixelSize: 10
                            color: ThemeProvider.getColor("text_subtle")
                            Layout.fillWidth: true
                        }
                        
                        Text {
                            text: "Lat: " + modelData.center[0].toFixed(4) + ", Lon: " + modelData.center[1].toFixed(4) + " | Zoom: " + modelData.zoom_level.toFixed(1)
                            font.family: ThemeProvider.getFont("body").family
                            font.pixelSize: 8
                            color: ThemeProvider.getColor("text_subtle")
                            Layout.fillWidth: true
                        }
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: goToBookmark(modelData)
                        onPressAndHold: bookmarkContextMenu.popup()
                    }
                }
            }
        }
        
        // Add bookmark button
        Button {
            text: "Add Bookmark"
            Layout.fillWidth: true
            
            onClicked: addBookmarkDialog.open()
        }
    }
    
    // Computed property for filtered bookmarks
    property var filteredBookmarks: {
        var searchText = bookmarkSearchField.text.toLowerCase()
        if (searchText === "") {
            return bookmarks
        }
        
        var filtered = []
        for (var i = 0; i < bookmarks.length; i++) {
            var bookmark = bookmarks[i]
            if (bookmark.name.toLowerCase().indexOf(searchText) !== -1 || 
                bookmark.description.toLowerCase().indexOf(searchText) !== -1) {
                filtered.push(bookmark)
            }
        }
        return filtered
    }
    
    // Functions
    function filterBookmarks() {
        // Trigger recomputation of filteredBookmarks
        filteredBookmarks = filteredBookmarks
    }
    
    function goToBookmark(bookmark) {
        // Implementation for going to bookmark
        console.log("Go to bookmark:", bookmark.name)
    }
    
    function removeBookmark(name) {
        backend.removeBookmark(name)
    }
    
    // Context menu
    Menu {
        id: bookmarkContextMenu
        
        MenuItem {
            text: "Go to Bookmark"
            onTriggered: goToBookmark(bookmarksList.currentItem.modelData)
        }
        
        MenuItem {
            text: "Edit Bookmark"
            onTriggered: editBookmark(bookmarksList.currentItem.modelData)
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Remove Bookmark"
            onTriggered: removeBookmark(bookmarksList.currentItem.modelData.name)
        }
    }
    
    function editBookmark(bookmark) {
        // Implementation for editing bookmark
        console.log("Edit bookmark:", bookmark.name)
    }
    
    // Add bookmark dialog
    Dialog {
        id: addBookmarkDialog
        title: "Add Bookmark"
        width: 400
        height: 300
        modal: true
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 10
            
            Label {
                text: "Name:"
            }
            
            TextField {
                id: bookmarkNameField
                Layout.fillWidth: true
                placeholderText: "Enter bookmark name"
            }
            
            Label {
                text: "Description:"
            }
            
            TextField {
                id: bookmarkDescField
                Layout.fillWidth: true
                placeholderText: "Enter description"
            }
            
            Label {
                text: "Latitude:"
            }
            
            TextField {
                id: bookmarkLatField
                Layout.fillWidth: true
                placeholderText: "Enter latitude"
            }
            
            Label {
                text: "Longitude:"
            }
            
            TextField {
                id: bookmarkLonField
                Layout.fillWidth: true
                placeholderText: "Enter longitude"
            }
            
            Label {
                text: "Zoom Level:"
            }
            
            Slider {
                id: bookmarkZoomSlider
                Layout.fillWidth: true
                from: 1
                to: 20
                value: 10
                stepSize: 0.1
            }
            
            Text {
                text: "Zoom: " + bookmarkZoomSlider.value.toFixed(1)
                font.family: ThemeProvider.getFont("body").family
                font.pixelSize: 10
                color: ThemeProvider.getColor("text_subtle")
            }
            
            RowLayout {
                Layout.fillWidth: true
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Add"
                    onClicked: {
                        var name = bookmarkNameField.text
                        var desc = bookmarkDescField.text
                        var lat = parseFloat(bookmarkLatField.text)
                        var lon = parseFloat(bookmarkLonField.text)
                        var zoom = bookmarkZoomSlider.value
                        
                        if (name && !isNaN(lat) && !isNaN(lon)) {
                            backend.addBookmark(name, desc, [lat, lon], zoom, [])
                            addBookmarkDialog.close()
                        }
                    }
                }
                
                Button {
                    text: "Cancel"
                    onClicked: addBookmarkDialog.close()
                }
            }
        }
    }
    
    Component.onCompleted: {
        // Load initial bookmarks
        bookmarks = backend.getBookmarks()
        // Connect to backend signals
        if (backend && backend.onBookmarkAdded && backend.onBookmarkAdded.connect) {
            backend.onBookmarkAdded.connect(function(bookmark) {
                bookmarks.push(bookmark)
                bookmarks = bookmarks // Trigger update
            })
        }
    }
} 
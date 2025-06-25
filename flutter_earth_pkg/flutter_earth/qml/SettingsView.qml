import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import Qt.labs.platform 1.1
// import Qt.labs.settings 1.0 // Not used here directly, backend handles settings persistence
import "./" // For ThemeProvider singleton

Rectangle {
    id: settingsView
    color: ThemeProvider.getColor("background", "#f3e5f5")
    anchors.fill: parent

    property var allSettings: backend.getAllSettings() // Full config for initial values
    property var currentThemeData: backend.getCurrentThemeData() // For sub-options
    property var availableThemesModel: backend.getAvailableThemes() // List of {name, display_name, category}

    // Properties for theme categorization
    property var categories: []
    property var themesByCategory: ({})
    property string selectedCategory: ""

    function findThemeIndex(themeName) {
        for (var i = 0; i < availableThemesModel.length; ++i) {
            if (availableThemesModel[i].name === themeName) return i;
        }
        return -1; // Default to first if not found or handle error
    }

    function buildThemeCategories() {
        // Build categories and themesByCategory from availableThemesModel
        console.log("buildThemeCategories: availableThemesModel =", JSON.stringify(availableThemesModel));
        var cats = [];
        var byCat = {};
        for (var i = 0; i < availableThemesModel.length; ++i) {
            var theme = availableThemesModel[i];
            var cat = theme.category || "Other";
            if (cats.indexOf(cat) === -1) cats.push(cat);
            if (!byCat[cat]) byCat[cat] = [];
            byCat[cat].push(theme);
        }
        categories = cats;
        themesByCategory = byCat;
        selectedCategory = cats.length > 0 ? cats[0] : "";
        console.log("buildThemeCategories: categories =", JSON.stringify(categories));
        console.log("buildThemeCategories: themesByCategory =", JSON.stringify(themesByCategory));
        console.log("buildThemeCategories: selectedCategory =", selectedCategory);
    }

    // React to config/setting changes
    Connections {
        target: backend
        function onConfigChanged(newConfig) { // newConfig is the full config dict
            console.log("SettingsView: Config changed, newConfig =", JSON.stringify(newConfig));
            allSettings = newConfig;
            currentThemeData = backend.getCurrentThemeData(); // Refresh full theme data too
            buildThemeCategories(); // Rebuild categories when themes change
            // Update checkboxes for theme sub-options
            var currentThemeOptions = currentThemeData.options || {};
            useCharacterCatchphrasesBox.checked = currentThemeOptions.use_character_catchphrases || false;
            showSpecialIconsBox.checked = currentThemeOptions.show_special_icons || false;
            enableAnimatedBackgroundBox.checked = currentThemeOptions.enable_animated_background || false;
        }
        function onSettingChanged(key, value) {
            console.log("SettingsView: Setting changed, key =", key, "value =", value);
            if (key === "theme") {
                buildThemeCategories(); // Rebuild categories when theme changes
                currentThemeData = backend.getCurrentThemeData(); // Update after theme name changes
                 var currentThemeOptions = currentThemeData.options || {};
                useCharacterCatchphrasesBox.checked = currentThemeOptions.use_character_catchphrases || false;
                showSpecialIconsBox.checked = currentThemeOptions.show_special_icons || false;
                enableAnimatedBackgroundBox.checked = currentThemeOptions.enable_animated_background || false;
            }
            if (key === "output_dir") {
                outputDirField.text = value;
            }
            if (key === "theme_suboptions") { // If suboptions are saved as one dict
                 var newOpts = value;
                 if (typeof value === 'string') { try { newOpts = JSON.parse(value); } catch (e) { return; } }
                 useCharacterCatchphrasesBox.checked = newOpts.use_character_catchphrases || false;
                 showSpecialIconsBox.checked = newOpts.show_special_icons || false;
                 enableAnimatedBackgroundBox.checked = newOpts.enable_animated_background || false;
            }
        }
    }

    Component.onCompleted: {
        console.log("SettingsView: Component.onCompleted");
        console.log("SettingsView: allSettings =", JSON.stringify(allSettings));
        console.log("SettingsView: currentThemeData =", JSON.stringify(currentThemeData));
        console.log("SettingsView: availableThemesModel =", JSON.stringify(availableThemesModel));
        buildThemeCategories();
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        Label {
            text: ThemeProvider.getCatchphrase("view_SettingsView", "Settings")
            font.family: ThemeProvider.getFont("title").family
            font.pixelSize: ThemeProvider.getFont("title").pixelSize
            font.bold: ThemeProvider.getFont("title").bold
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
            layer.enabled: true
            layer.effect: DropShadow {
                color: ThemeProvider.getColor("primary"); radius: 8; samples: 16; x: 0; y: 2; spread: 0.1
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ColumnLayout {
                width: parent.width
                spacing: 18

                // Theme selection
                GroupBox {
                    title: ThemeProvider.getCatchphrase("settings_group_theme", "Appearance")
                    Layout.fillWidth: true
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: ThemeProvider.getFont("body").pixelSize
                    color: ThemeProvider.getColor("widget_bg")
                    background: Rectangle {
                        color: ThemeProvider.getColor("widget_bg")
                        border.color: ThemeProvider.getColor("widget_border")
                        border.width: 2
                        radius: 12
                        layer.enabled: true
                        layer.effect: DropShadow {
                            color: ThemeProvider.getColor("primary"); radius: 12; samples: 16; x: 0; y: 2; spread: 0.08
                        }
                    }
                    ColumnLayout {
                        width: parent.width
                        spacing: 10
                        TabBar {
                            id: themeTabBar
                            Layout.fillWidth: true
                            Repeater {
                                model: categories
                                TabButton {
                                    text: modelData
                                    checked: selectedCategory === modelData
                                    onClicked: selectedCategory = modelData
                                    font.family: ThemeProvider.getFont("button").family
                                    font.pixelSize: ThemeProvider.getFont("button").pixelSize
                                    font.bold: ThemeProvider.getFont("button").bold
                                    background: Rectangle {
                                        color: checked ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("button_bg")
                                        border.color: checked ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("widget_border")
                                        border.width: checked ? 2 : 1
                                        radius: 8
                                    }
                                    contentItem: Text {
                                        text: modelData
                                        color: checked ? ThemeProvider.getColor("button_fg") : ThemeProvider.getColor("text")
                                        font.family: ThemeProvider.getFont("button").family
                                        font.pixelSize: ThemeProvider.getFont("button").pixelSize
                                        font.bold: ThemeProvider.getFont("button").bold
                                    }
                                }
                            }
                        }
                        GridLayout {
                            id: themeGrid
                            columns: 3
                            rowSpacing: 16
                            columnSpacing: 16
                            Layout.fillWidth: true
                            Repeater {
                                model: themesByCategory[selectedCategory] || []
                                Rectangle {
                                    width: 180; height: 90; radius: 12
                                    color: ThemeProvider.getColor("widget_bg")
                                    border.color: (allSettings.theme === modelData.name) ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("widget_border")
                                    border.width: (allSettings.theme === modelData.name) ? 4 : 1
                                    z: (allSettings.theme === modelData.name) ? 1 : 0
                                    layer.enabled: true
                                    layer.effect: DropShadow {
                                        color: (allSettings.theme === modelData.name) ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("widget_border");
                                        radius: (allSettings.theme === modelData.name) ? 16 : 8; samples: 16; x: 0; y: 2; spread: 0.10
                                    }
                                    property bool hovered: false
                                    Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutQuad } }
                                    scale: hovered ? 1.04 : 1.0
                                    RowLayout {
                                        anchors.fill: parent; anchors.margins: 10
                                        spacing: 10
                                        Rectangle { width: 36; height: 36; radius: 8; color: modelData.background || ThemeProvider.getColor("background"); border.color: modelData.primary || ThemeProvider.getColor("primary"); border.width: 2 }
                                        ColumnLayout {
                                            spacing: 2
                                            Label { text: modelData.display_name || modelData.name; font.bold: true; font.pixelSize: 16; color: ThemeProvider.getColor("text") }
                                            Label { text: modelData.category || "Other"; font.pixelSize: 11; color: ThemeProvider.getColor("text_subtle") }
                                        }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onEntered: parent.hovered = true
                                        onExited: parent.hovered = false
                                        onClicked: {
                                            if (allSettings.theme !== modelData.name) {
                                                backend.setTheme(modelData.name);
                                            }
                                        }
                                        cursorShape: Qt.PointingHandCursor
                                    }
                                }
                            }
                        }
                    }
                }

                // Theme Sub-options
                Label {
                    text: ThemeProvider.getCatchphrase("settings_label_theme_options", "Theme Options:")
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: ThemeProvider.getFont("body").pixelSize
                    color: ThemeProvider.getColor("text")
                    topPadding: 10
                }
                CheckBox {
                    id: useCharacterCatchphrasesBox
                    text: ThemeProvider.getCatchphrase("settings_opt_catchphrases", "Use Character Catchphrases")
                    checked: currentThemeData.options ? currentThemeData.options.use_character_catchphrases : false
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: ThemeProvider.getFont("body").pixelSize
                    indicator: Rectangle {
                        implicitWidth: 20; implicitHeight: 20; radius: 6
                        border.color: parent.checked ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("widget_border")
                        border.width: 2
                        color: parent.checked ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("widget_bg")
                        Rectangle {
                            anchors.centerIn: parent
                            width: 10; height: 10; radius: 3
                            color: parent.checked ? ThemeProvider.getColor("button_fg") : "transparent"
                            visible: parent.checked
                        }
                    }
                    onCheckedChanged: saveThemeSubOptions()
                }
                CheckBox {
                    id: showSpecialIconsBox
                    text: ThemeProvider.getCatchphrase("settings_opt_icons", "Show Special Icons")
                    checked: currentThemeData.options ? currentThemeData.options.show_special_icons : false
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: ThemeProvider.getFont("body").pixelSize
                    indicator: Rectangle {
                        implicitWidth: 20; implicitHeight: 20; radius: 6
                        border.color: parent.checked ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("widget_border")
                        border.width: 2
                        color: parent.checked ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("widget_bg")
                        Rectangle {
                            anchors.centerIn: parent
                            width: 10; height: 10; radius: 3
                            color: parent.checked ? ThemeProvider.getColor("button_fg") : "transparent"
                            visible: parent.checked
                        }
                    }
                    onCheckedChanged: saveThemeSubOptions()
                }
                CheckBox {
                    id: enableAnimatedBackgroundBox
                    text: ThemeProvider.getCatchphrase("settings_opt_animations", "Enable Animated Backgrounds")
                    checked: currentThemeData.options ? currentThemeData.options.enable_animated_background : false
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: ThemeProvider.getFont("body").pixelSize
                    indicator: Rectangle {
                        implicitWidth: 20; implicitHeight: 20; radius: 6
                        border.color: parent.checked ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("widget_border")
                        border.width: 2
                        color: parent.checked ? ThemeProvider.getColor("primary") : ThemeProvider.getColor("widget_bg")
                        Rectangle {
                            anchors.centerIn: parent
                            width: 10; height: 10; radius: 3
                            color: parent.checked ? ThemeProvider.getColor("button_fg") : "transparent"
                            visible: parent.checked
                        }
                    }
                    onCheckedChanged: saveThemeSubOptions()
                }

                // Output directory
                GroupBox {
                    title: ThemeProvider.getCatchphrase("settings_group_general", "General")
                    Layout.fillWidth: true
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: ThemeProvider.getFont("body").pixelSize
                    background: Rectangle {
                        color: ThemeProvider.getColor("widget_bg")
                        border.color: ThemeProvider.getColor("widget_border")
                        border.width: 2
                        radius: 12
                        layer.enabled: true
                        layer.effect: DropShadow {
                            color: ThemeProvider.getColor("primary"); radius: 12; samples: 16; x: 0; y: 2; spread: 0.08
                        }
                    }
                    ColumnLayout {
                        width: parent.width
                        RowLayout {
                            Label { text: ThemeProvider.getCatchphrase("settings_label_output_dir", "Output Directory:"); font.family: ThemeProvider.getFont("body").family; font.pixelSize: ThemeProvider.getFont("body").pixelSize; color: ThemeProvider.getColor("text") }
                            TextField {
                                id: outputDirField
                                text: allSettings.output_dir
                                onEditingFinished: { backend.setSetting("output_dir", text); }
                                Layout.fillWidth: true
                                font.family: ThemeProvider.getFont("body").family
                                font.pixelSize: ThemeProvider.getFont("body").pixelSize
                                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                            }
                            Button {
                                text: qsTr("Browse...")
                                onClicked: outputDirDialog.open()
                                font.family: ThemeProvider.getFont("button").family
                                font.pixelSize: ThemeProvider.getFont("button").pixelSize
                                font.bold: ThemeProvider.getFont("button").bold
                                background: Rectangle {
                                    color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                                    radius: ThemeProvider.getStyle("button_default").radius
                                    border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                                    border.width: ThemeProvider.getStyle("button_default").borderWidth
                                }
                                contentItem: Text {
                                    text: qsTr("Browse...")
                                    color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                                    font.family: ThemeProvider.getFont("button").family
                                    font.pixelSize: ThemeProvider.getFont("button").pixelSize
                                    font.bold: ThemeProvider.getFont("button").bold
                                }
                            }
                        }
                    }
                }

                FileDialog {
                    id: outputDirDialog
                    title: "Select Output Directory"
                    onAccepted: {
                        var selectedPath = file.toString().replace(/^(file:\/{2,3})/, "");
                        if (Qt.platform.os === "windows" && selectedPath.startsWith("/")) {
                            selectedPath = selectedPath.substring(1);
                        }
                        outputDirField.text = selectedPath;
                        backend.setSetting("output_dir", selectedPath);
                    }
                }

                // Action Buttons
                GroupBox {
                    title: ThemeProvider.getCatchphrase("settings_group_actions", "Actions")
                    Layout.fillWidth: true
                    font.family: ThemeProvider.getFont("body").family
                    font.pixelSize: ThemeProvider.getFont("body").pixelSize
                    background: Rectangle {
                        color: ThemeProvider.getColor("widget_bg")
                        border.color: ThemeProvider.getColor("widget_border")
                        border.width: 2
                        radius: 12
                        layer.enabled: true
                        layer.effect: DropShadow {
                            color: ThemeProvider.getColor("primary"); radius: 12; samples: 16; x: 0; y: 2; spread: 0.08
                        }
                    }
                    Flow {
                        width: parent.width
                        spacing: 12
                        Button {
                            text: ThemeProvider.getCatchphrase("action_reload_settings", "Reload Settings")
                            onClicked: backend.reloadConfig()
                            font.family: ThemeProvider.getFont("button").family
                            font.pixelSize: ThemeProvider.getFont("button").pixelSize
                            font.bold: ThemeProvider.getFont("button").bold
                            background: Rectangle {
                                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                                radius: ThemeProvider.getStyle("button_default").radius
                                border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                                border.width: ThemeProvider.getStyle("button_default").borderWidth
                            }
                            contentItem: Text {
                                text: ThemeProvider.getCatchphrase("action_reload_settings", "Reload Settings")
                                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                                font.family: ThemeProvider.getFont("button").family
                                font.pixelSize: ThemeProvider.getFont("button").pixelSize
                                font.bold: ThemeProvider.getFont("button").bold
                            }
                        }
                        Button {
                            text: ThemeProvider.getCatchphrase("action_clear_cache", "Clear Cache and Logs")
                            onClicked: {
                                if (backend && backend.clearCacheAndLogs) {
                                    backend.clearCacheAndLogs();
                                    clearDialog.text = ThemeProvider.getCatchphrase("dialog_msg_cleanup_complete", "All cache and log files have been cleared.");
                                    clearDialog.open();
                                }
                            }
                            font.family: ThemeProvider.getFont("button").family
                            font.pixelSize: ThemeProvider.getFont("button").pixelSize
                            font.bold: ThemeProvider.getFont("button").bold
                            background: Rectangle {
                                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey)
                                radius: ThemeProvider.getStyle("button_default").radius
                                border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey)
                                border.width: ThemeProvider.getStyle("button_default").borderWidth
                            }
                            contentItem: Text {
                                text: ThemeProvider.getCatchphrase("action_clear_cache", "Clear Cache and Logs")
                                color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey)
                                font.family: ThemeProvider.getFont("button").family
                                font.pixelSize: ThemeProvider.getFont("button").pixelSize
                                font.bold: ThemeProvider.getFont("button").bold
                            }
                        }
                    }
                }
            }
        }
        MessageDialog {
            id: clearDialog
            title: ThemeProvider.getCatchphrase("dialog_title_cleanup_complete", "Cleanup Complete")
            text: ""
            visible: false
            onAccepted: visible = false
        }
    }

    function saveThemeSubOptions() {
        // Save theme suboptions as a single object
        var subOptions = {
            use_character_catchphrases: useCharacterCatchphrasesBox.checked,
            show_special_icons: showSpecialIconsBox.checked,
            enable_animated_background: enableAnimatedBackgroundBox.checked
        };
        backend.setSetting("theme_suboptions", subOptions);
    }
}
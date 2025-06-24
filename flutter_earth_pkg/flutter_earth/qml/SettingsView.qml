import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
// import Qt.labs.settings 1.0 // Not used here directly, backend handles settings persistence
import "." // For ThemeProvider

Rectangle {
    id: settingsView
    color: ThemeProvider.getColor("background", "#f3e5f5")
    anchors.fill: parent

    property var allSettings: backend.getAllSettings() // Full config for initial values
    property var currentThemeData: backend.getCurrentThemeData() // For sub-options
    property var availableThemesModel: backend.getAvailableThemes() // List of {name, display_name, category}

    function findThemeIndex(themeName) {
        for (var i = 0; i < availableThemesModel.length; ++i) {
            if (availableThemesModel[i].name === themeName) return i;
        }
        return -1; // Default to first if not found or handle error
    }

    // React to config/setting changes
    Connections {
        target: backend
        function onConfigChanged(newConfig) { // newConfig is the full config dict
            allSettings = newConfig;
            currentThemeData = backend.getCurrentThemeData(); // Refresh full theme data too
            themeCombo.currentIndex = findThemeIndex(allSettings.theme);
            outputDirField.text = allSettings.output_dir;
            // Update checkboxes for theme sub-options
            var currentThemeOptions = currentThemeData.options || {};
            useCharacterCatchphrasesBox.checked = currentThemeOptions.use_character_catchphrases || false;
            showSpecialIconsBox.checked = currentThemeOptions.show_special_icons || false;
            enableAnimatedBackgroundBox.checked = currentThemeOptions.enable_animated_background || false;
        }
        function onSettingChanged(key, value) {
            if (key === "theme") {
                themeCombo.currentIndex = findThemeIndex(value);
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

    ColumnLayout {
        anchors.fill: parent // Changed from centerIn for scrollability
        anchors.margins: 20
        spacing: 20

        Label { // Changed from Text for consistency, can be Text
            text: ThemeProvider.getCatchphrase("view_SettingsView", "Settings")
            font: ThemeProvider.getFont("title")
            color: ThemeProvider.getColor("primary")
            Layout.alignment: Qt.AlignHCenter
        }

        ScrollView { // Added ScrollView for potentially many settings
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ColumnLayout {
                width: parent.width // Ensure inner layout uses ScrollView's width
                spacing: 15

                // Theme selection
                GroupBox {
                    title: ThemeProvider.getCatchphrase("settings_group_theme", "Appearance")
                    Layout.fillWidth: true
                    font: ThemeProvider.getFont("body") // GroupBox title font

                    ColumnLayout {
                        width: parent.width // Ensure inner layout uses GroupBox width
                        RowLayout {
                            Label { text: ThemeProvider.getCatchphrase("settings_label_theme", "Theme:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                            ComboBox {
                                id: themeCombo
                                model: availableThemesModel
                                textRole: "display_name" // Show user-friendly name
                                currentIndex: findThemeIndex(allSettings.theme)
                                font: ThemeProvider.getFont("body")
                                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                                popup.background: Rectangle { color: ThemeProvider.getColor("list_bg"); border.color: ThemeProvider.getColor("widget_border") }

                                Component.onCompleted: {
                                    // Ensure current theme is correctly selected if model loads after allSettings.theme
                                    if(allSettings && allSettings.theme) {
                                        currentIndex = findThemeIndex(allSettings.theme);
                                    }
                                }

                                onClicked: { // Refresh model in case it changed due to external factors (less likely here)
                                    availableThemesModel = backend.getAvailableThemes();
                                    if(allSettings && allSettings.theme) {
                                         currentIndex = findThemeIndex(allSettings.theme);
                                    }
                                }

                                onCurrentIndexChanged: {
                                    if (currentIndex >= 0 && availableThemesModel[currentIndex]) {
                                        var selectedThemeName = availableThemesModel[currentIndex].name;
                                        if (allSettings.theme !== selectedThemeName) {
                                            backend.setTheme(selectedThemeName);
                                        }
                                    }
                                }
                            }
                        }

                        // Theme Sub-options
                        Label {
                            text: ThemeProvider.getCatchphrase("settings_label_theme_options", "Theme Options:")
                            font: ThemeProvider.getFont("body");
                            color: ThemeProvider.getColor("text");
                            topPadding: 10
                        }
                        CheckBox {
                            id: useCharacterCatchphrasesBox
                            text: ThemeProvider.getCatchphrase("settings_opt_catchphrases", "Use Character Catchphrases")
                            checked: currentThemeData.options ? currentThemeData.options.use_character_catchphrases : false
                            font: ThemeProvider.getFont("body")
                            onCheckedChanged: saveThemeSubOptions()
                        }
                        CheckBox {
                            id: showSpecialIconsBox
                            text: ThemeProvider.getCatchphrase("settings_opt_icons", "Show Special Icons")
                            checked: currentThemeData.options ? currentThemeData.options.show_special_icons : false
                            font: ThemeProvider.getFont("body")
                            onCheckedChanged: saveThemeSubOptions()
                        }
                        CheckBox {
                            id: enableAnimatedBackgroundBox
                            text: ThemeProvider.getCatchphrase("settings_opt_animations", "Enable Animated Backgrounds")
                            checked: currentThemeData.options ? currentThemeData.options.enable_animated_background : false
                            font: ThemeProvider.getFont("body")
                            onCheckedChanged: saveThemeSubOptions()
                        }
                    }
                }

                // Output directory
                GroupBox {
                    title: ThemeProvider.getCatchphrase("settings_group_general", "General")
                    Layout.fillWidth: true
                    font: ThemeProvider.getFont("body")
                    ColumnLayout {
                         width: parent.width
                        RowLayout {
                            Label { text: ThemeProvider.getCatchphrase("settings_label_output_dir", "Output Directory:"); font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text") }
                            TextField {
                                id: outputDirField
                                text: allSettings.output_dir
                                onEditingFinished: { backend.setSetting("output_dir", text); }
                                Layout.fillWidth: true
                                font: ThemeProvider.getFont("body")
                                color: ThemeProvider.getColor(ThemeProvider.styles.text_input.textColorKey)
                                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.text_input.backgroundColorKey); border.color: ThemeProvider.getColor(ThemeProvider.styles.text_input.borderColorKey); radius: ThemeProvider.getStyle("text_input").radius }
                            }
                             Button {
                                text: qsTr("Browse...") // Standard, no catchphrase needed
                                onClicked: outputDirDialogForSettings.open()
                                font: ThemeProvider.getFont("button")
                                background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey); radius: ThemeProvider.getStyle("button_default").radius; border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey) }
                                contentItem: Text { text: parent.text; color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                            }
                        }
                    }
                }

                FileDialog { // Separate FileDialog for settings view
                    id: outputDirDialogForSettings
                    title: "Select Default Output Directory"
                    selectFolder: true
                    onAccepted: {
                        var selectedPath = fileUrl.toString().replace(/^(file:\/{2,3})/, "");
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
                    font: ThemeProvider.getFont("body")
                    Flow { // Use Flow for buttons to wrap if needed
                        width: parent.width
                        spacing: 10
                        Button {
                            text: ThemeProvider.getCatchphrase("action_reload_settings", "Reload Settings")
                            onClicked: backend.reloadConfig()
                            font: ThemeProvider.getFont("button")
                            background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey); radius: ThemeProvider.getStyle("button_default").radius; border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey) }
                            contentItem: Text { text: parent.text; color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
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
                            font: ThemeProvider.getFont("button")
                            background: Rectangle { color: ThemeProvider.getColor(ThemeProvider.styles.button_default.backgroundColorKey); radius: ThemeProvider.getStyle("button_default").radius; border.color: ThemeProvider.getColor(ThemeProvider.styles.button_default.borderColorKey) }
                            contentItem: Text { text: parent.text; color: ThemeProvider.getColor(ThemeProvider.styles.button_default.textColorKey); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        }
                    }
                }
            }
        }
        MessageDialog { // Themed MessageDialog
            id: clearDialog
            title: ThemeProvider.getCatchphrase("dialog_title_cleanup_complete", "Cleanup Complete")
            text: ""
            visible: false
            onAccepted: visible = false
            background: Rectangle { color: ThemeProvider.getColor("widget_bg"); border.color: ThemeProvider.getColor("widget_border") }
            contentItem: Text { text: clearDialog.text; font: ThemeProvider.getFont("body"); color: ThemeProvider.getColor("text"); wrapMode: Text.WordWrap }
        }
    }

    function saveThemeSubOptions() {
        var newSubOptions = {
            use_character_catchphrases: useCharacterCatchphrasesBox.checked,
            show_special_icons: showSpecialIconsBox.checked,
            enable_animated_background: enableAnimatedBackgroundBox.checked
        };
        // Save as a single dictionary object. ThemeProvider will listen for this key.
        backend.setSetting("theme_suboptions", newSubOptions);
        // Also update ThemeProvider's current options directly for immediate effect if backend signal is slow
        // This might be redundant if onSettingChanged in ThemeProvider is quick enough
        ThemeProvider.options = newSubOptions;
        ThemeProvider.currentTheme.options = newSubOptions; // Keep ThemeProvider's full theme data consistent
    }
}
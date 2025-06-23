import QtQuick 2.0

pragma Singleton

QtObject {
    id: style

    // These properties will now be driven by the Python backend.
    // The initial values are placeholders; they get updated on completion.
    property color background: "#2E2E2E"
    property color foreground: "#FFFFFF"
    property color primary: "#5A9BD5"
    property color secondary: "#7AC043"
    property color accent: "#F4B183"
    property color error: "#FF5555"
    property color success: "#66FF66"
    property color text: "#F0F0F0"
    property color text_subtle: "#B0B0B0"
    property color disabled: "#555555"
    property color widget_bg: "#3C3C3C"
    property color widget_border: "#505050"
    property color button_bg: "#5A9BD5"
    property color button_fg: "#FFFFFF"
    property color button_hover_bg: "#7FBCE9"
    property color entry_bg: "#252525"
    property color entry_fg: "#FFFFFF"
    property color entry_border: "#505050"
    property color list_bg: "#333333"
    property color list_fg: "#FFFFFF"
    property color list_selected_bg: "#5A9BD5"
    property color list_selected_fg: "#FFFFFF"
    property color tooltip_bg: "#FFFFE0"
    property color tooltip_fg: "#000000"
    property color progressbar_bg: "#555555"
    property color progressbar_fg: "#5A9BD5"

    function updateThemeColors(themeData) {
        if (!themeData) {
            console.log("Warning: updateThemeColors called with null data.")
            return;
        }
        
        background = themeData.background || "#2E2E2E";
        foreground = themeData.foreground || "#FFFFFF";
        primary = themeData.primary || "#5A9BD5";
        secondary = themeData.secondary || "#7AC043";
        accent = themeData.accent || "#F4B183";
        error = themeData.error || "#FF5555";
        success = themeData.success || "#66FF66";
        text = themeData.text || "#F0F0F0";
        text_subtle = themeData.text_subtle || "#B0B0B0";
        disabled = themeData.disabled || "#555555";
        widget_bg = themeData.widget_bg || "#3C3C3C";
        widget_border = themeData.widget_border || "#505050";
        button_bg = themeData.button_bg || "#5A9BD5";
        button_fg = themeData.button_fg || "#FFFFFF";
        button_hover_bg = themeData.button_hover_bg || "#7FBCE9";
        entry_bg = themeData.entry_bg || "#252525";
        entry_fg = themeData.entry_fg || "#FFFFFF";
        entry_border = themeData.entry_border || "#505050";
        list_bg = themeData.list_bg || "#333333";
        list_fg = themeData.list_fg || "#FFFFFF";
        list_selected_bg = themeData.list_selected_bg || "#5A9BD5";
        list_selected_fg = themeData.list_selected_fg || "#FFFFFF";
        tooltip_bg = themeData.tooltip_bg || "#FFFFE0";
        tooltip_fg = themeData.tooltip_fg || "#000000";
        progressbar_bg = themeData.progressbar_bg || "#555555";
        progressbar_fg = themeData.progressbar_fg || "#5A9BD5";
    }

    Connections {
        target: backend
        
        function onThemeChanged() {
            console.log("Style.qml: Detected theme change from backend.");
            var newThemeColors = backend.getCurrentThemeColors();
            updateThemeColors(newThemeColors);
        }
    }

    Component.onCompleted: {
        if (backend) {
            console.log("Style.qml: Component completed, loading initial theme.");
            var initialThemeColors = backend.getCurrentThemeColors();
            updateThemeColors(initialThemeColors);
        } else {
            console.log("Style.qml: Backend not available on component completion.");
        }
    }
} 
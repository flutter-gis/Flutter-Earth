"""
Manages animations for the Flutter Earth GUI, allowing for theme-specific
animation styles.
"""
from PyQt5 import QtCore, QtWidgets

class AnimationManager:
    """
    Handles the application of animations to widgets based on the current
    theme's animation profile.
    """
    def __init__(self, profile: str):
        self.set_profile(profile)

    def set_profile(self, profile: str):
        """Sets the animation profile to use."""
        self.profile = profile

    def apply_entrance_animation(self, widget: QtWidgets.QWidget):
        """
        Applies an entrance animation to a widget based on the current profile.
        """
        if self.profile == "gentle":
            self._animate_gentle_fade_in(widget)
        elif self.profile == "professional":
            self._animate_professional_fade_in(widget)
        else:
            # Default to professional if profile is unknown
            self._animate_professional_fade_in(widget)

    def _animate_professional_fade_in(self, widget: QtWidgets.QWidget):
        """A clean, quick fade-in animation."""
        effect = QtWidgets.QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        anim = QtCore.QPropertyAnimation(effect, b"opacity")
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        anim.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def _animate_gentle_fade_in(self, widget: QtWidgets.QWidget):
        """A slower, softer fade-in for a more delicate feel."""
        effect = QtWidgets.QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        anim = QtCore.QPropertyAnimation(effect, b"opacity")
        anim.setDuration(800) # Longer duration for a softer feel
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QtCore.QEasingCurve.InCubic) # A more gentle curve
        anim.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    # We can add more animation types here in the future,
    # e.g., for button clicks, panel slides, etc. 
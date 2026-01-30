"""Notification manager for Windows toast notifications."""

import threading


class NotificationManager:
    """Manage Windows toast notifications for achievements and milestones."""
    
    def __init__(self):
        """Initialize notification manager."""
        self.toaster = None
        self._init_toaster()
    
    def _init_toaster(self):
        """Initialize toast notifier."""
        try:
            from win10toast import ToastNotifier
            self.toaster = ToastNotifier()
        except Exception as e:
            print(f"Failed to initialize toast notifications: {e}")
            self.toaster = None
    
    def show_notification(self, title: str, message: str, duration: int = 5):
        """
        Show a Windows toast notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Display duration in seconds
        """
        if not self.toaster:
            print(f"Notification: {title} - {message}")
            return
        
        # Run in background thread to avoid blocking
        def _show():
            try:
                self.toaster.show_toast(
                    title,
                    message,
                    duration=duration,
                    threaded=True
                )
            except Exception as e:
                print(f"Error showing notification: {e}")
        
        thread = threading.Thread(target=_show)
        thread.daemon = True
        thread.start()
    
    def show_achievement(self, achievement_name: str):
        """Show achievement notification."""
        self.show_notification(
            "Achievement Unlocked! 🏆",
            achievement_name,
            duration=7
        )
    
    def show_daily_goal(self, words_count: int, streak: int = 0):
        """Show daily goal completion notification."""
        message = f"You've learned {words_count} words today!"
        if streak > 1:
            message += f" {streak} day streak! 🔥"
        
        self.show_notification(
            "Daily Goal Reached! 🎉",
            message,
            duration=5
        )
    
    def show_streak_milestone(self, streak: int):
        """Show streak milestone notification."""
        if streak >= 100:
            emoji = "🔥🔥🔥"
        elif streak >= 30:
            emoji = "🔥🔥"
        else:
            emoji = "🔥"
        
        self.show_notification(
            f"Streak Milestone! {emoji}",
            f"You've been learning for {streak} consecutive days!",
            duration=7
        )

import os
import sys
import threading
import json
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QTimeEdit,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, QTime, QTimer
import schedule
import time
from datetime import datetime, timedelta

# Reminder widget
class ReminderWidget(QPushButton):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setText("Take your medicine")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.clicked.connect(self.hide)


# Settings window
class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Medicine Reminder Settings")

        self.schedule_label = QLabel("Schedule:")
        self.schedule_input = QLineEdit()

        self.cutoff_label = QLabel("Cutoff Time:")
        self.cutoff_input = QTimeEdit()
        self.cutoff_input.setDisplayFormat("HH:mm")

        self.next_reminder_label = QLabel("Next Reminder:")
        self.next_reminder_value = QLabel()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.schedule_label)
        self.layout.addWidget(self.schedule_input)
        self.layout.addWidget(self.cutoff_label)
        self.layout.addWidget(self.cutoff_input)
        self.layout.addWidget(self.next_reminder_label)
        self.layout.addWidget(self.next_reminder_value)

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.save_button)
        self.layout.addLayout(self.button_layout)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.load_settings()
        self.update_next_reminder()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_next_reminder)
        self.timer.start(60000)  # Update every minute

    def save_settings(self):
        settings = {
            "schedule": self.schedule_input.text().split(","),
            "cutoff_time": self.cutoff_input.text(),
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        schedule.clear()
        schedule_reminders(settings, reminder_widget)
        print("Settings saved!")
        self.update_next_reminder()

    def load_settings(self):
        if not os.path.exists("settings.json"):
            default_settings = {
                "schedule": ["08:00", "12:00", "18:00"],
                "cutoff_time": "23:59",
            }
            with open("settings.json", "w") as f:
                json.dump(default_settings, f)

        with open("settings.json", "r") as f:
            settings = json.load(f)

        self.schedule_input.setText(",".join(settings["schedule"]))
        self.cutoff_input.setTime(QTime.fromString(settings["cutoff_time"], "HH:mm"))

        return settings

    def update_next_reminder(self):
        settings = self.load_settings()
        next_run = time_until_next_reminder(settings)
        if next_run is not None:
            now = datetime.now().time()
            delta = datetime.combine(datetime.today(), next_run) - datetime.combine(
                datetime.today(), now
            )
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.next_reminder_value.setText(f"{int(hours):02d}:{int(minutes):02d}")
        else:
            self.next_reminder_value.setText("No reminders scheduled")


def time_until_next_reminder(settings):
    now = datetime.now().time()
    times = [datetime.strptime(t, "%H:%M").time() for t in settings["schedule"]]
    times = [
        t
        if t > now
        else (datetime.combine(datetime.today(), t) + timedelta(days=1)).time()
        for t in times
    ]
    next_time = min(times, default=None)
    return next_time


def show_reminder(reminder_widget):
    reminder_widget.show()


def schedule_reminders(settings, reminder_widget):
    for time_string in settings["schedule"]:
        schedule.every().day.at(time_string).do(
            show_reminder, reminder_widget=reminder_widget
        )


def reminder_scheduler(settings, reminder_widget):
    schedule_reminders(settings, reminder_widget)
    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    global reminder_widget
    app = QApplication(sys.argv)

    settings_window = SettingsWindow()
    settings_window.show()

    settings = settings_window.load_settings()
    reminder_widget = ReminderWidget()

    scheduler_thread = threading.Thread(
        target=reminder_scheduler, args=(settings, reminder_widget)
    )
    scheduler_thread.daemon = True
    scheduler_thread.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

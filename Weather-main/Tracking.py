import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QUrl, QObject, pyqtSlot, QTimer
from PyQt5.QtQuick import QQuickView
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine, QQmlProperty
from geopy.distance import geodesic
import pyttsx3
import math

# Simulated path (lat, lon)
path = [
    (42.672, -83.215),
    (42.6725, -83.2155),
    (42.673, -83.216),
    (42.6735, -83.2165)
]

def get_arrow_emoji(start, end):
    dx = end[1] - start[1]  # longitude difference
    dy = end[0] - start[0]  # latitude difference
    angle = math.degrees(math.atan2(dy, dx))  # angle in degrees

    if -22.5 < angle <= 22.5:
        return "→"
    elif 22.5 < angle <= 67.5:
        return "⇗"
    elif 67.5 < angle <= 112.5:
        return "↑"
    elif 112.5 < angle <= 157.5:
        return "⇖"
    elif angle > 157.5 or angle <= -157.5:
        return "←"
    elif -157.5 < angle <= -112.5:
        return "⇙"
    elif -112.5 < angle <= -67.5:
        return "↓"
    elif -67.5 < angle <= -22.5:
        return "⇘"
    else:
        return "↑"
    
class GPSNavigator(QObject):
    def __init__(self, engine):
        super().__init__()
        self.engine = pyttsx3.init()
        self.qml_engine = engine
        self.map_obj = engine.rootObjects()[0].findChild(QObject, "mapObj")
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.steps = list(reversed(path))
        self.index = 0

    @pyqtSlot()
    def retrace_steps(self):
        self.index = 0
        self.timer.start(3000)  # every 3 seconds

    def next_step(self):
        if self.index < len(self.steps) - 1:
            start = self.steps[self.index]
            end = self.steps[self.index + 1]
            emoji = get_arrow_emoji(start, end)
            distance = int(geodesic(start, end).feet)
            text = f"{emoji} Go straight for {distance} feet"
            print(text)
            self.engine.say(text)
            self.engine.runAndWait()

            # Update marker on map
            self.map_obj.setProperty("latitude", end[0])
            self.map_obj.setProperty("longitude", end[1])

            self.index += 1
        else:
            self.engine.say("You have arrived back at the starting point.")
            self.engine.runAndWait()
            self.timer.stop()

# ---------- MAIN APP ----------
if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load(QUrl.fromLocalFile("map_view.qml"))

    gps_nav = GPSNavigator(engine)
    engine.rootContext().setContextProperty("gpsNav", gps_nav)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())

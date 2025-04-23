import sys
import requests
import queue
import geocoder  # Add this import
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt
import pyttsx3
import threading
import subprocess  # Add this import
import os
# from threading import Lock
# import speech_to_text as stt

class TTSManager:
    def __init__(self):
        self.tts_engine = pyttsx3.init(driverName='sapi5')
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('volume', 1.0)
        self.tts_engine.setProperty('rate', 150)
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def speak(self, text):
        # Add the text to the queue
        self.queue.put(text)

    def stop(self):
        # Stop the current speech
        self.tts_engine.stop()

    def _process_queue(self):
        while True:
            # Get the next text from the queue
            text = self.queue.get()
            if text is None:
                break
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.tts_manager = TTSManager()

        self.city_label = QLabel("Detected city: ", self)
        self.city_name_label = QLabel(self)  # Label to display the detected city
        self.state_label = QLabel("Detected state: ", self)
        self.state_name_label = QLabel(self)  # Label to display the detected state
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)

        self.initUI()
        self.setFocus()
        self.fetch_location_and_weather()  # Automatically fetch the user's location and weather

    def initUI(self):
        self.setWindowTitle("Weather App")

        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_name_label)
        vbox.addWidget(self.state_label)
        vbox.addWidget(self.state_name_label)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_name_label.setAlignment(Qt.AlignCenter)
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_name_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_name_label.setObjectName("city_name_label")
        self.state_label.setObjectName("state_label")
        self.state_name_label.setObjectName("state_name_label")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.setStyleSheet("""
            QLabel, QPushButton{
                font-family: calibri;
            }
            QLabel#city_label, QLabel#state_label{
                font-size: 30px;
                font-style: italic;
            }
            QLabel#city_name_label, QLabel#state_name_label{
                font-size: 40px;
                font-weight: bold;
            }
            QLabel#temperature_label{
                font-size: 75px;
            }
            QLabel#emoji_label{
                font-size: 100px;
                font-family: Segoe UI emoji;
            }
            QLabel#description_label{
                font-size: 50px;
            }
        """)

    def fetch_location_and_weather(self):
        """Fetch the user's current location and automatically get the weather."""
        try:
            g = geocoder.ip('me')  # Use geocoder to get the user's location
            if g.ok and g.city and g.state:
                self.city_name_label.setText(g.city)
                self.state_name_label.setText(g.state)
                self.speak(f"Detected your location as {g.city}, {g.state}.")
                self.get_weather()  # Automatically fetch the weather
            else:
                self.city_name_label.setText("Unknown")
                self.state_name_label.setText("Unknown")
                self.speak("Failed to detect your location. Please check your internet connection.")
        except Exception as e:
            
            print(f"Error fetching location: {e}")
            self.speak("An error occurred while detecting your location.")

    def get_weather(self):
        api_key = "97965af61bdc928256587c0420413016"
        city = self.city_name_label.text().strip()
        state = self.state_name_label.text().strip().upper()

        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state},US&appid={api_key}"

        try:
            geocoding_response = requests.get(geocoding_url)
            geocoding_response.raise_for_status()
            geocoding_data = geocoding_response.json()

            if len(geocoding_data) == 0:
                self.display_error("Location not found")
                return
            
            latitude = geocoding_data[0]['lat']
            longitude = geocoding_data[0]['lon']

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
            weather_response = requests.get(weather_url)
            weather_response.raise_for_status()
            weather_data = weather_response.json()

            if weather_data["cod"] == 200:
                self.display_weather(weather_data)

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection")
            self.speak("Connection Error: Check your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")
            self.speak("Timeout Error: The request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the URL")
            self.speak("Too many Redirects: Check the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Please fill in all of required fields")
            self.speak(f"Please fill in all of required fields")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()
        self.speak(message)



    def speak(self, text):
        # Use the TTS manager to speak the text
        self.tts_manager.speak(text)


    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15
        temperature_f = (temperature_k * 9/5) - 459.67
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]

        self.temperature_label.setText(f"{temperature_f:.0f}°F")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(weather_description)

        city = self.city_name_label.text().strip()
        state = self.state_name_label.text().strip()
        self.ask_for_walk(city, state, temperature_f, weather_description)

    def ask_for_walk(self, city, state, temperature_f, weather_description):
        self.speak(f"The current temperature in {city}, {state} is {temperature_f:.0f} degrees Fahrenheit with {weather_description}. Would you like to go for a walk today? Press space to start the walk.")
        self.setFocus()  # Ensure the window is focused to capture key events

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Space:
            self.launch_gps_tracking()

    def launch_gps_tracking(self):
        """Launch the GPSTracking.py script."""
        try:
            dir_name = os.path.dirname(os.path.abspath(__file__))
            gps_tracking_path = os.path.join(dir_name, 'GPSTracking.py')
            subprocess.Popen(['python', gps_tracking_path], shell=True)
        except Exception as e:
            print(f"Failed to launch GPS tracking app: {e}")

    @staticmethod
    def get_weather_emoji(weather_id):

        if 200 <= weather_id <= 232:
            return "⛈"
        elif 300 <= weather_id <= 321:
            return "🌦"
        elif 500 <= weather_id <= 531:
            return "🌧"
        elif 600 <= weather_id <= 622:
            return "❄"
        elif 701 <= weather_id <= 741:
            return "🌫"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪"
        elif weather_id == 800:
            return "☀"
        elif 801 <= weather_id <= 804:
            return "☁"
        else:
            return ""
        
class SpeakableLineEdit(QLineEdit):
    
    def __init__(self, tts_manager, message, parent=None):
        super().__init__(parent)
        self.tts_manager = tts_manager
        self.message = message

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.tts_manager.stop()  # Stop any ongoing messages
        self.tts_manager.speak(self.message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
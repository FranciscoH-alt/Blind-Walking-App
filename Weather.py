import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt
import pyttsx3
import threading

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.state_label = QLabel("Enter state ncode: ", self)
        self.state_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.tts_engine = pyttsx3.init(driverName='sapi5')
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[0].id)  # Or whichever index worked
        self.tts_engine.setProperty('volume', 1.0)
        self.tts_engine.setProperty('rate', 150)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")

        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.state_label)
        vbox.addWidget(self.state_input)    
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.state_label.setObjectName("state_label")
        self.state_input.setObjectName("state_input")
        self.get_weather_button.setObjectName("get_weather_button")
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
            QLineEdit#city_input, QLineEdit#state_input{
                font-size: 40px;
            }
            QPushButton#get_weather_button{
                font-size: 30px;
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

        self.get_weather_button.clicked.connect(self.get_weather)

        self.start_timer()

    def get_weather(self):

        api_key = "97965af61bdc928256587c0420413016"
        city = self.city_input.text().strip()
        state = self.state_input.text().strip().upper()

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
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()
        self.speak(message)

    def start_timer(self):
        timer = threading.Timer(1, self.speak, args=("Please enter your city and state code",))
        timer.start()

    def speak(self, text):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()


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

        city = self.city_input.text()
        state = self.state_input.text()
        self.speak(f"The current temperature in {city}, {state} is {temperature_f:.0f} degrees Fahrenheit with {weather_description}.")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
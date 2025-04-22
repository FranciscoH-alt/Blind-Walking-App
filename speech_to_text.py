# Python program to translate
# speech to text and text to speech


import speech_recognition as sr
import pyttsx3
import keyboard
import time

# Initialize the recognizer
r = sr.Recognizer()

yesSet = {"yes", "ye"}
noSet = {"no"}

# Function to convert text to
# speech
def speakText(command):
    # Initialize the engine
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()

def userCommand(input):
    if input in yesSet:
        print("Yes command has been confirmed")
        speakText("Yes received")

    elif input in noSet:
        print("No command has been confirmed")
        speakText("No received")
        

    else:
        print("Invalid command")
        speakText("Invalid command")

# Loop infinitely for user to
# speak

#Takes user keyboard input to start listening l
def startListening():
    print("Press 'l' to start listening for 5 seconds...")

    while True:
        if keyboard.is_pressed('l'):
            print("Listening started for 5 seconds...")
            start_time = time.time()

            while True:
                if time.time() - start_time > 5:
                    print("Listening timed out.")
                    break

                try:
                    with sr.Microphone() as source2:
                        r.adjust_for_ambient_noise(source2, duration=0.2)
                        print("Listening...")
                        audio2 = r.listen(source2, timeout=5)

                        MyText = r.recognize_google(audio2)
                        MyText = MyText.lower()

                        print("Did you say:", MyText)
                        userCommand(MyText)

                except sr.WaitTimeoutError:
                    print("No speech detected within timeout.")
                    continue
                except sr.RequestError as e:
                    print("Could not request results; {0}".format(e))
                except sr.UnknownValueError:
                    print("Unknown error encountered.")

startListening()
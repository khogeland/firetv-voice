import fire_instructions as fi
import speech_recognition as sr

mic = sr.Microphone()
recognizer = sr.Recognizer()

while True:
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                fi.do(recognizer.recognize_google(audio))
            except sr.UnknownValueError: pass
            except KeyboardInterrupt:
                exit(1)
    except Exception, e:
        print e
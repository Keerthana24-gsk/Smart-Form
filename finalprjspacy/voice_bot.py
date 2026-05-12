from selenium import webdriver
from selenium.webdriver.common.by import By
import speech_recognition as sr
import pyttsx3
import time
import re
import spacy

#  Load NLP model
nlp = spacy.load("en_core_web_sm")


def speak(text):
    print("Assistant:", text)
    engine = pyttsx3.init('sapi5')
    engine.setProperty('rate', 170)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()
    time.sleep(1)


def listen():
    r = sr.Recognizer()

    for _ in range(3):
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print("User:", text)
            return text.lower()
        except:
            speak("Sorry, please repeat")

    return ""


#  NLP ENTITY EXTRACTION
def extract_entities(text, field):
    doc = nlp(text)

    if "name" in field.lower():
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text

    if "address" in field.lower() or "location" in field.lower():
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                return ent.text

    return text


def clean_input(text, field):
    if not text:
        return ""

    text = text.lower().strip()
    words = text.split()

    # Fix spelling like "j o h n"
    if all(len(w) == 1 for w in words):
        text = "".join(words)

    # EMAIL FIX
    if "email" in field.lower():
        text = text.replace(" at the rate ", "@")
        text = text.replace(" at ", "@")
        text = text.replace(" dot ", ".")
        text = text.replace(" ", "")

        if "@gmail" in text and ".com" not in text:
            text += ".com"

    #  ADDRESS FIX
    elif "address" in field.lower():
        text = text.replace("  ", " ")

    #  PHONE FIX
    elif "phone" in field.lower():
        text = re.sub(r"\D", "", text)

    return text


def run_bot(form_url):

    driver = webdriver.Chrome()
    driver.get(form_url)

    time.sleep(6)

    speak("Form opened. Starting assistant.")

    questions = driver.find_elements(By.CLASS_NAME, "Qr7Oae")

    for q in questions:
        try:
            lines = q.text.split("\n")

            question_text = ""
            for line in lines:
                if len(line.strip()) > 3 and "required" not in line.lower():
                    question_text = line
                    break

            if question_text == "":
                continue

            speak("Please answer: " + question_text)
            time.sleep(2)

            answer = listen()
            answer = clean_input(answer, question_text)

            #  APPLY NLP
            answer = extract_entities(answer, question_text)

            if answer == "":
                speak("Skipping this question")
                continue

            #  CONFIRMATION LOOP
            while True:
                speak("You entered " + answer + ". Is this correct?")
                time.sleep(2)

                confirmation = listen()

                if "yes" in confirmation:
                    break
                elif "no" in confirmation:
                    speak("Please say the correct answer")
                    time.sleep(2)

                    answer = listen()
                    answer = clean_input(answer, question_text)
                    answer = extract_entities(answer, question_text)
                else:
                    speak("Please say yes or no")

            #  Handle input field
            try:
                input_box = q.find_element(By.TAG_NAME, "input")
            except:
                input_box = q.find_element(By.TAG_NAME, "textarea")

            input_box.clear()
            input_box.send_keys(answer)

            speak("Answer updated")
            time.sleep(2)

        except:
            continue

    speak("All fields are filled. Do you want to submit the form?")
    time.sleep(2)

    final = listen()

    if "yes" in final or "submit" in final:
        try:
            submit_btn = driver.find_element(By.XPATH, "//span[text()='Submit']")
            submit_btn.click()
            speak("Form submitted successfully")
        except:
            speak("Submit button not found")
    else:
        speak("Submission cancelled")
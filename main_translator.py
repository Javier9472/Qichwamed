import os
import json
import time
import queue
import numpy as np
import librosa
import tensorflow as tf
import sounddevice as sd
import speech_recognition as sr
import pygame

pygame.init()
pygame.mixer.init(frequency=16000, size=-16, channels=1)

MODEL_PATH = "model/cnn_model.h5"
LABELS_PATH = "model/labels.txt"
ES_TO_QUE_PATH = "routes/es_to_que.json"
QUE_TO_ES_PATH = "routes/que_to_es.json"
SAMPLE_RATE = 16000
DURATION = 2.5
SAMPLES = int(SAMPLE_RATE * DURATION)
IMG_SIZE = (128, 128)

with open(ES_TO_QUE_PATH, "r", encoding="utf-8") as f:
    es_to_que = json.load(f)
with open(QUE_TO_ES_PATH, "r", encoding="utf-8") as f:
    que_to_es = json.load(f)
model = tf.keras.models.load_model(MODEL_PATH)
with open(LABELS_PATH, "r", encoding="utf-8") as f:
    labels = [line.strip() for line in f]

q = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(indata.copy())

def grabar_audio():
    print("Grabando audio...")
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE):
        audio = np.zeros(SAMPLES, dtype=np.float32)
        total_frames = 0
        while total_frames < SAMPLES:
            data = q.get()
            frames = len(data)
            if total_frames + frames > SAMPLES:
                frames = SAMPLES - total_frames
            audio[total_frames:total_frames+frames] = data[:frames, 0]
            total_frames += frames
    return audio

def reproducir_audio(path):
    if os.path.exists(path):
        try:
            print(f"Reproduciendo: {path}")
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print("Error al reproducir con pygame:", e)
    else:
        print("Archivo no encontrado:", path)

def audio_to_mel(audio):
    mel = librosa.feature.melspectrogram(y=audio, sr=SAMPLE_RATE, n_mels=128)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_resized = tf.image.resize(mel_db[..., np.newaxis], IMG_SIZE).numpy()
    return np.expand_dims(mel_resized, axis=0)

def modo_espanol_a_quechua():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("\nHabla una palabra en ESPAÑOL...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        texto = recognizer.recognize_google(audio, language="es-PE").strip().lower()
        print(f"Dijiste: '{texto}'")

        if texto in es_to_que:
            info = es_to_que[texto]
            traduccion = info["traduccion"]
            audio_path = info["audio_quechua"]
            print(f"Traducción: {texto} → {traduccion}")
            reproducir_audio(audio_path)
        else:
            print("Palabra no encontrada en el diccionario español → quechua.")

    except sr.UnknownValueError:
        print("No se entendió tu voz.")
    except sr.RequestError as e:
        print(f"Error con Google API: {e}")

def modo_quechua_a_espanol():
    print("\nHabla una palabra en QUECHUA...")
    audio = grabar_audio()
    mel_spec = audio_to_mel(audio)
    prediction = model.predict(mel_spec)[0]
    pred_index = np.argmax(prediction)
    pred_label = labels[pred_index]
    confidence = prediction[pred_index]

    print(f"Palabra detectada: '{pred_label}' ({confidence*100:.2f}%)")

    if pred_label in que_to_es:
        info = que_to_es[pred_label]
        traduccion = info["traduccion"]
        audio_path = info["audio_español"]
        print(f"Traducción: {pred_label} → {traduccion}")
        reproducir_audio(audio_path)
    else:
        print("Palabra quechua no encontrada en el diccionario.")

if __name__ == "__main__":
    print("Traductor Médico Español ↔ Quechua")
    print("1. Español → Quechua")
    print("2. Quechua → Español")

    while True:
        opcion = input("\nElige modo (1 o 2, q para salir): ").strip()

        if opcion == "1":
            modo_espanol_a_quechua()
        elif opcion == "2":
            modo_quechua_a_espanol()
        elif opcion.lower() == "q":
            print("Hasta pronto.")
            break
        else:
            print("Opción no válida.")

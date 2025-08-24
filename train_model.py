import os
import numpy as np
import tensorflow as tf
import librosa
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping, ModelCheckpoint

DATASET_DIR = "database"
SAMPLE_RATE = 16000
DURATION = 2.5
SAMPLES_PER_TRACK = int(SAMPLE_RATE * DURATION)
IMG_SIZE = (128, 128)
BATCH_SIZE = 16
EPOCHS = 100
MODEL_PATH = "model/cnn_model.h5"
LABELS_PATH = "model/labels.txt"

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

def wav_to_mel_spectrogram(filepath):
    signal, sr = librosa.load(filepath, sr=SAMPLE_RATE)
    if len(signal) > SAMPLES_PER_TRACK:
        signal = signal[:SAMPLES_PER_TRACK]
    else:
        pad_width = SAMPLES_PER_TRACK - len(signal)
        signal = np.pad(signal, (0, pad_width), mode='constant')
    mel = librosa.feature.melspectrogram(y=signal, sr=sr, n_mels=128)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_resized = tf.image.resize(mel_db[..., np.newaxis], IMG_SIZE).numpy()
    return mel_resized

X, y = [], []
label_names = []
label_to_index = {}

for i, label in enumerate(sorted(os.listdir(DATASET_DIR))):
    class_dir = os.path.join(DATASET_DIR, label)
    if os.path.isdir(class_dir):
        label_names.append(label)
        label_to_index[label] = i
        for file in os.listdir(class_dir):
            if file.endswith(".wav"):
                path = os.path.join(class_dir, file)
                try:
                    spec = wav_to_mel_spectrogram(path)
                    X.append(spec)
                    y.append(i)
                except Exception as e:
                    print(f"Error procesando {path}: {e}")

X = np.array(X)
y = np.array(y)

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(IMG_SIZE[0], IMG_SIZE[1], 1)),
    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(128, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(len(label_names), activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

early_stop = EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True)
checkpoint = ModelCheckpoint(MODEL_PATH, monitor='val_accuracy', save_best_only=True, verbose=1)

history = model.fit(X_train, y_train,
                    validation_data=(X_val, y_val),
                    epochs=EPOCHS,
                    batch_size=BATCH_SIZE,
                    callbacks=[early_stop, checkpoint])

with open(LABELS_PATH, "w", encoding="utf-8") as f:
    for label in label_names:
        f.write(f"{label.strip().lower()}\n")

print(f"\nModelo entrenado y guardado en: {MODEL_PATH}")
print(f"Etiquetas guardadas en: {LABELS_PATH}")

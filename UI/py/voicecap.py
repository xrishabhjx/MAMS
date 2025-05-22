import os
import time
import wave
import threading
from datetime import datetime
import numpy as np
import pyaudio
import librosa
import pickle
from tensorflow.keras.models import load_model

# === SETTINGS ===
AUDIO_DIR = "assets/audio_data"
COMBINED_AUDIO_PATH = "assets/combined.wav"
RECORD_SECONDS = 5
GAP_SECONDS = 10  # Gap between recordings
SAMPLE_RATE = 22050
CHANNELS = 1
CHUNK = 1024
FORMAT = pyaudio.paInt16
N_MFCC = 40

MODEL_PATH = "assets/models/sentiment_cnn_model.h5"
PKL_PATH = "assets/models/le.pkl"

# Ensure output directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# === Load model and preprocessor ===
print("Loading model and preprocessing pipeline...")
model = load_model(MODEL_PATH)
with open(PKL_PATH, 'rb') as f:
    preprocessor = pickle.load(f)


# === Audio recording function ===
def record_audio(file_path):
    print(f" Recording audio: {file_path}")
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=SAMPLE_RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    for _ in range(0, int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))


# === Combine 3 audio files into 1 ===
def combine_audio(file_paths, output_path):
    combined_frames = b''
    for path in file_paths:
        with wave.open(path, 'rb') as wf:
            combined_frames += wf.readframes(wf.getnframes())

    # Save to one file
    with wave.open(output_path, 'wb') as wf_out:
        wf_out.setnchannels(CHANNELS)
        wf_out.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf_out.setframerate(SAMPLE_RATE)
        wf_out.writeframes(combined_frames)

    print(f" Combined audio saved to: {output_path}")


# === Feature Extraction & Prediction ===
def extract_features(file_path):
    signal, sr = librosa.load(file_path, sr=SAMPLE_RATE)
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=N_MFCC)
    mfcc_mean = np.mean(mfcc.T, axis=0)
    return mfcc_mean

def analyze_sentiment(audio_path):
    print(f" Analyzing sentiment from: {audio_path}")
    mfcc = extract_features(audio_path)
    x = np.expand_dims(mfcc, axis=0)       # (1, 40)
    x = np.reshape(x, (1, 40, 1, 1))        # (1, 40, 1, 1) for model input
    prediction = model.predict(x)


#     if preprocessor:
#         x = preprocessor.transform(x)

    classes = ['negative', 'neutral', 'positive']
    pred_class = classes[np.argmax(prediction)]
    print(f" Predicted Sentiment: {pred_class}")

    if pred_class == 'positive':
        return 1
    elif pred_class == 'neutral':
        return 0.5
    else:
        return 0

# === Main capture function ===
def capture_audio_sequence():
    print("Starting 3x audio capture over 30 seconds...")

    file_paths = []
    for i in range(3):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(AUDIO_DIR, f"audio_{i}_{timestamp}.wav")
        record_audio(file_path)
        file_paths.append(file_path)

        if i < 2:  # Wait only after the first two
            time.sleep(GAP_SECONDS)

    # Combine and analyze
    combine_audio(file_paths, COMBINED_AUDIO_PATH)
    result = analyze_sentiment(COMBINED_AUDIO_PATH)
    print(f" Final Sentiment Score: {result}")
    return result

# === Run Once ===
if __name__ == "__main__":
    capture_audio_sequence()
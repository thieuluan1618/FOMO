from transformers import pipeline
import soundfile as sf
import time
import streamlit as st


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.6f} seconds")
        return result
    return wrapper

@st.cache_resource
def load_tts(lang="vie"):
    return pipeline("text-to-speech", model=f"facebook/mms-tts-{lang}")

@timeit
def speak(text, tts=None, save_path=None, lang="vie"):
    if tts is None:
        tts = load_tts(lang)

    speech = tts(text)
    print(type(speech["audio"]))
    print(speech["audio"])
    audio = speech["audio"].squeeze()  # converts (1, N) → (N,)
    if save_path:
        sf.write(save_path, audio, samplerate=speech["sampling_rate"])
        print(f"Saved to {save_path}")
        return
    return audio, speech["sampling_rate"]

# Example use:
if __name__ == "__main__":
    load_tts(lang="eng")
    speak("""1️⃣ Using transformers (automatic download & caching)

If you just do:

from transformers import pipeline

tts = pipeline("text-to-speech", model="facebook/mms-tts-eng")


Hugging Face will automatically:

download the model once,

store it under your local cache (usually ~/.cache/huggingface/hub),

and reuse it later offline.

You can check the actual path via:

tts.model.config._name_or_path""", lang="eng")

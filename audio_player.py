import streamlit as st
import io
import base64
import numpy as np
import soundfile as sf  # or scipy.io.wavfile
from streamlit.components.v1 import html

def create_audio_player(audio_data, sample_rate, autoplay=False):
    """
    Create a custom audio player component from numpy audio data.
    
    Args:
        audio_data (np.ndarray): Audio data as numpy array
        sample_rate (int): Sample rate of the audio
        
    Returns:
        None: Displays the audio player component in Streamlit
    """
    # Convert NumPy array -> WAV bytes
    wav_buffer = io.BytesIO()
    sf.write(wav_buffer, audio_data, sample_rate, format="WAV")
    wav_bytes = wav_buffer.getvalue()

    # Convert to base64 for embedding
    b64_audio = base64.b64encode(wav_bytes).decode()
    audio_src = f"data:audio/wav;base64,{b64_audio}"

    # Custom minimal audio player
    html(f"""
<div class="audio-player">
  <button id="play-btn">▶</button>
  <audio id="audio" src="{audio_src}" preload="auto" {'autoplay="true"' if autoplay else ''}"></audio>
</div>

<style>
body {{
  margin: 0;
}}
.audio-player {{
  display: flex;
  align-items: center;
  gap: 10px;
}}
#play-btn {{
  font-size: 18px;
  width: 40px;
  height: 40px;
  border-radius: 0.5rem;
  cursor: pointer;
  background-color: rgb(255, 255, 255);
  border: 1px solid rgba(49, 51, 63, 0.2);
  transition: transform .1s;
}}
#play-btn:hover {{
  background-color: rgba(151, 166, 195, 0.15);
}}
#play-btn:active {{
  transform: scale(0.95);
}}
</style>

<script>
const btn = document.getElementById('play-btn');
const audio = document.getElementById('audio');
btn.addEventListener('click', () => {{
  if (audio.paused) {{
    audio.play();
    btn.textContent = '⏹';
  }} else {{
    audio.pause();
    audio.currentTime = 0;
    btn.textContent = '▶';
  }}
}});
audio.addEventListener('ended', () => {{
  btn.textContent = '▶';
}});
audio.play();
btn.textContent = '⏹';
</script>
""", height=80)



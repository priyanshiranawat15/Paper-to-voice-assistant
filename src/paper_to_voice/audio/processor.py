"""
Audio processing and consolidation functionality
"""

import os
import streamlit as st
from time import sleep
from tqdm import tqdm
from tempfile import NamedTemporaryFile
from pydub import AudioSegment
from pydub.generators import Sine

from .tts import generate_podcast_audio
from ..core.config import LIGHT_GUITAR_FREQ, AMBIENT_GUITAR_FREQ, GUITAR_DURATION


def store_voice(topic_dialog: dict) -> list[str]:
    """
    Generate voice files for all dialog parts
    
    Args:
        topic_dialog: Dictionary containing dialog content
        
    Returns:
        List of audio file paths
    """
    audio_path = []
    for topic, dialog in tqdm(topic_dialog.items()):
        # Check if dialog is a string or already a list
        if isinstance(dialog, str):
            dialog_speaker = dialog.split("\n")
        elif isinstance(dialog, list):
            dialog_speaker = dialog  # If it's already a list, use it directly
        else:
            continue  # Skip if dialog is neither a string nor a list

        for speaker in tqdm(dialog_speaker):
            one_dialog = speaker.strip()
            language_for_tts = "EN"

            if len(one_dialog) > 0:
                # Generate the podcast audio for each dialog
                audio_file_path = generate_podcast_audio(one_dialog, language_for_tts)
                audio_path.append(audio_file_path)

            sleep(5)
        break  # This break will stop after processing the first topic
    return audio_path


def consolidate_voice(audio_paths: list[str], voice_dir: str) -> str:
    """
    Consolidate multiple audio files into a single podcast file
    
    Args:
        audio_paths: List of audio file paths
        voice_dir: Directory to store voice files
        
    Returns:
        Path to the consolidated audio file
    """
    audio_segments = []
    voice_path = [paths for paths in audio_paths if paths != 'Empty Text']

    # Create guitar audio paths
    light_guitar_path = os.path.join(voice_dir, "light-guitar.wav")
    ambient_guitar_path = os.path.join(voice_dir, "ambient-guitar.wav")

    # Ensure guitar audio exists
    if not os.path.exists(light_guitar_path):
        Sine(LIGHT_GUITAR_FREQ).to_audio_segment(duration=GUITAR_DURATION).export(
            light_guitar_path, format="wav"
        )
    
    if not os.path.exists(ambient_guitar_path):
        Sine(AMBIENT_GUITAR_FREQ).to_audio_segment(duration=GUITAR_DURATION).export(
            ambient_guitar_path, format="wav"
        )

    # Add background guitar tracks
    audio_segments.append(AudioSegment.from_file(light_guitar_path))
    
    # Add voice tracks
    for audio_file_path in voice_path:
        try:
            audio_segment = AudioSegment.from_file(audio_file_path)
            audio_segments.append(audio_segment)
        except Exception as e:
            st.warning(f"Could not process audio file {audio_file_path}: {e}")

    # Add ambient guitar track
    audio_segments.append(AudioSegment.from_file(ambient_guitar_path))

    # Combine audio
    if audio_segments:
        combined_audio = sum(audio_segments)
        os.makedirs(os.path.join(voice_dir, "tmp"), exist_ok=True)
        
        with NamedTemporaryFile(dir=os.path.join(voice_dir, "tmp"), 
                                 delete=False, 
                                 suffix=".mp3") as temp_file:
            combined_audio.export(temp_file.name, format="mp3")
            return temp_file.name
    
    return None

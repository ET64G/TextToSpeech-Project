import asyncio
import os
import re
from typing import Iterable, List
import edge_tts
import pygame
import time

# This provides a blocking text-to-speech function  you can call from the GUI.
# Can both generate and play audio files.

DEFAULT_VOICE = "en-GB-RyanNeural"


def _clean_text_for_speech(text: str) -> str:
    """
    Cleans text to remove unwanted pauses from line breaks.
    - Replaces single newlines with spaces (line breaks within sentences)
    - Converts paragraph breaks (double+ newlines) to single spaces
    - Normalizes multiple spaces to single spaces
    - Removes leading/trailing whitespace
    """
    # Replace multiple newlines (paragraph breaks) with a single space
    text = re.sub(r"\n\s*\n", " ", text)
    
    # Replace all remaining single newlines with spaces
    text = text.replace("\n", " ")
    
    # Normalize multiple spaces to single spaces
    text = re.sub(r" +", " ", text)
    
    # Remove leading/trailing whitespace
    return text.strip()


async def _save_tts_async(text: str, out_path: str, voice: str = DEFAULT_VOICE) -> None:
    communicator = edge_tts.Communicate(text, voice=voice)
    await communicator.save(out_path)


def text_to_speech(text: str, out_path: str, voice: str = DEFAULT_VOICE) -> None:
    """
    Synchronous wrapper you can call from the GUI.
    Saves MP3 to out_path.
    Cleans the text first to remove unwanted pauses from line breaks.
    """
    # Clean the text to remove unwanted pauses
    cleaned_text = _clean_text_for_speech(text)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    asyncio.run(_save_tts_async(cleaned_text, out_path, voice))


def play_audio(path: str) -> None:
    """
    Play an audio file using pygame (blocks until finished).
    """
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

    # Wait until playback is finished
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.stop()
    pygame.mixer.quit()

# Global variable to track if mixer is initialized
_mixer_initialized = False
def init_mixer() -> None:
    """Initialize pygame mixer if not already initialized."""
    global _mixer_initialized
    if not _mixer_initialized:
        pygame.mixer.init()
        _mixer_initialized = True

def start_playback(path: str) -> None:
    """ 
    Start playing an audio file (non-blocking).
    Returns immediately, playback continues in background.
    """
    print(f"DEBUG: start_playback called with path: {path}") # Debug print
    init_mixer()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

def pause_playback() -> None:
    """ Pause the current playback."""
    if _mixer_initialized:
        pygame.mixer.music.pause()

def unpause_playback() -> None:
    """ Unpause the current playback."""
    if _mixer_initialized:
        pygame.mixer.music.unpause()

def stop_playback() -> None:
    """ Stop the current playback."""
    if _mixer_initialized:
        pygame.mixer.music.stop()

def is_playing() -> bool:
    """ Check if playback is currently active."""
    if _mixer_initialized:
        return pygame.mixer.music.get_busy()
    return False


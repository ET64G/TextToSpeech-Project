"""
Utility functions for the PDF to Speech application.
Contains helper functions for file validation, path management, and audio file handling.
"""

import os
from pathlib import Path


def is_valid_pdf_file(file_path: str) -> bool:
    """
    Validates if a file exists and has a .pdf extension.
    
    Args:
        file_path: The path to the file to validate
        
    Returns:
        True if the file exists and has .pdf extension, False otherwise
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return False

    # Check that it is a valid file and not a directory
    if not os.path.isfile(file_path):
        return False

    # Check that the extension is .pdf (case-insensitive)
    file_extension = Path(file_path).suffix.lower()
    return file_extension == ".pdf"


def get_temp_audio_path(filename: str = "pdf_tts_output.mp3") -> str:
    """
        Generates a full path for a temporary audio file in the system temp directory.
    
    Args:
        filename: The name of the audio file (default: "pdf_tts_output.mp3")
        
    Returns:
        Full path to the temporary audio file
    """
    import tempfile

    # Get the systems temporary directory ( works on both Windows and Linux)
    tmp_dir = tempfile.gettempdir()

    # Join the temp directory with the filename
    return os.path.join(tmp_dir, filename)


def get_unique_audio_path(base_name: str = "pdf_tts_output") -> str:
    """
    Generates a unique temporary audio file path to avoid overwriting previous files.
    Adds a timestamp to make the filename unique.
    
    Args:
        base_name: Base name for the file (without extension)
        
    Returns:
        Full path to a unique temporary audio file
    """
    import tempfile
    from datetime import datetime

    # Get temp directory
    temp_dir = tempfile.gettempdir()

    # Create a timestamp string (format: YYYYMMDD_HHMMSS)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create unique filename with time stamp
    unique_name = f"{base_name}_{timestamp}.mp3"

    # Join temp directory with unique name
    return os.path.join(temp_dir, unique_name)

def format_file_size(size_bytes: int) -> str:
    """
    Converts file size in bytes to a human-readable string.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB", "500 KB")
    """
    # Define size units
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

    

    


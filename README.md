# PDF/TXT to Speech Converter

A desktop application that converts PDF and text files to speech using Microsoft Edge's free text-to-speech service. Built with Python and Tkinter as part of the 100 Days of Code challenge.

## Features

- 📄 **File Support**: Read and extract text from PDF and TXT files
- 🎤 **Text-to-Speech**: Convert text to natural-sounding speech using edge-tts
- 🎚️ **Voice Selection**: Choose from multiple voices (US, UK accents)
- ▶️ **Audio Playback**: Play generated audio with pause, resume, and stop controls
- 💾 **Save Audio**: Export generated speech as MP3 files
- 📊 **Progress Tracking**: Visual progress bar during audio generation
- 🎨 **Status Indicators**: Color-coded status bar showing current operation state
- 🔄 **Play Saved Files**: Load and play previously saved audio files

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd AI-TextToSpeech-Project
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - **Windows**: `venv\Scripts\activate`
   - **Mac/Linux**: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. **Open a file**: Click "Open File" and select a PDF or TXT file
3. **Select voice**: Choose your preferred voice from the dropdown menu
4. **Generate speech**: Click "Read Aloud" to convert text to speech
5. **Control playback**: Use Pause, Resume, and Stop buttons during playback
6. **Save audio**: Click "Save Audio" to export the generated speech as an MP3 file
7. **Play saved files**: Click "Play Saved" to load and play previously saved audio files

## Project Structure

```
AI-TextToSpeech-Project/
├── main.py              # Application entry point
├── gui.py              # GUI components and user interface
├── pdf_processor.py    # PDF text extraction logic
├── tts_engine.py       # Text-to-speech conversion engine
├── utils.py            # Helper functions (file validation, path management)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Technologies Used

- **Python 3**: Core programming language
- **Tkinter**: GUI framework
- **edge-tts**: Microsoft Edge text-to-speech service (free, no API key required)
- **PDFPlumber**: PDF text extraction
- **pygame**: Audio playback control
- **shutil**: File operations

## Key Features Explained

### Voice Selection
The application supports multiple neural voices:
- Ryan (UK Male)
- Jenny (US Female)
- Guy (US Male)
- Libby (UK Female)

### Status Colors
- 🟢 **Green**: Ready, successful operations
- 🔵 **Blue**: Loading, generating, or playing
- 🟠 **Orange**: Paused
- 🔴 **Red**: Errors or stopped

## Requirements

See `requirements.txt` for the complete list of dependencies. Main packages:
- `edge-tts==7.2.7`
- `pdfplumber==0.11.9`
- `pygame==2.6.1`

## Notes

- Requires an internet connection for text-to-speech generation (edge-tts uses Microsoft's online service)
- Audio files are temporarily stored in the system temp directory
- The application uses threading to keep the GUI responsive during long operations

## License

This project is part of a learning exercise and is provided as-is.

## Acknowledgments

- Built as part of the 100 Days of Code challenge
- Uses Microsoft Edge TTS service (edge-tts) for free text-to-speech conversion

from tts_engine import text_to_speech, play_audio, start_playback, pause_playback, unpause_playback, stop_playback, is_playing
import shutil
import threading
from tkinter import (
    Tk, 
    Text, 
    Button, 
    END, 
    filedialog, 
    messagebox, 
    Scrollbar, 
    RIGHT, 
    Y, 
    LEFT, 
    BOTH,
    Label,
    StringVar,
    OptionMenu,
    )

from tkinter import ttk # Added for the progress bar
from pdf_processor import extract_text_from_pdf
from tts_engine import text_to_speech, play_audio
from utils import get_unique_audio_path, is_valid_pdf_file
from pathlib import Path

VOICE_LABEL_TO_ID = {
    "Ryan (Uk Male)": "en-GB-RyanNeural",
    "Jenny (US Female)": "en-US-JennyNeural",
    "Guy (US Male)": "en-US-GuyNeural",
    "Libby (UK Female)": "en-GB-LibbyNeural",
  }

# Cretae a list of voice labels for the dropdown menu
VOICE_LABELS = list(VOICE_LABEL_TO_ID.keys())

class PdfTtsApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("PDF/TXT File to Speech (100 Days of Code - AI Project)")
        self.root.geometry("900x600")

        # Text area + scrollbar
        scrollbar = Scrollbar(root)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.text_box = Text(root, wrap="word", yscrollcommand=scrollbar.set)
        self.text_box.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.text_box.yview)

        # Buttons
        self.open_btn = Button(root, text="Open File", command=self.open_pdf, width=15)
        self.open_btn.pack(pady=5)

        self.read_btn = Button(root, text="Read Aloud", command=self.read_aloud, width=15)
        self.read_btn.pack(pady=5)

        # Playback control buttons
        self.pause_btn = Button(root, text="Pause", command=self.pause_audio, width=15, state="disabled")
        self.pause_btn.pack(pady=5)

        self.stop_btn = Button(root, text="Stop", command=self.stop_audio, width=15, state="disabled")
        self.stop_btn.pack(pady=5)    

        self.save_btn = Button(root, text="Save", command=self.save_audio, width=15, state="disabled")
        self.save_btn.pack(pady=5)

        self.play_saved_btn = Button(root, text="Play", command=self.play_saved_audio, width=15)
        self.play_saved_btn.pack(pady=5)

        # Progress Bar (hidden by default)
        self.progress = ttk.Progressbar(root, mode='indeterminate', length=300)
        self.progress.pack(pady=5)
        self.progress.pack_forget() # Hide the progress bar initially
        
        # Voice Selection Dropdown        
        self.voice_var = StringVar(value=VOICE_LABELS[0]) # default voice
        self.voice_menu = OptionMenu(root, self.voice_var, *VOICE_LABELS) # * unpacks the list into individual arguments
        self.voice_menu.pack(pady=5)

        # Status label at the bottom
        self.status_label = Label(root, text="Ready", relief="sunken", anchor="w", padx=5, pady=2)
        self.status_label.pack(side="bottom", fill="x")

        self.audio_path = get_unique_audio_path()
        self.audio_exists = False
        self.is_playing_audio = False # Track if audio is currently playing
        self.is_paused = False # Track if audio is currently paused


    def update_status(self, message: str) -> None:
        """
        Updates the status label text with color coding.        
        Thread-safe: can be called from any thread.
        -> root.after is used to schedule the update to run in the main thread 
           because tkinter GUI components must be updated from the main thread.
        """
        # Determine color based on message content
        if "Ready" in message or "saved" in message.lower():
            color = "green"
        elif "Loading" in message or "Generating" in message or "Playing" in message:
            color = "blue"
        elif "Paused" in message:
            color = "orange"
        elif "Stopped" in message or "Error" in message:
            color = "red"
        else:
            color = "black"  # default color
        
        # Update both text and background color
        self.root.after(0, lambda: self.status_label.config(text=message, bg=color, fg="white"))


    def open_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title= "Select File",
            filetypes=[("PDF file", "*.pdf"), ("Text File", "*.txt")],
            defaultextension=".pdf",
        )
        if not path:
            return

        #Update status label
        self.update_status("Loading file ...")

        # Work out the file extension
        file_extension = Path(path).suffix.lower()

        try:
            if file_extension == ".pdf":
                # Validate that the file is a real PDF
                if not is_valid_pdf_file(path):
                    messagebox.showwarning("Invalid File", "Please select a valid PDF file.")
                    return

                text = extract_text_from_pdf(path)

            elif file_extension == ".txt":
                # Read plain text file
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()

            else:
                self.update_status("Ready")
                messagebox.showwarning("Invalid File", "Please select a valid PDF or Text file.")
                return

            if not text or not text.strip():
                self.update_status("Ready")
                messagebox.showwarining("Invalid File", "No extractable text found in this file." )
                return

            self.text_box.delete("1.0", END)
            self.text_box.insert(END, text)
            self.update_status("Ready")   # Successfully loaded file
            self.audio_exists = False
            self.save_btn.config(state="disabled")


        except Exception as e:
            self.update_status("Ready")
            messagebox.showerror("Error", str(e))


    def read_aloud(self) -> None:
        text = self.text_box.get("1.0", END).strip()
        if not text:
            messagebox.showwarning("No Text", "Please load a PDF or type some text first.")
            return

        # Update status
        self.update_status("Generating audio ...")

        # Show and start the progress bar
        self.progress.pack(pady=5)
        self.progress.start(10) # start animation (10ms interval)

        # Disable button to prevent multiple clicks
        self.read_btn.config(state="disabled")
        self.open_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.audio_exists = False

        thread = threading.Thread(target=self._generate_and_play, args=(text,), daemon=True)
        thread.start()

    def save_audio(self) -> None:
        """
        Checks if audio exists
        Opens a file dialog to choose where to save the file
        If user cancels, do nothing
        Copies the temp audio file to the user-specified location
        Shows a success message
        Handles errors and updates status
        Saves the generated audio file to a user-specified location
        """
        print("DEBUG save_audio: audio_exists =", self.audio_exists, "path =", self.audio_path)
        if not self.audio_exists or not self.audio_path:
            messagebox.showwarning("No Audio", "Please generate audio first by clicking 'Read Aloud'.")
            return

        # Ask where to save the file
        save_path = filedialog.asksaveasfilename(
            title="Save Audio File",
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("All Files", "*.*")]         
        )

        # If user cancelled, do nothing
        if not save_path:
            return

        try:                  
            # Copy the temp audio file the user specified location
            shutil.copy2(self.audio_path, save_path)

            # Show success message
            messagebox.showinfo("Success", f"Audio saved to:\n{save_path}.")
            self.update_status("Ready")

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save audio: {str(e)}")
            self.update_status("Ready")

        finally:
            # Re-enable buttons on the main thread
            self.root.after(0, lambda: self.play_saved_btn.config(state="normal"))     


    def play_saved_audio(self) -> None:
        """
        Opens a file dialog to select a saved MP3 file and plays it.
        """
        # Ask user to select an mp3 file
        file_path = filedialog.askopenfilename(
            title="Select Audio File to Play",
            filetypes=[("MP3 files", "*.mp3"), ("All Files", "*.*")],
            defaultextension=".mp3",
        )

        # If user cancelled, do nothing
        if not file_path:
            return

        # Validate that the file exists
        import os
        if not os.path.exists(file_path):
            messagebox.showwarning("File Not Found", "The selected file does not exist.")
            return
        
        try:
            # Disable buttons while playing
            self.read_btn.config(state="disabled")
            self.open_btn.config(state="disabled")
            self.save_btn.config(state="disabled")
            self.play_saved_btn.config(state="disabled")

            # Update status
            self.update_status("Playing saved audio ...")

            # Start playback (non-blocking)
            start_playback(file_path)
            self.is_playing_audio = True

            # Enable playback control buttons
            self.pause_btn.config(state="normal")
            self.stop_btn.config(state="normal")

            # Monitor playback in background
            threading.Thread(target=self._monitor_playback, daemon=True).start()        
     

            # Update status: done
            self.update_status("Ready")

        except Exception as e:
            # Show error message
            messagebox.showerror("Playback Error", f"Failed to play audio: {str(e)}")
            self.update_status("Ready")

        finally:
            # Re-enable buttons on the main thread
            self.read_btn.config(state="normal")
            self.open_btn.config(state="normal")
            self.save_btn.config(state="normal")
            self.play_saved_btn.config(state="normal")

    def pause_audio(self) -> None:
        """ Pause the current audio playback."""
        if self.is_playing_audio:
            pause_playback()
            self.is_paused = True
            self.update_status("Audio Paused")
            self.pause_btn.config(text="Resume", command=self.resume_audio)

    def resume_audio(self) -> None:
        """ Resume the current audio playback."""
        if self.is_playing_audio:
            unpause_playback()
            self.is_paused = False
            self.update_status("Playing Audio ...")
            self.pause_btn.config(text="Pause", command=self.pause_audio)
            
    def stop_audio(self) -> None:
        """ Stop the current audio playback."""
        if self.is_playing_audio:
            stop_playback()
            self.is_playing_audio = False
            self.is_paused = False
            self.update_status("Audio Stopped")
            # Disable control buttons
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")
            # Reset pause button text
            self.pause_btn.config(text="Pause", command=self.pause_audio)       


    def _monitor_playback(self) -> None:
        """ Monitor the current audio playback and update the GUI accordingly."""
        import time
        while self.is_playing_audio: # while audio is playing
            if not self.is_paused: # if audio is not paused
                if not is_playing:
                    # audio playback has finished
                    break
            time.sleep(0.1)

        # playback finished
        self.is_playing_audio = False
        self.root.after(0, lambda: self.pause_btn.config(state="disabled"))
        self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
        self.root.after(0),lambda: self.pause_btn.config(text="Pause", command=self.pause_audio)        
        self.root.after(0, lambda: self.update_status("Ready"))



    def _generate_and_play(self, text: str) -> None:
        try:
            # Temporary mp3 file (unique name)
            out_path = get_unique_audio_path()

            # Update status: generating
            self.update_status("Generating audio ...")
            label = self.voice_var.get()
            voice_id = VOICE_LABEL_TO_ID.get(label, "en-GB-RyanNeural" )            
            text_to_speech(text, out_path, voice=voice_id)

            # Update status: playing
            self.update_status("Playing Audio ...")
            self.audio_path = out_path
            self.audio_exists = True

            # Stop and hide progress bar
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.pack_forget())

            print("DEBUG -generate_and_play: audio_exists=", self.audio_exists, " path =", self.audio_path)
            play_audio(out_path)

            # Update status: done
            self.update_status("Ready")

            # Enable the save button (must be done on the main thread)
            # root.after is used to schedule the update to run in the main thread 
            # because tkinter GUI components must be updated from the main thread.
            self.root.after(0, lambda: self.save_btn.config(state="normal"))            

        except Exception as e:
            # Update status: error
            self.update_status("Ready")

            # Stop and hide progress bar on error
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.pack_forget()) 

            # We must show the messagebox in the main thread
            self.root.after(
                0,
                lambda: messagebox.showerror("TTS Error", str(e)),
            )
        finally:
            # Re-enable buttons on the main thread
            self.root.after(0, lambda: self.read_btn.config(state="normal"))
            self.root.after(0, lambda: self.open_btn.config(state="normal"))
          

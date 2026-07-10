"""
Voice Module for ORDIS-A.I.
Handles speech-to-text and text-to-speech functionality.
Note: This is a simplified implementation. Full voice capabilities would require
additional setup and dependencies.
"""

import os
import sys
import logging
import threading
import queue
import time
from typing import Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)

class VoiceEngine:
    def __init__(self, config: dict):
        """
        Initialize voice engine with configuration.

        Args:
            config: Configuration dictionary containing voice settings
        """
        self.config = config
        self.enabled = config.get('assistant', {}).get('voice_enabled', False)
        self.language = config.get('assistant', {}).get('voice_language', 'en-US')
        self.activation_phrase = config.get('assistant', {}).get('voice_activation_phrase', 'Hey ORDIS')

        # Voice components (will be initialized if enabled)
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.is_listening = False
        self.listen_thread = None
        self.callback_queue = queue.Queue()
        self.stop_event = threading.Event()

        # Initialize voice components if enabled
        if self.enabled:
            self._initialize_voice()
        else:
            logger.info("Voice engine is disabled in configuration")

    def _initialize_voice(self):
        """Initialize voice recognition and TTS engines."""
        try:
            # Try to import speech recognition
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

            # Try to import text-to-speech
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            # Set properties for clearer speech
            self.tts_engine.setProperty('rate', 180)    # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level

            logger.info("Voice engines initialized successfully")

            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

        except ImportError as e:
            logger.warning(f"Voice dependencies not available: {e}")
            logger.info("Voice functionality will be limited. Install dependencies:")
            logger.info("  pip install SpeechRecognition pyttsx3 pyaudio")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize voice engines: {e}")
            self.enabled = False

    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Convert text to speech.

        Args:
            text: Text to speak
            blocking: Whether to block until speech is complete

        Returns:
            bool: True if speech was initiated, False otherwise
        """
        if not self.enabled or not self.tts_engine:
            logger.warning("TTS engine not available or voice disabled")
            return False

        try:
            logger.info(f"Speaking: {text[:100]}{'...' if len(text) > 100 else ''}")
            self.tts_engine.say(text)
            if blocking:
                self.tts_engine.runAndWait()
            else:
                self.tts_engine.startLoop(False)
            return True
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            return False

    def listen_once(self, timeout: float = 5.0, phrase_timeout: float = 1.0) -> Optional[str]:
        """
        Listen for a single phrase and convert to text.

        Args:
            timeout: Maximum time to wait for speech to start
            phrase_timeout: Maximum time to wait between phrases

        Returns:
            Recognized text or None if no speech detected/error
        """
        if not self.enabled or not self.recognizer or not self.microphone:
            logger.warning("Speech recognition not available or voice disabled")
            return None

        try:
            logger.info("Listening for speech...")
            with self.microphone as source:
                # Listen for audio input
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_timeout)

            logger.info("Processing speech...")
            # Convert speech to text
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"Recognized: {text}")
            return text

        except sr.WaitTimeoutError:
            logger.info("Listening timeout - no speech detected")
            return None
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from speech recognition service: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during speech recognition: {e}")
            return None

    def start_continuous_listening(self, callback: Callable[[str], None]) -> bool:
        """
        Start continuous listening in background thread.

        Args:
            callback: Function to call with recognized text

        Returns:
            bool: True if listening started, False otherwise
        """
        if not self.enabled or not self.recognizer or not self.microphone:
            logger.warning("Cannot start continuous listening - voice not available")
            return False

        if self.is_listening:
            logger.warning("Already listening")
            return False

        try:
            self.stop_event.clear()
            self.is_listening = True
            self.listen_thread = threading.Thread(
                target=self._listen_loop,
                args=(callback,),
                daemon=True
            )
            self.listen_thread.start()
            logger.info("Started continuous listening")
            return True
        except Exception as e:
            logger.error(f"Failed to start continuous listening: {e}")
            self.is_listening = False
            return False

    def stop_continuous_listening(self) -> bool:
        """
        Stop continuous listening.

        Returns:
            bool: True if listening was stopped, False otherwise
        """
        if not self.is_listening:
            logger.warning("Not currently listening")
            return False

        try:
            self.stop_event.set()
            self.is_listening = False
            if self.listen_thread:
                self.listen_thread.join(timeout=2.0)
            logger.info("Stopped continuous listening")
            return True
        except Exception as e:
            logger.error(f"Error stopping continuous listening: {e}")
            return False

    def _listen_loop(self, callback: Callable[[str], None]):
        """
        Internal loop for continuous listening.

        Args:
            callback: Function to call with recognized text
        """
        logger.info("Voice listening loop started")
        while not self.stop_event.is_set():
            try:
                # Listen for speech with short timeout to check stop_event frequently
                text = self.listen_once(timeout=1.0, phrase_timeout=2.0)
                if text and not self.stop_event.is_set():
                    # Check if activation phrase is detected
                    if self.activation_phrase.lower() in text.lower():
                        # Remove activation phrase and process the rest
                        command_text = text.lower().replace(self.activation_phrase.lower(), '').strip()
                        if command_text:
                            logger.info(f"Activation phrase detected. Processing: {command_text}")
                            callback(command_text)
                        else:
                            # Just activation phrase, maybe respond with acknowledgment
                            self.speak("Yes?", blocking=False)
                    else:
                        # Speech detected but no activation phrase - ignore or process based on settings
                        pass
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            except Exception as e:
                logger.error(f"Error in voice listening loop: {e}")
                time.sleep(1.0)  # Wait before retrying

        logger.info("Voice listening loop stopped")

    def is_available(self) -> bool:
        """
        Check if voice functionality is available.

        Returns:
            bool: True if voice is available and enabled, False otherwise
        """
        return self.enabled and self.recognizer is not None and self.tts_engine is not None

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available TTS voices.

        Returns:
            List of voice dictionaries
        """
        if not self.tts_engine:
            return []

        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            for voice in voices:
                voice_list.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown'),
                    'age': getattr(voice, 'age', 'unknown')
                })
            return voice_list
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []

    def set_voice(self, voice_id: str) -> bool:
        """
        Set the TTS voice to use.

        Args:
            voice_id: ID of the voice to use

        Returns:
            bool: True if voice was set successfully, False otherwise
        """
        if not self.tts_engine:
            return False

        try:
            self.tts_engine.setProperty('voice', voice_id)
            logger.info(f"Voice set to: {voice_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False

    def set_language(self, language: str) -> bool:
        """
        Set the language for speech recognition.

        Args:
            language: Language code (e.g., 'en-US', 'es-ES')

        Returns:
            bool: True if language was set successfully, False otherwise
        """
        self.language = language
        logger.info(f"Language set to: {language}")
        return True

    def cleanup(self):
        """Clean up voice resources."""
        logger.info("Cleaning up voice engine...")
        self.stop_continuous_listening()
        # Note: pyttsx3 doesn't require explicit cleanup in most cases

# Example usage and testing
if __name__ == "__main__":
    # Simple test configuration
    config = {
        "assistant": {
            "voice_enabled": False,  # Set to True to test voice (requires dependencies)
            "voice_language": "en-US",
            "voice_activation_phrase": "Hey ORDIS"
        }
    }

    voice = VoiceEngine(config)

    if voice.is_available():
        print("Voice engine is available")
        # Test TTS
        voice.speak("Hello, this is ORDIS-A.I. voice system testing.")
        print("Spoke test message")
    else:
        print("Voice engine is not available (disabled or missing dependencies)")
        print("To enable voice:")
        print("  1. Install dependencies: pip install SpeechRecognition pyttsx3 pyaudio")
        print("  2. Set 'voice_enabled': true in config")
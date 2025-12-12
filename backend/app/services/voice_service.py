import logging
import os
import uuid
from typing import Optional
import time

logger = logging.getLogger(__name__)


class VoiceService:
    """Service for voice/audio operations (TTS and STT)"""
    
    # Audio storage directory
    AUDIO_DIR = "audio_outputs"
    
    @staticmethod
    def ensure_audio_dir():
        """Create audio directory if it doesn't exist"""
        os.makedirs(VoiceService.AUDIO_DIR, exist_ok=True)
    
    @staticmethod
    async def generate_speech(
        text: str,
        language: str = "en",
    ) -> str:
        """
        Generate speech from text using gTTS (Google Text-to-Speech)
        
        Args:
            text: Text to convert to speech
            language: Language code (en, yo, ha, ig)
            
        Returns:
            Path to generated audio file
        """
        try:
            from gtts import gTTS
            
            logger.info(f"Generating speech for {len(text)} characters in {language}")
            
            # Ensure audio directory exists
            VoiceService.ensure_audio_dir()
            
            # Map custom language codes to gTTS codes
            language_map = {
                "en": "en",
                "yo": "yo",  # Yoruba
                "ha": "ha",  # Hausa
                "ig": "ig",  # Igbo
            }
            
            gtts_lang = language_map.get(language, "en")
            
            # Generate speech
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Save to temporary file
            audio_filename = f"{uuid.uuid4()}.mp3"
            audio_path = os.path.join(VoiceService.AUDIO_DIR, audio_filename)
            
            tts.save(audio_path)
            
            logger.info(f"Speech generated: {audio_path}")
            
            # Return relative path
            return f"/api/audio/{audio_filename}"
            
        except ImportError:
            logger.error("gTTS not installed. Install with: pip install gtts")
            raise Exception("Text-to-speech service not available. Install gTTS: pip install gtts")
        except Exception as e:
            logger.error(f"Speech generation failed: {str(e)}")
            raise
    
    @staticmethod
    async def transcribe_audio(
        audio_data: bytes,
        language: str = "en",
    ) -> str:
        """
        Transcribe audio to text using Google Cloud Speech-to-Text API
        
        Args:
            audio_data: Audio file bytes
            language: Language code (en, yo, ha, ig)
            
        Returns:
            Transcribed text
        """
        try:
            # TODO: Implement Google Cloud Speech-to-Text
            # For now, return placeholder
            
            logger.info(f"Voice input received ({len(audio_data)} bytes) in {language}")
            logger.warning("Google Cloud Speech-to-Text not yet implemented")
            
            return "Voice input received. Speech-to-text will be implemented with Google Cloud Speech API soon."
            
            # Uncomment below when Google Cloud Speech-to-Text is set up:
            """
            from google.cloud import speech
            
            logger.info(f"Transcribing audio ({len(audio_data)} bytes) using Google Cloud")
            
            # Language code mapping
            language_code_map = {
                "en": "en-US",
                "yo": "yo-NG",  # Yoruba - Nigeria
                "ha": "ha-NG",  # Hausa - Nigeria
                "ig": "ig-NG",  # Igbo - Nigeria
            }
            
            language_code = language_code_map.get(language, "en-US")
            
            # Initialize client
            client = speech.SpeechClient()
            
            # Configure audio
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                language_code=language_code,
                model="default",
            )
            
            # Perform transcription
            response = client.recognize(config=config, audio=audio)
            
            # Extract transcribed text
            transcribed_text = ""
            for result in response.results:
                transcribed_text += result.alternatives[0].transcript + " "
            
            transcribed_text = transcribed_text.strip()
            
            if not transcribed_text:
                logger.warning("No speech detected in audio")
                raise Exception("No speech detected in the audio")
            
            logger.info(f"Transcription complete: {transcribed_text[:50]}")
            
            return transcribed_text
            """
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}")
            raise
    
    @staticmethod
    def cleanup_old_audio(max_age_hours: int = 24):
        """
        Clean up old audio files
        
        Args:
            max_age_hours: Delete files older than this many hours
        """
        try:
            logger.info(f"Cleaning up audio files older than {max_age_hours} hours")
            
            if not os.path.exists(VoiceService.AUDIO_DIR):
                return
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(VoiceService.AUDIO_DIR):
                file_path = os.path.join(VoiceService.AUDIO_DIR, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        logger.info(f"Deleted old audio file: {filename}")
            
        except Exception as e:
            logger.error(f"Audio cleanup failed: {str(e)}")
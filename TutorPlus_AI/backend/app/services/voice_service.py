import logging
import os
import tempfile
import uuid
from typing import Optional
import io

try:
    from pydub import AudioSegment
    from pydub.utils import mediainfo
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

logger = logging.getLogger(__name__)


class VoiceService:
    """Service for voice/audio operations (TTS and STT)"""
    
    # Audio storage directory
    AUDIO_DIR = "audio_outputs"
    
    def __init__(self):
        # Create audio directory if it doesn't exist
        os.makedirs(self.AUDIO_DIR, exist_ok=True)
    
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
            raise Exception("Text-to-speech service not available")
        except Exception as e:
            logger.error(f"Speech generation failed: {str(e)}")
            raise
    
    @staticmethod
    async def transcribe_audio(
        audio_data: bytes,
        language: str = "en",
    ) -> str:
        """
        Transcribe audio to text using Whisper (OpenAI)
        
        Args:
            audio_data: Audio file bytes
            language: Language code (en, yo, ha, ig)
            
        Returns:
            Transcribed text
        """
        try:
            import whisper
            
            logger.info(f"Transcribing audio ({len(audio_data)} bytes) in {language}")
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            # Load Whisper model
            model = whisper.load_model("base")
            
            # Transcribe
            result = model.transcribe(tmp_path, language=language)
            
            transcribed_text = result["text"].strip()
            
            # Cleanup
            os.unlink(tmp_path)
            
            logger.info(f"Transcription complete: {transcribed_text[:50]}")
            
            return transcribed_text
            
        except ImportError:
            logger.error("Whisper not installed. Install with: pip install openai-whisper")
            raise Exception("Speech-to-text service not available")
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
            import time
            
            logger.info(f"Cleaning up audio files older than {max_age_hours} hours")
            
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
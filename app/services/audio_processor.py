"""
Audio processing service for speech-to-text conversion
"""
import os
import tempfile
import asyncio
from typing import Optional, Tuple
import openai
from fastapi import HTTPException, UploadFile

from app.config import settings
from app.utils.validators import validate_audio_file, sanitize_filename

# Simple fallback for audio processing without pydub/librosa
def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)

def estimate_audio_duration(file_path: str) -> float:
    """Estimate audio duration based on file size (very rough approximation)"""
    size_mb = get_file_size_mb(file_path)
    # Rough estimate: 1MB ≈ 1 minute for typical audio quality
    return size_mb * 60.0


class AudioProcessor:
    """Service for processing audio files and converting speech to text"""

    def __init__(self):
        """Initialize the audio processor with OpenAI client"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required for audio processing")

        openai.api_key = settings.openai_api_key
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    async def process_audio_file(self, file: UploadFile) -> Tuple[str, float, float]:
        """
        Process uploaded audio file and convert to text

        Returns:
            Tuple of (transcribed_text, confidence_score, duration_seconds)
        """
        # Validate the uploaded file
        validate_audio_file(file)

        # Save uploaded file temporarily
        temp_file_path = await self._save_temp_file(file)

        try:
            # Get audio duration
            duration = await self._get_audio_duration(temp_file_path)

            # Convert to appropriate format if needed
            processed_file_path = await self._preprocess_audio(temp_file_path)

            # Transcribe using OpenAI Whisper
            transcription_result = await self._transcribe_audio(processed_file_path)

            # Extract text and confidence
            text = transcription_result.get('text', '').strip()
            confidence = self._calculate_confidence(transcription_result)

            return text, confidence, duration

        finally:
            # Clean up temporary files
            self._cleanup_temp_files([temp_file_path])

    async def _save_temp_file(self, file: UploadFile) -> str:
        """Save uploaded file to temporary location"""
        sanitized_filename = sanitize_filename(file.filename or "audio_file")

        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, sanitized_filename)

        try:
            # Read and save file content
            content = await file.read()
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(content)

            return temp_file_path

        except Exception as e:
            self._cleanup_temp_files([temp_file_path])
            raise HTTPException(
                status_code=500,
                detail=f"Error saving uploaded file: {str(e)}"
            )

    async def _get_audio_duration(self, file_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            # Use simple file size estimation
            return estimate_audio_duration(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to process audio file: {str(e)}"
            )

    async def _preprocess_audio(self, file_path: str) -> str:
        """
        Preprocess audio file for optimal transcription
        For now, just return the original file (preprocessing disabled)
        """
        try:
            # For now, just return the original file
            # In production, you might want to install ffmpeg and use pydub
            return file_path

        except Exception as e:
            # If preprocessing fails, return original file
            print(f"Audio preprocessing failed: {e}")
            return file_path

    async def _transcribe_audio(self, file_path: str) -> dict:
        """Transcribe audio using OpenAI Whisper API"""
        try:
            with open(file_path, 'rb') as audio_file:
                # Use OpenAI Whisper API for transcription
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    language="en"  # Can be made configurable
                )

                return {
                    'text': response.text,
                    'segments': getattr(response, 'segments', []),
                    'language': getattr(response, 'language', 'en')
                }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error transcribing audio: {str(e)}"
            )

    def _calculate_confidence(self, transcription_result: dict) -> float:
        """
        Calculate confidence score based on transcription result
        """
        # If segments are available, calculate average confidence
        segments = transcription_result.get('segments', [])
        if segments:
            confidences = []
            for segment in segments:
                if 'avg_logprob' in segment:
                    # Convert log probability to confidence (0-1)
                    confidence = min(1.0, max(0.0, (segment['avg_logprob'] + 1.0)))
                    confidences.append(confidence)

            if confidences:
                return sum(confidences) / len(confidences)

        # Fallback: estimate confidence based on text quality
        text = transcription_result.get('text', '')
        if not text:
            return 0.0

        # Simple heuristic: longer, more coherent text = higher confidence
        word_count = len(text.split())
        if word_count < 5:
            return 0.6
        elif word_count < 20:
            return 0.75
        else:
            return 0.85

    def _cleanup_temp_files(self, file_paths: list):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)

                # Also remove the directory if it's empty
                dir_path = os.path.dirname(file_path)
                if os.path.exists(dir_path) and not os.listdir(dir_path):
                    os.rmdir(dir_path)

            except Exception as e:
                print(f"Warning: Could not clean up temporary file {file_path}: {e}")

    async def save_audio_file(self, file: UploadFile, user_id: int, response_id: int) -> str:
        """
        Save audio file permanently for a user response

        Returns:
            File path where the audio is saved
        """
        # Create user-specific directory
        user_dir = os.path.join(settings.upload_dir, f"user_{user_id}")
        os.makedirs(user_dir, exist_ok=True)

        # Generate unique filename
        sanitized_filename = sanitize_filename(file.filename or "audio_response")
        name, ext = os.path.splitext(sanitized_filename)
        final_filename = f"response_{response_id}_{name}{ext}"
        final_path = os.path.join(user_dir, final_filename)

        # Save file
        content = await file.read()
        with open(final_path, 'wb') as f:
            f.write(content)

        return final_path

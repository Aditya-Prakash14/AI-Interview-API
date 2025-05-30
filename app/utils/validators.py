"""
Validation utilities for file uploads and data validation
"""
import os
from typing import List, Optional
from fastapi import HTTPException, UploadFile
from app.config import settings


def validate_audio_file(file: UploadFile) -> bool:
    """
    Validate uploaded audio file
    """
    # Check file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.audio_formats_list:
        raise HTTPException(
            status_code=400,
            detail=f"File format not supported. Allowed formats: {', '.join(settings.audio_formats_list)}"
        )

    # Check file size
    if hasattr(file, 'size') and file.size:
        max_size = settings.max_file_size_mb * 1024 * 1024  # Convert MB to bytes
        if file.size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )

    return True


def validate_file_content(file_path: str) -> bool:
    """
    Validate file content (simplified version without python-magic)
    """
    try:
        # Simple validation based on file extension for now
        # In production, you might want to install libmagic and use python-magic
        file_extension = file_path.split('.')[-1].lower()
        if file_extension not in settings.audio_formats_list:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension: {file_extension}"
            )

        return True
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error validating file content: {str(e)}"
        )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other security issues
    """
    # Remove directory separators and other dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    sanitized = filename

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')

    # Limit filename length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext

    return sanitized


def validate_text_input(text: str, min_length: int = 10, max_length: int = 5000) -> bool:
    """
    Validate text input for interview responses
    """
    if not text or not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text response cannot be empty"
        )

    text_length = len(text.strip())

    if text_length < min_length:
        raise HTTPException(
            status_code=400,
            detail=f"Text response too short. Minimum length: {min_length} characters"
        )

    if text_length > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Text response too long. Maximum length: {max_length} characters"
        )

    return True


def validate_score_range(score: int, min_score: int = 0, max_score: int = 100) -> bool:
    """
    Validate score is within acceptable range
    """
    if not isinstance(score, int):
        raise ValueError("Score must be an integer")

    if score < min_score or score > max_score:
        raise ValueError(f"Score must be between {min_score} and {max_score}")

    return True


def clean_text_input(text: str) -> str:
    """
    Clean and normalize text input
    """
    if not text:
        return ""

    # Remove excessive whitespace
    cleaned = ' '.join(text.split())

    # Remove or replace special characters that might cause issues
    # Keep basic punctuation but remove control characters
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\t')

    return cleaned.strip()

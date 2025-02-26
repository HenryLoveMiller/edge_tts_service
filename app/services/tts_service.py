# app/services/tts_service.py
import edge_tts
import os
import logging
from flask import current_app
from .github_service import GitHubService

class TTSService:
    SUPPORTED_VOICES = {
        "zh-CN-XiaoxiaoNeural": "Chinese Female",
        "zh-CN-YunxiNeural": "Chinese Male",
        "en-US-AriaNeural": "English Female",
        "en-US-GuyNeural": "English Male",
        "ja-JP-NanamiNeural": "Japanese Female"
    }

    @classmethod
    def get_supported_voices(cls):
        return cls.SUPPORTED_VOICES

    def __init__(self):
        self.temp_files = []

    def _get_github_file_info(self, filename):
        """Helper method to get GitHub file info"""
        return GitHubService._get_github_file_info(filename)

    async def generate_speech(self, text, filename, voice=None, rate=None, volume=None):
        """Generate speech file"""
        voice = voice or 'en-US-AriaNeural'
        rate = rate or '+0%'
        volume = volume or '+0%'

        if voice not in self.SUPPORTED_VOICES:
            raise ValueError(f"Unsupported voice. Please choose from: {list(self.SUPPORTED_VOICES.keys())}")

        storage_method = current_app.config['STORAGE_METHOD']

        if storage_method == 'github':
            # Check if the file already exists on GitHub
            file_url = self.check_github_file_exists(filename)
            if file_url:
                logging.info(f"File {filename} already exists on GitHub. Returning existing file URL.")
                return file_url

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume
        )

        local_storage_dir = current_app.config['LOCAL_STORAGE_DIR']
        if not os.path.exists(local_storage_dir):
            os.makedirs(local_storage_dir)

        local_file_path = os.path.join(local_storage_dir, filename)

        await communicate.save(local_file_path)

        if storage_method == 'github':
            file_url = self.upload_to_github(local_file_path, filename)
            return file_url

        return local_file_path

    def check_github_file_exists(self, filename):
        """Check if the file already exists on GitHub and return the URL if it does"""
        return GitHubService.check_github_file_exists(filename)

    def upload_to_github(self, file_path, filename):
        """Upload the file to GitHub and return the raw file URL"""
        return GitHubService.upload_to_github(file_path, filename)

    def cleanup(self):
        """Clean up temporary files"""
        for file_path in self.temp_files:
            try:
                os.unlink(file_path)
            except Exception as e:
                logging.error(f"Failed to delete temporary file {file_path}: {e}")
        self.temp_files = []
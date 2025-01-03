# app/services/tts_service.py
import edge_tts
import tempfile
import os
import base64
import requests
import logging
from flask import current_app

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
        repo = current_app.config['GITHUB_REPO']
        branch = current_app.config['GITHUB_BRANCH']
        folder = current_app.config['GITHUB_FOLDER']
        if folder:
            url = f"https://api.github.com/repos/{repo}/contents/{folder}/{filename}"
            raw_file_url = f"https://github.com/{repo}/raw/refs/heads/{branch}/{folder}/{filename}"
        else:
            url = f"https://api.github.com/repos/{repo}/contents/{filename}"
            raw_file_url = f"https://github.com/{repo}/raw/refs/heads/{branch}/{filename}"
        
        headers = {
            'Authorization': f'token {current_app.config['GITHUB_TOKEN']}',
            'Content-Type': 'application/json'
        }
        
        return url, raw_file_url, headers

    async def generate_speech(self, text, filename, voice=None, rate=None, volume=None):
        """Generate speech file"""
        voice = voice or 'en-US-AriaNeural'
        rate = rate or '+0%'
        volume = volume or '+0%'

        if voice not in self.SUPPORTED_VOICES:
            raise ValueError(f"Unsupported voice. Please choose from: {list(self.SUPPORTED_VOICES.keys())}")

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

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        await communicate.save(temp_file_path)
        
        # Upload the file to GitHub
        try:
            file_url = self.upload_to_github(temp_file_path, filename)
        except Exception as e:
            logging.error(f"Failed to upload file to GitHub: {e}")
            raise
        finally:
            os.unlink(temp_file_path)
        
        return file_url

    def check_github_file_exists(self, filename):
        """Check if the file already exists on GitHub and return the URL if it does"""
        url, raw_file_url, headers = self._get_github_file_info(filename)
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return raw_file_url
        elif response.status_code != 404:
            logging.error(f"GitHub API error: {response.status_code} {response.text}")
            response.raise_for_status()
        
        return None

    def upload_to_github(self, file_path, filename):
        """Upload the file to GitHub and return the raw file URL"""
        url, raw_file_url, headers = self._get_github_file_info(filename)
        
        # Check if the file already exists
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info(f"File {filename} already exists. Returning existing file URL.")
            return raw_file_url
        elif response.status_code != 404:
            logging.error(f"GitHub API error: {response.status_code} {response.text}")
            response.raise_for_status()
        
        # If the file does not exist, upload it
        with open(file_path, 'rb') as file:
            content = base64.b64encode(file.read()).decode('utf-8')
        
        data = {
            'message': f'Add {filename}',
            'content': content,
            'branch': current_app.config['GITHUB_BRANCH']
        }
        
        response = requests.put(url, json=data, headers=headers)
        
        if response.status_code not in [200, 201]:
            logging.error(f"GitHub API error: {response.status_code} {response.text}")
            response.raise_for_status()
        
        return raw_file_url

    def cleanup(self):
        """Clean up temporary files"""
        for file_path in self.temp_files:
            try:
                os.unlink(file_path)
            except Exception as e:
                logging.error(f"Failed to delete temporary file {file_path}: {e}")
        self.temp_files = []
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

    async def generate_speech(self, text, filename, voice=None, rate=None, volume=None):
        """生成语音文件"""
        voice = voice or 'en-US-AriaNeural'
        rate = rate or '+0%'
        volume = volume or '+0%'

        if voice not in self.SUPPORTED_VOICES:
            raise ValueError(f"Unsupported voice. Please choose from: {list(self.SUPPORTED_VOICES.keys())}")

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

    def upload_to_github(self, file_path, filename):
        """Upload the file to GitHub and return the raw file URL"""
        with open(file_path, 'rb') as file:
            content = base64.b64encode(file.read()).decode('utf-8')
        
        repo = current_app.config['GITHUB_REPO']
        branch = current_app.config['GITHUB_BRANCH']
        token = current_app.config['GITHUB_TOKEN']
        folder = current_app.config['GITHUB_FOLDER']
        if folder:
            url = f"https://api.github.com/repos/{repo}/contents/{folder}/{filename}"
            raw_file_url = f"https://github.com/{repo}/raw/refs/heads/{branch}/{folder}/{filename}"
        else:
            url = f"https://api.github.com/repos/{repo}/contents/{filename}"
            raw_file_url = f"https://github.com/{repo}/raw/refs/heads/{branch}/{filename}"
        
        headers = {
            'Authorization': f'token {token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'message': f'Add {filename}',
            'content': content,
            'branch': branch
        }
        
        response = requests.put(url, json=data, headers=headers)
        
        if response.status_code != 201:
            logging.error(f"GitHub API error: {response.status_code} {response.text}")
            response.raise_for_status()
        
        return raw_file_url

    def cleanup(self):
        """清理临时文件"""
        for file_path in self.temp_files:
            try:
                os.unlink(file_path)
            except Exception as e:
                logging.error(f"Failed to delete temporary file {file_path}: {e}")
        self.temp_files = []
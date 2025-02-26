import base64
import requests
import logging
from flask import current_app

class GitHubService:
    @staticmethod
    def _get_github_file_info(filename):
        """Helper method to get GitHub file info"""
        repo = current_app.config["GITHUB_REPO"]
        branch = current_app.config["GITHUB_BRANCH"]
        folder = current_app.config["GITHUB_FOLDER"]
        if folder:
            url = f"https://api.github.com/repos/{repo}/contents/{folder}/{filename}"
            raw_file_url = f"https://github.com/{repo}/raw/refs/heads/{branch}/{folder}/{filename}"
        else:
            url = f"https://api.github.com/repos/{repo}/contents/{filename}"
            raw_file_url = f"https://github.com/{repo}/raw/refs/heads/{branch}/{filename}"
        
        headers = {
            "Authorization": f"token {current_app.config['GITHUB_TOKEN']}",
            "Content-Type": "application/json"
        }
        
        return url, raw_file_url, headers

    @staticmethod
    def check_github_file_exists(filename):
        """Check if the file already exists on GitHub and return the URL if it does"""
        url, raw_file_url, headers = GitHubService._get_github_file_info(filename)
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return raw_file_url
        elif response.status_code != 404:
            logging.error(f"GitHub API error: {response.status_code} {response.text}")
            response.raise_for_status()
        
        return None

    @staticmethod
    def upload_to_github(file_path, filename):
        """Upload the file to GitHub and return the raw file URL"""
        url, raw_file_url, headers = GitHubService._get_github_file_info(filename)
        
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

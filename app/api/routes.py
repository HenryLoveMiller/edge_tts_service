from flask import request, redirect, send_file, current_app
from . import api
from ..services.tts_service import TTSService
from ..services.github_service import GitHubService
from ..utils.decorators import async_route
from ..utils.text_utils import generate_filename
import logging

@api.route('/voices', methods=['GET'])
def get_voices():
    """Get supported voices list"""
    return {
        "status": "success",
        "voices": TTSService.get_supported_voices()
    }

@api.route('/tts', methods=['GET', 'POST'])
@async_route
async def text_to_speech():
    """Text to speech interface"""
    try:
        if request.method == 'GET':
            # Get text from GET request query parameters
            text = request.args.get('text')
            voice = request.args.get('voice')
            rate = request.args.get('rate')
            volume = request.args.get('volume')
            dl = request.args.get('dl')
        elif request.method == 'POST':
            # Get text from POST request JSON data
            data = request.get_json()
            if not data or 'text' not in data:
                return {"status": "error", "message": "Missing required parameter: text"}, 400
            text = data['text']
            voice = data.get('voice')
            rate = data.get('rate')
            volume = data.get('volume')
            dl = data.get('dl')
        else:
            return {"status": "error", "message": "Method not allowed"}, 405

        # Generate filename based on input text
        filename = f"{generate_filename(text)}.mp3"
        
        tts_service = TTSService()
        local_file_path = await tts_service.generate_speech(
            text=text,
            filename=filename,
            voice=voice,
            rate=rate,
            volume=volume
        )

        if dl == '1':
            return send_file(local_file_path, as_attachment=True)
        elif dl == '2':
            return redirect(f"{request.host_url}player?filename={filename}")

        storage_method = current_app.config['STORAGE_METHOD']
        if storage_method == 'github':
            play_audio_url = f"{request.host_url}player?filename={filename}"
        else:
            play_audio_url = f"{request.host_url}static/audio/{filename}"

        return {
            "status": "success",
            "file_path": local_file_path,
            "play_audio_url": play_audio_url
        }
        
    except ValueError as e:
        logging.error(f"ValueError in text_to_speech: {e}")
        return {"status": "error", "message": str(e)}, 400
    except Exception as e:
        logging.error(f"Exception in text_to_speech: {e}")
        return {"status": "error", "message": str(e)}, 500

@api.route('/player', methods=['GET'])
def play_audio():
    """Play audio file page"""
    filename = request.args.get('filename')
    if not filename:
        return {"status": "error", "message": "Missing required parameter: filename"}, 400

    raw_file_url = GitHubService.check_github_file_exists(filename)
    if not raw_file_url:
        return {"status": "error", "message": "File not found on GitHub"}, 404

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Play Audio</title>
    </head>
    <body>
        <audio controls autoplay>
            <source src="{raw_file_url}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
    </body>
    </html>
    """

from flask import request, send_file
from . import api
from ..services.tts_service import TTSService
from ..utils.decorators import async_route
from ..utils.text_utils import generate_filename
import logging

@api.route('/voices', methods=['GET'])
def get_voices():
    """获取支持的声音列表"""
    return {
        "status": "success",
        "voices": TTSService.get_supported_voices()
    }

@api.route('/tts', methods=['POST'])
@async_route
async def text_to_speech():
    """文字转语音接口"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return {"status": "error", "message": "Missing required parameter: text"}, 400
        
        text = data['text']
        # 生成基于输入文本的文件名
        filename = f"{generate_filename(text)}.mp3"
            
        tts_service = TTSService()
        file_url = await tts_service.generate_speech(
            text=text,
            filename=filename,
            voice=data.get('voice'),
            rate=data.get('rate'),
            volume=data.get('volume')
        )
        
        return {"status": "success", "file_url": file_url}
        
    except ValueError as e:
        logging.error(f"ValueError in text_to_speech: {e}")
        return {"status": "error", "message": str(e)}, 400
    except Exception as e:
        logging.error(f"Exception in text_to_speech: {e}")
        return {"status": "error", "message": str(e)}, 500

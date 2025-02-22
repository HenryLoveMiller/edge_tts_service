import re
from pypinyin import lazy_pinyin

def sanitize_text(text):
    """
    清理文本，移除不必要的字符
    """
    # 移除首尾空白
    text = text.strip()
    # 移除换行符
    text = text.replace('\n', '')
    # 移除回车符
    text = text.replace('\r', '')

    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)

    return text

def generate_filename(text, char_limit=100):
    """
    从输入文本中截取前几个字符作为文件名，确保正确处理中文字符
    
    Args:
        text: 输入文本
        char_limit: 截取的字符数量
    Returns:
        生成的文件名
    """
    # 清理文本
    text = sanitize_text(text)
    
    if not text:
        return "tts_output"
        
    # 确保文本是 UTF-8 编码
    if isinstance(text, bytes):
        text = text.decode('utf-8')
        
    # 直接截取字符，UTF-8 字符串会正确处理中文
    filename = text[:char_limit]
    
    if re.search(r'[\u4e00-\u9fff]', filename):
        filename = '-'.join(lazy_pinyin(filename))    

    # 如果生成的文件名为空，使用默认名称
    if not filename:
        filename = "tts_output"
        
    return filename

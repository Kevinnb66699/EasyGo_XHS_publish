from flask import Flask, request, jsonify
from xhs import XhsClient
import requests
import logging
import time
import tempfile
import os
from functools import wraps
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def mask_cookie(cookie: str) -> str:
    """隐藏敏感 Cookie 信息用于日志记录"""
    if not cookie or len(cookie) < 10:
        return "***"
    return cookie[:10] + "..." + cookie[-5:]


def retry_on_failure(max_retries=3, delay=1):
    """指数退避重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"第 {attempt + 1} 次尝试失败: {str(e)}，等待 {wait_time}秒后重试")
                    time.sleep(wait_time)
        return wrapper
    return decorator


def validate_cookie(cookie: str) -> bool:
    """验证 Cookie 格式是否包含必要字段"""
    if not cookie:
        return False
    required_fields = ['a1']
    cookie_dict = {}
    for item in cookie.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            cookie_dict[key.strip()] = value.strip()
    
    return all(field in cookie_dict for field in required_fields)


@app.route('/')
def index():
    """API 根路径"""
    return jsonify({
        'message': 'XiaoHongShu Publish API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'publish': '/api/publish'
        }
    })


@app.route('/api/health')
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'xiaohongshu-publish-api',
        'version': '1.0.0'
    })


@app.route('/api/publish', methods=['POST'])
def publish():
    """小红书笔记发布接口"""
    temp_files = []
    
    try:
        # 1. 获取并验证 Cookie
        cookie = request.headers.get('X-XHS-Cookie')
        if not cookie:
            logger.error("请求缺少 X-XHS-Cookie header")
            return jsonify({
                'success': False,
                'error': 'X-XHS-Cookie header is required'
            }), 400
        
        logger.info(f"收到发布请求，Cookie: {mask_cookie(cookie)}")
        
        if not validate_cookie(cookie):
            logger.error("Cookie 格式无效或缺少必要字段")
            return jsonify({
                'success': False,
                'error': 'Invalid cookie format or expired'
            }), 401
        
        # 2. 解析并验证请求体
        data = request.get_json()
        if not data:
            logger.error("请求体为空")
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        title = data.get('title')
        content = data.get('content')
        image_url = data.get('image_url')
        image_urls = data.get('image_urls', [])
        is_private = data.get('is_private', False)
        
        if not title:
            logger.error("缺少 title 字段")
            return jsonify({
                'success': False,
                'error': 'title is required'
            }), 400
            
        if not content:
            logger.error("缺少 content 字段")
            return jsonify({
                'success': False,
                'error': 'content is required'
            }), 400
        
        logger.info(f"笔记信息 - 标题: {title[:20]}, 内容长度: {len(content)}, 私密: {is_private}")
        
        # 3. 初始化小红书客户端
        try:
            client = XhsClient(cookie=cookie)
            logger.info("小红书客户端初始化成功")
        except Exception as e:
            logger.error(f"小红书客户端初始化失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to initialize XHS client: {str(e)}'
            }), 500
        
        # 4. 处理图片
        image_files = []
        urls_to_download = []
        
        if image_url:
            urls_to_download = [image_url]
        elif image_urls:
            urls_to_download = image_urls[:9]
        
        if urls_to_download:
            logger.info(f"开始下载 {len(urls_to_download)} 张图片")
            
            for idx, url in enumerate(urls_to_download):
                try:
                    logger.info(f"下载图片 {idx + 1}/{len(urls_to_download)}: {url}")
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    ext = Path(url).suffix or '.jpg'
                    if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        ext = '.jpg'
                    
                    temp_file = tempfile.NamedTemporaryFile(
                        mode='wb', 
                        suffix=ext, 
                        delete=False
                    )
                    temp_file.write(response.content)
                    temp_file.close()
                    
                    temp_files.append(temp_file.name)
                    image_files.append(temp_file.name)
                    
                    logger.info(f"图片 {idx + 1} 下载成功，大小: {len(response.content)} bytes")
                except Exception as e:
                    logger.warning(f"图片 {idx + 1} 处理失败: {str(e)}")
            
            logger.info(f"成功下载 {len(image_files)}/{len(urls_to_download)} 张图片")
        
        # 5. 发布笔记
        @retry_on_failure(max_retries=3, delay=2)
        def publish_note():
            logger.info("开始发布笔记到小红书")
            
            truncated_title = title[:20]
            if len(title) > 20:
                logger.warning(f"标题被截断: {title} -> {truncated_title}")
            
            result = client.create_image_note(
                title=truncated_title,
                desc=content,
                files=image_files if image_files else [],
                is_private=is_private
            )
            
            logger.info(f"小红书 API 返回: {result}")
            return result
        
        result = publish_note()
        
        note_id = result.get('note_id') or result.get('id')
        if not note_id:
            logger.error(f"返回结果中没有找到 note_id: {result}")
            raise ValueError('Failed to get note_id from response')
        
        note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
        
        logger.info(f"笔记发布成功! ID: {note_id}, URL: {note_url}")
        
        return jsonify({
            'success': True,
            'note_id': note_id,
            'note_url': note_url
        })
        
    except Exception as e:
        logger.error(f"发生错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        # 清理临时文件
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.info(f"已清理临时文件: {temp_file}")
            except Exception as e:
                logger.warning(f"清理临时文件失败: {str(e)}")

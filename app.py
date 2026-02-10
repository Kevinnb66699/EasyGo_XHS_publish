from flask import Flask, request, jsonify
from xhs import XhsClient
import requests
import logging
import sys
import time
import tempfile
import os
from functools import wraps
from pathlib import Path

# 配置日志 - 针对 Vercel 优化
def setup_logger():
    """配置适合生产环境的日志系统"""
    # 创建 logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # 移除所有现有的 handler
    logger.handlers.clear()
    
    # 创建 console handler 并设置为输出到 stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 创建 formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加 handler 到 logger
    logger.addHandler(console_handler)
    
    # 确保日志立即输出（重要！）
    logger.propagate = False
    
    return logger

logger = setup_logger()

# 初始化 Flask 应用
app = Flask(__name__)

# 记录应用启动
logger.info("=" * 50)
logger.info("Flask 应用启动成功")
logger.info(f"Python 版本: {sys.version}")
logger.info("=" * 50)
sys.stdout.flush()  # 强制刷新输出


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
                        logger.error(f"重试 {max_retries} 次后仍然失败: {str(e)}")
                        sys.stdout.flush()
                        raise
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"第 {attempt + 1} 次尝试失败: {str(e)}，等待 {wait_time}秒后重试")
                    sys.stdout.flush()
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


# ========== 全局错误处理器 ==========

@app.errorhandler(Exception)
def handle_exception(e):
    """捕获所有未处理的异常"""
    logger.error("=" * 50)
    logger.error(f"未捕获的异常: {type(e).__name__}")
    logger.error(f"错误信息: {str(e)}", exc_info=True)
    logger.error("=" * 50)
    sys.stdout.flush()  # 强制刷新日志
    
    return jsonify({
        'success': False,
        'error': f'Internal server error: {str(e)}',
        'error_type': type(e).__name__
    }), 500


@app.errorhandler(404)
def handle_404(e):
    """处理 404 错误"""
    logger.warning(f"404 错误 - 路径: {request.path}")
    sys.stdout.flush()
    
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'path': request.path
    }), 404


@app.errorhandler(400)
def handle_400(e):
    """处理 400 错误"""
    logger.warning(f"400 错误: {str(e)}")
    sys.stdout.flush()
    
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'message': str(e)
    }), 400


@app.before_request
def log_request():
    """记录每个请求"""
    logger.info(f"收到请求 [{request.method}] {request.path}")
    logger.info(f"来源 IP: {request.remote_addr}")
    logger.info(f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
    sys.stdout.flush()


@app.after_request
def log_response(response):
    """记录每个响应"""
    logger.info(f"响应状态码: {response.status_code}")
    sys.stdout.flush()
    return response


@app.get('/')
def index():
    """API 根路径"""
    logger.info("访问根路径")
    sys.stdout.flush()
    return jsonify({
        'message': 'XiaoHongShu Publish API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'publish': '/api/publish'
        }
    })


@app.get('/api/health')
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'xiaohongshu-publish-api',
        'version': '1.0.0'
    })


@app.post('/api/publish')
def publish():
    """小红书笔记发布接口"""
    logger.info("开始处理发布请求")
    sys.stdout.flush()
    
    temp_files = []
    
    try:
        # 1. 获取并验证 Cookie
        cookie = request.headers.get('X-XHS-Cookie')
        if not cookie:
            logger.error("请求缺少 X-XHS-Cookie header")
            sys.stdout.flush()
            return jsonify({
                'success': False,
                'error': 'X-XHS-Cookie header is required'
            }), 400
        
        logger.info(f"收到发布请求，Cookie: {mask_cookie(cookie)}")
        sys.stdout.flush()
        
        if not validate_cookie(cookie):
            logger.error("Cookie 格式无效或缺少必要字段")
            sys.stdout.flush()
            return jsonify({
                'success': False,
                'error': 'Invalid cookie format or expired'
            }), 401
        
        # 2. 解析并验证请求体
        data = request.get_json()
        if not data:
            logger.error("请求体为空")
            sys.stdout.flush()
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
            sys.stdout.flush()
            return jsonify({
                'success': False,
                'error': 'title is required'
            }), 400
            
        if not content:
            logger.error("缺少 content 字段")
            sys.stdout.flush()
            return jsonify({
                'success': False,
                'error': 'content is required'
            }), 400
        
        logger.info(f"笔记信息 - 标题: {title[:20]}, 内容长度: {len(content)}, 私密: {is_private}")
        sys.stdout.flush()
        
        # 3. 初始化小红书客户端
        try:
            logger.info("正在初始化小红书客户端...")
            sys.stdout.flush()
            
            # 获取签名服务器 URL（必须配置）
            sign_server_url = os.environ.get('XHS_SIGN_SERVER_URL', '')
            
            if not sign_server_url:
                logger.error("❌ 未配置 XHS_SIGN_SERVER_URL 环境变量")
                logger.error("在 Vercel 上必须配置外部签名服务器才能使用")
                logger.error("请参考文档配置签名服务: https://github.com/ReaJason/xhs")
                sys.stdout.flush()
                return jsonify({
                    'success': False,
                    'error': 'XHS_SIGN_SERVER_URL environment variable is required',
                    'message': 'Please configure an external signature service for Vercel deployment'
                }), 500
            
            logger.info(f"✅ 使用外部签名服务: {sign_server_url}")
            sys.stdout.flush()
            
            # 使用外部签名服务
            def external_sign(uri, data=None, a1="", web_session=""):
                """调用外部签名服务"""
                try:
                    logger.info(f"请求签名 - URI: {uri}")
                    sys.stdout.flush()
                    
                    response = requests.post(
                        f"{sign_server_url}/sign",
                        json={
                            "uri": uri,
                            "data": data,
                            "a1": a1,
                            "web_session": web_session
                        },
                        timeout=10
                    )
                    response.raise_for_status()
                    signs = response.json()
                    
                    logger.info(f"签名获取成功: {signs}")
                    sys.stdout.flush()
                    return signs
                except Exception as e:
                    logger.error(f"签名服务请求失败: {str(e)}")
                    sys.stdout.flush()
                    raise
            
            # 创建客户端（必须提供 sign 参数）
            client = XhsClient(cookie=cookie, sign=external_sign)
            
            logger.info("✅ 小红书客户端初始化成功")
            logger.info(f"Client 类型: {type(client)}")
            logger.info(f"External sign 函数: {client.external_sign}")
            sys.stdout.flush()
            
            # 验证 create_image_note 方法是否存在和可调用
            if not hasattr(client, 'create_image_note'):
                logger.error("❌ XhsClient 没有 create_image_note 方法")
                logger.error("可能是 xhs 库版本不兼容,请检查 requirements.txt")
                sys.stdout.flush()
                return jsonify({
                    'success': False,
                    'error': 'XhsClient does not have create_image_note method',
                    'message': 'Please check xhs library version'
                }), 500
            
            create_method = getattr(client, 'create_image_note', None)
            if create_method is None or not callable(create_method):
                logger.error(f"❌ create_image_note 不可调用: {create_method}")
                sys.stdout.flush()
                return jsonify({
                    'success': False,
                    'error': 'create_image_note method is not callable'
                }), 500
                
            logger.info("✅ create_image_note 方法验证通过")
            sys.stdout.flush()
            
        except Exception as e:
            logger.error(f"❌ 小红书客户端初始化失败: {str(e)}", exc_info=True)
            sys.stdout.flush()
            return jsonify({
                'success': False,
                'error': f'Failed to initialize XHS client: {str(e)}',
                'error_type': type(e).__name__,
                'hint': 'Please check XHS_SIGN_SERVER_URL environment variable'
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
            sys.stdout.flush()
            
            for idx, url in enumerate(urls_to_download):
                try:
                    logger.info(f"下载图片 {idx + 1}/{len(urls_to_download)}: {url}")
                    sys.stdout.flush()
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
                    sys.stdout.flush()
                except Exception as e:
                    logger.warning(f"图片 {idx + 1} 处理失败: {str(e)}")
                    sys.stdout.flush()
            
            logger.info(f"成功下载 {len(image_files)}/{len(urls_to_download)} 张图片")
            sys.stdout.flush()
        
        # 5. 验证是否有图片
        if not image_files:
            logger.error("小红书笔记必须包含至少一张图片")
            sys.stdout.flush()
            return jsonify({
                'success': False,
                'error': 'At least one image is required for XHS note'
            }), 400
        
        # 6. 发布笔记
        @retry_on_failure(max_retries=3, delay=2)
        def publish_note():
            logger.info("开始发布笔记到小红书")
            sys.stdout.flush()
            
            truncated_title = title[:20]
            if len(title) > 20:
                logger.warning(f"标题被截断: {title} -> {truncated_title}")
                sys.stdout.flush()
            
            logger.info(f"调用 create_image_note，参数：")
            logger.info(f"  title: {truncated_title}")
            logger.info(f"  desc: {content[:50]}...")
            logger.info(f"  files: {len(image_files)} 个文件")
            logger.info(f"  is_private: {is_private}")
            sys.stdout.flush()
            
            # 确保调用方法正确
            result = client.create_image_note(
                truncated_title,  # title
                content,           # desc
                image_files,       # files
                is_private=is_private
            )
            
            logger.info(f"小红书 API 返回: {result}")
            sys.stdout.flush()
            return result
        
        result = publish_note()
        
        note_id = result.get('note_id') or result.get('id')
        if not note_id:
            logger.error(f"返回结果中没有找到 note_id: {result}")
            sys.stdout.flush()
            raise ValueError('Failed to get note_id from response')
        
        note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
        
        logger.info(f"笔记发布成功! ID: {note_id}, URL: {note_url}")
        sys.stdout.flush()
        
        return jsonify({
            'success': True,
            'note_id': note_id,
            'note_url': note_url
        })
        
    except Exception as e:
        logger.error("=" * 50)
        logger.error(f"发布过程中发生错误: {type(e).__name__}")
        logger.error(f"错误详情: {str(e)}", exc_info=True)
        logger.error("=" * 50)
        sys.stdout.flush()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500
    
    finally:
        # 清理临时文件
        logger.info(f"开始清理 {len(temp_files)} 个临时文件")
        sys.stdout.flush()
        
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.info(f"已清理临时文件: {temp_file}")
            except Exception as e:
                logger.warning(f"清理临时文件失败: {str(e)}")
        
        sys.stdout.flush()


# Vercel 需要这个
application = app

if __name__ == '__main__':
    # 本地开发
    app.run(debug=True, host='0.0.0.0', port=5000)

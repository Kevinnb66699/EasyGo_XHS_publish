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
    """
    验证 Cookie 格式是否包含必要字段
    
    根据官方文档：https://reajason.github.io/xhs/basic.html
    小红书 Cookie 必须包含以下三个字段：
    - a1: 主要认证字段
    - web_session: 会话标识
    - webId: 设备/浏览器标识
    """
    if not cookie:
        return False
    
    # 小红书必需的三个 Cookie 字段
    required_fields = ['a1', 'web_session', 'webId']
    cookie_dict = {}
    
    for item in cookie.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            cookie_dict[key.strip()] = value.strip()
    
    # 检查是否所有必需字段都存在且非空
    missing_fields = [field for field in required_fields if field not in cookie_dict or not cookie_dict[field]]
    
    if missing_fields:
        logger.warning(f"❌ Cookie 缺少必需字段: {', '.join(missing_fields)}")
        logger.warning(f"   当前 Cookie 包含的字段: {list(cookie_dict.keys())}")
        logger.warning(f"   请确保 Cookie 包含: a1, web_session, webId")
        sys.stdout.flush()
        return False
    
    logger.info(f"✅ Cookie 验证通过，包含所有必需字段: {required_fields}")
    sys.stdout.flush()
    return True


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
                'error': 'Invalid cookie: missing required fields',
                'message': 'Cookie must contain: a1, web_session, and webId',
                'hint': 'Please get complete cookie from xiaohongshu.com while logged in'
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
                logger.error("请先启动签名服务器并设置环境变量")
                logger.error("")
                logger.error("启动步骤：")
                logger.error("  1. 启动签名服务器: python sign_server.py")
                logger.error("  2. 设置环境变量: set XHS_SIGN_SERVER_URL=http://localhost:5005")
                logger.error("  3. 启动发布服务器: python app.py")
                logger.error("")
                logger.error("或者使用快捷脚本: start_all.bat (Windows) 或 ./start_all.sh (Linux/Mac)")
                logger.error("")
                logger.error("详细文档: README_SIGN_SERVER.md")
                sys.stdout.flush()
                return jsonify({
                    'success': False,
                    'error': 'XHS_SIGN_SERVER_URL environment variable is required',
                    'message': 'Please start sign_server.py first and set XHS_SIGN_SERVER_URL environment variable',
                    'hint': 'Run: python sign_server.py, then set XHS_SIGN_SERVER_URL=http://localhost:5005'
                }), 500
            
            logger.info(f"✅ 使用外部签名服务: {sign_server_url}")
            sys.stdout.flush()
            
            # 从 Cookie 中提取必需的三个字段
            cookie_dict = {}
            for item in cookie.split(';'):
                item = item.strip()
                if '=' in item:
                    key, value = item.split('=', 1)
                    cookie_dict[key.strip()] = value.strip()
            
            cookie_a1 = cookie_dict.get('a1', '')
            cookie_web_session = cookie_dict.get('web_session', '')
            cookie_web_id = cookie_dict.get('webId', '')
            
            logger.info(f"📝 从 Cookie 提取认证信息:")
            logger.info(f"   a1: {cookie_a1[:20]}...")
            logger.info(f"   web_session: {cookie_web_session[:20]}...")
            logger.info(f"   webId: {cookie_web_id[:20]}...")
            sys.stdout.flush()
            
            # 签名缓存（避免相同请求重复签名）
            sign_cache = {}
            sign_request_count = [0]  # 使用列表以便在闭包中修改
            
            # 使用外部签名服务
            def external_sign(uri, data=None, a1="", web_session=""):
                """
                调用外部签名服务（带重试机制和智能缓存）
                
                注意：发布笔记需要多次签名是正常的！
                - 获取上传凭证（/api/media/v1/upload/web/permit）
                - 上传图片（可能需要签名）
                - 发布笔记（/web_api/sns/v2/note）
                每个请求的 URI 和 data 不同，签名也必须不同，不能重用！
                
                优化策略：
                - 对于相同的 uri + data，使用缓存（避免重复请求）
                - 失败后才重试，成功的签名直接使用
                """
                # 如果 XhsClient 没有传递，使用从 Cookie 中提取的值
                actual_a1 = a1 if a1 else cookie_a1
                actual_web_session = web_session if web_session else cookie_web_session
                actual_web_id = cookie_web_id
                
                # 生成缓存键（基于 uri 和 data）
                import json
                import hashlib
                cache_key = hashlib.md5(
                    f"{uri}:{json.dumps(data, sort_keys=True)}".encode()
                ).hexdigest()
                
                # 检查缓存
                if cache_key in sign_cache:
                    logger.info(f"♻️ 使用缓存的签名 - URI: {uri}")
                    sys.stdout.flush()
                    return sign_cache[cache_key]
                
                # 增加请求计数
                sign_request_count[0] += 1
                request_num = sign_request_count[0]
                
                max_retries = 3
                last_error = None
                
                for attempt in range(max_retries):
                    try:
                        logger.info(f"📝 [签名请求 #{request_num}] [尝试 {attempt + 1}/{max_retries}] URI: {uri}")
                        sys.stdout.flush()
                        
                        response = requests.post(
                            f"{sign_server_url}/sign",
                            json={
                                "uri": uri,
                                "data": data,
                                "a1": actual_a1,
                                "web_session": actual_web_session,
                                "web_id": actual_web_id
                            },
                            timeout=15
                        )
                        response.raise_for_status()
                        signs = response.json()
                        
                        # 检查返回格式
                        if 'x-s' not in signs or 'x-t' not in signs:
                            raise ValueError(f"签名服务返回格式错误: {signs}")
                        
                        # 缓存成功的签名
                        sign_cache[cache_key] = signs
                        
                        logger.info(f"✅ [签名请求 #{request_num}] 签名获取成功")
                        sys.stdout.flush()
                        return signs
                        
                    except Exception as e:
                        last_error = e
                        logger.warning(f"❌ [签名请求 #{request_num}] [尝试 {attempt + 1}/{max_retries}] 失败: {str(e)}")
                        sys.stdout.flush()
                        
                        if attempt < max_retries - 1:
                            wait_time = 1 * (attempt + 1)
                            logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                            sys.stdout.flush()
                            time.sleep(wait_time)
                
                # 所有重试都失败
                logger.error(f"💥 [签名请求 #{request_num}] 重试 {max_retries} 次后仍然失败")
                sys.stdout.flush()
                raise last_error
            
            #进行一次请求，获取签名端a1，并设置到cookie中
            response = requests.get(f"{sign_server_url}/web_a1")
            web_a1 = response.json().get('web_a1')
            cookie.replace(cookie_a1,web_a1,1)
                
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
            logger.info("=" * 60)
            logger.info("开始发布笔记到小红书")
            logger.info("=" * 60)
            sys.stdout.flush()
            
            truncated_title = title[:20]
            if len(title) > 20:
                logger.warning(f"⚠️ 标题被截断: {title} -> {truncated_title}")
                sys.stdout.flush()
            
            logger.info(f"📋 笔记参数：")
            logger.info(f"  • 标题: {truncated_title}")
            logger.info(f"  • 内容: {content[:100]}{'...' if len(content) > 100 else ''}")
            logger.info(f"  • 内容长度: {len(content)} 字符")
            logger.info(f"  • 图片数量: {len(image_files)}")
            logger.info(f"  • 私密笔记: {is_private}")
            
            # 验证内容
            if len(content) < 4:
                logger.error("❌ 内容太短，小红书要求至少 4 个字符")
                raise ValueError("Content too short, minimum 4 characters required")
            
            if len(truncated_title) < 1:
                logger.error("❌ 标题不能为空")
                raise ValueError("Title cannot be empty")
            
            sys.stdout.flush()
            
            # 记录即将开始的 API 调用流程
            logger.info("📡 开始 API 调用流程：")
            logger.info("  步骤1: 获取图片上传凭证（需要签名）")
            logger.info("  步骤2: 上传图片文件")
            logger.info("  步骤3: 发布笔记内容（需要签名）")
            sys.stdout.flush()
            
            try:
                # 调用发布方法
                result = client.create_image_note(
                    truncated_title,  # title
                    content,           # desc
                    image_files,       # files
                    is_private=is_private
                )
                
                logger.info(f"✅ 小红书 API 返回: {result}")
                sys.stdout.flush()
                return result
                
            except Exception as e:
                # 详细的错误日志
                logger.error("=" * 60)
                logger.error(f"❌ 发布失败！错误类型: {type(e).__name__}")
                logger.error(f"❌ 错误信息: {str(e)}")
                
                # 如果是 DataFetchError，提取详细信息
                if hasattr(e, 'args') and len(e.args) > 0:
                    error_data = e.args[0]
                    if isinstance(error_data, dict):
                        logger.error(f"❌ 错误代码: {error_data.get('code', 'unknown')}")
                        logger.error(f"❌ 错误消息: {error_data.get('msg', 'no message')}")
                        
                        # 根据错误代码提供建议
                        code = error_data.get('code')
                        if code == -1:
                            logger.error("💡 code: -1 可能原因：")
                            logger.error("   1. 内容违规（敏感词、广告等）")
                            logger.error("   2. 图片格式或大小问题")
                            logger.error("   3. 标题或内容格式不符合要求")
                            logger.error("   4. 请求过于频繁")
                            logger.error("   5. Cookie 已过期或无效")
                        elif code == -100:
                            logger.error("💡 code: -100 表示无登录信息，请检查 Cookie")
                        elif code == 300012:
                            logger.error("💡 code: 300012 表示需要验证码")
                
                logger.error("=" * 60)
                sys.stdout.flush()
                raise
        
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
        logger.error(f"❌ 发布过程中发生错误: {type(e).__name__}")
        logger.error(f"❌ 错误详情: {str(e)}", exc_info=True)
        logger.error("=" * 50)
        sys.stdout.flush()
        
        # 构建详细的错误响应
        error_response = {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }
        
        # 如果是 DataFetchError，提取小红书的错误信息
        if hasattr(e, 'args') and len(e.args) > 0:
            error_data = e.args[0]
            if isinstance(error_data, dict):
                error_response['xhs_error'] = error_data
                error_response['xhs_code'] = error_data.get('code')
                error_response['xhs_msg'] = error_data.get('msg', '')
                
                # 根据错误代码提供建议
                code = error_data.get('code')
                suggestions = []
                
                if code == -1:
                    suggestions = [
                        "检查内容是否包含敏感词或广告",
                        "检查图片格式是否正确（支持 jpg、png、gif、webp）",
                        "检查标题和内容长度是否符合要求",
                        "尝试降低请求频率",
                        "重新获取 Cookie（可能已过期）"
                    ]
                elif code == -100:
                    suggestions = [
                        "Cookie 无效或已过期",
                        "请重新登录小红书并获取新的 Cookie",
                        "确保 Cookie 包含 a1、web_session、webId 三个字段"
                    ]
                elif code == 300012:
                    suggestions = [
                        "触发了验证码机制",
                        "降低请求频率",
                        "等待一段时间后再试"
                    ]
                
                if suggestions:
                    error_response['suggestions'] = suggestions
        
        return jsonify(error_response), 500
    
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

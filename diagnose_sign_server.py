#!/usr/bin/env python3
"""
签名服务器诊断工具
用于排查签名生成问题
"""

import requests
import json
import time

def print_header(msg):
    print(f"\n{'='*70}")
    print(f"  {msg}")
    print(f"{'='*70}\n")

def diagnose_sign_server(server_url):
    """诊断签名服务器"""
    server_url = server_url.rstrip('/')
    
    print_header("🔍 签名服务器诊断工具")
    print(f"服务器地址: {server_url}\n")
    
    # 1. 检查服务器健康状态
    print("📋 步骤 1: 检查服务器健康状态")
    print("-" * 70)
    try:
        response = requests.get(f"{server_url}/health", timeout=10)
        health_data = response.json()
        
        print(f"✅ 服务器响应正常")
        print(f"\n完整健康数据:")
        print(json.dumps(health_data, indent=2, ensure_ascii=False))
        
        # 检查关键字段
        status = health_data.get('status')
        browser_ready = health_data.get('browser_ready')
        a1 = health_data.get('a1', '')
        
        print(f"\n关键指标:")
        print(f"  状态: {status} {'✅' if status == 'healthy' else '❌'}")
        print(f"  浏览器就绪: {browser_ready} {'✅' if browser_ready else '❌'}")
        print(f"  A1 Cookie: {a1[:30] if a1 else '(空)'}... {'✅' if a1 else '❌'}")
        
        if status != 'healthy' or not browser_ready or not a1:
            print(f"\n⚠️ 警告: 服务器状态异常，签名功能可能无法正常工作")
            print(f"💡 建议: ")
            print(f"   1. 等待 1-2 分钟让浏览器完全初始化")
            print(f"   2. 检查 Render 日志查看错误信息")
            print(f"   3. 尝试重启服务")
            return
            
    except Exception as e:
        print(f"❌ 服务器健康检查失败: {e}")
        return
    
    time.sleep(1)
    
    # 2. 测试签名生成（详细版）
    print_header("📋 步骤 2: 测试签名生成（详细诊断）")
    
    test_cases = [
        {
            "name": "测试用例 1: 基本请求（无 data）",
            "payload": {
                "uri": "/api/sns/web/v1/user_posted",
                "data": None,
                "a1": "test_a1",
                "web_session": "test_session"
            }
        },
        {
            "name": "测试用例 2: 带空对象 data",
            "payload": {
                "uri": "/api/sns/web/v1/user_posted",
                "data": {},
                "a1": "test_a1",
                "web_session": "test_session"
            }
        },
        {
            "name": "测试用例 3: 带参数的请求",
            "payload": {
                "uri": "/api/sns/web/v1/feed",
                "data": {
                    "num": 20,
                    "cursor_score": ""
                },
                "a1": "test_a1",
                "web_session": "test_session"
            }
        }
    ]
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\n{test['name']}")
        print("-" * 70)
        
        try:
            print(f"请求参数:")
            print(json.dumps(test['payload'], indent=2, ensure_ascii=False))
            
            print(f"\n正在发送请求...")
            response = requests.post(
                f"{server_url}/sign",
                json=test['payload'],
                timeout=30
            )
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n完整响应:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # 详细检查
                x_s = data.get('x-s')
                x_t = data.get('x-t')
                
                print(f"\n字段检查:")
                print(f"  x-s 存在: {x_s is not None} {'✅' if x_s else '❌'}")
                print(f"  x-s 类型: {type(x_s).__name__}")
                print(f"  x-s 长度: {len(str(x_s)) if x_s else 0}")
                print(f"  x-s 值: {str(x_s)[:100] if x_s else '(空)'}")
                
                print(f"\n  x-t 存在: {x_t is not None} {'✅' if x_t else '❌'}")
                print(f"  x-t 类型: {type(x_t).__name__}")
                print(f"  x-t 值: {x_t}")
                
                # 判断
                if x_s and x_t:
                    print(f"\n✅ 测试通过: 签名完整")
                elif x_t and not x_s:
                    print(f"\n❌ 测试失败: 只有 x-t，缺少 x-s")
                    print(f"\n可能的原因:")
                    print(f"  1. 浏览器中的 window._webmsxyw 函数返回异常")
                    print(f"  2. 小红书页面加载不完整")
                    print(f"  3. 签名函数版本更新")
                elif x_s and not x_t:
                    print(f"\n❌ 测试失败: 只有 x-s，缺少 x-t")
                else:
                    print(f"\n❌ 测试失败: x-s 和 x-t 都为空")
                    
            else:
                print(f"\n❌ 请求失败")
                print(f"响应内容: {response.text[:500]}")
                
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
        
        if idx < len(test_cases):
            print(f"\n等待 2 秒后进行下一个测试...")
            time.sleep(2)
    
    # 3. 检查服务器日志建议
    print_header("📋 步骤 3: 排查建议")
    
    print("""
如果签名只返回 x-t 而没有 x-s，可能的原因和解决方案：

🔍 可能原因 1: 浏览器环境初始化不完整
   症状: browser_ready=true 但签名不完整
   解决: 
   - 查看 Render 日志中是否有 JavaScript 错误
   - 检查 stealth.min.js 是否下载成功
   - 尝试重启服务让浏览器重新初始化

🔍 可能原因 2: 小红书网站访问失败
   症状: 可以生成签名但字段不完整
   解决:
   - 检查服务器能否正常访问 xiaohongshu.com
   - 检查网络连接和防火墙设置
   - 查看日志中访问小红书页面的状态

🔍 可能原因 3: window._webmsxyw 函数异常
   症状: 只返回部分字段
   解决:
   - 这是小红书的签名函数，可能页面还没完全加载
   - 增加等待时间（sign_server.py 第 145 行）
   - 查看浏览器控制台是否有 JavaScript 错误

🔍 可能原因 4: 签名服务器代码问题
   症状: 特定情况下返回字段不全
   解决:
   - 检查 sign_server.py 第 199-211 行的签名生成逻辑
   - 确认 encrypt_params["X-s"] 的大小写正确
   - 添加更多日志输出调试

📚 下一步操作:

1. 查看 Render 实时日志:
   登录 Render Dashboard → 选择服务 → Logs

2. 手动测试浏览器函数:
   在服务器上运行 Python，手动执行签名查看详细错误

3. 检查依赖版本:
   确认 playwright==1.48.0 和 chromium 版本匹配

4. 联系我帮助:
   提供 Render 日志和完整错误信息
""")

if __name__ == "__main__":
    print("🚀 签名服务器诊断工具\n")
    
    server_url = input("请输入签名服务器地址 (例如: https://your-server.onrender.com): ").strip()
    
    if not server_url:
        print("❌ 错误: 请提供服务器地址")
        exit(1)
    
    try:
        diagnose_sign_server(server_url)
    except KeyboardInterrupt:
        print("\n\n已取消诊断")
    except Exception as e:
        print(f"\n❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()

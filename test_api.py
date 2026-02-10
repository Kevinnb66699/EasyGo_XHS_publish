#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书发布 API 测试脚本

使用方法:
1. 修改 COOKIE 变量为你的小红书 Cookie
2. 修改 API_URL 为你的 API 地址（本地或 Vercel）
3. 运行: python test_api.py
"""

import requests
import json

# ================== 配置区域 ==================
# 修改为你的小红书 Cookie
COOKIE = "a1=your_a1_value; webId=your_webid; web_session=your_session"

# API 地址
# 本地测试: http://localhost:5000
# Vercel: https://your-app.vercel.app
API_URL = "http://localhost:5000"
# ============================================


def test_health_check():
    """测试健康检查接口"""
    print("\n" + "="*50)
    print("测试 1: 健康检查")
    print("="*50)
    
    try:
        response = requests.get(f"{API_URL}/api/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
        return False


def test_publish_text_only():
    """测试发布纯文字笔记"""
    print("\n" + "="*50)
    print("测试 2: 发布纯文字笔记")
    print("="*50)
    
    headers = {
        "Content-Type": "application/json",
        "X-XHS-Cookie": COOKIE
    }
    
    data = {
        "title": "API 测试笔记",
        "content": "这是通过 API 自动发布的测试笔记。\n\n如果你看到这条笔记，说明 API 工作正常！✨"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/publish",
            headers=headers,
            json=data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 发布失败: {str(e)}")
        return False


def test_publish_with_image():
    """测试发布带单张图片的笔记"""
    print("\n" + "="*50)
    print("测试 3: 发布带单张图片的笔记")
    print("="*50)
    
    headers = {
        "Content-Type": "application/json",
        "X-XHS-Cookie": COOKIE
    }
    
    data = {
        "title": "图片测试笔记",
        "content": "这是一张测试图片\n\n图片来自 Lorem Picsum",
        "image_url": "https://picsum.photos/800/600"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/publish",
            headers=headers,
            json=data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 发布失败: {str(e)}")
        return False


def test_publish_with_multiple_images():
    """测试发布多张图片的笔记"""
    print("\n" + "="*50)
    print("测试 4: 发布多张图片的笔记")
    print("="*50)
    
    headers = {
        "Content-Type": "application/json",
        "X-XHS-Cookie": COOKIE
    }
    
    data = {
        "title": "多图测试",
        "content": "这是一组测试图片\n\n包含多张随机图片",
        "image_urls": [
            "https://picsum.photos/800/600?random=1",
            "https://picsum.photos/800/600?random=2",
            "https://picsum.photos/800/600?random=3"
        ]
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/publish",
            headers=headers,
            json=data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 发布失败: {str(e)}")
        return False


def test_error_missing_cookie():
    """测试缺少 Cookie 的错误处理"""
    print("\n" + "="*50)
    print("测试 5: 错误处理 - 缺少 Cookie")
    print("="*50)
    
    headers = {
        "Content-Type": "application/json"
        # 故意不传 X-XHS-Cookie
    }
    
    data = {
        "title": "测试笔记",
        "content": "这条笔记不应该被发布"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/publish",
            headers=headers,
            json=data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        # 期望返回 400 错误
        return response.status_code == 400
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_error_missing_title():
    """测试缺少标题的错误处理"""
    print("\n" + "="*50)
    print("测试 6: 错误处理 - 缺少标题")
    print("="*50)
    
    headers = {
        "Content-Type": "application/json",
        "X-XHS-Cookie": COOKIE
    }
    
    data = {
        # 故意不传 title
        "content": "这条笔记不应该被发布"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/publish",
            headers=headers,
            json=data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        # 期望返回 400 错误
        return response.status_code == 400
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "🚀 " + "="*50)
    print("小红书发布 API 测试脚本")
    print("="*50)
    print(f"API 地址: {API_URL}")
    print(f"Cookie: {COOKIE[:20]}..." if len(COOKIE) > 20 else f"Cookie: {COOKIE}")
    
    # 检查 Cookie 是否已配置
    if COOKIE == "a1=your_a1_value; webId=your_webid; web_session=your_session":
        print("\n⚠️  警告: 请先在脚本中配置你的小红书 Cookie！")
        print("在脚本顶部找到 COOKIE 变量并修改为你的真实 Cookie。")
        return
    
    results = []
    
    # 运行测试
    results.append(("健康检查", test_health_check()))
    
    # 询问是否要执行会实际发布笔记的测试
    print("\n" + "-"*50)
    response = input("⚠️  以下测试会实际发布笔记到小红书，是否继续? (y/n): ")
    if response.lower() == 'y':
        results.append(("发布纯文字笔记", test_publish_text_only()))
        results.append(("发布单张图片笔记", test_publish_with_image()))
        results.append(("发布多张图片笔记", test_publish_with_multiple_images()))
    else:
        print("跳过发布测试")
    
    # 错误处理测试（不会实际发布）
    results.append(("错误处理-缺少Cookie", test_error_missing_cookie()))
    results.append(("错误处理-缺少标题", test_error_missing_title()))
    
    # 输出测试结果
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查日志")


if __name__ == "__main__":
    main()

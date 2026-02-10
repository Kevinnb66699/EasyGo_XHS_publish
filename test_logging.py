#!/usr/bin/env python3
"""
测试日志功能的脚本
用于验证日志是否正常输出
"""
import requests
import json
import sys

# 配置
BASE_URL = "http://localhost:5000"  # 本地测试
# BASE_URL = "https://your-app.vercel.app"  # 部署后替换为 Vercel URL

def test_health():
    """测试健康检查接口"""
    print("\n" + "=" * 50)
    print("测试 1: 健康检查接口")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def test_missing_cookie():
    """测试缺少 Cookie 的情况"""
    print("\n" + "=" * 50)
    print("测试 2: 缺少 Cookie (应该返回 400)")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/publish",
            json={"title": "测试", "content": "测试内容"},
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 400
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def test_invalid_cookie():
    """测试无效 Cookie 的情况"""
    print("\n" + "=" * 50)
    print("测试 3: 无效 Cookie (应该返回 401)")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/publish",
            headers={"X-XHS-Cookie": "invalid_cookie"},
            json={"title": "测试", "content": "测试内容"},
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 401
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def test_missing_title():
    """测试缺少标题的情况"""
    print("\n" + "=" * 50)
    print("测试 4: 缺少标题 (应该返回 400)")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/publish",
            headers={"X-XHS-Cookie": "a1=test123; web_session=test456"},
            json={"content": "测试内容"},
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 400
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def test_404():
    """测试 404 错误"""
    print("\n" + "=" * 50)
    print("测试 5: 不存在的路径 (应该返回 404)")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/nonexistent", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 404
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试日志功能")
    print(f"目标 URL: {BASE_URL}")
    print("=" * 50)
    
    tests = [
        ("健康检查", test_health),
        ("缺少 Cookie", test_missing_cookie),
        ("无效 Cookie", test_invalid_cookie),
        ("缺少标题", test_missing_title),
        ("404 错误", test_404),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 执行失败: {str(e)}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print("\n" + "=" * 50)
    print(f"总计: {passed_count}/{total_count} 测试通过")
    print("=" * 50)
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！日志功能正常。")
        print("\n💡 提示: 检查终端输出，应该能看到详细的日志信息。")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} 个测试失败，请检查日志。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

import requests
import json
from datetime import datetime

def login():
    """登录并获取令牌"""
    login_url = "http://localhost:8000/user/login"
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(login_url, json=login_data, headers=headers)
        print(f"登录状态码: {response.status_code}")
        print(f"登录响应: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if 'results' in response_data and 'token' in response_data['results']:
                token = response_data['results']['token']
                print(f"✅ 登录成功，获取到令牌: {token}")
                return token
            else:
                print("❌ 未能从响应中提取令牌")
                return None
        else:
            print("❌ 登录失败")
            return None
    except Exception as e:
        print(f"❌ 登录出错: {str(e)}")
        return None

def test_create_environment(token=None):
    """测试创建环境配置"""
    if not token:
        print("⚠️ 未提供令牌，尝试登录获取")
        token = login()
        if not token:
            print("❌ 无法继续测试，未获取到令牌")
            return False
    
    url = "http://localhost:8000/config/project-view"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    payload = {
        "name": f"测试环境-{current_time}",
        "host": "localhost",
        "port": 3306,
        "username": "testuser",
        "password": "testpass",
        "database": "testdb"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"创建环境配置状态码: {response.status_code}")
        print(f"创建环境配置响应内容: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ 测试通过：环境配置创建成功！")
            return True
        else:
            print("❌ 测试失败：环境配置创建失败！")
            return False
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        return False

def test_get_environment_list(token=None):
    """测试获取环境配置列表"""
    if not token:
        print("⚠️ 未提供令牌，尝试登录获取")
        token = login()
        if not token:
            print("❌ 无法继续测试，未获取到令牌")
            return False
    
    url = "http://localhost:8000/config/project-view"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"获取环境配置列表状态码: {response.status_code}")
        print(f"获取环境配置列表响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 测试通过：成功获取环境配置列表！")
            return True
        else:
            print("❌ 测试失败：获取环境配置列表失败！")
            return False
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        return False

def run_all_tests():
    """运行所有测试"""
    token = login()
    if not token:
        print("❌ 登录失败，无法继续测试")
        return
    
    tests = [
        test_create_environment,
        test_get_environment_list
    ]
    
    results = []
    for test in tests:
        print(f"\n运行测试: {test.__name__}")
        result = test(token)
        results.append((test.__name__, result))
    
    print("\n测试结果汇总:")
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

if __name__ == "__main__":
    # 登录并测试环境配置相关功能
    token = login()
    if token:
        print("登录测试通过")
        test_create_environment(token)
        # 暂时注释掉这部分，分开测试
        # print("\n===== 测试获取环境配置列表 =====")
        # test_get_environment_list(token)

import requests
import json

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
            # 根据实际返回的 JSON 结构进行解析
            if 'results' in response_data and 'token' in response_data['results']:
                token = response_data['results']['token']
                print(f"✅ 登录成功，获取到令牌: {token}")
                return token
            else:
                print("❌ 未能从响应中提取令牌")
                print(f"响应结构: {response_data}")
                return None
        else:
            print("❌ 登录失败")
            return None
    except Exception as e:
        print(f"❌ 登录出错: {str(e)}")
        return None

def test_create_project(token=None):
    """测试创建项目接口"""
    if not token:
        print("⚠️ 未提供令牌，尝试登录获取")
        token = login()
        if not token:
            print("❌ 无法继续测试，未获取到令牌")
            return False
    
    url = "http://localhost:8000/conf/envir-view"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    from datetime import datetime
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    payload = {
        "name": f"测试项目-自动化测试-{current_time}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"创建项目状态码: {response.status_code}")
        print(f"创建项目响应内容: {response.text}")
        
        # 检查响应内容，如果服务器返回 200 但实际的 code 是 201，也算成功
        response_data = response.json()
        if response.status_code == 201 or (response.status_code == 200 and response_data.get('code') == 201):
            print("✅ 测试通过：项目创建成功！")
            print(f"项目ID: {response_data.get('results', {}).get('id')}")
            print(f"项目名称: {response_data.get('results', {}).get('name')}")
            print(f"创建时间: {response_data.get('results', {}).get('created')}")
            return True
        else:
            print("❌ 测试失败：项目创建失败！")
            return False
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        return False

if __name__ == "__main__":
    test_create_project()

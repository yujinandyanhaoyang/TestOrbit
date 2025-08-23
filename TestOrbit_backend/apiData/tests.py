from django.test import TestCase
from django.contrib.auth import get_user_model
from apiData.models import ApiCaseModule, ApiCase, ApiCaseStep
from config.models import Environment
from utils.constant import API, WAITING

# Create your tests here.

class ApiCaseTestDataCreator(TestCase):
    """
    为 ACM00000001 模块创建测试数据的测试类
    包含5条测试用例，每条用例包含2个步骤
    """
    
    def setUp(self):
        """设置测试环境"""
        # 获取或创建用户模型
        User = get_user_model()
        self.user = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )[0]
        
        # 获取或创建测试模块
        self.module = ApiCaseModule.objects.get_or_create(
            id='ACM00000001',
            defaults={
                'name': '测试模块',
                'position': 0,
                'module_related': []
            }
        )[0]
        
        # 获取或创建默认环境
        self.environment = Environment.objects.get_or_create(
            id=1,
            defaults={'name': '默认环境'}
        )[0]
    
    def test_create_api_test_cases(self):
        """创建5条API测试用例，每条包含2个步骤"""
        
        test_cases_data = [
            {
                'name': '用户登录接口测试',
                'remark': '测试用户登录功能的完整流程',
                'steps': [
                    {
                        'step_name': '发送登录请求',
                        'type': 'api',
                        'params': {
                            'path': '/api/login',
                            'method': 'POST',
                            'headers': {'Content-Type': 'application/json'},
                            'body': {'username': 'testuser', 'password': 'testpass123'}
                        }
                    },
                    {
                        'step_name': '验证登录响应',
                        'type': 'api',
                        'params': {
                            'path': '/api/user/profile',
                            'method': 'GET',
                            'headers': {'Authorization': 'Bearer ${token}'},
                            'body': {}
                        }
                    }
                ]
            },
            {
                'name': '商品查询接口测试',
                'remark': '测试商品搜索和详情查询功能',
                'steps': [
                    {
                        'step_name': '搜索商品列表',
                        'type': 'api',
                        'params': {
                            'path': '/api/products/search',
                            'method': 'GET',
                            'headers': {'Content-Type': 'application/json'},
                            'body': {'keyword': 'iPhone', 'page': 1, 'limit': 10}
                        }
                    },
                    {
                        'step_name': '获取商品详情',
                        'type': 'api',
                        'params': {
                            'path': '/api/products/${product_id}',
                            'method': 'GET',
                            'headers': {'Content-Type': 'application/json'},
                            'body': {}
                        }
                    }
                ]
            },
            {
                'name': '订单创建接口测试',
                'remark': '测试创建订单和支付流程',
                'steps': [
                    {
                        'step_name': '创建订单',
                        'type': 'api',
                        'params': {
                            'path': '/api/orders',
                            'method': 'POST',
                            'headers': {'Content-Type': 'application/json', 'Authorization': 'Bearer ${token}'},
                            'body': {
                                'product_id': '12345',
                                'quantity': 2,
                                'delivery_address': '北京市朝阳区测试地址'
                            }
                        }
                    },
                    {
                        'step_name': '确认支付',
                        'type': 'api',
                        'params': {
                            'path': '/api/orders/${order_id}/pay',
                            'method': 'POST',
                            'headers': {'Content-Type': 'application/json', 'Authorization': 'Bearer ${token}'},
                            'body': {'payment_method': 'alipay', 'amount': 2999.00}
                        }
                    }
                ]
            },
            {
                'name': '用户信息管理测试',
                'remark': '测试用户信息的查询和更新功能',
                'steps': [
                    {
                        'step_name': '获取用户信息',
                        'type': 'api',
                        'params': {
                            'path': '/api/user/profile',
                            'method': 'GET',
                            'headers': {'Authorization': 'Bearer ${token}'},
                            'body': {}
                        }
                    },
                    {
                        'step_name': '更新用户信息',
                        'type': 'api',
                        'params': {
                            'path': '/api/user/profile',
                            'method': 'PUT',
                            'headers': {'Content-Type': 'application/json', 'Authorization': 'Bearer ${token}'},
                            'body': {
                                'nickname': '新昵称',
                                'phone': '13800138000',
                                'email': 'newemail@example.com'
                            }
                        }
                    }
                ]
            },
            {
                'name': '文件上传接口测试',
                'remark': '测试文件上传和下载功能',
                'steps': [
                    {
                        'step_name': '上传文件',
                        'type': 'api',
                        'params': {
                            'path': '/api/files/upload',
                            'method': 'POST',
                            'headers': {'Authorization': 'Bearer ${token}'},
                            'body': {
                                'file': '@test_image.jpg',
                                'category': 'avatar'
                            }
                        }
                    },
                    {
                        'step_name': '获取文件信息',
                        'type': 'api',
                        'params': {
                            'path': '/api/files/${file_id}',
                            'method': 'GET',
                            'headers': {'Authorization': 'Bearer ${token}'},
                            'body': {}
                        }
                    }
                ]
            }
        ]
        
        created_cases = []
        
        # 创建测试用例和步骤
        for case_data in test_cases_data:
            print(f"创建测试用例: {case_data['name']}")
            
            # 创建 ApiCase
            api_case = ApiCase.objects.create(
                name=case_data['name'],
                module=self.module,
                remark=case_data['remark'],
                status=WAITING,
                creater=self.user,
                updater=self.user
            )
            
            # 创建步骤
            for step_index, step_data in enumerate(case_data['steps'], 1):
                print(f"  创建步骤 {step_index}: {step_data['step_name']}")
                
                ApiCaseStep.objects.create(
                    case=api_case,
                    step_name=step_data['step_name'],
                    step_order=step_index,
                    type=step_data['type'],
                    status=WAITING,
                    enabled=True,
                    params=step_data['params'],
                    timeout=30,
                    source='user_api',
                    env_id=self.environment
                )
            
            created_cases.append(api_case)
        
        # 验证创建结果
        self.assertEqual(len(created_cases), 5, "应该创建5条测试用例")
        
        for case in created_cases:
            steps = ApiCaseStep.objects.filter(case=case)
            self.assertEqual(steps.count(), 2, f"用例 {case.name} 应该包含2个步骤")
            
            # 验证步骤顺序
            step_orders = list(steps.values_list('step_order', flat=True))
            self.assertEqual(sorted(step_orders), [1, 2], "步骤顺序应该是1和2")
        
        print(f"✅ 成功创建了 {len(created_cases)} 条测试用例")
        print("📊 创建统计:")
        print(f"  - 测试用例数量: {ApiCase.objects.filter(module=self.module).count()}")
        print(f"  - 测试步骤数量: {ApiCaseStep.objects.filter(case__module=self.module).count()}")
        
        return created_cases
    
    def test_verify_test_data_structure(self):
        """验证创建的测试数据结构"""
        # 先创建测试数据
        self.test_create_api_test_cases()
        
        # 验证模块下的用例数量
        cases = ApiCase.objects.filter(module=self.module)
        self.assertEqual(cases.count(), 5)
        
        # 验证每个用例的步骤数量
        for case in cases:
            steps = ApiCaseStep.objects.filter(case=case)
            self.assertEqual(steps.count(), 2)
            
            # 验证步骤的基本结构
            for step in steps:
                self.assertIsNotNone(step.step_name)
                self.assertIsNotNone(step.params)
                self.assertIn('path', step.params)
                self.assertIn('method', step.params)
                self.assertTrue(step.enabled)
        
        print("✅ 测试数据结构验证通过")


class ApiCaseStepModelTest(TestCase):
    """ApiCaseStep 模型功能测试"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get_or_create(
            username='test_user_model',
            defaults={'email': 'test_model@example.com'}
        )[0]
        
        self.module = ApiCaseModule.objects.get_or_create(
            id='ACM00000001',
            defaults={'name': '测试模块', 'position': 0, 'module_related': []}
        )[0]
        
        self.case = ApiCase.objects.create(
            name='模型测试用例',
            module=self.module,
            creater=self.user,
            updater=self.user
        )
    
    def test_get_step_params(self):
        """测试 get_step_params 方法"""
        test_params = {
            'path': '/api/test',
            'method': 'GET',
            'headers': {'Content-Type': 'application/json'}
        }
        
        step = ApiCaseStep.objects.create(
            case=self.case,
            step_name='测试步骤',
            step_order=1,
            type='api',
            params=test_params
        )
        
        result = step.get_step_params()
        self.assertEqual(result, test_params)
        
        # 测试空参数
        step_empty = ApiCaseStep.objects.create(
            case=self.case,
            step_name='空参数步骤',
            step_order=2,
            type='api',
            params=None
        )
        
        result_empty = step_empty.get_step_params()
        self.assertEqual(result_empty, {})
    
    def test_update_step_params(self):
        """测试 update_step_params 方法"""
        step = ApiCaseStep.objects.create(
            case=self.case,
            step_name='更新测试步骤',
            step_order=1,
            type='api',
            params={'old': 'value'}
        )
        
        new_params = {
            'path': '/api/updated',
            'method': 'POST',
            'body': {'data': 'new_value'}
        }
        
        result = step.update_step_params(new_params)
        self.assertTrue(result)
        
        # 重新加载并验证
        step.refresh_from_db()
        self.assertEqual(step.params, new_params)
    
    def test_get_api_info(self):
        """测试 get_api_info 方法"""
        test_params = {
            'path': '/api/info',
            'method': 'GET',
            'headers': {'Authorization': 'Bearer token'}
        }
        
        step = ApiCaseStep.objects.create(
            case=self.case,
            step_name='API信息测试',
            step_order=1,
            type='api',
            params=test_params,
            timeout=60,
            source='user_api'
        )
        
        api_info = step.get_api_info()
        
        self.assertEqual(api_info['name'], 'API信息测试')
        self.assertEqual(api_info['path'], '/api/info')
        self.assertEqual(api_info['method'], 'GET')
        self.assertEqual(api_info['timeout'], 60)
        self.assertEqual(api_info['source'], 'user_api')
        self.assertEqual(api_info['params'], test_params)


if __name__ == '__main__':
    # 如果直接运行此文件，可以创建测试数据
    import django
    import os
    
    # 设置 Django 环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
    django.setup()
    
    print("🚀 开始创建测试数据...")
    
    # 创建测试实例并运行
    test_creator = ApiCaseTestDataCreator()
    test_creator.setUp()
    
    try:
        created_cases = test_creator.test_create_api_test_cases()
        print(f"🎉 测试数据创建完成！共创建 {len(created_cases)} 条测试用例")
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        import traceback
        traceback.print_exc()

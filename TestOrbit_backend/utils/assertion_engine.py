"""
断言引擎模块
处理HTTP请求响应的断言验证
"""
import json
import re
import jsonpath
from lxml import etree

class AssertionResult:
    """
    断言结果类
    存储断言的执行结果信息
    """
    def __init__(self, success, message, rule=None, actual_value=None):
        self.success = success
        self.message = message
        self.rule = rule
        self.actual_value = actual_value

    def to_dict(self):
        """
        将断言结果转为字典格式
        """
        result = {
            'success': self.success,
            'message': self.message
        }
        
        # 如果有rule信息，添加到结果中
        if self.rule:
            rule_info = {
                'id': self.rule.id,
                'type': self.rule.type,
                'expression': self.rule.expression,
                'operator': self.rule.operator,
                'expected_value': self.rule.expected_value
            }
            result['rule'] = rule_info
            
        # 如果有实际值，添加到结果中
        if self.actual_value is not None:
            result['actual_value'] = self.actual_value
            
        return result


class AssertionEngine:
    """
    断言引擎
    处理各种类型的断言验证
    """
    
    @staticmethod
    def assert_response(response, assertion_rules):
        """
        对HTTP响应执行一系列断言规则
        
        Args:
            response (dict): HTTP响应对象
            assertion_rules (list): 断言规则列表
            
        Returns:
            list: 断言结果列表
        """
        results = []
        
        # 遍历所有启用的断言规则
        for rule in [r for r in assertion_rules if r.enabled]:
            # 根据断言类型选择对应的断言方法
            if rule.type == 'jsonpath':
                result = AssertionEngine._assert_jsonpath(response, rule)
            elif rule.type == 'regex':
                result = AssertionEngine._assert_regex(response, rule)
            elif rule.type == 'xpath':
                result = AssertionEngine._assert_xpath(response, rule)
            elif rule.type == 'header':
                result = AssertionEngine._assert_header(response, rule)
            elif rule.type == 'status_code':
                result = AssertionEngine._assert_status_code(response, rule)
            else:
                # 未知的断言类型
                result = AssertionResult(
                    success=False,
                    message=f"未知的断言类型: {rule.type}",
                    rule=rule
                )
                
            results.append(result.to_dict())
            
        return results
    
    @staticmethod
    def _assert_jsonpath(response, rule):
        """
        执行JSONPath断言
        
        Args:
            response (dict): HTTP响应对象
            rule (AssertionRule): 断言规则
            
        Returns:
            AssertionResult: 断言结果
        """
        try:
            # 获取响应体数据
            if isinstance(response, dict) and 'body' in response:
                # 确保响应体是JSON对象
                if isinstance(response['body'], str):
                    try:
                        json_data = json.loads(response['body'])
                    except json.JSONDecodeError:
                        return AssertionResult(
                            success=False,
                            message="响应体不是有效的JSON格式",
                            rule=rule
                        )
                else:
                    json_data = response['body']
            else:
                # 如果没有body字段，尝试直接使用response作为JSON数据
                json_data = response
            
            # 应用JSONPath表达式
            expression = rule.expression
            matches = jsonpath.jsonpath(json_data, expression)
            
            # 如果没有匹配结果
            if matches is False:
                return AssertionResult(
                    success=False,
                    message=f"JSONPath表达式 '{expression}' 未匹配到任何内容",
                    rule=rule,
                    actual_value=None
                )
                
            # 获取匹配结果的第一个值(如果是多值结果)
            actual_value = matches[0] if matches else None
            
            # 执行断言比较
            result = AssertionEngine._compare_values(
                actual_value, 
                rule.expected_value, 
                rule.operator
            )
            
            if result.success:
                result.message = f"断言成功: {expression} {rule.operator} {rule.expected_value}"
            else:
                result.message = f"断言失败: 期望 {expression} {rule.operator} {rule.expected_value}，实际值为 {actual_value}"
                
            result.rule = rule
            result.actual_value = actual_value
            
            return result
            
        except Exception as e:
            return AssertionResult(
                success=False,
                message=f"JSONPath断言执行出错: {str(e)}",
                rule=rule
            )
    
    @staticmethod
    def _assert_regex(response, rule):
        """
        执行正则表达式断言
        
        Args:
            response (dict): HTTP响应对象
            rule (AssertionRule): 断言规则
            
        Returns:
            AssertionResult: 断言结果
        """
        try:
            # 从响应中提取文本内容
            if isinstance(response, dict) and 'body' in response:
                text = response['body']
                if not isinstance(text, str):
                    text = json.dumps(text)
            else:
                # 如果没有body字段，尝试直接使用response
                text = str(response)
                
            # 应用正则表达式
            pattern = rule.expression
            matches = re.findall(pattern, text)
            
            # 如果没有匹配结果
            if not matches:
                return AssertionResult(
                    success=False,
                    message=f"正则表达式 '{pattern}' 未匹配到任何内容",
                    rule=rule,
                    actual_value=None
                )
                
            # 获取匹配结果的第一个值
            actual_value = matches[0] if matches else None
            
            # 执行断言比较
            result = AssertionEngine._compare_values(
                actual_value, 
                rule.expected_value, 
                rule.operator
            )
            
            if result.success:
                result.message = f"断言成功: 正则表达式 '{pattern}' {rule.operator} {rule.expected_value}"
            else:
                result.message = f"断言失败: 期望正则表达式 '{pattern}' {rule.operator} {rule.expected_value}，实际值为 {actual_value}"
                
            result.rule = rule
            result.actual_value = actual_value
            
            return result
            
        except Exception as e:
            return AssertionResult(
                success=False,
                message=f"正则表达式断言执行出错: {str(e)}",
                rule=rule
            )
    
    @staticmethod
    def _assert_xpath(response, rule):
        """
        执行XPath断言
        
        Args:
            response (dict): HTTP响应对象
            rule (AssertionRule): 断言规则
            
        Returns:
            AssertionResult: 断言结果
        """
        try:
            # 从响应中提取HTML/XML内容
            if isinstance(response, dict) and 'body' in response:
                html_content = response['body']
                if not isinstance(html_content, str):
                    return AssertionResult(
                        success=False,
                        message="响应体不是有效的HTML/XML格式",
                        rule=rule
                    )
            else:
                # 如果没有body字段，尝试直接使用response
                html_content = str(response)
                
            # 解析HTML/XML
            try:
                # 尝试解析HTML
                parser = etree.HTMLParser()
                tree = etree.fromstring(html_content, parser)
            except:
                try:
                    # 尝试解析XML
                    tree = etree.fromstring(html_content.encode('utf-8'))
                except:
                    return AssertionResult(
                        success=False,
                        message="无法解析响应体为HTML或XML",
                        rule=rule
                    )
            
            # 应用XPath表达式
            xpath_expr = rule.expression
            matches = tree.xpath(xpath_expr)
            
            # 如果没有匹配结果
            if not matches:
                return AssertionResult(
                    success=False,
                    message=f"XPath表达式 '{xpath_expr}' 未匹配到任何内容",
                    rule=rule,
                    actual_value=None
                )
                
            # 获取匹配结果，如果是元素则转换为文本
            actual_value = None
            if len(matches) > 0:
                first_match = matches[0]
                if hasattr(first_match, 'text'):
                    actual_value = first_match.text
                else:
                    actual_value = str(first_match)
            
            # 执行断言比较
            result = AssertionEngine._compare_values(
                actual_value, 
                rule.expected_value, 
                rule.operator
            )
            
            if result.success:
                result.message = f"断言成功: XPath '{xpath_expr}' {rule.operator} {rule.expected_value}"
            else:
                result.message = f"断言失败: 期望 XPath '{xpath_expr}' {rule.operator} {rule.expected_value}，实际值为 {actual_value}"
                
            result.rule = rule
            result.actual_value = actual_value
            
            return result
            
        except Exception as e:
            return AssertionResult(
                success=False,
                message=f"XPath断言执行出错: {str(e)}",
                rule=rule
            )
    
    @staticmethod
    def _assert_header(response, rule):
        """
        执行HTTP头断言
        
        Args:
            response (dict): HTTP响应对象
            rule (AssertionRule): 断言规则
            
        Returns:
            AssertionResult: 断言结果
        """
        try:
            # 从响应中提取头信息
            if isinstance(response, dict) and 'headers' in response:
                headers = response['headers']
                if not isinstance(headers, dict):
                    return AssertionResult(
                        success=False,
                        message="响应头不是有效的字典格式",
                        rule=rule
                    )
            else:
                # 如果没有headers字段
                return AssertionResult(
                    success=False,
                    message="响应中没有headers字段",
                    rule=rule
                )
                
            # 获取指定的头
            header_name = rule.expression
            # 不区分大小写查找头
            header_found = False
            actual_value = None
            
            for k, v in headers.items():
                if k.lower() == header_name.lower():
                    header_found = True
                    actual_value = v
                    break
            
            if not header_found:
                return AssertionResult(
                    success=False,
                    message=f"响应头中未找到 '{header_name}'",
                    rule=rule,
                    actual_value=None
                )
                
            # 执行断言比较
            result = AssertionEngine._compare_values(
                actual_value, 
                rule.expected_value, 
                rule.operator
            )
            
            if result.success:
                result.message = f"断言成功: 响应头 '{header_name}' {rule.operator} {rule.expected_value}"
            else:
                result.message = f"断言失败: 期望响应头 '{header_name}' {rule.operator} {rule.expected_value}，实际值为 {actual_value}"
                
            result.rule = rule
            result.actual_value = actual_value
            
            return result
            
        except Exception as e:
            return AssertionResult(
                success=False,
                message=f"响应头断言执行出错: {str(e)}",
                rule=rule
            )
    
    @staticmethod
    def _assert_status_code(response, rule):
        """
        执行HTTP状态码断言
        
        Args:
            response (dict): HTTP响应对象
            rule (AssertionRule): 断言规则
            
        Returns:
            AssertionResult: 断言结果
        """
        try:
            # 从响应中提取状态码
            if isinstance(response, dict) and 'status_code' in response:
                status_code = response['status_code']
                if not isinstance(status_code, (int, str)):
                    status_code = str(status_code)
            else:
                # 如果没有status_code字段
                return AssertionResult(
                    success=False,
                    message="响应中没有status_code字段",
                    rule=rule
                )
            
            # 转换为相同的类型进行比较
            if isinstance(status_code, str) and rule.expected_value.isdigit():
                status_code = int(status_code)
                expected_value = int(rule.expected_value)
            else:
                expected_value = rule.expected_value
                
            # 执行断言比较
            result = AssertionEngine._compare_values(
                status_code, 
                expected_value, 
                rule.operator
            )
            
            if result.success:
                result.message = f"断言成功: 状态码 {status_code} {rule.operator} {expected_value}"
            else:
                result.message = f"断言失败: 期望状态码 {rule.operator} {expected_value}，实际状态码为 {status_code}"
                
            result.rule = rule
            result.actual_value = status_code
            
            return result
            
        except Exception as e:
            return AssertionResult(
                success=False,
                message=f"状态码断言执行出错: {str(e)}",
                rule=rule
            )
    
    @staticmethod
    def _compare_values(actual, expected, operator):
        """
        根据操作符比较两个值
        
        Args:
            actual: 实际值
            expected: 期望值
            operator: 比较操作符
            
        Returns:
            AssertionResult: 比较结果
        """
        # 如果实际值是None且期望值不是None，直接失败
        if actual is None and expected is not None and operator not in ['null', 'empty']:
            return AssertionResult(success=False, message="实际值为None")
            
        # 转换类型以便比较
        if isinstance(expected, str) and not isinstance(actual, str):
            # 尝试转换数值类型
            try:
                if '.' in expected:
                    expected = float(expected)
                    if isinstance(actual, (int, float)):
                        # 保持数值比较
                        pass
                    else:
                        actual = float(actual) if actual is not None else None
                elif expected.isdigit():
                    expected = int(expected)
                    if isinstance(actual, (int, float)):
                        # 保持数值比较
                        pass
                    else:
                        actual = int(actual) if actual is not None else None
            except (ValueError, TypeError):
                # 如果转换失败，使用字符串比较
                expected = str(expected)
                actual = str(actual) if actual is not None else None
        elif isinstance(actual, str) and not isinstance(expected, str):
            # 转换实际值为字符串
            expected = str(expected)
            
        # 根据操作符进行比较
        success = False
        try:
            if operator == '==':
                success = actual == expected
            elif operator == '!=':
                success = actual != expected
            elif operator == '>':
                success = actual > expected
            elif operator == '<':
                success = actual < expected
            elif operator == '>=':
                success = actual >= expected
            elif operator == '<=':
                success = actual <= expected
            elif operator == 'contains':
                if isinstance(actual, str) and isinstance(expected, str):
                    success = expected in actual
                elif isinstance(actual, (list, tuple)):
                    success = expected in actual
                else:
                    success = False
            elif operator == 'not_contains':
                if isinstance(actual, str) and isinstance(expected, str):
                    success = expected not in actual
                elif isinstance(actual, (list, tuple)):
                    success = expected not in actual
                else:
                    success = True
            elif operator == 'starts_with':
                if isinstance(actual, str) and isinstance(expected, str):
                    success = actual.startswith(expected)
                else:
                    success = False
            elif operator == 'ends_with':
                if isinstance(actual, str) and isinstance(expected, str):
                    success = actual.endswith(expected)
                else:
                    success = False
            elif operator == 'empty':
                success = actual == '' or actual == [] or actual == {} or actual is None
            elif operator == 'not_empty':
                success = actual != '' and actual != [] and actual != {} and actual is not None
            elif operator == 'null':
                success = actual is None
            elif operator == 'not_null':
                success = actual is not None
            else:
                return AssertionResult(
                    success=False, 
                    message=f"不支持的操作符: {operator}"
                )
        except Exception as e:
            return AssertionResult(
                success=False,
                message=f"比较值时出错: {str(e)}"
            )
            
        # 创建比较结果
        if success:
            message = f"比较成功: {actual} {operator} {expected}"
        else:
            message = f"比较失败: {actual} {operator} {expected}"
            
        return AssertionResult(success=success, message=message)

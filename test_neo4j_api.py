import unittest
import requests
import json
import os


class Neo4jAPITestCase(unittest.TestCase):
    BASE_URL = "http://localhost:5000"  # 确保这是你的Flask应用地址
    NEO4J_ENDPOINT = "/neo4j/query"  # 确认这是正确的端点

    def setUp(self):
        self.valid_query = "MATCH (n) RETURN n LIMIT 5"
        self.invalid_query = "INVALID CYPHER QUERY"

        # 添加调试信息
        print("\n测试环境检查:")
        print(f"Flask应用URL: {self.BASE_URL}")
        print(f"Neo4j端点: {self.NEO4J_ENDPOINT}")

        # 检查服务是否可用
        try:
            response = requests.get(self.BASE_URL, timeout=5)
            print(f"Flask应用状态: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"无法连接到Flask应用: {str(e)}")
            self.skipTest("Flask应用不可用")

    def test_valid_query(self):
        """测试有效的Cypher查询"""
        url = f"{self.BASE_URL}{self.NEO4J_ENDPOINT}"
        headers = {'Content-Type': 'application/json'}
        data = {'query': self.valid_query}

        print(f"\n测试有效查询: {self.valid_query}")
        response = requests.post(url, headers=headers, data=json.dumps(data))

        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        self.assertEqual(response.status_code, 200)

        try:
            response_data = response.json()
            self.assertIn('success', response_data)
            self.assertTrue(response_data['success'])
            self.assertIn('data', response_data)
        except json.JSONDecodeError:
            self.fail("响应不是有效的JSON格式")

    # 其他测试方法保持不变...


if __name__ == '__main__':
    unittest.main()
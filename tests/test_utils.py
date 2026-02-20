"""
测试工具和辅助函数
"""
import json
import tempfile
import os

def create_test_config():
    """创建测试配置文件"""
    config = {
        'database': {
            'url': 'sqlite:///test.db',
            'echo': False
        },
        'server': {
            'host': '127.0.0.1',
            'port': 8000
        },
        'ai': {
            'enabled': False,
            'model': 'test-model'
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        return f.name

def cleanup_test_files(*files):
    """清理测试文件"""
    for file_path in files:
        if os.path.exists(file_path):
            os.unlink(file_path)

def assert_dict_contains(expected, actual):
    """断言字典包含关系"""
    for key, value in expected.items():
        assert key in actual, f"Key '{key}' not found in actual dict"
        if isinstance(value, dict):
            assert_dict_contains(value, actual[key])
        else:
            assert actual[key] == value, f"Value mismatch for key '{key}': expected {value}, got {actual[key]}"
"""
Pytest 配置和夹具
"""
import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def test_data_dir():
    """测试数据目录夹具"""
    test_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(test_dir, exist_ok=True)
    return test_dir

@pytest.fixture
def sample_feed_data():
    """示例订阅源数据夹具"""
    return {
        'name': '测试订阅源',
        'url': 'https://example.com/rss',
        'category': '技术',
        'interval': 3600
    }

@pytest.fixture
def sample_article_data():
    """示例文章数据夹具"""
    return {
        'title': '测试文章标题',
        'url': 'https://example.com/article',
        'content': '这是测试文章内容',
        'summary': '测试文章摘要',
        'feed_id': 1
    }
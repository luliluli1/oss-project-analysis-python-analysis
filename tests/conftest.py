import pytest
import sys
from pathlib import Path
import pandas as pd

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置测试数据目录
TEST_DATA_DIR = project_root / "tests" / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)

@pytest.fixture
def sample_commits():
    """生成示例提交数据"""
    return [
        {
            'commit_hash': 'abc123',
            'author': 'John Doe',
            'date': '2025-01-11 10:30:00',
            'message': 'Fix bug in data collection',
            'lines_added': 45,
            'lines_deleted': 12,
            'files_changed': 3
        },
        {
            'commit_hash': 'def456', 
            'author': 'Jane Smith',
            'date': '2025-01-11 14:45:00',
            'message': 'Add visualization feature',
            'lines_added': 120,
            'lines_deleted': 5,
            'files_changed': 4
        }
    ]

# 新增 fixture
@pytest.fixture
def sample_dataframe(sample_commits):
    """创建示例DataFrame"""
    return pd.DataFrame(sample_commits)

@pytest.fixture
def output_dir(tmp_path):
    """创建临时输出目录"""
    output_dir = tmp_path / "analysis_output"
    output_dir.mkdir()
    return str(output_dir)
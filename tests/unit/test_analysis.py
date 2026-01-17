import pytest
import pandas as pd
from pathlib import Path
import shutil
import os
from src.analysis import analyze_commit_patterns

class TestAnalysis:
    def setup_method(self):
        """为每个测试创建临时目录"""
        self.test_output_dir = Path("temp_test_output")
        self.test_output_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """清理测试文件"""
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir)
    
    def test_analyze_commit_patterns_basic(self):
        """测试基本的提交模式分析功能"""
        # 创建测试数据
        test_data = pd.DataFrame({
            'commit_hash': ['abc123', 'def456', 'ghi789'],
            'author': ['Alice', 'Bob', 'Charlie'],
            'date': ['2025-01-11 10:30:00', '2025-01-12 14:45:00', '2025-01-13 09:15:00'],
            'message': ['Fix bug', 'Add feature', 'Update docs'],
            'lines_added': [5, 10, 2],
            'lines_deleted': [2, 3, 1]
        })
        
        # 运行分析
        result = analyze_commit_patterns(
            test_data, 
            output_dir=str(self.test_output_dir)
        )
        
        # 验证结果
        assert "weekday_distribution" in result
        assert "total_commits" in result
        assert "output_directory" in result
        
        # 验证文件生成（使用 Path 对象）
        expected_file = self.test_output_dir / "weekday_distribution.png"
        
        # 调试信息
        print(f"Expected file path: {expected_file}")
        print(f"File exists: {expected_file.exists()}")
        if expected_file.exists():
            print(f"File size: {expected_file.stat().st_size} bytes")
        
        # 断言文件存在
        assert expected_file.exists(), f"文件未生成: {expected_file}"
        assert expected_file.stat().st_size > 0, "文件为空"
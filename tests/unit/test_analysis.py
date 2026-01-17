import pytest
import pandas as pd
import os
from pathlib import Path
import tempfile
import shutil
from src.analysis import analyze_commit_patterns

class TestAnalysis:
    def setup_method(self):
        """为每个测试创建临时目录"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_output_dir = self.test_dir / "output"
        self.test_output_dir.mkdir(exist_ok=True)
        
        # 创建测试数据文件
        self.test_data_path = self.test_dir / "test_commits.csv"
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'commit_hash': ['abc123', 'def456', 'ghi789'],
            'author': ['Alice', 'Bob', 'Charlie'],
            'date': ['2025-01-11 10:30:00', '2025-01-12 14:45:00', '2025-01-13 09:15:00'],
            'message': ['Fix bug', 'Add feature', 'Update docs'],
            'lines_added': [5, 10, 2],
            'lines_deleted': [2, 3, 1],
            'files_changed': [1, 2, 1]
        })
        
        # 保存为CSV文件
        test_data.to_csv(str(self.test_data_path), index=False)
    
    def teardown_method(self):
        """清理测试文件"""
        if self.test_dir.exists():
            shutil.rmtree(str(self.test_dir))
    
    def test_analyze_commit_patterns_basic(self):
        """测试基本的提交模式分析功能"""
        print(f"\n🔍 测试路径信息:")
        print(f"测试数据文件: {self.test_data_path.resolve()}")
        print(f"输出目录: {self.test_output_dir.resolve()}")
        
        # 正确调用：传入文件路径字符串，而不是DataFrame
        result = analyze_commit_patterns(
            str(self.test_data_path),  # 文件路径
            str(self.test_output_dir)  # 输出目录
        )
        
        # 验证结果
        assert isinstance(result, pd.DataFrame), "应返回DataFrame"
        assert len(result) > 0, "DataFrame不应为空"
        
        # 验证生成的文件
        expected_files = [
            "weekday_distribution.png",
            "hourly_distribution.png", 
            "contributors_distribution.png",
            "monthly_trends.png",
            "message_types_pie.png",
            "analysis_report.md",
            "processed_data.csv",
            "summary.txt"
        ]
        
        for filename in expected_files:
            file_path = self.test_output_dir / filename
            assert file_path.exists(), f"文件未生成: {filename}"
            assert file_path.stat().st_size > 0, f"文件为空: {filename}"
            print(f"✅ 验证: {filename} (大小: {file_path.stat().st_size} bytes)")
        
        print(f"\n🎉 测试通过! 生成了 {len(list(self.test_output_dir.iterdir()))} 个文件")
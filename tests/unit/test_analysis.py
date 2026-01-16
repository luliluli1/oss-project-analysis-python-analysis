import pytest
import pandas as pd
import matplotlib.pyplot as plt
import os
import tempfile
from src.analysis import analyze_commit_patterns

class TestAnalysis:
    
    def test_analyze_commit_patterns_basic(self, sample_dataframe, output_dir):
        """测试基本分析功能 - 移除monkeypatch"""
        # 创建独立的输入目录
        input_dir = tempfile.mkdtemp()
        input_path = os.path.join(input_dir, "test_data.csv")
        sample_dataframe.to_csv(input_path, index=False)
        
        # 运行分析（不使用monkeypatch）
        result = analyze_commit_patterns(input_path, output_dir)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        
        # 验证关键文件生成
        expected_files = [
            'weekday_distribution.png',
            'hourly_distribution.png',
            'contributors_distribution.png',
            'monthly_trends.png',
            'message_types_pie.png',
            'analysis_report.md',
            'processed_data.csv'
        ]
        
        # 验证输出目录内容
        print("\n🔍 验证输出目录内容:")
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"   📄 {file} (大小: {os.path.getsize(file_path)} bytes)")
        
        for file in expected_files:
            file_path = os.path.join(output_dir, file)
            assert os.path.exists(file_path), f"文件 {file} 未生成，路径: {file_path}"
            assert os.path.getsize(file_path) > 0, f"文件 {file} 为空，路径: {file_path}"
    
    def test_invalid_date_handling(self, sample_dataframe, output_dir):
        """测试无效日期处理"""
        # 创建独立的输入目录
        input_dir = tempfile.mkdtemp()
        input_path = os.path.join(input_dir, "invalid_dates.csv")
        
        # 修改一条记录的日期为无效值
        sample_dataframe.at[0, 'date'] = 'invalid-date'
        sample_dataframe.to_csv(input_path, index=False)
        
        # 运行分析
        result = analyze_commit_patterns(input_path, output_dir)
        
        # 验证无效日期被修复
        assert len(result) == 2
        assert not pd.isna(result.iloc[0]['date'])
        assert result.iloc[0]['date'].year == 2025
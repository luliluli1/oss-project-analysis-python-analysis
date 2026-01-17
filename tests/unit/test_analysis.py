import pytest
import pandas as pd
import os
from pathlib import Path
import tempfile
import shutil
import matplotlib
matplotlib.use('Agg')  # 确保使用非交互式后端

from src.analysis import analyze_commit_patterns

class TestAnalysis:
    """
    测试分析模块的核心功能
    """
    
    def setup_method(self):
        """为每个测试创建隔离的临时环境"""
        # 创建临时目录
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_output_dir = self.test_dir / "output"
        self.test_output_dir.mkdir(exist_ok=True)
        
        # 创建测试数据文件
        self.test_data_path = self.test_dir / "test_commits.csv"
        
        # 创建包含必要列的测试数据
        test_data = pd.DataFrame({
            'commit_hash': ['abc123', 'def456', 'ghi789', 'jkl012', 'mno345'],
            'author': ['Alice', 'Bob', 'Charlie', 'Alice', 'David'],
            'date': [
                '2025-01-11 10:30:00',
                '2025-01-12 14:45:00', 
                '2025-01-13 09:15:00',
                '2025-01-13 16:20:00',
                '2025-01-14 11:05:00'
            ],
            'message': [
                'Fix bug in authentication flow',
                'Add feature: user profile page',
                'Update documentation for API endpoints',
                'Refactor database connection logic',
                'Improve error handling in request module'
            ],
            'lines_added': [15, 42, 8, 23, 17],
            'lines_deleted': [3, 5, 2, 11, 4],
            'files_changed': [2, 3, 1, 4, 2]
        })
        
        # 保存为CSV文件
        test_data.to_csv(str(self.test_data_path), index=False)
        
        print(f"\n🧪 测试环境设置:")
        print(f"临时目录: {self.test_dir}")
        print(f"测试数据文件: {self.test_data_path}")
        print(f"输出目录: {self.test_output_dir}")
    
    def teardown_method(self):
        """清理测试环境"""
        try:
            if self.test_dir.exists():
                # 关闭所有matplotlib图形
                import matplotlib.pyplot as plt
                plt.close('all')
                # 递归删除临时目录
                shutil.rmtree(str(self.test_dir), ignore_errors=True)
            print("🧹 测试环境已清理")
        except Exception as e:
            print(f"⚠️  清理测试环境时出错: {str(e)}")
    
    def test_analyze_commit_patterns_basic(self):
        """测试基本的提交模式分析功能"""
        print(f"\n🔍 运行分析功能测试...")
        
        try:
            # 正确调用：传入文件路径字符串
            result = analyze_commit_patterns(
                str(self.test_data_path),  # 文件路径
                str(self.test_output_dir)  # 输出目录
            )
            
            # 验证返回结果
            assert isinstance(result, pd.DataFrame), "应返回DataFrame对象"
            assert len(result) > 0, "返回的DataFrame不应为空"
            print(f"✅ 分析成功完成，处理了 {len(result)} 条记录")
            
            # 验证生成的文件
            self._verify_generated_files()
            
        except Exception as e:
            print(f"❌ 分析执行失败: {str(e)}")
            # 检查输出目录内容
            if self.test_output_dir.exists():
                print("\n📁 输出目录内容:")
                for item in self.test_output_dir.iterdir():
                    print(f"  - {item.name} (大小: {item.stat().st_size} 字节)")
            raise
    
    def _verify_generated_files(self):
        """验证生成的文件"""
        print("\n✅ 验证生成的文件:")
        
        # 关键文件（必须存在）
        critical_files = [
            ("analysis_report.md", "Markdown分析报告"),
            ("processed_data.csv", "处理后的数据文件"),
            ("summary.txt", "摘要文件")
        ]
        
        # 图表文件（可能部分失败，但至少应生成大部分）
        chart_files = [
            ("weekday_distribution.png", "星期分布图"),
            ("hourly_distribution.png", "小时分布图"),
            ("contributors_distribution.png", "贡献者分布图"),
            ("monthly_trends.png", "月度趋势图"),
            ("message_types_pie.png", "提交消息类型分布图"),
            ("code_structure_analysis.png", "代码结构分析图")
        ]
        
        # 验证关键文件
        critical_failures = 0
        for filename, description in critical_files:
            file_path = self.test_output_dir / filename
            if file_path.exists() and file_path.stat().st_size > 0:
                print(f"  ✅ {description}: {filename} (大小: {file_path.stat().st_size} 字节)")
            else:
                print(f"  ❌ {description} 未生成或为空: {filename}")
                critical_failures += 1
        
        assert critical_failures == 0, f"关键文件验证失败: {critical_failures} 个文件未生成"
        
        # 验证图表文件
        successful_charts = 0
        failed_charts = []
        
        for filename, description in chart_files:
            file_path = self.test_output_dir / filename
            if file_path.exists() and file_path.stat().st_size > 1000:  # 图表应大于1KB
                print(f"  ✅ {description}: {filename} (大小: {file_path.stat().st_size} 字节)")
                successful_charts += 1
            else:
                status = "不存在" if not file_path.exists() else "文件过小"
                print(f"  ⚠️  {description} 未成功生成: {filename} ({status})")
                failed_charts.append((filename, description))
        
        # 检查图表生成率
        success_rate = successful_charts / len(chart_files)
        print(f"\n📊 图表生成统计: {successful_charts}/{len(chart_files)} ({success_rate:.1%})")
        
        # 至少60%的图表应成功生成
        assert success_rate >= 0.6, (
            f"图表生成率过低: {success_rate:.1%} (<60%)\n"
            f"失败的图表: {', '.join([desc for _, desc in failed_charts])}"
        )
        
        # 特别验证核心图表
        core_charts = ["weekday_distribution.png", "hourly_distribution.png"]
        for chart in core_charts:
            chart_path = self.test_output_dir / chart
            assert chart_path.exists() and chart_path.stat().st_size > 1000, (
                f"核心图表未生成: {chart}"
            )
        
        print(f"🎉 所有文件验证通过! 总共生成了 {len(list(self.test_output_dir.iterdir()))} 个文件")

    def test_analysis_with_minimal_data(self):
        """测试使用最小数据集的分析功能"""
        print("\n🔍 测试最小数据集分析...")
        
        # 创建最小测试数据
        minimal_data = pd.DataFrame({
            'commit_hash': ['min123'],
            'author': ['TestUser'],
            'date': ['2025-01-15 08:30:00'],
            'message': ['Minimal test commit'],
            'lines_added': [1],
            'lines_deleted': [0],
            'files_changed': [1]
        })
        
        minimal_path = self.test_dir / "minimal_test.csv"
        minimal_data.to_csv(str(minimal_path), index=False)
        
        output_dir = self.test_dir / "minimal_output"
        output_dir.mkdir(exist_ok=True)
        
        try:
            result = analyze_commit_patterns(
                str(minimal_path),
                str(output_dir)
            )
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            
            # 验证至少生成了关键文件
            required_files = ["analysis_report.md", "processed_data.csv"]
            for filename in required_files:
                file_path = output_dir / filename
                assert file_path.exists(), f"关键文件未生成: {filename}"
                assert file_path.stat().st_size > 0, f"文件为空: {filename}"
            
            print("✅ 最小数据集测试通过")
            
        except Exception as e:
            print(f"❌ 最小数据集测试失败: {str(e)}")
            if output_dir.exists():
                print("\n📁 最小数据集输出内容:")
                for item in output_dir.iterdir():
                    print(f"  - {item.name} (大小: {item.stat().st_size} 字节)")
            raise
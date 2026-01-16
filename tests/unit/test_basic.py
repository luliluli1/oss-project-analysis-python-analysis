import pytest

def test_basic_math():
    """验证测试环境是否正常工作"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6

def test_import_analysis():
    """验证可以导入分析模块"""
    from src.analysis import analyze_commit_patterns
    assert callable(analyze_commit_patterns)
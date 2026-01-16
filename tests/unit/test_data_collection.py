import pytest
from src.data_collection import collect_commit_data
import pandas as pd
import os

def test_sample_data(sample_commits):
    """测试 sample_commits fixture 是否正常工作"""
    assert len(sample_commits) == 2
    assert sample_commits[0]['author'] == 'John Doe'
    assert sample_commits[1]['lines_added'] == 120
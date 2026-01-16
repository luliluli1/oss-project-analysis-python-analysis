import git
import pandas as pd
from datetime import datetime
import os
import subprocess
import sys
from tqdm import tqdm

def collect_commit_data(repo_path, output_path):
    """
    收集Git仓库的提交历史数据（主函数）
    
    Args:
        repo_path (str): 仓库路径
        output_path (str): 输出CSV文件路径
    
    Returns:
        pd.DataFrame: 包含提交数据的DataFrame
    """
    return collect_commit_data_robust(repo_path, output_path)

def collect_commit_data_robust(repo_path, output_path):
    """
    健壮的提交数据收集函数，处理浅层克隆限制
    """
    print(f"🔍 正在分析仓库: {os.path.abspath(repo_path)}")
    repo = git.Repo(repo_path)
    
    # 使用 git log 命令直接获取数据（比 commit.stats 更可靠）
    print("📊 获取提交历史数据...")
    try:
        log_output = subprocess.check_output([
            'git', '-C', repo_path, 'log', '--format=%H|%an|%ad|%s', 
            '--date=iso', '--numstat', '--no-renames', '-n', '1128'
        ], stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
    except subprocess.CalledProcessError as e:
        print(f"❌ git 命令执行失败: {e}")
        print(f"错误输出: {e.output.decode('utf-8', errors='ignore')}")
        raise
    
    # 解析 git log 输出
    commits = []
    current_commit = {}
    file_changes = []
    
    for line in tqdm(log_output.split('\n'), desc="处理提交"):
        if not line.strip():
            continue
            
        # 提交行: hash|author|date|message
        if '|' in line and not '\t' in line and len(line.split('|')) >= 4:
            if current_commit and 'hash' in current_commit:
                # 计算统计信息
                current_commit['lines_added'] = sum(fc['added'] for fc in file_changes)
                current_commit['lines_deleted'] = sum(fc['deleted'] for fc in file_changes)
                current_commit['files_changed'] = len(file_changes)
                commits.append(current_commit)
            
            parts = line.strip().split('|')
            current_commit = {
                'hash': parts[0],
                'commit_hash': parts[0][:7],
                'author': parts[1],
                'date': parts[2].replace(' +0000', ''),  # 移除时区
                'message': parts[3][:80] if len(parts) > 3 else "无提交信息"
            }
            file_changes = []
        
        # 文件变更行: added deleted filename
        elif '\t' in line:
            parts = line.strip().split('\t')
            if len(parts) >= 3 and parts[0] and parts[1]:
                try:
                    # 处理二进制文件或重命名情况
                    if parts[0] == '-' or parts[1] == '-':
                        added = 0
                        deleted = 0
                    else:
                        added = int(parts[0]) if parts[0].isdigit() else 0
                        deleted = int(parts[1]) if parts[1].isdigit() else 0
                    
                    file_changes.append({
                        'added': added,
                        'deleted': deleted,
                        'filename': parts[2]
                    })
                except (ValueError, IndexError):
                    # 跳过无法解析的行
                    continue
    
    # 处理最后一个提交
    if current_commit and 'hash' in current_commit:
        current_commit['lines_added'] = sum(fc['added'] for fc in file_changes)
        current_commit['lines_deleted'] = sum(fc['deleted'] for fc in file_changes)
        current_commit['files_changed'] = len(file_changes)
        commits.append(current_commit)
    
    print(f"\n✅ 成功收集 {len(commits)} 条提交记录!")
    
    # 创建DataFrame
    df = pd.DataFrame(commits)
    
    # 保存数据
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"💾 数据已保存至: {os.path.abspath(output_path)}")
    
    return df

def collect_commit_data_safe(repo_path, output_path):
    """
    安全模式：跳过有问题的提交
    """
    print(f"🔍 正在分析仓库: {os.path.abspath(repo_path)}")
    repo = git.Repo(repo_path)
    commits = list(repo.iter_commits('main', max_count=1128))
    
    data = []
    skipped = 0
    
    print("收集提交数据中 (安全模式)...")
    for i, commit in enumerate(tqdm(commits, desc="处理提交"), 1):
        try:
            # 尝试获取统计信息
            try:
                stats = commit.stats
                insertions = stats.total['insertions']
                deletions = stats.total['deletions']
                files_changed = stats.total['files']
            except Exception as e:
                # 备用方法：使用 git 命令获取统计
                stats_output = repo.git.show(commit.hexsha, '--numstat', '--format=')
                lines = stats_output.strip().split('\n')
                insertions = 0
                deletions = 0
                files_changed = 0
                
                for line in lines:
                    if not line.strip():
                        continue
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        try:
                            if parts[0] != '-':
                                insertions += int(parts[0])
                            if parts[1] != '-':
                                deletions += int(parts[1])
                            files_changed += 1
                        except ValueError:
                            continue
            
            # 转换日期
            commit_time = datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S')
            
            data.append({
                'commit_hash': commit.hexsha[:7],
                'author': commit.author.name,
                'date': commit_time,
                'message': commit.message.strip().split('\n')[0][:80],
                'lines_added': insertions,
                'lines_deleted': deletions,
                'files_changed': files_changed
            })
        except Exception as e:
            skipped += 1
            if skipped <= 5:  # 只显示前5个错误
                print(f"⚠️ 跳过提交 {commit.hexsha[:7]}: {str(e)}")
            continue
    
    if skipped > 0:
        print(f"🟡 跳过了 {skipped} 个有问题的提交")
    
    print(f"\n✅ 成功收集 {len(data)} 条提交记录!")
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 保存数据
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"💾 数据已保存至: {os.path.abspath(output_path)}")
    
    return df

if __name__ == "__main__":
    # 配置路径
    REPO_PATH = "data/repos/requests"  # 从项目根目录运行
    OUTPUT_PATH = "data/processed/requests_commits.csv"
    
    # 选择收集方法
    print("="*50)
    print("选择数据收集方法:")
    print("1. 健壮模式 (推荐) - 使用 git log 命令，最可靠")
    print("2. 安全模式 - 跳过有问题的提交")
    choice = input("请选择 (1/2): ").strip() or "1"
    
    if choice == "1":
        collect_commit_data_robust(REPO_PATH, OUTPUT_PATH)
    else:
        collect_commit_data_safe(REPO_PATH, OUTPUT_PATH)
import git
import os
import shutil

def setup_requests_repo():
    """在运行时克隆 requests 仓库（而非作为子模块）"""
    repo_path = "data/repos/requests"
    
    if os.path.exists(repo_path):
        print(f"✅ requests 仓库已存在，跳过克隆")
        return
    
    print("🔄 克隆 requests 仓库 (使用特殊参数)...")
    os.makedirs(os.path.dirname(repo_path), exist_ok=True)
    
    # 使用从知识库获取的特殊参数
    repo = git.Repo.clone_from(
        "https://github.com/psf/requests.git",
        repo_path,
        config='fetch.fsck.badTimezone=ignore',  # 修复时间戳问题
        depth=300  # 仅克隆最近300次提交
    )
    
    print(f"✅ 克隆成功! 提交数量: {len(list(repo.iter_commits()))}")
    return repo

if __name__ == "__main__":
    setup_requests_repo()
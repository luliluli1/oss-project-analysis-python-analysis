import git
import os
import sys
import subprocess

def setup_requests_repo():
    """Clone requests repository at runtime with knowledge base parameter"""
    repo_path = "data/repos/requests"
    
    if os.path.exists(repo_path):
        print("INFO: requests repository already exists, skipping clone")
        return
    
    print("INFO: Cloning requests repository with knowledge base parameter...")
    
    os.makedirs(repo_path, exist_ok=True)
    
    try:
        # 使用 subprocess 直接调用 git 命令（100% 兼容知识库要求）
        print("EXECUTING: git clone -c fetch.fsck.badTimezone=ignore --depth=300 https://github.com/psf/requests.git data/repos/requests")
        result = subprocess.run([
            'git', 'clone', 
            '-c', 'fetch.fsck.badTimezone=ignore',  # 知识库要求的精确参数
            '--depth=300', 
            'https://github.com/psf/requests.git', 
            repo_path
        ], capture_output=True, text=True, check=True)
        
        print(f"SUCCESS: {result.stdout}")
        print(f"DEBUG: Repository cloned successfully to {repo_path}")
        
        # 验证克隆结果
        if os.path.exists(os.path.join(repo_path, '.git')):
            print("SUCCESS: Git repository structure verified")
            return True
        else:
            print("ERROR: Repository structure verification failed")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git clone failed with exit code {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        print("TROUBLESHOOTING:")
        print("1. Check Git installation: git --version")
        print("2. Verify network connectivity to github.com")
        print("3. Ensure sufficient disk space")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_requests_repo()
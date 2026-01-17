import git
import os
import sys

def setup_requests_repo():
    """Clone requests repository at runtime"""
    repo_path = "data/repos/requests"
    
    if os.path.exists(repo_path):
        print("INFO: requests repository already exists, skipping clone")
        return
    
    print("INFO: Cloning requests repository with special parameters...")
    
    os.makedirs(repo_path, exist_ok=True)
    
    try:
        # Apply special parameter from documentation to handle bad timestamp
        repo = git.Repo.clone_from(
            "https://github.com/psf/requests.git",
            repo_path,
            config={'fetch.fsck.badTimezone': 'ignore'},
            depth=300
        )
        commit_count = len(list(repo.iter_commits()))
        print(f"SUCCESS: Clone successful! Commit count: {commit_count}")
        return repo
    except Exception as e:
        print(f"ERROR: Clone failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_requests_repo()
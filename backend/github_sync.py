"""
GitHub Auto-Sync Service
Automatically commits and pushes progress data to GitHub for persistence
"""
import os
import json
import subprocess
from datetime import datetime

class GitHubSync:
    """Sync progress data to GitHub for persistence across deployments"""
    
    def __init__(self):
        self.repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.progress_file = os.path.join(self.repo_path, 'backend', 'progress_data.json')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO', 'GateLogX/GATE-DAYWISE-TRACKER')
        
    def configure_git(self):
        """Configure git with credentials"""
        try:
            # Set git user
            subprocess.run(['git', 'config', 'user.email', 'bot@gatetracker.com'], 
                         cwd=self.repo_path, check=True)
            subprocess.run(['git', 'config', 'user.name', 'GATE Tracker Bot'], 
                         cwd=self.repo_path, check=True)
            
            # Set remote with token
            if self.github_token:
                remote_url = f'https://{self.github_token}@github.com/{self.github_repo}.git'
                subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], 
                             cwd=self.repo_path, check=False)
            
            return True
        except Exception as e:
            print(f"Git config error: {e}")
            return False
    
    def pull_latest(self):
        """Pull latest progress from GitHub"""
        try:
            if not self.github_token:
                print("No GitHub token - skipping pull")
                return False
                
            self.configure_git()
            
            # Pull latest changes
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main', '--rebase'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ Pulled latest progress from GitHub")
                return True
            else:
                print(f"Pull warning: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Pull error: {e}")
            return False
    
    def commit_and_push(self, message="Update progress via WhatsApp"):
        """Commit and push progress to GitHub"""
        try:
            if not self.github_token:
                print("⚠️ No GitHub token - progress will be lost on redeploy!")
                return False
            
            self.configure_git()
            
            # Check if file exists and has changes
            if not os.path.exists(self.progress_file):
                print("No progress file to commit")
                return False
            
            # Add progress file
            subprocess.run(['git', 'add', 'backend/progress_data.json'], 
                         cwd=self.repo_path, check=True)
            
            # Check if there are changes
            status = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd=self.repo_path, capture_output=True, text=True)
            
            if not status.stdout.strip():
                print("No changes to commit")
                return True
            
            # Commit
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f"{message} - {timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], 
                         cwd=self.repo_path, check=True, capture_output=True)
            
            # Push
            result = subprocess.run(
                ['git', 'push', 'origin', 'main'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                print(f"✅ Pushed progress to GitHub: {commit_msg}")
                return True
            else:
                print(f"Push error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("Push timeout - GitHub might be slow")
            return False
        except Exception as e:
            print(f"Commit/push error: {e}")
            return False
    
    def sync_progress(self):
        """Full sync: pull then push"""
        self.pull_latest()
        return self.commit_and_push()

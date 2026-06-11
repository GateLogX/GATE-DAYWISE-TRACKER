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
        self.git_initialized = False
        
    def init_git_repo(self):
        """Initialize git repository if not exists (for Render deployment)"""
        try:
            if not self.github_token:
                print("⚠️ No GITHUB_TOKEN - cannot initialize git sync")
                return False
            
            # Check if .git exists
            git_dir = os.path.join(self.repo_path, '.git')
            git_exists = os.path.exists(git_dir)
            
            if git_exists:
                print("📦 Git directory exists, configuring remote...")
            else:
                print("📦 Initializing new git repository...")
                # Initialize git repo
                result = subprocess.run(['git', 'init'], cwd=self.repo_path, 
                                      check=True, capture_output=True, text=True)
                print("   ✓ Git init complete")
            
            print(f"   Repo path: {self.repo_path}")
            print(f"   Remote: {self.github_repo}")
            
            # Configure git user
            subprocess.run(['git', 'config', 'user.email', 'bot@gatetracker.com'], 
                         cwd=self.repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'GATE Tracker Bot'], 
                         cwd=self.repo_path, check=True, capture_output=True)
            print("   ✓ Git config complete")
            
            # Check if remote exists, remove if it does
            check_remote = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                        cwd=self.repo_path, capture_output=True)
            if check_remote.returncode == 0:
                print("   Removing existing remote...")
                subprocess.run(['git', 'remote', 'remove', 'origin'], 
                             cwd=self.repo_path, capture_output=True)
            
            # Add remote with token (hide token in logs)
            remote_url = f'https://{self.github_token}@github.com/{self.github_repo}.git'
            result = subprocess.run(['git', 'remote', 'add', 'origin', remote_url], 
                         cwd=self.repo_path, check=True, capture_output=True, text=True)
            print("   ✓ Remote added")
            
            # Fetch from remote
            print("   Fetching from GitHub...")
            result = subprocess.run(['git', 'fetch', 'origin', 'main'], cwd=self.repo_path, 
                         check=True, capture_output=True, text=True, timeout=30)
            print("   ✓ Fetch complete")
            
            # Check current branch
            check_branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                        cwd=self.repo_path, capture_output=True, text=True)
            current_branch = check_branch.stdout.strip() if check_branch.returncode == 0 else ""
            
            if current_branch != 'main':
                # Checkout or create main branch
                result = subprocess.run(['git', 'checkout', '-B', 'main', 'origin/main'], 
                             cwd=self.repo_path, check=True, capture_output=True, text=True)
                print("   ✓ Checked out main branch")
            else:
                # Reset to match remote
                subprocess.run(['git', 'reset', '--hard', 'origin/main'], 
                             cwd=self.repo_path, check=True, capture_output=True, text=True)
                print("   ✓ Reset to origin/main")
            
            self.git_initialized = True
            print("✅ Git repository initialized successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git init error: {e}")
            print(f"   stdout: {e.stdout if hasattr(e, 'stdout') else 'N/A'}")
            print(f"   stderr: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
            return False
        except Exception as e:
            print(f"⚠️ Git init unexpected error: {e}")
            return False
        
    def configure_git(self):
        """Configure git with credentials"""
        try:
            # Initialize git if needed
            if not self.git_initialized:
                self.init_git_repo()
            
            # Set git user
            subprocess.run(['git', 'config', 'user.email', 'bot@gatetracker.com'], 
                         cwd=self.repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'GATE Tracker Bot'], 
                         cwd=self.repo_path, check=True, capture_output=True)
            
            # Update remote URL with token
            if self.github_token:
                remote_url = f'https://{self.github_token}@github.com/{self.github_repo}.git'
                subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], 
                             cwd=self.repo_path, check=False, capture_output=True)
            
            return True
        except Exception as e:
            print(f"Git config error: {e}")
            return False
    
    def pull_latest(self):
        """Pull latest progress from GitHub"""
        try:
            if not self.github_token:
                print("⚠️ No GitHub token - skipping pull (set GITHUB_TOKEN env var)")
                return False
            
            print("🔄 Attempting to pull latest progress from GitHub...")
            
            # Initialize git if needed
            if not self.git_initialized:
                print("📦 Git not initialized yet, initializing now...")
                if not self.init_git_repo():
                    print("⚠️ Could not initialize git - will work with local file only")
                    return False
            
            self.configure_git()
            
            # Reset any local changes first (in case of conflicts)
            subprocess.run(['git', 'reset', '--hard'], cwd=self.repo_path, 
                         capture_output=True, timeout=10)
            
            # Pull latest changes
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main', '--rebase'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully pulled latest progress from GitHub")
                return True
            else:
                print(f"⚠️ Pull warning (non-fatal): {result.stderr.strip()}")
                # Not a fatal error - continue with local file
                return False
                
        except Exception as e:
            print(f"⚠️ Pull error (non-fatal): {e}")
            # Not a fatal error - backend will continue with local file
            return False
    
    def commit_and_push(self, message="Update progress via WhatsApp"):
        """Commit and push progress to GitHub (only progress_data.json to avoid deployment loops)"""
        try:
            if not self.github_token:
                print("⚠️ No GitHub token - progress will be lost on redeploy!")
                return False
            
            self.configure_git()
            
            # Only add progress_data.json (NOT app_data.json to avoid deployment loops)
            subprocess.run(['git', 'add', 'backend/progress_data.json'], 
                         cwd=self.repo_path, check=True)
            
            # Check if there are changes
            status = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd=self.repo_path, capture_output=True, text=True)
            
            if not status.stdout.strip():
                print("No changes to commit")
                return True
            
            # Commit with [skip ci] to prevent Render auto-deploy
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f"{message} - {timestamp} [skip ci]"
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
                print(f"✅ Pushed to GitHub: {commit_msg}")
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

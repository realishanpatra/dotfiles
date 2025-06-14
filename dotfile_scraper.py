import os
import re
import shutil
import tempfile
import praw
from git import Repo

# === Reddit API Credentials ===
REDDIT_CLIENT_ID = 'SK_0AKF_jE_KCy7SHZbDWw'
REDDIT_CLIENT_SECRET = 'mYZQRljR-FLu-8EVvXbtfYa4gskBIQ'
REDDIT_USER_AGENT = 'dotfile_collector by /u/realishanpatra'

# === Settings ===
SUBREDDITS = ['unixporn', 'dotfiles']
NUM_POSTS = 100
SAVE_DIR = 'newcollected'

# Dotfile patterns to collect
DOTFILE_PATTERNS = [
    '.zshrc', '.bashrc', '.vimrc', '.xinitrc', '.Xresources', '.tmux.conf',
    '.config', '.profile', '.aliases', '.gitconfig', '.i3', '.bspwm', '.nvim'
]

def extract_github_links(text):
    return re.findall(r'(https?://github\.com/[^\s/]+/[^\s/]+)', text)

def is_dotfile(filepath):
    return any(pattern in filepath for pattern in DOTFILE_PATTERNS)

def clone_and_copy(repo_url):
    try:
        temp_dir = tempfile.mkdtemp()
        Repo.clone_from(repo_url, temp_dir)

        repo_name = repo_url.rstrip('/').split('/')[-1]
        save_path = os.path.join(SAVE_DIR, repo_name)
        os.makedirs(save_path, exist_ok=True)

        copied = False
        for root, _, files in os.walk(temp_dir):
            for name in files:
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, temp_dir)

                if is_dotfile(rel_path) and os.path.getsize(full_path) > 0:
                    dest_path = os.path.join(save_path, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(full_path, dest_path)
                    print(f"📄 Copied: {rel_path}")
                    copied = True
                elif is_dotfile(rel_path):
                    print(f"⚠️ Skipped empty file: {rel_path}")

        shutil.rmtree(temp_dir)
        if copied:
            print(f"✅ Done with {repo_url}")
        else:
            print(f"❌ No valid dotfiles found in {repo_url}")

    except Exception as e:
        print(f"❌ Error with {repo_url}: {e}")

def main():
    os.makedirs(SAVE_DIR, exist_ok=True)

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

    seen = set()
    for subreddit in SUBREDDITS:
        for post in reddit.subreddit(subreddit).top(limit=NUM_POSTS, time_filter='all'):
            links = extract_github_links(post.selftext + " " + post.url)
            for link in links:
                if link not in seen:
                    seen.add(link)
                    clone_and_copy(link)

    # Git commit and push
    try:
        repo = Repo('.')
        repo.git.add(A=True)
        if repo.is_dirty():
            repo.index.commit("Add new collected dotfiles from Reddit")
            repo.remote(name='origin').push()
            print("🚀 Changes pushed to GitHub!")
        else:
            print("🟰 No new changes to commit.")
    except Exception as e:
        print(f"❌ Git error: {e}")

if __name__ == '__main__':
    main()

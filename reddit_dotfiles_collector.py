import praw
import os
import re
import requests
from git import Repo
from urllib.parse import urlparse

# === Reddit API Credentials ===
REDDIT_CLIENT_ID = 'SK_0AKF_jE_KCy7SHZbDWw'
REDDIT_CLIENT_SECRET = 'mYZQRljR-FLu-8EVvXbtfYa4gskBIQ'
REDDIT_USER_AGENT = 'dotfile_collector by /u/realishanpatra'

# === GitHub Repo Config ===
REPO_URL = "https://github.com/realishanpatra/dotfiles.git"
LOCAL_REPO_PATH = os.path.expanduser("~/my_dotfiles_repo")
TARGET_FOLDER = os.path.join(LOCAL_REPO_PATH, "collected")

# === Subreddits and Patterns ===
SUBREDDITS = ["unixporn", "dotfiles", "linux"]
GITHUB_REPO_PATTERN = re.compile(r'https?://github\.com/[\w\-_]+/[\w\-_]+')
RAW_FILE_PATTERN = re.compile(r'https?://(?:gist\.githubusercontent\.com|pastebin\.com/raw)/[\w/\-]+')

# === Setup Reddit ===
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def clone_main_repo():
    if not os.path.exists(LOCAL_REPO_PATH):
        print("[+] Cloning your GitHub dotfiles repo...")
        Repo.clone_from(REPO_URL, LOCAL_REPO_PATH)
    else:
        print("[=] Repo already cloned.")
    os.makedirs(TARGET_FOLDER, exist_ok=True)

def download_raw_file(url, author):
    try:
        file_name = url.split("/")[-1]
        author_folder = os.path.join(TARGET_FOLDER, f"{author}_raw")
        os.makedirs(author_folder, exist_ok=True)
        file_path = os.path.join(author_folder, file_name)

        print(f"[+] Downloading: {url}")
        r = requests.get(url)
        if r.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(r.text)
        else:
            print(f"[-] Failed to download: {url} (HTTP {r.status_code})")
    except Exception as e:
        print(f"[-] Error: {e}")

def clone_repo(url, author):
    try:
        repo_name = urlparse(url).path.strip("/").replace("/", "_")
        repo_folder = os.path.join(TARGET_FOLDER, f"{author}_github_{repo_name}")
        if not os.path.exists(repo_folder):
            print(f"[+] Cloning repo: {url}")
            Repo.clone_from(url, repo_folder)
        else:
            print(f"[=] Repo already exists: {repo_folder}")
    except Exception as e:
        print(f"[-] Git clone failed: {url} ({e})")

def process_posts():
    for sub in SUBREDDITS:
        subreddit = reddit.subreddit(sub)
        for post in subreddit.hot(limit=30):
            if post.stickied:
                continue
            author = post.author.name if post.author else "unknown"
            text = post.selftext + " " + post.url

            for url in GITHUB_REPO_PATTERN.findall(text):
                clone_repo(url, author)

            for url in RAW_FILE_PATTERN.findall(text):
                download_raw_file(url, author)

def commit_and_push():
    try:
        repo = Repo(LOCAL_REPO_PATH)
        repo.git.add(all=True)
        if repo.is_dirty():
            repo.index.commit("Update collected dotfiles from Reddit")
            origin = repo.remote(name="origin")
            origin.push()
            print("[✓] Changes pushed to your GitHub repo.")
        else:
            print("[=] No new changes to commit.")
    except Exception as e:
        print(f"[-] Git commit/push failed: {e}")

if __name__ == "__main__":
    clone_main_repo()
    process_posts()
    commit_and_push()

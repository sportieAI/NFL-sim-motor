import subprocess
import sys

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)
    print(result.stdout)

def push_all(commit_msg):
    run_cmd('git add -A')
    run_cmd(f'git commit -m "{commit_msg}"')
    run_cmd('git push origin main')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python git_push_all.py \"Your commit message\"")
        sys.exit(1)
    push_all(sys.argv[1])

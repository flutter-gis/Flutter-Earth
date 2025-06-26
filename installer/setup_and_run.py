import os
import subprocess
import sys
from datetime import datetime

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
NODE_DIR = os.path.join(REPO_ROOT, 'node-v22.17.0-win-x64')
ELECTRON_DIR = os.path.join(REPO_ROOT, 'Flutter-Earth')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'setup_and_run.log')

COREPACK_CMD = os.path.join(NODE_DIR, 'corepack.cmd')
NPM_CMD = os.path.join(NODE_DIR, 'npm.cmd')

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def run(cmd, cwd=None, use_node_env=True, extra_env=None):
    log(f">>> Running: {' '.join(cmd)} (in {cwd or os.getcwd()})")
    env = os.environ.copy()
    if use_node_env:
        env["PATH"] = NODE_DIR + os.pathsep + env["PATH"]
        env["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"
    if extra_env:
        env.update(extra_env)
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True, env=env)
    for line in proc.stdout:
        print(line, end='')
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line)
    proc.wait()
    if proc.returncode != 0:
        log(f"ERROR: Command failed: {' '.join(cmd)}")
        sys.exit(proc.returncode)

def main():
    # Clear old log
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    log("=== Fluttershy's Gentle Earth Explorer Installer ===\n")

    # 0. Enable corepack if available
    if os.path.exists(COREPACK_CMD):
        log("Enabling corepack (for advanced package management)...")
        run([COREPACK_CMD, 'enable'], use_node_env=True)
    else:
        log("corepack.cmd not found, skipping corepack enable.")

    # 0.5. Set npm config strict-ssl false
    log("Setting npm config strict-ssl false to bypass self-signed certificate errors...")
    run([NPM_CMD, 'config', 'set', 'strict-ssl', 'false'], use_node_env=True)

    # 1. Install Python dependencies if requirements.txt exists
    req_path = os.path.join(ELECTRON_DIR, 'requirements.txt')
    if os.path.exists(req_path):
        log("Installing Python dependencies...")
        run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], cwd=ELECTRON_DIR, use_node_env=False)
    else:
        log("No requirements.txt found, skipping Python dependencies.")

    # 2. Install Node.js/Electron dependencies
    pkg_path = os.path.join(ELECTRON_DIR, 'package.json')
    if os.path.exists(pkg_path):
        log("Installing Node.js/Electron dependencies...")
        run([NPM_CMD, 'install'], cwd=ELECTRON_DIR, use_node_env=True)
    else:
        log("No package.json found, skipping Node.js/Electron dependencies.")

    # 3. Launch the Electron desktop app
    if os.path.exists(pkg_path):
        log("Launching Electron desktop app...")
        run([NPM_CMD, 'start'], cwd=ELECTRON_DIR, use_node_env=True)
    else:
        log("Cannot launch Electron app: package.json not found.")

    log("\n=== Setup complete! ===")
    input("Press Enter to exit...")

if __name__ == '__main__':
    main() 
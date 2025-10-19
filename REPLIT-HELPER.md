# REPLIT-HELPER.md

> **Complete guide for agents deploying auto-hyperflask to Replit via SSH**

This document provides step-by-step instructions for an AI agent (or developer) to deploy auto-hyperflask to Replit using only SSH credentials and the GitHub repository URL.

## 📋 Prerequisites

You need:
1. **GitHub Repository URL**: `https://github.com/realityinspector/auto-hyperflask`
2. **Replit SSH Connection String**: Format `ssh -i <key> -p 22 <uuid>@<host>.replit.dev`

Example SSH connection:
```bash
ssh -i ~/.ssh/replit -p 22 db0caf53-d121-4b66-94d5-5b829fcb7de3@db0caf53-d121-4b66-94d5-5b829fcb7de3-00-3bp1d70cttq69.worf.replit.dev
```

## 🚀 Deployment Steps

### Step 1: Connect to Replit via SSH

```bash
ssh -i ~/.ssh/replit -p 22 <uuid>@<host>.replit.dev
```

**Expected output:**
```
Linux buildroot 5.15.0 #1 SMP x86_64 GNU/Linux
Welcome to Replit!
```

**Important:** Replit SSH sessions do NOT automatically load the Nix environment. You must use `nix-shell` for all commands that require system packages.

### Step 2: Check Current Directory State

```bash
ls -la
pwd
```

If there's already content in the directory, you may need to clear it or work in a subdirectory.

### Step 3: Clone the Repository

```bash
# If directory is empty
git clone https://github.com/realityinspector/auto-hyperflask.git .

# OR if directory has content, clone to subdirectory
git clone https://github.com/realityinspector/auto-hyperflask.git auto-hyperflask
cd auto-hyperflask
```

**Verify the clone:**
```bash
ls -la
# Should see: .replit, replit.nix, shell.nix, pyproject.toml, package.json, etc.
```

### Step 4: Enter Nix Shell Environment

**CRITICAL:** All subsequent commands MUST be run inside `nix-shell` or prefixed with `nix-shell --run "command"`.

```bash
# Option 1: Enter nix-shell interactively
nix-shell

# Option 2: Run commands with nix-shell wrapper
nix-shell --run "python3 --version"
```

**Why?** The `shell.nix` file:
- Loads all system dependencies from `replit.nix`
- Sets up `LD_LIBRARY_PATH` for Playwright
- Activates Python virtual environment (if it exists)

### Step 5: Run Automated Setup

The repository includes an automated setup script that handles everything:

```bash
nix-shell --run "bash scripts/replit-setup.sh"
```

**What this does (7 steps, ~2 minutes):**
1. Creates Python virtual environment with system packages
2. Upgrades pip
3. Installs Python dependencies (including dev and e2e tools)
4. Installs Node.js dependencies
5. Builds frontend assets (JS, CSS, icons)
6. Sets up SQLite database and seeds with test data
7. Runs validation tests (unit + integration)

**Expected final output:**
```
✅ Setup complete!

🎉 AutoHyperFlask is ready to use!

📝 What's been configured:
   • Python virtual environment created
   • All dependencies installed
   • Frontend assets built (JS, CSS, icons)
   • Database initialized with test data
   • 8 validation tests passed

🔑 Test accounts (password: 'password'):
   • user1@test.com
   • user2@test.com
   • admin@test.com

🌐 Access your app:
   • Local: http://localhost:5000
   • Replit: Check the webview panel
```

### Step 6: Verify Setup

Check that the setup marker file was created:

```bash
ls -la .replit-initialized
# Should exist and be empty
```

Verify virtual environment:

```bash
nix-shell --run "source venv/bin/activate && python3 -c 'import hyperflask; print(hyperflask.__version__)'"
# Should output: 0.5.x
```

Verify database:

```bash
nix-shell --run "source venv/bin/activate && ls -lh database/app.db"
# Should show database file with size > 100KB
```

### Step 7: Start Development Server

```bash
nix-shell --run "bash scripts/replit-run.sh"
```

**OR manually:**

```bash
nix-shell
source venv/bin/activate
cp config_dev.yml config.yml
python3 -m hyperflask dev
```

**Expected output:**
```
🚀 Starting AutoHyperFlask development server...
📝 Access your app at: http://localhost:5000

 * Serving Flask app 'app'
 * Running on http://0.0.0.0:5000
```

### Step 8: Run Tests (Optional)

**Run all tests:**
```bash
nix-shell --run "source venv/bin/activate && python3 -m pytest tests/ -v"
```

**Run E2E tests only:**
```bash
nix-shell --run "source venv/bin/activate && python3 -m pytest tests/test_e2e_playwright.py -v"
```

**Skip E2E tests (faster):**
```bash
nix-shell --run "source venv/bin/activate && python3 -m pytest tests/ -v -m 'not e2e'"
```

## 🔍 Troubleshooting

### Issue: "command not found: python3"

**Cause:** Not running inside nix-shell

**Fix:**
```bash
nix-shell --run "python3 --version"
# OR enter nix-shell first
nix-shell
python3 --version
```

### Issue: "externally-managed-environment" error

**Cause:** Trying to install Python packages outside virtual environment

**Fix:** The setup script creates a venv automatically. If you need to manually install:
```bash
nix-shell --run "python3 -m venv venv --system-site-packages"
nix-shell --run "source venv/bin/activate && pip install -e ."
```

### Issue: "ImportError: libstdc++.so.6: cannot open shared object"

**Cause:** Playwright libraries not in LD_LIBRARY_PATH

**Fix:** Ensure you're using `nix-shell`, which sets LD_LIBRARY_PATH automatically via `shell.nix`

### Issue: "ModuleNotFoundError: No module named 'app'"

**Cause:** Package not installed with editable mode

**Fix:**
```bash
nix-shell --run "source venv/bin/activate && pip install -e ."
```

### Issue: "AttributeError: 'NoneType' object has no attribute 'Model'"

**Cause:** Database not initialized or app context issue

**Fix:**
```bash
nix-shell --run "source venv/bin/activate && python3 scripts/reset_db.py --seed --confirm"
```

### Issue: Playwright tests fail with missing browser

**Cause:** Chromium not installed for Playwright

**Fix:**
```bash
nix-shell --run "source venv/bin/activate && python3 -m playwright install chromium"
```

**Note:** On Replit, Chromium is provided by Nix (`replit.nix` includes `pkgs.chromium`), so this should not be necessary.

### Issue: Tests fail after setup

**Symptom:** Some tests fail on first run, especially static file routing tests

**Likely causes:**
- Assets not built correctly
- Wrong config file active
- Database not seeded

**Fix:**
```bash
# Rebuild assets
nix-shell --run "npm run build:force"

# Reset database
nix-shell --run "source venv/bin/activate && python3 scripts/reset_db.py --seed --confirm"

# Ensure dev config
cp config_dev.yml config.yml

# Re-run tests
nix-shell --run "source venv/bin/activate && python3 -m pytest tests/ -v"
```

## 📁 Key Files and Their Purpose

| File | Purpose |
|------|---------|
| `.replit` | Replit configuration (run commands, onBoot hook) |
| `replit.nix` | System dependencies (Python, Node, Chromium, etc.) |
| `shell.nix` | Nix shell environment with LD_LIBRARY_PATH setup |
| `pyproject.toml` | Python project config and dependencies |
| `package.json` | Node.js dependencies and build scripts |
| `scripts/replit-setup.sh` | Automated onboarding (first-time setup) |
| `scripts/replit-run.sh` | Development server launcher |
| `scripts/replit-deploy.sh` | Production deployment script |
| `.replit-initialized` | Marker file (created after successful setup) |

## 🔧 Advanced: Manual Setup (If Automated Script Fails)

If the automated setup script fails, you can run steps manually:

```bash
# 1. Enter nix-shell
nix-shell

# 2. Create virtual environment
python3 -m venv venv --system-site-packages
source venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install Python dependencies
pip install -e ".[dev,e2e]"

# 5. Install Node dependencies
npm install

# 6. Build assets
npm run build

# 7. Setup database
cp config_dev.yml config.yml
python3 scripts/reset_db.py --seed --confirm

# 8. Run tests
python3 -m pytest tests/test_setup.py -v

# 9. Create marker file
touch .replit-initialized

# 10. Start server
python3 -m hyperflask dev
```

## 🎯 Success Criteria

A successful deployment should have:

1. ✅ `.replit-initialized` file exists
2. ✅ `venv/` directory with Python virtual environment
3. ✅ `node_modules/` directory with npm packages
4. ✅ `public/dist/main.js` (JavaScript bundle, ~242KB)
5. ✅ `public/dist/main.css` (CSS bundle with TailwindCSS)
6. ✅ `public/bootstrap-icons/` (icon fonts)
7. ✅ `database/app.db` (SQLite database, >100KB)
8. ✅ Dev server running on port 5000
9. ✅ At least 8 unit/integration tests passing
10. ✅ Homepage accessible at http://localhost:5000

## 🌐 Accessing the App

### From SSH Session

The dev server binds to `0.0.0.0:5000`, but you can't access it directly from SSH.

**Options:**
1. **Replit Webview**: If this Repl has webview enabled, Replit will automatically proxy port 5000
2. **Port Forwarding**: Use SSH tunneling (if your SSH client supports it)
3. **Replit UI**: Open the Repl in Replit's web interface to access the webview

### Test Accounts

All test accounts use password: `password`

- `user1@test.com` - Regular user with timeline entries
- `user2@test.com` - Regular user with timeline entries
- `admin@test.com` - Admin user (first registered user)

## 📚 Additional Resources

- **Hyperflask Documentation**: https://docs.hyperflask.dev
- **Replit Nix Documentation**: https://docs.replit.com/replit-workspace/nix
- **AutoHyperFlask README**: [README.md](README.md)
- **Deployment Improvements**: [DEPLOYMENT-IMPROVEMENTS.md](DEPLOYMENT-IMPROVEMENTS.md)
- **One-Click Plan**: [AUTOHYPERFLASK-ONE-CLICK-PLAN.md](AUTOHYPERFLASK-ONE-CLICK-PLAN.md)

## 🤖 Agent-Specific Tips

If you're an AI agent deploying this:

1. **Always use `nix-shell`**: Wrap every command that needs system packages
2. **Check for errors**: After each step, verify success before proceeding
3. **Read output**: The setup script provides detailed progress messages
4. **Use markers**: Check for `.replit-initialized` to avoid re-running setup
5. **Validate incrementally**: Test after database setup, asset building, etc.
6. **SSH sessions timeout**: Complete deployment in one session if possible
7. **Git is available**: You can commit/push changes directly from Replit SSH
8. **Test selectively**: Use `-m 'not e2e'` to skip slow E2E tests during initial validation

## 🔄 Re-running Setup

If you need to start fresh:

```bash
# Remove marker file
rm .replit-initialized

# Re-run setup
nix-shell --run "bash scripts/replit-setup.sh"
```

Or manually clean everything:

```bash
# Remove virtual environment
rm -rf venv/

# Remove node modules
rm -rf node_modules/

# Remove built assets
npm run clean

# Remove database
rm -f database/app.db

# Remove marker
rm -f .replit-initialized

# Re-run setup
nix-shell --run "bash scripts/replit-setup.sh"
```

---

**Questions or issues?** Check [DEPLOYMENT-IMPROVEMENTS.md](DEPLOYMENT-IMPROVEMENTS.md) for comprehensive troubleshooting and optimization recommendations.

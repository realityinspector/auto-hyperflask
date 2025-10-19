# AutoHyperFlask

> **Production-ready [Hyperflask](https://hyperflask.dev) starter template with one-click Replit deployment**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Hyperflask](https://img.shields.io/badge/framework-Hyperflask-blueviolet.svg)](https://hyperflask.dev)

AutoHyperFlask is a fully-configured, production-ready starter template for building full-stack Python web applications with Hyperflask. It includes a complete modern asset pipeline, comprehensive testing infrastructure, mobile-responsive design, and zero-config deployment to Replit.

**🎯 Perfect for:** Rapid prototyping, SaaS MVPs, internal tools, and learning Hyperflask

## ✨ Features

- 🚀 **One-Click Deployment** - Deploy to Replit with zero configuration
- ⚡ **Modern Asset Pipeline** - esbuild + TailwindCSS with intelligent caching
- 🎨 **Beautiful UI** - DaisyUI components + Bootstrap Icons
- 📱 **Mobile-First** - Fully responsive with comprehensive mobile testing
- ✅ **Comprehensive Testing** - 30+ tests (unit, integration, E2E with Playwright)
- 🔒 **Security First** - Automated secret scanning, secure defaults
- 🗃️ **Dual Database** - SQLite (dev) + PostgreSQL (production)
- 🎭 **Interactive Frontend** - Alpine.js + HTMX pre-configured
- 📦 **Smart Builds** - Only rebuilds when files actually change
- 🧪 **Test Fixtures** - Reusable Playwright fixtures for user/admin testing

## 🚀 Quick Start

### Option 1: Deploy to Replit (Recommended)

1. Fork this repository or import it to Replit
2. Set `FLASK_SECRET_KEY` in Replit Secrets
3. Click "Run" - that's it!

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/realityinspector/auto-hyperflask.git
cd auto-hyperflask

# Install Python dependencies
python3 -m pip install -e .

# Install frontend dependencies and build assets
npm install
npm run build

# Setup development database
cp config_dev.yml config.yml
python3 scripts/reset_db.py --seed --confirm

# Run development server
python3 -m hyperflask dev
```

Visit http://localhost:5000

**Demo accounts:** `user1@test.com`, `user2@test.com`, `admin@test.com` (all with password: `password`)

## 📚 What's Included

This is a **timeline-based photo submission application** that demonstrates:

- User authentication and authorization
- Database models and relationships
- File-based routing with `.jpy` files
- Admin dashboard (first registered user becomes admin)
- Responsive mobile-friendly UI
- Modern frontend tooling

**Use it as a starting point** and customize to build your own application!

## Development Environment

### Local Development (SQLite)

```bash
# Use development config
cp config_dev.yml config.yml

# Install Python dependencies
python3 -m pip install -e .

# Install frontend dependencies and build assets
npm install
npm run build

# Reset and seed database
python3 scripts/reset_db.py --seed --confirm

# Run development server
python3 -m hyperflask dev
```

Visit http://localhost:5000

**Test accounts:** user1@test.com, user2@test.com, admin@test.com

### Using Dev Containers (VS Code)

1. Open your project folder in VS Code
2. Use the Dev Containers: Reopen in Container command from the Command Palette
3. Launch your app using F5

### Using Other Editors

1. [Install devcontainers-cli](https://github.com/devcontainers/cli#npm-install)
2. Start dev container: `devcontainer up --workspace-folder .`
3. Launch your app: `devcontainer exec uv run hyperflask dev`
4. Go to http://localhost:5000

## Asset Pipeline

This app uses a modern asset pipeline with **esbuild** and **TailwindCSS** to bundle JavaScript and CSS.

### Quick Start

```bash
# Install frontend dependencies
npm install

# Build all assets (JS + CSS + icons)
npm run build

# Watch mode for development
npm run dev
```

### What Gets Built

- **JavaScript Bundle** (`public/dist/main.js`)
  - Alpine.js for reactive components
  - HTMX for dynamic HTML updates
  - HTMX SSE extension for real-time events
  - Minified for production (~242KB)

- **CSS Bundle** (`public/dist/main.css`)
  - TailwindCSS utilities
  - DaisyUI components
  - Custom styles from `app/assets/main.css`

- **Bootstrap Icons** (`public/bootstrap-icons/`)
  - Full icon font and CSS
  - Automatically copied from node_modules

### Build Scripts

```bash
# Smart build (only rebuilds if source files changed)
npm run build

# Force build (rebuild even if no changes)
npm run build:force

# Build all components (used internally)
npm run build:all

# Development build (with sourcemaps and watch mode)
npm run dev

# Build individual components
npm run build:js       # JavaScript only
npm run build:css      # CSS only
npm run build:icons    # Icons only

# Clean build artifacts
npm run clean

# Clean macOS system files (.DS_Store, etc.)
npm run clean:macos
```

### Smart Build System

The build system includes intelligent change detection:
- Calculates MD5 hashes of all source files
- Only rebuilds when files have actually changed
- Caches build state in `.build-cache.json`
- Automatically cleans macOS system files before each build
- Saves significant time on repeated builds

**How it works:**
1. First run: No cache, builds everything
2. Subsequent runs: Compares file hashes, skips build if no changes
3. Use `npm run build:force` to override and rebuild anyway

**Watched files:**
- `app/assets/main.js`
- `app/assets/main.css`
- `build.js`
- `tailwind.config.js`
- `package.json`
- All `.jpy` and `.html` files in `app/pages/` and `app/templates/`

### Auto-Build on Replit

The `.replit` configuration automatically runs `npm run build` before starting the dev server or deploying to production. No manual intervention needed!

### Asset Testing

All assets have comprehensive E2E tests:

```bash
# Run asset tests
python3 -m pytest tests/test_assets.py -v

# Tests verify:
# - Assets exist and are not empty
# - JavaScript bundle includes Alpine.js and HTMX
# - CSS bundle includes TailwindCSS utilities
# - Assets are served correctly by Flask
# - Homepage includes compiled assets
```

### File Structure

```
app/
├── assets/
│   ├── main.js          # JavaScript entry point
│   └── main.css         # CSS entry point (Tailwind directives)
├── templates/
│   └── layout.html      # Base template with asset tags
└── pages/               # Route templates (.jpy files)

public/
└── dist/                # Compiled assets (gitignored)
    ├── main.js
    └── main.css

build.js                 # esbuild configuration
tailwind.config.js       # TailwindCSS configuration
scripts/copy-icons.js    # Bootstrap Icons copy script
```

## Database Management

### Reset Database

```bash
# Clear all data (will prompt for confirmation)
python3 scripts/reset_db.py

# Clear and reseed with test data
python3 scripts/reset_db.py --seed

# Clear and reseed without confirmation (for CI/CD)
python3 scripts/reset_db.py --seed --confirm
```

### Seed Database

```bash
# Add test data without clearing
python3 scripts/seed_db.py
```

See [scripts/README.md](scripts/README.md) for more details.

## Testing

### Test Suite Overview

This project has three types of tests:
1. **Unit/Integration Tests** - Database, models, and Flask routes
2. **Asset Pipeline Tests** - Verify asset building and serving
3. **E2E Tests with Playwright** - Browser-based visual and interaction testing

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test suites
python3 -m pytest tests/test_setup.py -v        # Database and route tests (9 tests)
python3 -m pytest tests/test_assets.py -v       # Asset pipeline tests (7 tests)
python3 -m pytest tests/test_e2e_playwright.py -v  # E2E browser tests

# Reset database before E2E tests
python3 scripts/reset_db.py --seed --confirm
python3 -m pytest tests/
```

### Playwright E2E Testing

The project includes comprehensive end-to-end testing with Playwright:

**Installation:**
```bash
# Install Playwright (already in pyproject.toml)
python3 -m pip install pytest-playwright

# Install browser binaries
python3 -m playwright install chromium
```

**Running E2E Tests:**
```bash
# Run all E2E tests (headless)
python3 -m pytest tests/test_e2e_playwright.py -v

# Run in headed mode (see the browser)
python3 -m pytest tests/test_e2e_playwright.py -v --headed

# Run specific test class
python3 -m pytest tests/test_e2e_playwright.py::TestAssetLoading -v

# Generate test screenshots
python3 -m pytest tests/test_e2e_playwright.py::TestVisualRegression -v
```

**What E2E Tests Cover:**
- ✅ Asset loading (CSS, JS, icons)
- ✅ JavaScript initialization (Alpine.js, HTMX)
- ✅ Navigation and routing
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Accessibility (semantic HTML, keyboard navigation)
- ✅ Performance metrics
- ✅ Visual regression testing with screenshots

**Playwright Fixtures:**
The project includes reusable Playwright fixtures for common testing scenarios:
- `user_actions` - Basic user interactions
- `admin_actions` - Admin-specific actions
- `timeline_actions` - Timeline page interactions
- `logged_in_user` - Pre-authenticated user
- `logged_in_admin` - Pre-authenticated admin

See `tests/fixtures/playwright_fixtures.py` for the complete fixture library.

### Test Image Fixtures

Test images are generated automatically:

```bash
# Generate test images for upload testing
python3 tests/fixtures/generate_test_images.py
```

This creates various test images in `tests/fixtures/images/` for testing photo uploads and display.

## Deployment

### Replit Deployment

The app is configured for **one-click Replit deployment** with automatic asset building.

1. Set environment variables in Replit Secrets:
   ```
   FLASK_SECRET_KEY=<your-secret-key>
   ```

2. Click "Deploy" button in Replit
   - Automatically installs dependencies (Python + npm)
   - Builds assets (`npm run build`)
   - Switches to `config_prod.yml` (PostgreSQL)
   - Creates database schema
   - Deploys to production

**Note**: Assets are automatically built on every deployment. No manual build step required!

### Manual Deployment

```bash
# Install dependencies
npm install

# Build production assets
npm run build

# Use production config
cp config_prod.yml config.yml

# Set environment variable
export FLASK_SECRET_KEY=<your-secret-key>

# Initialize production database
python3 -m hyperflask db create-all

# Deploy
python3 -m hyperflask deploy
```

## Configuration

- **Development**: `config_dev.yml` (SQLite)
- **Production**: `config_prod.yml` (PostgreSQL)
- **Default**: `config.yml` (currently SQLite)

The `.replit` file automatically switches between dev and prod configs.

## 🔒 Security

See [SECURITY.md](SECURITY.md) for security policies, best practices, and vulnerability reporting.

**Important:** Never commit sensitive credentials to version control. Use environment variables for all secrets.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Run tests (`python3 -m pytest tests/ -v`)
4. Run security scan (`detect-secrets scan --all-files .`)
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

Please ensure:
- All tests pass
- No secrets in code
- Follow existing code style
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Hyperflask](https://hyperflask.dev) - Modern full-stack Python framework
- Styled with [TailwindCSS](https://tailwindcss.com) + [DaisyUI](https://daisyui.com)
- Interactive with [Alpine.js](https://alpinejs.dev) + [HTMX](https://htmx.org)
- Icons by [Bootstrap Icons](https://icons.getbootstrap.com)
- Testing with [Playwright](https://playwright.dev)

## 📖 Documentation

- [Hyperflask Documentation](https://docs.hyperflask.dev)
- [AUTOHYPERFLASK-ONE-CLICK-PLAN.md](AUTOHYPERFLASK-ONE-CLICK-PLAN.md) - Detailed analysis and roadmap
- [scripts/README.md](scripts/README.md) - Database and utility scripts
- [SECURITY.md](SECURITY.md) - Security policies and best practices

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/realityinspector/auto-hyperflask/issues)
- **Discussions**: [GitHub Discussions](https://github.com/realityinspector/auto-hyperflask/discussions)
- **Hyperflask**: [Hyperflask Discord](https://discord.gg/hyperflask)

---

**⭐ If you find this useful, please star the repository!**

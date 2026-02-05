# MansionRadio Bot - Release Bundle & Distribution Guide

## Overview

The MansionRadio Bot is now fully prepared for public release with automated bare metal installation support. This document explains:

1. **What's in the release bundle**
2. **How to create and distribute releases**
3. **Installation methods available**
4. **Release versioning and management**

## Release Bundle Contents

The release bundle (`mansion-radio-bot-0.1.0.tar.gz`) contains:

```
mansion-radio-bot-0.1.0/
├── README.md                      # Quick start (entry point)
├── INSTALLATION.md                # Detailed installation guide (NEW!)
├── RELEASE_NOTES.md              # Version info and changelog (NEW!)
├── requirements.txt              # Python dependencies
│
├── scripts/
│   ├── install.sh                # Automated installer (NEW!)
│   ├── setup.sh                  # Manual setup helper
│   └── build.sh                  # Docker builder
│
├── src/                          # Python source code
│   ├── main.py
│   ├── bot.py
│   └── fetchers/azuracast.py
│
├── config/
│   └── .env.example              # Configuration template
│
├── docker/                       # Docker deployment
│   ├── Dockerfile
│   └── docker-compose.example.yml
│
├── systemd/
│   └── mansion-radio-bot.service # Systemd service template
│
└── docs/
    ├── ARCHITECTURE.md           # Technical design
    ├── DEPLOY_BAREMETAL.md      # Manual setup guide
    ├── DEPLOY_DOCKER.md         # Docker guide
    ├── DEPLOY_PORTAINER.md      # Portainer guide
    └── TROUBLESHOOT_*.md        # Troubleshooting
```

## Installation Methods (in order of ease)

### 1. **Automated Installer** ⭐ RECOMMENDED
**Best for:** Users who want "just works" installation
```bash
tar -xzf mansion-radio-bot-0.1.0.tar.gz
cd mansion-radio-bot
sudo bash scripts/install.sh
```
- ✅ One command to complete setup
- ✅ Creates user, virtualenv, dependencies, systemd service
- ✅ Configurable (custom users, skip systemd, dry-run)
- ✅ Perfect for Raspberry Pi and Linux servers

### 2. **Manual Setup Script**
**Best for:** Users who want some control but still automated
```bash
bash scripts/setup.sh
source venv/bin/activate
python src/main.py
```
- Creates venv and installs dependencies
- Manual systemd setup required
- Good for development/testing

### 3. **Fully Manual**
**Best for:** Advanced users, custom configurations, troubleshooting
See `INSTALLATION.md` or `docs/DEPLOY_BAREMETAL.md` for step-by-step instructions.

### 4. **Docker**
**Best for:** Containerized deployment, Portainer users
```bash
docker-compose up --build
```
See `docs/DEPLOY_DOCKER.md` for details.

## Creating Releases

### Release Checklist

Before creating a release tag:

1. **Update version files**
   ```bash
   # Update any version references in:
   # - README.md (if version mentioned)
   # - RELEASE_NOTES.md (new section for this version)
   # - Any other docs mentioning version numbers
   ```

2. **Update RELEASE_NOTES.md**
   - Add new version section
   - List all changes (features, fixes, docs, etc.)
   - Document requirements and system compatibility
   - Include installation instructions

3. **Test the release bundle**
   ```bash
   # Build the bundle
   tar --exclude='.git' --exclude='.ruff_cache' --exclude='__pycache__' \
       --exclude='*.pyc' --exclude='.env' \
       --exclude='docker/docker-compose.yml' \
       -czf mansion-radio-bot-VERSION.tar.gz mansionradio/
   
   # Extract and test installer
   cd /tmp
   mkdir test-bundle && cd test-bundle
   tar -xzf /path/to/mansion-radio-bot-VERSION.tar.gz
   bash mansion-radio-bot/scripts/install.sh --dry-run
   ```

4. **Commit all changes**
   ```bash
   git add RELEASE_NOTES.md INSTALLATION.md README.md
   git commit -m "chore: Prepare v1.0.0 release"
   ```

5. **Create git tag**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0
   
   - Feature 1
   - Feature 2
   - Bug fix 1
   "
   git push origin main
   git push origin v1.0.0
   ```

6. **Create GitHub Release** (on GitHub.com)
   - Go to: https://github.com/Pontuzz/mansionradio/releases
   - Click "Draft a new release"
   - Select the tag you just created
   - Title: "Release v1.0.0: Short Description"
   - Description: Copy from RELEASE_NOTES.md section for this version
   - Upload the `.tar.gz` file as a release asset
   - Mark as "Latest release" if applicable

### Current Release: v0.1.0

**Released:** 2026-02-05

Features:
- ✅ Automated bare metal installer (`scripts/install.sh`)
- ✅ Comprehensive installation guide (`INSTALLATION.md`)
- ✅ Release notes and versioning (`RELEASE_NOTES.md`)
- ✅ Full documentation (deployment, architecture, troubleshooting)
- ✅ Docker support with example configs
- ✅ Systemd service for auto-start
- ✅ State machine architecture with SASL support

**Bundle:** `mansion-radio-bot-0.1.0.tar.gz` (38 KB)

## Distribution Methods

### 1. **GitHub Releases** (RECOMMENDED)
- Easiest for users
- Automatic download
- Release notes included
- Can edit after creation

**URL Format:**
```
https://github.com/Pontuzz/mansionradio/releases/download/v0.1.0/mansion-radio-bot-0.1.0.tar.gz
```

### 2. **Direct Link**
If hosting elsewhere:
```bash
wget https://your-server.com/mansion-radio-bot-0.1.0.tar.gz
```

### 3. **Package Managers** (Future)
Could add to:
- Python Package Index (PyPI)
- Homebrew (macOS)
- Snap (Ubuntu)
- APT/Debian repositories

## User Installation from Release

Users would install like this:

```bash
# Step 1: Download release bundle
wget https://github.com/Pontuzz/mansionradio/releases/download/v0.1.0/mansion-radio-bot-0.1.0.tar.gz

# Step 2: Extract
tar -xzf mansion-radio-bot-0.1.0.tar.gz
cd mansion-radio-bot

# Step 3: Run installer (easiest)
sudo bash scripts/install.sh

# Step 4: Configure
sudo nano /home/radiobot/mansion-radio-bot/.env

# Step 5: Start
sudo systemctl start mansion-radio-bot
```

That's it! Everything else is automated.

## Version Strategy

### Versioning Scheme: Semantic Versioning (SemVer)

Format: `MAJOR.MINOR.PATCH[-PRERELEASE]`

- **MAJOR**: Breaking changes, major new features
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, documentation updates
- **PRERELEASE**: alpha, beta, rc (e.g., v1.0.0-beta.1)

### Examples

- `v0.1.0` - Initial release
- `v0.2.0` - Add multi-station support (minor feature)
- `v0.2.1` - Bug fix for poll interval (patch)
- `v1.0.0` - Stable production release (major)
- `v1.1.0-beta.1` - Pre-release for testing

## Managing the Release Bundle

### Bundle File Size
Current size: ~38 KB (compressed)

Breakdown:
- Source code (~5 KB)
- Documentation (~15 KB)
- Config templates (~1 KB)
- Scripts (~7 KB)

This is very lightweight and easy to distribute.

### Updating Bundle Contents

When making a new release:

```bash
# 1. Make code changes, update docs
git add <files>
git commit -m "..."

# 2. Update RELEASE_NOTES.md with new version
# 3. Commit release prep
git commit -m "chore: Prepare vX.X.X release"

# 4. Tag the release
git tag -a vX.X.X -m "Release vX.X.X"

# 5. Build new bundle with updated version number
VERSION="X.X.X"
tar --exclude='.git' --exclude='.ruff_cache' \
    --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='.env' --exclude='docker/docker-compose.yml' \
    -czf mansion-radio-bot-${VERSION}.tar.gz mansionradio/

# 6. Create GitHub release and upload bundle
```

## Release Checklist Template

For future releases, use this checklist:

```markdown
## Release v?.?.? Checklist

- [ ] Update RELEASE_NOTES.md with new version section
- [ ] Update any version numbers in documentation
- [ ] Run automated tests (if any exist)
- [ ] Test bundle creation and extraction
- [ ] Test `scripts/install.sh --dry-run`
- [ ] Commit all changes with message "chore: Prepare vX.X.X release"
- [ ] Create git tag: `git tag -a vX.X.X -m "Release vX.X.X"`
- [ ] Push commits and tags: `git push origin main --tags`
- [ ] Build release bundle
- [ ] Create GitHub release with:
  - [ ] Tag version
  - [ ] Release title
  - [ ] RELEASE_NOTES.md content in description
  - [ ] Bundle file uploaded
  - [ ] Marked as "Latest" if applicable
- [ ] Update any external references (websites, etc.)
```

## Documentation Updates per Release

For each release:

1. **RELEASE_NOTES.md**
   - Add new version section at top
   - List all features, fixes, known issues
   - Include installation and update instructions
   - Mention any breaking changes

2. **INSTALLATION.md**
   - Update version number if needed
   - Update any changed installation steps
   - Update system requirements if changed

3. **docs/DEPLOY_*.md**
   - Update examples if configuration changed
   - Add any new deployment options
   - Update troubleshooting if needed

4. **README.md**
   - Update feature list if major changes
   - Update quick start if steps changed
   - Mention new deployment methods

## Rollback Procedure

If a release has critical issues:

1. **Mark as broken** on GitHub release page
2. **Revert commit** that caused issue
3. **Create new patch release** with fix
4. **Communicate** to users about workaround

Example:
```bash
# If v1.0.0 is broken
git revert <commit-hash>  # Revert problematic commit
git tag -a v1.0.1 -m "Emergency hotfix for v1.0.0 issue"
# Create new release v1.0.1
```

## Future Release Roadmap

### v0.2.0 (Planned)
- Multi-station AzuraCast support
- Song history tracking
- Statistics dashboard
- Configurable announcement formats

### v0.3.0 (Planned)
- Automatic IRC reconnection with backoff
- Rate limiting for API
- Webhook support
- Plugin system

### v1.0.0 (Planned)
- Stable production release
- Web UI for management
- Database persistence
- Performance optimizations

## Success Metrics

A successful release means:

- ✅ Bundle downloads without issues
- ✅ Installer runs without errors
- ✅ Bot connects to IRC and announces songs
- ✅ Systemd service auto-starts correctly
- ✅ Users can update to new version smoothly
- ✅ No breaking changes without major version bump

## Support Resources

When users ask for help:

1. Point to `INSTALLATION.md` for setup
2. Point to docs/TROUBLESHOOT_*.md for issues
3. Check logs with: `sudo journalctl -u mansion-radio-bot -f`
4. If code issue: GitHub issues with logs/config (no passwords!)

## Quick Reference

### Building a Release Bundle
```bash
cd /path/to/mansionradio
VERSION="0.1.0"
tar --exclude='.git' --exclude='.ruff_cache' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='.env' --exclude='docker/docker-compose.yml' \
    -czf mansion-radio-bot-${VERSION}.tar.gz mansionradio/
```

### Testing the Bundle
```bash
cd /tmp
tar -xzf mansion-radio-bot-${VERSION}.tar.gz
cd mansionradio
bash scripts/install.sh --dry-run
```

### Creating a GitHub Release
1. Push all commits and tags first
2. Go to: https://github.com/Pontuzz/mansionradio/releases/new
3. Select tag version
4. Add title and description
5. Upload `.tar.gz` file
6. Publish release

### Sharing the Release
```
Download: https://github.com/Pontuzz/mansionradio/releases/download/v0.1.0/mansion-radio-bot-0.1.0.tar.gz

Installation:
tar -xzf mansion-radio-bot-0.1.0.tar.gz && cd mansion-radio-bot && sudo bash scripts/install.sh
```

---

**Status:** v0.1.0 release ready for public distribution  
**Bundle Location:** `/home/pontuzz/projects/mansion-radio-bot-0.1.0.tar.gz`  
**Size:** 38 KB  
**Test Status:** ✅ Verified extract and installer work correctly

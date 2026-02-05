# MansionRadio Bot - Project Guidelines for Agents

## Project Overview

IRC bot that polls an AzuraCast instance and announces currently playing songs to IRC channels. Production-ready with proper SASL authentication and state machine architecture.

**Repository:** https://github.com/Pontuzz/mansionradio  
**License:** MIT  
**Python Version:** 3.8+

## Project Type: Public OSS (Pattern 2)

**Key characteristics:**
- ✅ Source code committed (main.py, bot.py, etc.)
- ✅ Only credentials (.env) are gitignored
- ✅ Example configs (.example files) are committed
- ✅ Users clone and deploy directly
- 🌍 Designed for public GitHub release

**For Docwriter:** All referenced paths must exist in repo. Examples should match production code exactly. Focus on path verification and accuracy.

## Documentation Structure

```
├── README.md                    # Entry point + quick start
├── docs/
│   ├── README.md               # Navigation index
│   ├── ARCHITECTURE.md         # Design & technical deep dive
│   ├── DEPLOY_*.md             # Deployment method guides
│   └── TROUBLESHOOT_*.md       # Issue-specific guides
├── AGENTS.md                   # This file
└── docs/docker-compose.example.yml
```

## Key Files (All Committed)

**Verify these exist when documenting:**
- `main.py` - Entry point
- `bot.py` - IRC bot implementation
- `fetchers/azuracast.py` - AzuraCast API client
- `Dockerfile`, `setup.sh`, `requirements.txt`
- `systemd/mansion-radio-bot.service` - Systemd service
- `.env.example` - Configuration template
- `docker-compose.example.yml` - Docker template

**Do NOT document (gitignored):**
- `.env` files - Real credentials (reference `.env.example` instead)
- `docker-compose.yml` - Production config (reference `.example` instead)
- `logs/`, `__pycache__/`, `.pyc` files - Generated artifacts

## Documentation Audience Levels

| Document | Audience | Skill Level |
|----------|----------|-------------|
| README.md | New users | Beginner |
| DEPLOY_DOCKER.md | Docker users | Intermediate |
| DEPLOY_BAREMETAL.md | Linux/systemd users | Intermediate-Advanced |
| DEPLOY_PORTAINER.md | Portainer UI users | Intermediate |
| ARCHITECTURE.md | Contributing developers | Advanced |
| TROUBLESHOOT_*.md | All levels | Varies |

## Anonymization Rules (Documentation Only)

| Real Value | Placeholder |
|------------|-------------|
| `irc.example.com` | `irc.example.com` (kept generic) |
| `radio.example.com` | `radio.example.com` (kept generic) |
| `station_id` | `station_id` (variable name) |
| Account names | `your_sasl_username` |
| Passwords | `<your-sasl-password>` |
| IPv4 addresses | `[your-internal-ip]` |
| Hostnames | `[your-docker-host]` |

## Documentation Standards

**Markdown:**
- Use ATX headers (#, ##), max 3 levels in quick-start docs
- Always specify language in code blocks (```bash, ```python)
- Internal links: relative paths (docs/ARCHITECTURE.md)
- External links: full URLs

**Code examples:**
- Use `$` prefix for bash commands
- Show expected output separately
- Test examples before documenting

**Configuration:**
- Match `.env.example` format exactly
- Include inline comments for variables
- Use realistic (but anonymized) values

**Deployment steps:**
- Number steps, include expected output
- Provide success indicators
- Include rollback instructions

## Verification Checklist (For Docwriter)

- ✅ All file paths exist in repo (not gitignored)
- ✅ Code examples are tested and accurate
- ✅ Examples match production code exactly
- ✅ All links (internal/external) work
- ✅ No credentials appear in ANY file
- ✅ Anonymization is consistent
- ✅ Configuration examples match .env.example
- ✅ Deployment steps are validated

## When to Update Docs

- New features added
- Default values change
- Log formats or outputs change
- New deployment methods supported
- Bug fixes affecting usage

---

**Last Updated:** 2026-02-05

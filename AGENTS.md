# MansionRadio Bot - Project Guidelines

## Project Purpose
IRC bot that polls an AzuraCast instance and announces currently playing songs to IRC channels. Production-ready with proper SASL authentication and state machine architecture.

## Documentation Standards

### Structure
- `README.md` - Entry point with quick start, configuration, basic troubleshooting
- `docs/ARCHITECTURE.md` - Technical deep dive (design decisions, state machine, SASL flow)
- `docs/DEPLOY_*.md` - Method-specific deployment guides (Docker, Bare Metal, Portainer)
- `docs/TROUBLESHOOT_*.md` - Issue-specific troubleshooting guides

### Audience Levels

| Document | Audience | Skill Level |
|----------|----------|-------------|
| README.md | First-time users | Beginner to Intermediate |
| DEPLOY_DOCKER.md | Users with Docker knowledge | Intermediate |
| DEPLOY_BAREMETAL.md | Linux/systemd users | Intermediate to Advanced |
| DEPLOY_PORTAINER.md | Portainer UI users | Intermediate |
| ARCHITECTURE.md | Contributing developers | Advanced |
| TROUBLESHOOT_*.md | All levels (issue-specific) | Varies |

### Documentation Completeness Criteria

**Must verify:**
- ✅ All code examples are tested and accurate
- ✅ All file paths exist and are correct
- ✅ All links (internal and external) are functional
- ✅ All environment variables have descriptions
- ✅ All placeholder values use consistent naming (see below)
- ✅ No credentials, IP addresses, or infrastructure names appear (use placeholders)
- ✅ Configuration examples match `.env.example` and `docker-compose.example.yml`
- ✅ Deployment steps have been validated on target platform

**Quality checks:**
- Command outputs (logs, CLI) are up-to-date with current version
- Error messages match actual bot output
- Troubleshooting steps are logically ordered (easy-to-hard)
- Prerequisites are clearly stated before each section

### Anonymization & Placeholder Rules

**For documentation only** (not in actual working code):

| Real Value | Placeholder | Context |
|------------|-------------|---------|
| `irc.example.com` | `irc.example.com` | IRC server (kept generic) |
| `radio.example.com` | `radio.example.com` | AzuraCast server (kept generic) |
| `station_id` | `station_id` | AzuraCast station identifier |
| Account names | `your_sasl_username` | SASL account name |
| Passwords | `<your-sasl-password>` | Any credential |
| Channel names | `#radio`, `#music` | IRC channels (use realistic examples) |
| Bot nickname | `MassionRadio` | Use actual bot name (it's generic) |
| Any IPv4 | `[your-internal-ip]` or `[server-ip]` | IP addresses |
| Hostnames | `[your-docker-host]` or `[portainer-server]` | Generic server names |

### Consistency Guidelines

**Markdown formatting:**
- Headers: ATX style (`#`, `##`, etc.), max 3 levels in quick-start docs
- Code blocks: Always specify language (```bash, ```python, etc.)
- Lists: Use `-` for unordered, numbers for sequential steps
- Links: Relative paths for internal docs (`docs/ARCHITECTURE.md`), full URLs for external

**Command examples:**
- Use `$` prefix for bash commands (not `>` or `#`)
- Show expected output in separate code blocks
- Explain what each flag does (at least first time)

**Configuration examples:**
- Match `.env.example` format exactly
- Show both optional and required variables
- Include inline comments for complex variables
- Use realistic (but anonymized) example values

**Deployment steps:**
- Number each step, break into substeps if needed
- Show expected output after each step
- Provide rollback/undo instructions
- Include success indicators (how to verify)

## File References & Paths

**Always verify these exist before documenting:**
- `main.py` - Entry point
- `bot.py` - Core bot implementation
- `fetchers/azuracast.py` - API client
- `Dockerfile` - Docker image definition
- `docker-compose.example.yml` - Docker Compose template
- `setup.sh` - Bare metal setup script
- `systemd/mansion-radio-bot.service` - Systemd service file
- `.env.example` - Environment configuration template
- `requirements.txt` - Python dependencies

**Do NOT document:**
- `docker-compose.yml` - This is production, gitignored, use `.example` version instead
- `.env` files - These are gitignored, use `.env.example` instead
- `logs/` directory - Generated at runtime, not committed
- `__pycache__/` or `.pyc` files - Generated artifacts

## Link Patterns

**Internal links:**
```markdown
# Same directory
See [ARCHITECTURE](./ARCHITECTURE.md)

# From docs/ to root
See [Configuration](../README.md#configuration)

# From root to docs/
See [Deployment guide](docs/DEPLOY_DOCKER.md)
```

**External links:**
```markdown
- [AzuraCast Docs](https://www.azuracast.com/)
- [python-irc library](https://python-irc.readthedocs.io/)
- [RFC 5802 SASL](https://tools.ietf.org/html/rfc5802)
```

## Version & Update Notes

- **Repository:** https://github.com/Pontuzz/mansionradio
- **License:** MIT
- **Last Updated:** 2026-02-05
- **Python Version:** 3.8+
- **IRC Standard:** RFC 1459 with modern extensions (CAP negotiation)

## Maintenance

- All docs should reference specific code sections with `file:line_number` format
- Update docs when:
  - New features are added
  - Default values in code change
  - Command outputs or log formats change
  - New deployment methods are supported
- Remove docs when:
  - Features are deprecated
  - Deployment methods are no longer supported
  - Issues are resolved and workarounds no longer needed

## Testing Documentation

Before publishing doc updates:
- Test all code examples (run them, verify output)
- Verify all file paths exist (check repo structure)
- Follow all deployment steps on target platform
- Validate all links work (especially cross-document references)
- Check that anonymized examples are consistent across docs

---

**Last Updated:** 2026-02-05

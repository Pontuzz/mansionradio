# Documentation Index

Welcome to the MansionRadio Bot documentation. Start with the relevant section based on your needs.

## Quick Navigation

- **New user?** → Start at [README.md](../README.md)
- **Want to understand the design?** → [Architecture](./ARCHITECTURE.md)
- **Ready to deploy?** → Pick your method below
- **Something not working?** → See [Troubleshooting](./TROUBLESHOOT_PORTAINER.md)

---

## Architecture & Design

### [ARCHITECTURE.md](./ARCHITECTURE.md)
Deep technical dive into the bot's design decisions.

**Covers:**
- State machine architecture (5 connection states)
- SASL authentication flow (RFC 5802 PLAIN)
- Why we parse raw IRC messages instead of using library events
- Async polling architecture and change detection
- Reconnection logic and error recovery

**Best for:** Developers contributing to the project, or anyone wanting to understand "why it works this way"

**Audience:** Advanced (assumes IRC protocol knowledge)

---

## Deployment

Choose your deployment method:

### [DEPLOY_DOCKER.md](./DEPLOY_DOCKER.md)
Deploy using Docker and docker-compose for testing and multi-host scenarios.

**Covers:**
- Building the Docker image
- Running with docker-compose
- Environment variable configuration
- Monitoring logs
- Updating the container

**Best for:** Local testing, CI/CD, or environments with Docker available

**Audience:** Intermediate (Docker knowledge assumed)

**Time to deploy:** ~5 minutes

---

### [DEPLOY_BAREMETAL.md](./DEPLOY_BAREMETAL.md)
Deploy directly on Linux with systemd for production environments.

**Covers:**
- Virtual environment setup
- Installation and permissions
- Creating systemd service file
- Auto-start configuration
- Log management
- Updating and restarting

**Best for:** Production Linux servers, on-premises deployment

**Audience:** Intermediate to Advanced (Linux/systemd knowledge assumed)

**Time to deploy:** ~15 minutes (plus OS-specific setup)

---

### [DEPLOY_PORTAINER.md](./DEPLOY_PORTAINER.md)
Deploy via Portainer UI for centralized container management.

**Covers:**
- Creating new container in Portainer
- Configuring environment variables
- Setting up volumes and networking
- Monitoring container health
- Updating the container
- Using Portainer's built-in tools

**Best for:** Infrastructure with existing Portainer setup

**Audience:** Intermediate (Portainer UI knowledge assumed)

**Time to deploy:** ~10 minutes

---

## Troubleshooting

### [TROUBLESHOOT_PORTAINER.md](./TROUBLESHOOT_PORTAINER.md)
Troubleshooting guide for issues specific to Portainer deployments.

**Covers:**
- Container won't start
- Connection failures (IRC server not reachable)
- SASL authentication problems
- No song announcements appearing
- API connection issues
- Log interpretation guide

**Best for:** When something goes wrong in production

**Audience:** Any deployment method (general troubleshooting + Portainer-specific)

---

## Configuration Reference

For detailed configuration options, see [Configuration](../README.md#configuration) in the README.

**Environment variables:**
- `IRC_SERVER` - IRC server hostname
- `IRC_PORT` - IRC server port (usually 6697 for TLS)
- `BOT_NICKNAME` - Bot's IRC nickname
- `IRC_CHANNELS` - Channels to join (comma-separated)
- `SASL_USERNAME` - Account name for SASL auth (optional)
- `SASL_PASSWORD` - SASL password (optional)
- `AZURACAST_API` - AzuraCast API endpoint URL
- `POLL_INTERVAL` - How often to poll API (seconds)
- `LOG_LEVEL` - Logging level (INFO default, or DEBUG)
- `TZ` - Timezone for timestamps (optional)

---

## Choosing Your Deployment Method

| Method | Best For | Complexity | Setup Time |
|--------|----------|-----------|-----------|
| **Docker** | Testing, dev, multi-host | Low | 5 min |
| **Bare Metal** | Production Linux, permanent | Medium | 15 min |
| **Portainer** | Existing infrastructure, UI management | Medium | 10 min |

**Decision tree:**
1. Do you have Docker installed? → Use **Docker**
2. Do you have Portainer managing containers? → Use **Portainer**
3. Are you deploying on a Linux server? → Use **Bare Metal**

---

## Common Tasks

### Update the bot
- **Docker:** Pull new image, restart container
- **Bare Metal:** `git pull origin main`, restart systemd service
- **Portainer:** Update Git reference, rebuild image, restart container

See your deployment guide for specific steps.

### Check logs
- **Docker:** `docker logs [container-name]`
- **Bare Metal:** `journalctl -u mansion-radio-bot -f`
- **Portainer:** View in Portainer UI → Containers → [bot-name] → Logs tab

### Test the bot is working
1. Check it's connected to IRC (look for state transitions in logs)
2. Send `!playing` command in IRC channel to get current song
3. Verify announcements appear when songs change

### Change configuration
1. Update `.env` (Bare Metal) or environment variables (Docker/Portainer)
2. Restart the bot
3. Check logs for successful connection

---

## Getting Help

### If you're stuck:

1. **Check the logs** - They tell you exactly what's happening
2. **Read Troubleshooting** - Most common issues are there
3. **Verify configuration** - Is `AZURACAST_API` correct? Can IRC server be reached?
4. **Test manually** - Connect to IRC server with another client to verify connectivity

### For different problems:

- **Won't connect to IRC?** → Check [Troubleshooting](./TROUBLESHOOT_PORTAINER.md#wont-connect)
- **No announcements?** → Check [Troubleshooting](./TROUBLESHOOT_PORTAINER.md#no-announcements)
- **SASL auth failing?** → Check [SASL Flow](./ARCHITECTURE.md#sasl-authentication)
- **Questions about design?** → Read [Architecture](./ARCHITECTURE.md)

---

## Contributing

To update documentation:
1. Make changes to relevant `.md` files
2. Test all code examples work
3. Verify all links are correct
4. Submit changes with clear description of what was updated

See [AGENTS.md](../AGENTS.md) for documentation standards.

---

**Last Updated:** 2026-02-05

# MansionNET Radio Bot - HS01 Deployment

## Quick Start

This bot automatically announces songs from MansionNET Radio to IRC.

---

## Deployment to HS01

### Prerequisites
- HS01 with Docker and Portainer installed
- SSH access to HS01
- `scp` available on your machine

### 3 Simple Steps

**Step 1: Copy project to HS01**
```bash
scp -r ~/projects/mansionradio user@hs01:~/
```

**Step 2: Build Docker image on HS01**
```bash
ssh user@hs01
cd ~/mansionradio
docker build -t mansion-radio-bot:latest .
```
Wait 3-5 minutes for build to complete.

**Step 3: Deploy in Portainer (on HS01)**
1. Open Portainer UI on HS01
2. **Stacks** → **Add Stack**
3. **Web Editor**
4. Paste `docker-compose.yml` (see DEPLOY_HS01.md)
5. Name: `mansion-radio-bot`
6. **Deploy the stack**

---

## After Deployment

**Verify in Portainer:**
- Go to **Stacks** → **mansion-radio-bot**
- All containers should be **green** ✓

**Check logs:**
- Click **mansion-radio-bot** container
- View **Logs** tab
- Should show: `[INFO] Connected to IRC server`

**Test in IRC:**
- Join: `irc.inthemansion.com:6697 #radio`
- Wait for next song (max 15 seconds)
- Bot announces: `♫ Now playing: Artist - Title (Album)`

---

## Documentation

- **DEPLOY_HS01.md** ← Start here for detailed instructions
- **README.md** - Full overview
- **docs/DEPLOY_PORTAINER.md** - Portainer guide
- **docs/TROUBLESHOOT_PORTAINER.md** - If issues arise

---

## Configuration

Default configuration (in docker-compose.yml):
```yaml
IRC_SERVER=irc.inthemansion.com
IRC_PORT=6697
BOT_NICKNAME=MansionRadio
IRC_CHANNELS=#radio
AZURACAST_API=https://radio.inthemansion.com/api/nowplaying/mansionnet
POLL_INTERVAL=15
```

To customize after deployment:
1. In Portainer: **Stacks** → **mansion-radio-bot** → **Editor**
2. Modify environment variables
3. **Update the stack**

---

## Features

✅ Real-time song announcements  
✅ TLS encrypted IRC connection (6697)  
✅ 15-second polling interval  
✅ Automatic reconnection on failure  
✅ Auto-restart on crash  
✅ Comprehensive logging  

---

## Quick Commands (SSH on HS01)

```bash
# Check image exists
docker images | grep mansion-radio-bot

# View container logs
docker logs -f mansion-radio-bot

# Stop/start container
docker stop mansion-radio-bot
docker start mansion-radio-bot
```

---

## Troubleshooting

See **DEPLOY_HS01.md** for troubleshooting guide.

---

**Ready? Follow the 3 steps above and report back!** 🚀

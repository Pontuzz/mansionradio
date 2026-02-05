# MansionRadio Bot - Architecture & Design Principles

## Overview

This IRC bot announces currently playing songs from an AzuraCast radio station. It's designed following battle-tested patterns from eggdrop, a bot that has been in production for 25+ years.

## Architecture Layers

### 1. Connection Layer (State Machine)

The bot tracks explicit connection states, never assuming IRC registration status:

```
DISCONNECTED
    ↓
CONNECTING (CAP LS sent, awaiting response)
    ↓
AUTHENTICATING (SASL in progress, if enabled)
    ↓
REGISTERED (001 WELCOME received)
    ↓
ACTIVE (Channels joined, ready to announce)
```

**Why This Matters:**
- IRC registration is asynchronous and multi-step
- SASL negotiation can take time
- Eggdrop's experience: assuming state leads to hard-to-debug race conditions
- We validate every transition explicitly

### 2. Authentication Layer (SASL)

We implement SASL PLAIN following RFC 4616 and eggdrop's proven pattern.

**Key Architectural Decision: Raw Message Parsing**

The Python `irc.bot` library uses an event dispatch system that doesn't properly handle SASL `AUTHENTICATE +` messages. The `+` argument is lost or empty when processed as an Event object.

Solution: Override `on_all_raw_messages()` to parse raw IRC directly, using eggdrop's `newsplit()` and `fixcolon()` pattern:

```python
# Parse: ":source command args"
parts = raw_line.split(None, 2)
if parts[0].startswith(":"):
    command = parts[1]
    msg_part = parts[2]
else:
    command = parts[0]
    msg_part = parts[1]
```

**SASL Flow:**

1. **Socket connects** → `_connect()` calls parent
2. **CAP LS sent** → Query available capabilities (TLS already negotiated)
3. **Server responds** → `on_all_raw_messages` parses CAP response
4. **CAP ACK :sasl** → Bot transitions to AUTHENTICATING state
5. **Send AUTHENTICATE PLAIN** → Request SASL PLAIN mechanism
6. **Server sends AUTHENTICATE +** → Server ready for credentials
7. **Send AUTHENTICATE {base64}** → Send credentials (format: `\0username\0password`)
8. **Server responds 903/904/906** → Authentication success/failure
9. **Send CAP END** → Complete capability negotiation
10. **Server sends 001 WELCOME** → Registration complete

**Why SASL Ownership Matters:**

In eggdrop's CAP handler (servmsg.c:1670-1673), the code explicitly checks:
- If SASL is enabled AND negotiated, SASL code owns `CAP END` (avoids race condition)
- Otherwise, CAP handler sends `CAP END` immediately

We do this at the raw message level: SASL handlers send `CAP END`, not the generic CAP handler.

### 3. Polling Layer

The bot runs a daemon thread (`_poll_loop`) that:
- Only polls when in ACTIVE state
- Calls AzuraCast API every `poll_interval` seconds
- Detects song changes by tracking song ID
- Respects rate limiting (never announces faster than poll interval)

**Rate Limiting Philosophy (from Eggdrop):**

Eggdrop's penalty system assigns costs to IRC commands:
- `PRIVMSG` = base penalty + 1 second per recipient
- Our single channel announcement = ~2 seconds penalty
- Multiple channels = 2 + N seconds (where N = number of channels)

We respect this naturally: announcements only happen on song changes (typically 30+ min apart), which is well within server limits.

### 4. Announcement Layer

When a song change is detected:
1. Format message: `♫ Now playing: Artist - Title (Album)`
2. Announce to each channel sequentially
3. Log each announcement
4. Track last announcement time for rate limiting

**Important:** Announcements only happen when bot is ACTIVE (channels joined).

## Key Design Decisions & Lessons from Eggdrop

### Decision 1: Raw Message Parsing for SASL

**Why Not Use Event System?**
- `irc.bot` parses `AUTHENTICATE +` but loses the `+` argument
- Event handlers receive empty or malformed data
- Race conditions possible with event queue ordering

**Our Solution:**
- Override `on_all_raw_messages()` to intercept raw IRC
- Parse manually using proven eggdrop pattern
- Guarantees correct handling of minimal-argument messages

### Decision 2: Explicit State Machine

**Why Not Just Track Booleans?**
- Easy to get into invalid states (e.g., active but not registered)
- Hard to debug state-related issues
- Eggdrop learned this after 25 years: explicit state wins

**Our Solution:**
- `BotState` enum with 5 distinct states
- Every state transition is logged
- Code can assert preconditions (e.g., only announce when ACTIVE)

### Decision 3: Async SASL with Timeout Protection

**Why Not Block During Auth?**
- SASL negotiation can take seconds
- Blocking would freeze the event loop
- Network timeouts could lock up the bot

**Our Solution:**
- SASL happens asynchronously during registration
- Server enforces 8-second registration timeout (UnrealIRCd default)
- If SASL doesn't complete in time, server closes connection
- Bot automatically reconnects and tries again

### Decision 4: Separate Polling Thread

**Why Not Poll in Event Handlers?**
- Event handlers must return quickly to avoid blocking
- Network requests can be slow (timeouts, delays)
- API outages would freeze IRC connection

**Our Solution:**
- Daemon thread polls API continuously
- Main thread handles IRC events
- Thread-safe: only reads `last_song_data`, writes only when changed

### Decision 5: Minimal Logging

**Eggdrop's Philosophy:**
- `LOG_SERV`: Important events (connection, auth, errors)
- `LOG_DEBUG`: Diagnostic details (message parsing, state changes)
- Don't log every single message (performance)

**Our Implementation:**
- INFO level: State transitions, SASL flow, channel joins, announcements
- DEBUG level: Raw message dumps, parsing details
- Skipped: Per-message logging (too noisy)

## Configuration

```env
IRC_SERVER=irc.example.com
IRC_PORT=6697
BOT_NICKNAME=MansionRadio
IRC_CHANNELS=#bots,#radio
SASL_USERNAME=your_account_name        # Account that owns the registered nick
SASL_PASSWORD=<actual-password>
AZURACAST_API=https://radio.example.com/api/nowplaying/station_id
POLL_INTERVAL=10             # Seconds between API polls
```

## Error Recovery

**Connection Lost:**
- State resets to DISCONNECTED
- SASL auth state cleared
- `irc.bot` automatically reconnects (exponential backoff)
- Bot attempts next server in list after failures

**SASL Failed (904):**
- Log error
- Send CAP END to complete negotiation
- Attempt to continue (may fail to join registered channels)
- Will auto-reconnect and retry

**API Unavailable:**
- Poll loop logs error and continues
- Doesn't affect IRC connection
- Next poll attempt in `poll_interval` seconds
- User command `!playing` fails gracefully

**Timeout During Registration:**
- Server closes connection (8-second timeout)
- Bot reconnects automatically
- Retry with fresh SASL negotiation

## Performance Considerations

**Memory:**
- Single bot instance with minimal state
- Polling thread uses negligible CPU (sleep between polls)
- Event thread responsive to IRC messages

**Network:**
- PRIVMSG announces: ~1 per song (typically 20+ min apart)
- API polls: ~1 every 10 seconds (configurable)
- SASL negotiation: ~100 bytes during connect
- Respects IRC server penalty system

**Reliability:**
- Automatic reconnection on network failure
- Graceful handling of API outages
- Clean state cleanup prevents resource leaks

## Testing Checklist

- [ ] Bot connects and sends CAP LS
- [ ] CAP ACK :sasl received and parsed correctly
- [ ] SASL PLAIN authentication completes (903 received)
- [ ] CAP END sent after auth
- [ ] 001 WELCOME received
- [ ] Bot joins configured channels
- [ ] Song announcement works
- [ ] !playing command works
- [ ] API polling continues (check logs)
- [ ] Disconnect and reconnection works
- [ ] SASL failure handled gracefully (try 904)

## Files & Responsibilities

- **bot.py**: Core IRC bot with state machine and SASL
- **main.py**: Configuration loading and entry point
- **fetchers/azuracast.py**: AzuraCast API client
- **requirements.txt**: Python dependencies
- **Dockerfile**: Container build (Python 3.11 Alpine, uid 1000)

## References & Inspiration

- **Eggdrop**: https://github.com/eggheads/eggdrop (servmsg.c, sasl.c, server.c)
- **RFC 3954**: SASL PLAIN over IRC
- **RFC 4616**: SASL PLAIN authentication mechanism
- **Python irc library**: https://python-irc.readthedocs.io/

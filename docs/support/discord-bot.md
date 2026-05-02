# Discord Bot Commands

Solana Vibe Station's Discord bot provides convenient commands for managing your services directly from Discord. This is the fastest way to get service information and update your account.

## Getting Started

### Join Our Discord

1. Navigate to [https://discord.gg/solanavibestation](https://discord.gg/solanavibestation)
2. Accept rules and verify your account
3. Head to #bot-commands to interact with SVS bot
4. Read #bot-help for detailed command documentation

### Authenticating Your Account

Before using bot commands, authenticate your Discord account:

```
/auth <your-account-email>
```

The bot will send a verification link via Discord DM. Click it to verify and link your Discord account to your SVS account.

## Common Commands

### IP Whitelist Management

#### View Current Whitelist

```
/whitelist list
```

Returns all IPs currently whitelisted for your account:
- Each IP with description
- Most recent additions first
- Shows CIDR ranges if configured

#### Add IP to Whitelist

```
/whitelist add <ip-address> [description]
```

**Examples:**
```
/whitelist add 203.0.113.45
/whitelist add 203.0.113.45 "Office network"
/whitelist add 203.0.113.0/24 "Office subnet"
```

Takes effect within 30 seconds. You can immediately use the new IP.

#### Remove IP from Whitelist

```
/whitelist remove <ip-address>
```

**Example:**
```
/whitelist remove 203.0.113.45
```

Connections from this IP will stop working immediately after removal.

#### Update IP Description

```
/whitelist describe <ip-address> <new-description>
```

**Example:**
```
/whitelist describe 203.0.113.45 "Updated: NYC office"
```

### Connection Information

#### Get gRPC Endpoint Details

```
/grpc info
```

Returns:
- Endpoint URL (grpc.solanavibestation.com:443)
- Your tier and concurrent stream limit
- Number of active connections
- Bandwidth usage this month

#### Get RPC Connection Details

```
/rpc info
```

Returns:
- RPC endpoint URL
- Current API key (obfuscated)
- Request rate limits
- Usage statistics

### Service Status

#### Check Service Health

```
/status
```

Returns:
- gRPC service status (up/down)
- RPC service status (up/down)
- Network latency
- Current uptime
- Any ongoing maintenance

#### Get Detailed Status

```
/status detailed
```

Extended information:
- Historical uptime percentage
- Recent incidents
- Performance metrics
- Upcoming maintenance window

### Account & Billing

#### View Account Summary

```
/account
```

Shows:
- Account email
- Joined date
- Active services
- Current tier
- Next billing date

#### Check Billing Status

```
/billing
```

Returns:
- Current balance
- Next invoice date
- Payment method on file
- Auto-renewal status
- Recent invoices (last 3)

#### List Your Services

```
/services
```

Shows all active services:
- gRPC streaming (with tier)
- RPC access
- VPS instances (with names)
- Add-on services

### Troubleshooting

#### Report an Issue

```
/support <issue-description>
```

**Example:**
```
/support gRPC connection timing out from office network
```

Creates a support ticket that our team reviews within 4 hours.

#### Request Help

```
/help [topic]
```

**Examples:**
```
/help
/help whitelist
/help grpc
/help rpc
```

Returns guides and common solutions.

## Advanced Commands

### Bulk Operations

#### Add Multiple IPs

```
/whitelist batch add
ip1: 203.0.113.45
ip2: 203.0.113.46
ip3: 203.0.113.47
```

Adds multiple IPs in one command. Useful when adding entire office ranges.

#### Export Whitelist

```
/whitelist export
```

Exports your current whitelist as JSON file. Download via Discord DM.

### Usage Statistics

#### View Monthly Usage

```
/usage [service] [month]
```

**Examples:**
```
/usage grpc march
/usage rpc
/usage
```

Shows:
- Data transferred
- Request counts
- Peak usage times
- Billing impact

#### Bandwidth Report

```
/bandwidth
```

Detailed breakdown:
- Inbound bandwidth
- Outbound bandwidth
- Peak hours
- Projected monthly total

### Alert Configuration

#### Set Up IP Whitelist Alert

```
/alerts whitelist on
```

Notifies you via Discord when someone adds/removes IPs from your account.

#### Enable Service Alerts

```
/alerts service on
```

Alerts for:
- Service outages
- Major issues
- Maintenance windows
- High usage warnings

#### View Alert Settings

```
/alerts status
```

Shows all configured alerts and notification preferences.

## Command Reference

### Syntax Guide

Commands follow this pattern:
```
/command [required-param] [optional-param]
```

**Parameters:**
- `<param>` = Required
- `[param]` = Optional
- `|` = Or (choose one)

### Getting Command Help

```
/help <command>
```

**Examples:**
```
/help whitelist
/help grpc info
```

Shows detailed help for any command.

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `Not authenticated` | Discord account not linked | Run `/auth <email>` |
| `Invalid IP format` | IP address malformed | Check IP format (e.g., 203.0.113.45) |
| `Already whitelisted` | IP already in list | Use `/whitelist list` to check |
| `Invalid parameter` | Wrong command syntax | Use `/help <command>` for syntax |
| `Rate limited` | Too many commands too fast | Wait a moment and retry |

## Bot Etiquette

### Best Practices

- Use #bot-commands channel (not in other channels)
- Don't spam commands—wait for response before reissuing
- Keep sensitive details (IPs, keys) out of public channels
- Check #announcements before asking about outages
- Use threads for multi-step troubleshooting

### Privacy

- Bot commands are logged for security
- Your personal data (email, IPs) is not shared publicly
- Use DMs for sensitive issues
- All whitelist information is only visible to you

## Troubleshooting Bot Issues

### Bot Not Responding

1. Verify you're in #bot-commands channel
2. Check Discord bot status: `/status`
3. Ensure your account is authenticated: `/auth`
4. Wait 30 seconds and try again
5. Report issue: `/support Bot not responding`

### Command Not Recognized

```
/help <command-name>
```

Returns "Command not found" if typo or command doesn't exist.

**Check:**
- Command name spelling
- Parameters in correct format
- Whether command requires authentication

### Authentication Issues

1. Ensure your email is correct: `/auth your-email@example.com`
2. Check Discord DM for verification link
3. Click verification link within 10 minutes
4. Try command again

**Still not working?** Create support ticket with bot issues.

## Advanced Examples

### Setting Up New Server

```bash
# Get your new server IP first
curl https://checkip.amazonaws.com

# Then in Discord:
/whitelist add 203.0.113.100 "New production server"

# Verify it's added:
/whitelist list
```

### Monitoring Usage

```
# Daily usage check
/usage grpc
/usage rpc

# Alert setup
/alerts service on

# Bandwidth monitoring
/bandwidth
```

### Multi-User Coordination

```
# User A adds their IP
/whitelist add 203.0.113.50 "Developer A"

# User B adds their IP
/whitelist add 203.0.113.51 "Developer B"

# Team lead reviews
/whitelist list
```

## Mobile Access

The Discord bot works equally well on:
- Discord Desktop
- Discord Mobile App
- Discord Web
- Any Discord client

Just type the same commands in #bot-commands channel.

## Security Notes

### Never Share

- Your API keys (even partial)
- Your account email in public channels
- Screenshots with whitelisted IPs visible
- Private bot commands in public channels

### Whitelist Security

- Only share whitelisted IPs with trusted team members
- Remove access when team members leave
- Use descriptive names to track who uses each IP
- Review whitelist monthly: `/whitelist list`

### Reporting Issues

Found a security issue?
- Don't post publicly
- DM support with details
- Use private support channel
- Do not test vulnerabilities on production

## Getting More Help

### Where to Ask

- **Simple questions** - Post in #help-general
- **Bot commands** - Use `/help <command>`
- **Troubleshooting** - Create support ticket: `/support`
- **Billing issues** - DM support team privately
- **Security issues** - Report privately to security team

### Support Hours

- Discord: 24/7 community support
- Official support: Monday-Friday, 8am-6pm ET
- Critical issues: 24/7 emergency support

## Command List Summary

| Command | Purpose |
|---------|---------|
| `/auth` | Link your Discord account |
| `/whitelist list` | View whitelisted IPs |
| `/whitelist add` | Add IP to whitelist |
| `/whitelist remove` | Remove IP from whitelist |
| `/whitelist describe` | Update IP description |
| `/grpc info` | Get gRPC endpoint info |
| `/rpc info` | Get RPC endpoint info |
| `/status` | Check service status |
| `/account` | View account details |
| `/billing` | Check billing info |
| `/services` | List active services |
| `/support` | Create support ticket |
| `/help` | Get command help |
| `/usage` | View usage stats |
| `/bandwidth` | Get bandwidth report |
| `/alerts` | Configure alerts |

---

**Need help?** Join our Discord and post in #help-general or use `/support` to create a ticket.

For detailed documentation on services, see:
- [gRPC Streaming Setup](../grpc/streaming-setup.md)
- [VPS Management](../vps-cloud/managing-your-vps.md)
- [Troubleshooting Guide](./troubleshooting.md)

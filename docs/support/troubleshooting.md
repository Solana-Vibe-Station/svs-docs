# Troubleshooting Guide

This guide covers common issues and solutions for Solana Vibe Station services. Start with the most relevant section for your problem.

## General Connection Issues

### Connection Refused / Timeout

**Symptoms:**
- Cannot connect to RPC/gRPC endpoint
- `Connection refused` error
- Connection times out after 30+ seconds

**Causes:**
- IP not whitelisted
- Firewall blocking outbound traffic
- Service is down or restarting
- Incorrect endpoint URL or port

**Solutions:**

1. **Verify IP Whitelist**
   ```bash
   # Check your public IP
   curl https://checkip.amazonaws.com

   # Confirm it's whitelisted in cloud dashboard
   # Log into https://cloud.solanavibestation.com
   # Navigate to gRPC or VPS > Whitelist
   ```

2. **Test connectivity to endpoint**
   ```bash
   # Test basic connectivity
   curl -v https://grpc.solanavibestation.com:443

   # For RPC endpoint
   curl -X POST https://rpc.solanavibestation.com \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "getHealth", "id": 1}'
   ```

3. **Check firewall rules**
   - Confirm outbound HTTPS (443) is allowed
   - Check if proxy or NAT is changing your IP
   - Disable VPN/proxy temporarily to test

4. **Restart your application**
   ```bash
   # Stop and restart your service
   systemctl restart your-service
   ```

5. **Check service status**
   - Visit our status page: [status.solanavibestation.com](https://status.solanavibestation.com)
   - Check Discord #status channel for maintenance notices

### DNS Resolution Failed

**Symptoms:**
- `Failed to resolve host`
- `getaddrinfo: Name or service not known`

**Causes:**
- DNS server issues
- Incorrect endpoint domain name
- Network connectivity to DNS

**Solutions:**

```bash
# Check if DNS resolves
nslookup grpc.solanavibestation.com
dig grpc.solanavibestation.com

# Try alternative DNS
# Use Google DNS (8.8.8.8)
nslookup -server 8.8.8.8 grpc.solanavibestation.com

# Flush DNS cache (Linux)
sudo systemctl restart systemd-resolved

# Check DNS from your VPS
ssh user@vps-ip "nslookup grpc.solanavibestation.com"
```

## Authentication Errors

### 401 Unauthorized / 403 Forbidden

**Symptoms:**
- `401 Unauthorized` response
- `403 Forbidden` error
- `Invalid credentials` message

**Causes:**
- IP not whitelisted
- Whitelisted IP changed (VPN, proxy)
- API credentials expired
- Service requires re-authentication

**Solutions:**

1. **For gRPC (IP Whitelist):**
   ```bash
   # Verify your current IP
   curl -s https://checkip.amazonaws.com

   # Add to whitelist in cloud dashboard
   # Settings > gRPC > IP Whitelist > Add IP
   ```

2. **For RPC with API keys:**
   ```bash
   # Verify API key is correct
   curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://rpc.solanavibestation.com
   ```

3. **Check whitelist propagation**
   - Wait 30 seconds after adding IP
   - Clear any cached credentials
   - Restart your client application

4. **If using VPN/Proxy:**
   - Your actual IP is masked
   - Either whitelist proxy IP or disable VPN
   - Some VPNs rotate IPs—use static IP option

5. **Multiple IPs?**
   ```bash
   # If application spans multiple servers
   # Add all server IPs to whitelist
   # Or use CIDR range: 203.0.113.0/24
   ```

### Rate Limiting (429 Too Many Requests)

**Symptoms:**
- `429 Too Many Requests` response
- Service requests rejected with 429 error
- Intermittent failures that resolve after waiting

**Causes:**
- Exceeded request rate limit
- Too many concurrent connections
- Burst traffic spike
- Rate limit quota depleted

**Solutions:**

1. **Identify your rate limit**
   - Check cloud dashboard for your service tier
   - Contact support for tier-specific limits
   - Usually listed in API documentation

2. **Implement request throttling**
   ```python
   import time
   from functools import wraps

   def rate_limit(max_calls, time_window):
       min_interval = time_window / max_calls
       last_called = [0]

       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               elapsed = time.time() - last_called[0]
               wait_time = min_interval - elapsed
               if wait_time > 0:
                   time.sleep(wait_time)
               last_called[0] = time.time()
               return func(*args, **kwargs)
           return wrapper
       return decorator

   @rate_limit(100, 60)  # 100 requests per 60 seconds
   def my_api_call():
       pass
   ```

3. **Reduce concurrent requests**
   - Lower the number of simultaneous connections
   - Queue requests instead of parallel processing
   - Use connection pooling with max limits

4. **Upgrade your tier**
   - If you legitimately need higher limits
   - Check cloud dashboard for tier options
   - Contact sales for custom rate limits

5. **Monitor usage**
   ```bash
   # Track request rate
   tail -f /var/log/app.log | grep "requests"

   # Count requests per minute
   grep -o 'timestamp' /var/log/app.log | \
     uniq -c | tail -10
   ```

## WebSocket & Streaming Issues

### WebSocket Connection Drops

**Symptoms:**
- WebSocket closes unexpectedly
- `Connection closed` error without retry
- Persistent subscription disconnections

**Causes:**
- Network instability
- Server timeout after inactivity
- Firewall closing idle connections
- Client-side issue (not reading stream)

**Solutions:**

1. **Implement connection keep-alive**
   ```javascript
   const WebSocket = require('ws');

   const ws = new WebSocket('wss://rpc.solanavibestation.com');

   // Send ping every 30 seconds
   const interval = setInterval(() => {
       if (ws.readyState === ws.OPEN) {
           ws.ping();
       }
   }, 30000);

   ws.on('close', () => {
       clearInterval(interval);
       console.log('WebSocket closed, attempting reconnect...');
   });
   ```

2. **Add reconnection logic**
   ```python
   import time
   import websocket

   def connect_with_retry(url, max_retries=5):
       for attempt in range(max_retries):
           try:
               ws = websocket.create_connection(url)
               return ws
           except Exception as e:
               wait_time = 2 ** attempt  # Exponential backoff
               print(f"Attempt {attempt + 1} failed. Retrying in {wait_time}s...")
               time.sleep(wait_time)
       raise Exception(f"Failed to connect after {max_retries} attempts")
   ```

3. **Monitor connection health**
   ```bash
   # Check WebSocket connection status
   netstat -an | grep -i websocket

   # Monitor for dropped connections in logs
   tail -f app.log | grep -i "websocket\|closed\|disconnect"
   ```

4. **Check firewall timeout settings**
   - Some firewalls close idle connections after 5-10 minutes
   - Implement ping/pong or heartbeat messages
   - Request whitelisting of your IP if possible

5. **Review server logs**
   - Check cloud dashboard logs for disconnection reason
   - Errors often indicate invalid subscription or rate limiting
   - Look for "closed by server" messages

## Data & Query Issues

### Historical Data Not Returning Results

**Symptoms:**
- Empty results for historical queries
- Slot not found error
- Timeout waiting for historical data

**Causes:**
- Data is being pruned (old slots deleted)
- Incorrect query parameters
- Service doesn't retain that history
- Slot hasn't been processed yet

**Solutions:**

1. **Check available history window**
   ```bash
   # Query for oldest available slot
   curl -X POST https://rpc.solanavibestation.com \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "getFirstAvailableBlock",
       "id": 1
     }'
   ```

2. **Verify slot exists**
   ```bash
   # Check if slot has been processed
   curl -X POST https://rpc.solanavibestation.com \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "getBlock",
       "params": [YOUR_SLOT_NUMBER],
       "id": 1
     }'
   ```

3. **Use appropriate query method**
   - For recent data: Use gRPC streaming
   - For historical: Use RPC methods with proper slot ranges
   - Verify your service tier includes history retention

4. **Check service tier**
   - Different tiers have different history depth
   - Basic tier might only have last 5 days
   - Pro tier might have months of history
   - Contact support for history retention details

## VPS-Specific Issues

### High Resource Usage

**Symptoms:**
- CPU usage consistently >80%
- Memory running low
- Disk space warnings

**Solutions:**

1. **Identify resource hogs**
   ```bash
   # Top CPU consumers
   top -b -n 1 | head -20
   ps aux --sort=-%cpu | head -10

   # Top memory consumers
   ps aux --sort=-%mem | head -10

   # Disk space usage
   df -h
   du -sh /* | sort -rh
   ```

2. **Scale resources in dashboard**
   - Log into cloud control panel
   - Go to Upgrades tab
   - Increase CPU cores or RAM
   - Changes take effect immediately for CPU

3. **Optimize application**
   - Profile your application
   - Look for memory leaks (ps output growing over time)
   - Reduce logging verbosity
   - Implement caching to reduce queries

4. **Monitor actively**
   ```bash
   # Real-time monitoring
   watch -n 1 'ps aux | grep your-app'

   # Memory leak detection
   /usr/bin/time -v ./your-application

   # Set up alerts in cloud dashboard
   ```

### SSH Access Issues

**Symptoms:**
- Cannot SSH into VPS
- `Connection refused` on port 22
- `Permission denied (publickey)`

**Solutions:**

1. **Verify SSH port is open**
   - Check cloud dashboard firewall rules
   - Add inbound rule for TCP port 22
   - Restrict source IP to your location

2. **Check SSH service is running**
   ```bash
   # From VPS console if available
   sudo systemctl status ssh
   sudo systemctl restart ssh
   ```

3. **Verify SSH key permissions**
   ```bash
   # On your local machine
   chmod 600 ~/.ssh/your-key.pem
   chmod 700 ~/.ssh/
   ```

4. **Test SSH connection**
   ```bash
   # Verbose output to see what fails
   ssh -vvv -i ~/.ssh/your-key.pem user@vps-ip

   # Check if port is open
   nc -zv vps-ip 22
   ```

5. **Regenerate SSH key if needed**
   - Contact support to reset access
   - Generate new SSH keypair
   - Upload public key to VPS

### Disk Space Full

**Symptoms:**
- "No space left on device" errors
- Application crashes from disk space
- Cannot write to logs

**Solutions:**

```bash
# Find large files
du -sh /* | sort -rh
find / -type f -size +1G

# Check disk usage by directory
df -h

# Clean up logs
sudo rm /var/log/*.old
sudo truncate -s 0 /var/log/syslog

# Clear cache
sudo apt-get clean
sudo apt-get autoclean
```

**Prevent future issues:**
1. Log rotate configuration
2. Set up disk space alerts in dashboard
3. Upgrade disk size if consistently near limit
4. Archive old data to cloud storage

## Firewall & Network Issues

### Port Closed or Unreachable

**Symptoms:**
- Service listening but cannot connect from outside
- `Connection refused` or `Connection timed out`

**Solutions:**

1. **Verify service is running**
   ```bash
   sudo ss -tunl | grep :PORT
   sudo netstat -ln | grep :PORT
   ```

2. **Check firewall rule exists**
   - Log into cloud dashboard
   - Navigate to VPS > Firewall
   - Verify inbound rule for your port
   - Rule should have correct protocol (TCP/UDP)

3. **Test from another machine**
   ```bash
   # From external machine
   nc -zv your-vps-ip your-port
   telnet your-vps-ip your-port
   ```

4. **Check if port is restricted**
   - Some ports (25, 53, 445) are restricted network-wide
   - See [Restricted Ports](../vps-cloud/restricted-ports.md)
   - Use alternative port if restricted

5. **Verify IP whitelist for gRPC**
   - If using gRPC, check IP whitelist setting
   - May need to whitelist the connecting client IP
   - For CIDR ranges, ensure IP falls within range

## Getting Additional Help

### Before Contacting Support

- Check this troubleshooting guide
- Review service status page
- Check Discord #help channel
- Try basic debugging (telnet, curl, logs)

### How to Get Support

1. **Discord** - Fastest for community help
   - Join [https://discord.gg/solanavibestation](https://discord.gg/solanavibestation)
   - Post in #help with error message and steps taken

2. **Cloud Platform Support Tickets**
   - Log into [https://cloud.solanavibestation.com](https://cloud.solanavibestation.com)
   - Go to Support > Create Ticket
   - Include:
     - Error message or symptom
     - Steps to reproduce
     - Relevant logs or configuration
     - When issue started

3. **Useful Information to Provide**
   ```bash
   # System information
   uname -a
   lsb_release -a

   # Service status
   systemctl status your-service

   # Error logs
   journalctl -u your-service -n 50
   tail -f /var/log/your-app.log

   # Network diagnostics
   curl -v https://endpoint
   netstat -an | grep your-port
   ```

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Service down or port closed | Check service status, firewall rules |
| `401 Unauthorized` | Invalid/missing credentials | Verify API key or IP whitelist |
| `429 Too Many Requests` | Rate limited | Reduce request rate or upgrade tier |
| `DNS resolution failed` | DNS issues | Try alternative DNS, check domain |
| `TLS/SSL error` | Certificate or encryption issue | Update client TLS library |
| `No space left on device` | Disk full | Clean up files, resize disk |
| `Too many open files` | Resource limit reached | Increase file descriptor limit |
| `Connection timeout` | Network unreachable or blocked | Check firewall, network path |

## Performance Optimization

### Slow Response Times

```bash
# Measure latency to endpoint
ping -c 5 grpc.solanavibestation.com
curl -w "@curl-format.txt" https://rpc.solanavibestation.com

# Monitor application bottlenecks
perf top
htop
```

### Reducing Latency

- Use gRPC instead of REST for real-time data
- Batch RPC requests together
- Use connection pooling
- Monitor and optimize database queries
- Consider caching strategies

---

**Not finding your issue?** Contact support through Discord or cloud dashboard with:
- Exact error message
- Steps to reproduce
- Relevant logs
- Your service tier

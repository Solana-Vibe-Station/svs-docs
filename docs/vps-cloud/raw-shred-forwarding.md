# Raw Shred Forwarding

## Overview

Raw Shred Forwarding allows you to receive raw Solana protocol shreds directly to your VPS. This advanced feature is essential for validator operators, data archiving services, and applications requiring complete ledger history.

## What Are Shreds?

Shreds are the smallest building blocks of the Solana blockchain. A shred is:

- A fragment of a block proposal (typically ~1KB in size)
- Transmitted in real-time by validators producing blocks
- Immediately available before full block confirmation
- Essential for validators to reconstruct blocks and maintain consensus
- Required for some types of ledger archiving and indexing

### Why Raw Shred Forwarding?

**Advantages:**
- Access shreds in real-time before block confirmation
- Participate in validator consensus
- Archive complete ledger history
- Monitor block production patterns
- Build custom indexing solutions
- Detect and analyze failed blocks

**Use Cases:**
- Validator operators who need shred reconstruction
- Data archiving and historical ledger services
- Block exploration and analysis tools
- Custom data indexing pipelines
- Research and monitoring applications

## Getting Started

### Prerequisites

- Active SVS VPS instance
- Access to cloud management dashboard
- Basic networking knowledge
- Inbound firewall rule for shred forwarding port

### Step 1: Purchase Raw Shred Forwarding

Raw Shred Forwarding is available as an add-on:

#### During VPS Purchase

1. When creating a new VPS, check **Add-ons**
2. Select **Raw Shred Forwarding**
3. Choose your shred forwarding port (default: 8000-8010)
4. Complete checkout

#### After VPS Purchase

1. Log into [https://cloud.solanavibestation.com](https://cloud.solanavibestation.com)
2. Navigate to your VPS instance
3. Go to **Billing** tab
4. Click **Add Services**
5. Select **Raw Shred Forwarding**
6. Configure port settings
7. Confirm and pay

### Step 2: Configure Firewall

Raw Shred Forwarding requires inbound traffic on a specific port. You must allow this in your firewall.

#### Via Cloud Dashboard

1. Navigate to your VPS
2. Click **Firewall** tab
3. Click **Add Inbound Rule**
4. Configure:
   - **Protocol**: UDP
   - **Port**: Your shred forwarding port (typically 8000-8010)
   - **Source**: `0.0.0.0/0` (or restrict to specific validator IPs)
   - **Description**: "Raw Shred Forwarding"
5. Click **Save**

#### Via SSH on Your VPS

```bash
# Example with UFW (Ubuntu)
sudo ufw allow in 8000:8010/udp comment 'Raw Shred Forwarding'
```

**Important:** Without the firewall rule, you won't receive any shreds.

### Step 3: Configure Your Application

#### Connection Details

After enabling Raw Shred Forwarding, you'll see:
- **Shred Port**: The UDP port receiving shreds
- **Local Address**: Your VPS IP address
- **Status**: Active or Inactive

#### Example: Solana Validator Configuration

Add to your validator config:

```yaml
shred_forwarding:
  enabled: true
  address: "YOUR_VPS_IP"
  port: 8000
  filter:
    forward_all: false
    leader_only: true
```

#### Example: Custom Application (Python)

```python
import socket

def receive_shreds(port=8000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))

    print(f"Listening for shreds on port {port}")

    while True:
        data, addr = sock.recvfrom(65535)
        print(f"Received shred from {addr}")
        # Process shred data
        process_shred(data)

def process_shred(shred_data):
    # Parse and store shred
    # Update ledger or database
    pass

if __name__ == '__main__':
    receive_shreds()
```

### Step 4: Verify Shred Reception

Monitor shred traffic on your VPS:

```bash
# Install netstat if needed
sudo apt-get install net-tools

# Monitor UDP traffic on shred port
netstat -un | grep 8000

# Use tcpdump to verify packets arriving
sudo tcpdump -i eth0 -n udp port 8000

# Monitor with ss (modern alternative)
ss -ul | grep 8000
```

## Shred Specifications

### Shred Format

Each UDP packet contains:
- **Header** - Metadata about the shred
- **Payload** - Actual shred data
- **Signature** - Validator signature

### Data Rate

Expected traffic for shred forwarding:
- **Normal network** - 1-3 Mbps during peak times
- **Consensus activity** - Can spike to 10+ Mbps
- **Quiet periods** - <100 Kbps

Size planning for your VPS:
- Continuous operation: Plan for 3-5 Mbps sustained
- Peak handling: 10+ Mbps bursts
- Monitor actual usage in dashboard

### Packet Size

- Individual shreds: ~1KB
- Some packets batched: up to 1400 bytes
- UDP fragmentation: Possible on high-load networks

## Advanced Configuration

### Multiple Shred Ports

If you need multiple shred streams:

1. In Billing tab, add additional Raw Shred Forwarding services
2. Each will have a dedicated port
3. Add firewall rules for each port

### Port Restrictions

Some ports are restricted on SVS infrastructure. See [Restricted Ports](./restricted-ports.md) for details. Most commonly used shred ports (8000-8010) are available.

### Filtering Shreds

Some applications allow filtering which shreds are forwarded:

```yaml
shred_forwarding:
  leader_only: true      # Only shreds from current leader
  slot_range: [1000000, 1100000]  # Specific slot range
```

## Monitoring & Troubleshooting

### Shred Reception Stopped

**Problem:** No shreds arriving after working

**Solutions:**
1. Check firewall rule is still active
2. Verify UDP port in firewall list
3. Restart shred forwarding service
4. Check system logs: `journalctl -u solana-validator`
5. Confirm no DDoS protection blocking traffic

### High Bandwidth Usage

**Problem:** Unexpected bandwidth spike

**Solutions:**
1. Monitor shred port: `tcpdump -i eth0 port 8000 -w capture.pcap`
2. Check for broadcast storms
3. Review slot leader schedule
4. Verify filter configuration working correctly
5. Consider limiting shred stream to specific slots

### Shred Processing Lag

**Problem:** Can't keep up with shred rate

**Solutions:**
1. Increase VPS CPU cores via dashboard
2. Optimize shred processing algorithm
3. Use multi-threading for packet processing
4. Consider spreading across multiple VPS instances
5. Monitor CPU/RAM usage in dashboard

### Firewall Rule Not Taking Effect

**Problem:** Added firewall rule but still no traffic

**Solutions:**
1. Verify rule shows in firewall list (refresh page)
2. Check protocol is set to UDP (not TCP)
3. Port should be correct (8000, not 8001)
4. Source can be 0.0.0.0/0 or specific validator IP
5. Wait 30 seconds for rule propagation
6. Test with: `echo "test" | nc -u -w0 127.0.0.1 8000`

## Costs

Raw Shred Forwarding is billed as an add-on service:
- Base cost: See cloud dashboard pricing
- Bandwidth charges: Included in base cost
- Scale: Same cost regardless of shred volume

See [Managing Your VPS - Billing](./managing-your-vps.md#billing-management) for detailed cost information.

## Disabling Raw Shred Forwarding

To remove the service:

1. Navigate to **Billing** tab
2. Find **Raw Shred Forwarding** in active services
3. Click **Cancel Service**
4. Firewall rules must be removed manually if desired
5. Billing stops on next renewal cycle

## Best Practices

### Network Configuration

- Whitelist only necessary validator IPs if possible
- Monitor firewall logs for unusual traffic
- Use separate VPS for shred processing if high-volume
- Implement rate limiting on your application

### Data Management

- Archive shreds with timestamps
- Deduplicate shreds from multiple sources
- Implement retry logic for dropped packets
- Monitor disk space for shred storage

### Performance Optimization

- Process shreds asynchronously
- Use UDP receive buffer tuning: `net.core.rmem_max`
- Consider using multiple network interfaces
- Monitor CPU usage to avoid bottlenecks

### Monitoring

- Set up alerts in dashboard for bandwidth spike
- Log connection errors and dropped packets
- Track processing latency
- Monitor CPU/memory consumption

## Support & Troubleshooting

Need help with Raw Shred Forwarding?

1. Check firewall rules first - most issues are firewall-related
2. Verify UDP port listening: `netstat -ul | grep PORT`
3. Monitor actual traffic: `tcpdump -i eth0 udp port 8000`
4. Check service logs on your VPS
5. Submit support ticket with:
   - Firewall configuration
   - tcpdump capture file
   - Application logs
   - Expected vs actual shred rate

## Next Steps

- [Managing Your VPS](./managing-your-vps.md) - Dashboard overview
- [Restricted Ports](./restricted-ports.md) - Port limitations
- [Troubleshooting](../support/troubleshooting.md) - General troubleshooting guide

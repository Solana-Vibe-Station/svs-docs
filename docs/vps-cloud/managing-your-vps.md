# Managing Your VPS

## Dashboard Overview

The Solana Vibe Station cloud platform provides a comprehensive management interface for your VPS. From your dashboard, you can monitor resources, manage configurations, and scale your infrastructure in real-time without requiring assistance from our support team.

Access your dashboard at [https://cloud.solanavibestation.com](https://cloud.solanavibestation.com)

## Firewall Management

Control inbound and outbound traffic to your VPS with granular firewall rules.

### Accessing Firewall Settings

1. Log into the cloud dashboard
2. Select your VPS instance
3. Navigate to **Firewall** tab
4. View current rules or click **Edit Rules**

### Adding Inbound Rules

Inbound rules control what traffic is allowed into your VPS:

1. Click **Add Inbound Rule**
2. Configure:
   - **Port/Port Range** - Single port (22) or range (8000-8099)
   - **Protocol** - TCP, UDP, or both
   - **Source** - Specific IP, CIDR range, or 0.0.0.0/0 (all)
   - **Description** - Optional note for your reference
3. Click **Save**

**Example:** Allow SSH from your office
- Protocol: TCP
- Port: 22
- Source: 203.0.113.0/24
- Description: "Office SSH access"

### Adding Outbound Rules

Outbound rules control what traffic your VPS can send:

1. Click **Add Outbound Rule**
2. Configure destination, port, and protocol
3. Most servers allow all outbound by default

### Common Port Rules

| Service | Port | Protocol | Notes |
|---------|------|----------|-------|
| SSH | 22 | TCP | Restrict this to known IPs |
| Solana RPC | 8899 | TCP | For JSON-RPC |
| Solana TPU | 8001 | UDP | For validator communication |
| gRPC | 443 | TCP | For Geyser gRPC |
| HTTP | 80 | TCP | Web services |
| HTTPS | 443 | TCP | Secure web services |

### Restricted Ports

Certain ports are restricted and cannot be opened. See [Restricted Ports](./restricted-ports.md) for details.

### Raw Shred Forwarding Firewall

If using Raw Shred Forwarding, you must add an inbound allow rule for the shred forwarding port. See [Raw Shred Forwarding](./raw-shred-forwarding.md) for setup instructions.

## Storage Management

Monitor and manage your VPS disk space.

### Viewing Storage Usage

1. Navigate to **Storage** tab
2. View current usage:
   - Used space
   - Total capacity
   - Available space percentage
3. See breakdown by mount point

### Resizing Disk Space

Resize your disk without downtime:

1. Click **Resize Disk**
2. Enter new size (must be larger than current)
3. Review cost increase
4. Click **Confirm**

The resize happens in the background—your VPS stays running.

### Backup Management

#### Automatic Backups

- Enabled by default
- Frequency: Daily snapshots
- Retention: Last 7 days (configurable)
- No additional cost

#### Manual Backups

Create on-demand snapshots:

1. Click **Create Backup**
2. Optional description (e.g., "Pre-migration backup")
3. Click **Confirm**

#### Restore from Backup

1. Click **Manage Backups**
2. Select backup from list
3. Click **Restore**
4. VPS will restart with previous state

**Note:** Restoring overwrites all changes since the backup was created.

## Logs & Monitoring

Access service logs and system information.

### System Logs

1. Navigate to **Logs** tab
2. View real-time system logs including:
   - Boot messages
   - System errors
   - Service restarts
3. Filter by date range
4. Download log files for analysis

### Boot Logs

View kernel messages and initialization logs from the last boot. Helpful for diagnosing startup issues.

### Access Logs

If running web services, view HTTP access logs and error messages.

## Usage Monitoring

Track resource consumption in real-time.

### Accessing Usage Metrics

1. Navigate to **Usage** tab
2. View dashboards for:

#### CPU Usage

- Current CPU percentage
- Historical 24-hour graph
- Peak usage times
- CPU cores in use

#### RAM Usage

- Current memory consumption
- Total available memory
- Swap usage
- Memory trends over time

#### Network Usage

- Inbound bandwidth
- Outbound bandwidth
- Total data transferred
- Peak traffic times

#### Disk I/O

- Read/write operations per second
- Storage throughput (MB/s)
- Disk utilization percentage

### Setting Usage Alerts

Configure alerts for resource thresholds:

1. Click **Set Alerts**
2. Choose metric (CPU, RAM, bandwidth, disk)
3. Set threshold percentage
4. Choose notification method (email, Discord, etc.)
5. Save

## Billing Management

Handle payments, renewals, and cost optimization.

### Viewing Invoices

1. Navigate to **Billing** tab
2. View all invoices with:
   - Invoice date
   - Amount
   - Due date
   - Status (paid, pending, overdue)
3. Download PDF for records
4. Email invoice to accounting

### Payment Methods

1. Click **Manage Payment Methods**
2. Add credit card, debit card, or crypto wallet
3. Set default payment method
4. Remove old payment methods

Supported payment methods:
- Credit cards (Visa, Mastercard, Amex)
- Bank transfers
- Cryptocurrency (USDC, SOL)
- Custom billing arrangements

### Auto-Renewal Settings

Control automatic billing for VPS renewal:

1. Go to **Billing** > **Auto-Renewal**
2. Toggle **Auto-Renew** on/off
3. Choose renewal frequency:
   - Hourly
   - Daily
   - Monthly
   - Annually (usually discounted)
4. Confirm payment method is valid

Auto-renewal charges occur 24 hours before expiration. If payment fails, your VPS will be suspended until payment is received.

### Cost Breakdown

View detailed cost analysis:

1. Click **Cost Breakdown**
2. See itemized charges:
   - Base VPS cost
   - Resource upgrades (CPU, RAM, storage)
   - Add-on services (Raw Shred Forwarding, backups, etc.)
   - Discounts applied
3. Month-to-date and projected monthly costs

### Billing Alerts

Set alerts for cost thresholds:

1. Click **Budget Alerts**
2. Set monthly spending limit
3. Choose alert frequency
4. Get notified before overages

## Upgrades & Scaling

Scale resources in real-time without downtime.

### Upgrading CPU Cores

1. Navigate to **Upgrades** tab
2. Click **CPU** > **Upgrade**
3. Select new core count
4. Review cost increase
5. Click **Confirm**

Takes effect immediately—no restart required.

### Adding RAM

1. Click **RAM** > **Upgrade**
2. Select new RAM amount
3. Review changes
4. Confirm upgrade

Memory upgrade requires a brief restart (usually <1 minute).

### Increasing Storage

See [Storage Management](#storage-management) section above.

### Downgrading Resources

You can downgrade CPU and RAM at any time:

1. Click **CPU/RAM** > **Downgrade**
2. Select new lower amount
3. Prorated refund will be applied to next billing cycle
4. Confirm

## Collaborators & Team Access

Share access with team members with role-based permissions.

### Inviting Collaborators

1. Navigate to **Collaborators** tab
2. Click **Invite Collaborator**
3. Enter email address
4. Select role:
   - **Admin** - Full access including billing changes
   - **Manager** - Can manage VPS settings but not billing
   - **Viewer** - Read-only access to dashboard
5. Click **Send Invite**

Collaborators receive an email to accept the invitation.

### Managing Collaborator Access

1. View all collaborators
2. Change role: Click collaborator > select new role
3. Remove access: Click **Remove Collaborator**

Removed collaborators immediately lose dashboard access.

### Payment & Billing Authority

Only account owners and billing admins can:
- Add/remove payment methods
- Modify auto-renewal settings
- View detailed billing information

## Support Tickets

Submit technical issues directly through your dashboard.

### Creating a Support Ticket

1. Navigate to **Support** tab
2. Click **Create Ticket**
3. Fill in:
   - **Title** - Brief description of issue
   - **Category** - Performance, connectivity, security, billing, etc.
   - **Description** - Detailed explanation and steps to reproduce
   - **Attachments** - Logs, screenshots, configs (optional)
4. Set **Priority** (Low, Medium, High, Critical)
5. Click **Submit**

### Ticket Status Tracking

Track ticket progress:

| Status | Meaning |
|--------|---------|
| **Open** | Ticket received, awaiting assignment |
| **In Progress** | Support team actively working on issue |
| **Waiting on You** | We need additional info or testing from you |
| **Resolved** | Issue fixed, awaiting your confirmation |
| **Closed** | Ticket complete and verified |

### Expected Response Times

- **Critical** - 1 hour
- **High** - 4 hours
- **Medium** - 24 hours
- **Low** - 48 hours

### Ticket Communication

1. Click ticket to view conversation
2. Add replies and updates
3. Upload new files or logs
4. Attach debug information as needed
5. Mark as resolved when issue is fixed

## Self-Service Management

Most aspects of your VPS can be managed directly without contacting support:
- Firewall rules
- Storage resizing
- Backup/restore
- Resource upgrades
- Payment methods
- Collaborator access

Only contact support for issues beyond your control or technical troubleshooting.

## Best Practices

### Security

- Restrict SSH (port 22) to known IPs
- Use strong firewall rules
- Regularly rotate backups
- Monitor firewall logs for suspicious activity
- Enable resource alerts to detect anomalies

### Performance

- Monitor resource usage regularly
- Upgrade CPU/RAM before hitting limits
- Use SSD storage for high-performance workloads
- Optimize firewall rules (avoid overly permissive rules)
- Schedule backups during low-traffic periods

### Billing

- Set up billing alerts before budget limits
- Review cost breakdown monthly
- Use auto-renewal for uninterrupted service
- Consider longer billing cycles for discounts

## Troubleshooting

### Can't Connect via SSH

- Verify SSH (port 22) is open in firewall
- Check your IP is in the allowed source
- Confirm you're using correct username and key
- Review system logs for connection errors

### High CPU/Memory Usage

- Review running processes on VPS
- Check for resource-intensive services
- Monitor with Usage tab to identify culprits
- Consider scaling up resources if legitimate usage

### Storage Full

- Review disk usage with `df -h` on VPS
- Delete unnecessary files or logs
- Resize disk in Storage tab
- Set up disk space alerts

### Billing Issues

- Verify payment method is valid
- Check auto-renewal is enabled
- Review billing history for errors
- Contact support for disputes

## Getting Help

- **Discord** - Community support and chat
- **Cloud Dashboard** - Submit support tickets
- **Email** - For billing or sensitive issues

---

Next steps:
- [Raw Shred Forwarding](./raw-shred-forwarding.md)
- [Restricted Ports](./restricted-ports.md)
- [Troubleshooting](../support/troubleshooting.md)

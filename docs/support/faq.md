# Frequently Asked Questions

## Pricing & Billing

### How much does gRPC streaming cost?

Pricing varies by tier based on concurrent stream limits. See [https://cloud.solanavibestation.com/pricing](https://cloud.solanavibestation.com/pricing) for current rates. You can also purchase through Discord.

### Are there setup fees?

No. Solana Vibe Station charges only for the services you use. No hidden fees, no setup charges, no minimum contracts.

### Can I upgrade or downgrade my tier?

Yes. You can upgrade immediately in the cloud dashboard. Downgrades take effect at the next billing cycle with a prorated refund.

### What payment methods do you accept?

We accept:
- Credit cards (Visa, Mastercard, American Express)
- Bank transfers
- Cryptocurrency (USDC, SOL)
- Custom billing arrangements for enterprise customers

### Do you offer annual discounts?

Yes. Annual billing typically offers 15-20% savings compared to monthly. Check the cloud dashboard during checkout.

### Can I get a refund?

Refunds are available within 7 days of purchase for unused services. Contact support for refund requests.

## Performance & Reliability

### What's your uptime SLA?

We maintain industry-leading uptime. Check our status page at [status.solanavibestation.com](https://status.solanavibestation.com) for current and historical uptime metrics.

### How fast is your gRPC streaming?

With our Atlanta datacenter colocation and direct-attach SFP+ cables, gRPC latency is typically <1ms to RPC infrastructure. Network latency varies based on your location.

### Do you have DDoS protection?

Yes. Our infrastructure includes network-level DDoS mitigation to protect against large-scale attacks.

### What happens if there's an outage?

All customers are automatically notified via:
- Status page updates
- Discord #status channel
- Email notifications (if configured)
- Cloud dashboard alerts

### How often is data backed up?

VPS backups run automatically once daily. You can also create manual backups anytime. Backups are retained for 7 days.

## Supported Methods & Features

### What subscription types does gRPC support?

gRPC supports:
- Account changes
- Transaction confirmations
- Block production
- Slot updates
- Entry data

See [gRPC Overview](../grpc/overview.md) for detailed information.

### Can I use gRPC for historical data?

gRPC is optimized for real-time streaming. For historical queries, use our RPC API instead. Some tiers include historical data retention.

### Does your RPC support all Solana methods?

We support all standard Solana RPC methods. Some premium methods require higher tiers. Check the API documentation for method-by-tier breakdown.

### Can I run validators on SVS VPS?

Yes. SVS VPS is optimized for validators. You have full control over OS, ports, and network configuration. Raw Shred Forwarding is available as an add-on.

### What operating systems are available?

Standard options include:
- Ubuntu (various versions)
- Debian
- CentOS
- AlmaLinux

Custom OS requests available for enterprise customers.

## Data & History

### How much historical data is retained?

Retention depends on your tier:
- **Starter** - Last 1 day
- **Pro** - Last 7 days
- **Enterprise** - Last 30 days
- Custom retention available

Contact sales for extended history requirements.

### Can I export data from gRPC?

You can consume data via gRPC streaming. Exporting data is up to your application. We recommend writing to local storage or database.

### Is there a data transfer limit?

No hard limits, but we have fair use policies. Enterprise tier customers get custom limits. Contact support for high-volume use cases.

### Can I get historical blockchain data from your RPC?

Yes, within retention windows. Query historical accounts, transactions, blocks using standard Solana RPC methods.

## API Limits

### What are the rate limits?

Rate limits depend on your tier. Check your cloud dashboard or contact support for tier-specific limits.

### What happens when I hit a rate limit?

You'll receive a 429 (Too Many Requests) response. Implement exponential backoff and retry after the specified duration.

### How do I increase my rate limit?

Upgrade to a higher tier in the cloud dashboard. For custom limits, contact our sales team.

### Do rate limits reset?

Rate limits reset on a per-minute basis. For example: 1000 requests per minute means 1000 per 60-second window.

## Technical Questions

### Do I need an API key for gRPC?

No API key needed. Authentication is via IP whitelist only. Whitelist your server IP in the cloud dashboard.

### Can I use gRPC from multiple servers?

Yes. Add all server IPs to your whitelist. You can whitelist individual IPs or CIDR ranges.

### What's the difference between gRPC and RPC?

- **gRPC** - Real-time streaming, lower latency, binary protocol
- **RPC** - Traditional JSON-RPC, query-based, easier integration

Use gRPC for real-time events, RPC for historical queries.

### Can I filter subscriptions on gRPC?

Yes. Each subscription supports custom filters:
- Account owner
- Account address
- Transaction signature
- Slot range
- And more

See [gRPC Streaming Setup](../grpc/streaming-setup.md) for examples.

### What are shreds?

Shreds are fragments of block data transmitted in real-time. Raw Shred Forwarding delivers these to your VPS for archive systems, indexers, and validators.

### Is TLS required for connections?

Yes. All connections must use TLS/SSL encryption (port 443 for gRPC).

## VPS-Specific

### Can I resize my VPS?

Yes. Resize CPU, RAM, or storage anytime. CPU upgrades take effect immediately. Memory upgrades require a brief restart. Storage resizing is seamless.

### What's included in "unlimited bandwidth"?

Standard tier includes high-capacity bandwidth. Extremely unusual usage patterns may be throttled. Contact support for burst requirements.

### Can I use IPv6?

Currently IPv6 support is limited. Contact support if you need IPv6 access.

### Are ports restricted?

Yes, certain ports are restricted for security. See [Restricted Ports](../vps-cloud/restricted-ports.md) for details.

### Can I install any software?

Yes. You have full root/sudo access. Install any software compatible with your OS. Some ports are restricted—see restricted ports guide.

### Do you provide managed services?

No, VPS is unmanaged. You control your OS, software, and configurations. We provide infrastructure and support.

## Account & Access

### How many people can access my account?

Add unlimited collaborators in the cloud dashboard. Set role-based permissions:
- Admin (full access)
- Manager (service management)
- Viewer (read-only)

### Can I change my account email?

Contact support to change your account email. We'll need to verify your identity.

### What if I forget my password?

Use "Forgot Password" on the login page. You'll receive a reset link via email.

### How do I secure my account?

- Use a strong password
- Enable 2FA if available
- Limit collaborator access
- Monitor IP whitelist
- Review access logs regularly

### Can I delete my account?

Yes. Contact support to request account deletion. All services will be terminated and data deleted.

## Support & Community

### How do I get support?

Multiple channels:
- **Discord** - Fastest for community help
- **Cloud Dashboard** - Submit technical tickets
- **Email** - For sensitive issues

### What are response times?

- Critical: 1 hour
- High: 4 hours
- Medium: 24 hours
- Low: 48 hours

### Is there a Discord community?

Yes! Join [https://discord.gg/solanavibestation](https://discord.gg/solanavibestation) for real-time support, discussions, and updates.

### Can I report security issues?

Yes. For security concerns:
- Don't post publicly
- DM security team on Discord
- Email security@solanavibestation.com

Thank you for reporting responsibly.

### Is there documentation beyond this?

Yes. Check the full documentation at [docs.solanavibestation.com](https://docs.solanavibestation.com) for detailed guides.

## Troubleshooting

### My connection is timing out

1. Verify your IP is whitelisted
2. Check firewall allows outbound HTTPS (443)
3. Try from a different network
4. Contact support with error details

See [Troubleshooting Guide](./troubleshooting.md) for detailed help.

### I can't see my gRPC data

1. Verify IP whitelist is configured
2. Confirm your subscription filters are correct
3. Check if data exists for your query
4. Review service logs for errors

### My VPS is down

1. Check cloud dashboard status
2. Verify you haven't exceeded disk space
3. Check if auto-renewal payment failed
4. Contact support immediately

### Rate limiting is blocking me

1. Implement exponential backoff
2. Batch requests together
3. Upgrade to higher tier
4. Contact sales for custom limits

## Sales & Enterprise

### Do you offer custom tiers?

Yes. Contact our sales team at sales@solanavibestation.com for:
- Custom rate limits
- Extended history retention
- Private infrastructure
- Custom SLAs
- Volume discounts

### Do you offer on-premise solutions?

Not currently. All services run in our Atlanta datacenter. Contact sales to discuss enterprise options.

### What's your typical customer?

We serve:
- Solana validators
- RPC providers
- Data indexers
- Trading firms
- Web3 applications
- Blockchain researchers

### Can I get a demo?

Yes. Contact sales@solanavibestation.com to schedule a demo and discuss your needs.

### Do you have case studies?

Yes. Check our website for customer success stories. You can also ask in Discord about real-world implementations.

## Miscellaneous

### Can I use gRPC with the Solana CLI?

The Solana CLI doesn't natively support gRPC. Use our RPC endpoint or integrate gRPC client libraries in your application.

### What's the difference between gRPC Streaming and gRPC Reflection?

gRPC Streaming is for consuming real-time blockchain events. Reflection is a protocol feature we support for introspection.

### How do I contribute to SVS?

We're always looking for:
- Community feedback
- Bug reports
- Documentation improvements
- Community tools and integrations

Join Discord to get involved!

### Is SVS open source?

Parts of our infrastructure are open source. Check GitHub for public repositories. Core services are proprietary.

### When will feature X be available?

Check the Discord #roadmap channel for upcoming features. Suggest features in #feature-requests.

## Still Have Questions?

Didn't find your answer? Contact us:
- **Discord** - [Join our server](https://discord.gg/solanavibestation)
- **Support Ticket** - Create one in cloud dashboard
- **Email** - support@solanavibestation.com

---

Last updated: February 2026

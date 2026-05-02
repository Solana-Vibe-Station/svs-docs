# Historical Data

Solana Vibe Station provides fast access to historical blockchain data through dedicated on-premise servers in Atlanta, GA. All historical data is stored locally, enabling significantly faster retrieval compared to cloud-based RPC providers.

## What is Historical Data?

Historical data refers to information about blocks, transactions, and accounts from the blockchain's past. This includes:

- Block contents and metadata
- Transaction details and execution results
- Account states at specific points in time
- Transaction signatures and confirmation statuses
- Slot information and timing

Historical data is essential for:
- Blockchain explorers and analysis tools
- Compliance and auditing
- Building on-chain indices
- Recovering transaction details
- Analyzing trading activity

## Accessing Historical Data

### Endpoint

Historical data is accessed via the `/historical` path on any standard RPC endpoint:

```
https://{tier}.rpc.solanavibestation.com/historical
```

Example URLs:
- `https://basic.rpc.solanavibestation.com/historical`
- `https://elite.rpc.solanavibestation.com/historical`

### Request Format

Historical data requests use the standard Solana JSON-RPC format:

```bash
curl -X POST https://basic.rpc.solanavibestation.com/historical \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getBlock",
    "params": [12345678]
  }'
```

## Supported Methods

The following methods are available on the `/historical` endpoint:

| Method | Description | Use Case |
|--------|-------------|----------|
| `getBlock` | Retrieve all transactions and metadata for a specific block | Analyze block contents |
| `getBlocks` | Retrieve a range of block numbers | Index historical blocks |
| `getBlockTime` | Get the estimated time when a block was created | Timeline queries |
| `getBlocksWithLimit` | Get a range of blocks with a result limit | Paginate through blocks |
| `getFirstAvailableBlock` | Get the first block available in the ledger | Determine data availability |
| `getSignaturesForAddress` | Get transaction signatures for an address | Find all address transactions |
| `getSignatureStatuses` | Get confirmation status of transactions | Verify transaction finality |
| `getSlot` | Get the current or historical slot number | Timing information |
| `getTransaction` | Get detailed information for a specific transaction | Retrieve transaction data |

## Commitment Level

Historical data requests only support the `finalized` commitment level. This ensures you receive only fully committed, irreversible blockchain data.

If you omit the commitment parameter, it defaults to `finalized`:

```javascript
{
  "method": "getTransaction",
  "params": ["SIGNATURE"], // commitment defaults to "finalized"
}

// Explicit finalized commitment
{
  "method": "getTransaction",
  "params": ["SIGNATURE", { "commitment": "finalized" }],
}
```

## Performance Characteristics

Historical data queries on SVS are significantly faster than cloud-based alternatives because:

1. **Local Storage**: All data is stored on dedicated on-premise servers in Atlanta
2. **No Network Hops**: Direct access without routing through multiple cloud regions
3. **Optimized Indexing**: Data is indexed for rapid retrieval by block, transaction, or account
4. **Dedicated Hardware**: Servers are optimized exclusively for historical queries

Typical performance:
- **getBlock**: 10-50ms
- **getTransaction**: 5-20ms
- **getSignaturesForAddress**: 50-200ms (depends on address activity)

Performance varies based on network load and query complexity.

## Example: Fetch a Historical Block

```bash
curl -X POST https://basic.rpc.solanavibestation.com/historical \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getBlock",
    "params": [
      234567890,
      {
        "encoding": "json",
        "maxSupportedTransactionVersion": 0
      }
    ]
  }'
```

Response includes:
- `parentSlot`: Previous block slot
- `blockTime`: Unix timestamp
- `transactions`: All transactions in the block
- `rewards`: Validator rewards (if any)

## Example: Get All Transactions for an Address

Retrieve all transaction signatures for a specific address:

```javascript
async function getAddressHistory(address) {
  const response = await fetch(
    "https://basic.rpc.solanavibestation.com/historical",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "getSignaturesForAddress",
        params: [
          address,
          {
            limit: 100, // Max 1000, default 1000
            before: undefined, // Optional: signature to start before
            until: undefined, // Optional: signature to end at
            commitment: "finalized",
          },
        ],
      }),
    }
  );

  const data = await response.json();
  return data.result; // Array of signature objects
}

// Usage
const signatures = await getAddressHistory(
  "11111111111111111111111111111111"
);
signatures.forEach((sig) => {
  console.log(`Signature: ${sig.signature}`);
  console.log(`Block Time: ${sig.blockTime}`);
  console.log(`Status: ${sig.err ? "Failed" : "Success"}`);
});
```

## Example: Retrieve a Historical Transaction

Get full details of a specific transaction:

```javascript
async function getTransactionDetails(signature) {
  const response = await fetch(
    "https://basic.rpc.solanavibestation.com/historical",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "getTransaction",
        params: [
          signature,
          {
            encoding: "json",
            maxSupportedTransactionVersion: 0,
            commitment: "finalized",
          },
        ],
      }),
    }
  );

  const data = await response.json();
  const tx = data.result;

  console.log(`Slot: ${tx.slot}`);
  console.log(`Block Time: ${tx.blockTime}`);
  console.log(`Confirmations: ${tx.confirmations}`);

  // Metadata
  const meta = tx.transaction.meta;
  console.log(`Fee: ${meta.fee} lamports`);
  console.log(`Status: ${meta.err ? "Failed" : "Success"}`);

  // Instructions
  const instructions = tx.transaction.message.instructions;
  console.log(`Instructions: ${instructions.length}`);

  return tx;
}
```

## Example: Paginate Through Historical Blocks

Iterate through blocks in a range:

```javascript
async function indexBlocks(startSlot, endSlot) {
  const blocks = [];

  for (let slot = startSlot; slot <= endSlot; slot += 1000) {
    const response = await fetch(
      "https://basic.rpc.solanavibestation.com/historical",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: 1,
          method: "getBlocksWithLimit",
          params: [
            slot,
            1000, // Max 1000 blocks per request
            { commitment: "finalized" },
          ],
        }),
      }
    );

    const data = await response.json();
    const blockSlots = data.result;

    if (!blockSlots || blockSlots.length === 0) break;

    for (const blockSlot of blockSlots) {
      const blockData = await getBlock(blockSlot);
      blocks.push(blockData);
    }

    console.log(`Indexed ${blocks.length} blocks...`);
  }

  return blocks;
}
```

## Data Availability

The first available block in the SVS ledger can be queried with:

```bash
curl -X POST https://basic.rpc.solanavibestation.com/historical \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getFirstAvailableBlock",
    "params": []
  }'
```

This returns the slot number of the earliest available block. All blocks from this slot forward are queryable via the historical endpoint.

## Rate Limits

Historical data requests are subject to the same rate limits as standard RPC requests on your tier. However, historical queries may incur slightly higher resource usage due to data volume.

For tier-specific limits, see [RPC Services Overview](./overview.md).

## Best Practices

1. **Batch Requests**: Use `getBlocks` and `getBlocksWithLimit` to fetch multiple blocks efficiently
2. **Cache Results**: Store historical data locally to avoid repeated queries
3. **Pagination**: Use `before` and `until` parameters to paginate signature queries
4. **Error Handling**: Handle missing blocks or transactions gracefully (they may have been pruned)
5. **Monitor Performance**: Track query times and adjust batch sizes if needed

## Limitations

- Only `finalized` commitment is supported
- Some very old blocks may not be available (outside the retention period)
- Maximum 1000 signatures per request for `getSignaturesForAddress`
- Maximum 1000 blocks per request for `getBlocksWithLimit`
- Transaction data is only available for finalized transactions

## OpenAPI Specification

The complete OpenAPI specification for historical methods is available at `/api-specs/historical-rpc.yaml`.

## Pricing

Historical data access is included in all RPC tier subscriptions. No additional cost for using the `/historical` endpoint.

## Need Help?

For questions about historical data access or indexing strategies, see [Support](../support.md).

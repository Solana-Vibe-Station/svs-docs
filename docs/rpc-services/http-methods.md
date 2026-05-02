# Supported HTTP RPC Methods

Solana Vibe Station supports all standard Solana JSON-RPC methods. This page lists the complete set of available HTTP methods with brief descriptions. For detailed parameter documentation, method examples, and response schemas, refer to the official [Solana RPC API documentation](https://solana.com/docs/rpc/).

## Account Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| `getAccountInfo` | Retrieve information about an account including balance and data | [Docs](https://solana.com/docs/rpc/http/getAccountInfo) |
| `getMultipleAccounts` | Retrieve information for multiple accounts in a single request | [Docs](https://solana.com/docs/rpc/http/getMultipleAccounts) |
| `getProgramAccounts` | Retrieve all accounts owned by a specific program | [Docs](https://solana.com/docs/rpc/http/getProgramAccounts) |
| `getTokenAccountBalance` | Retrieve the balance of a token account | [Docs](https://solana.com/docs/rpc/http/getTokenAccountBalance) |
| `getTokenAccountsByDelegate` | Get all token accounts by delegate | [Docs](https://solana.com/docs/rpc/http/getTokenAccountsByDelegate) |
| `getTokenAccountsByOwner` | Get all token accounts for a specific owner | [Docs](https://solana.com/docs/rpc/http/getTokenAccountsByOwner) |
| `getTokenLargestAccounts` | Retrieve the largest token accounts for a specific mint | [Docs](https://solana.com/docs/rpc/http/getTokenLargestAccounts) |
| `getTokenSupply` | Retrieve the total supply of a token | [Docs](https://solana.com/docs/rpc/http/getTokenSupply) |

## Block Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| `getBlock` | Retrieve detailed information about a specific block | [Docs](https://solana.com/docs/rpc/http/getBlock) |
| `getBlockHeight` | Retrieve the current block height | [Docs](https://solana.com/docs/rpc/http/getBlockHeight) |
| `getBlocks` | Retrieve a range of confirmed block numbers | [Docs](https://solana.com/docs/rpc/http/getBlocks) |
| `getBlocksWithLimit` | Retrieve confirmed blocks with a limit | [Docs](https://solana.com/docs/rpc/http/getBlocksWithLimit) |
| `getBlockTime` | Retrieve the estimated time when a block was created | [Docs](https://solana.com/docs/rpc/http/getBlockTime) |

## Cluster Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| `getClusterNodes` | Retrieve information about all nodes in the cluster | [Docs](https://solana.com/docs/rpc/http/getClusterNodes) |
| `getEpochInfo` | Retrieve information about the current epoch | [Docs](https://solana.com/docs/rpc/http/getEpochInfo) |
| `getEpochSchedule` | Retrieve the schedule of the current epoch | [Docs](https://solana.com/docs/rpc/http/getEpochSchedule) |
| `getGenesisHash` | Retrieve the hash of the genesis block | [Docs](https://solana.com/docs/rpc/http/getGenesisHash) |
| `getHealth` | Retrieve the health status of the node | [Docs](https://solana.com/docs/rpc/http/getHealth) |
| `getVersion` | Retrieve the version of the Solana node | [Docs](https://solana.com/docs/rpc/http/getVersion) |

## Fee Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| `getFeeForMessage` | Retrieve the estimated fee for a specific message | [Docs](https://solana.com/docs/rpc/http/getFeeForMessage) |
| `getRecentBlockhash` | Retrieve the recent blockhash and fee calculator | [Docs](https://solana.com/docs/rpc/http/getRecentBlockhash) |
| `getLatestBlockhash` | Retrieve the latest blockhash | [Docs](https://solana.com/docs/rpc/http/getLatestBlockhash) |
| `getMinimumBalanceForRentExemption` | Retrieve the minimum balance required to avoid rent | [Docs](https://solana.com/docs/rpc/http/getMinimumBalanceForRentExemption) |

## Program Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| `simulateTransaction` | Simulate a transaction without committing it | [Docs](https://solana.com/docs/rpc/http/simulateTransaction) |
| `sendTransaction` | Submit a signed transaction to the network | [Docs](https://solana.com/docs/rpc/http/sendTransaction) |

## Slot Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| `getSlot` | Retrieve the current slot | [Docs](https://solana.com/docs/rpc/http/getSlot) |
| `getSlotLeader` | Retrieve the public key of the slot leader | [Docs](https://solana.com/docs/rpc/http/getSlotLeader) |
| `getSlotLeaders` | Retrieve the slot leaders for a range of slots | [Docs](https://solana.com/docs/rpc/http/getSlotLeaders) |

## Stake Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| `getStakeActivation` | Retrieve the activation status of a stake account | [Docs](https://solana.com/docs/rpc/http/getStakeActivation) |
| `getStakeMinimumDelegation` | Retrieve the minimum delegation amount for stake accounts | [Docs](https://solana.com/docs/rpc/http/getStakeMinimumDelegation) |

## Transaction Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| `getSignaturesForAddress` | Retrieve signatures for an address | [Docs](https://solana.com/docs/rpc/http/getSignaturesForAddress) |
| `getSignatureStatuses` | Retrieve confirmation status of multiple transactions | [Docs](https://solana.com/docs/rpc/http/getSignatureStatuses) |
| `getTransaction` | Retrieve detailed information about a transaction | [Docs](https://solana.com/docs/rpc/http/getTransaction) |
| `getTransactionCount` | Retrieve the transaction count | [Docs](https://solana.com/docs/rpc/http/getTransactionCount) |

## Validator Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| `getVoteAccounts` | Retrieve information about all vote accounts | [Docs](https://solana.com/docs/rpc/http/getVoteAccounts) |

## Other Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| `getBalance` | Retrieve the balance of an account in lamports | [Docs](https://solana.com/docs/rpc/http/getBalance) |
| `getInflationGovernor` | Retrieve information about the inflation governor | [Docs](https://solana.com/docs/rpc/http/getInflationGovernor) |
| `getInflationRate` | Retrieve the current inflation rate | [Docs](https://solana.com/docs/rpc/http/getInflationRate) |
| `getInflationReward` | Retrieve inflation rewards for validators | [Docs](https://solana.com/docs/rpc/http/getInflationReward) |
| `getSupply` | Retrieve the total supply of SOL | [Docs](https://solana.com/docs/rpc/http/getSupply) |
| `getLargestAccounts` | Retrieve the largest accounts by balance | [Docs](https://solana.com/docs/rpc/http/getLargestAccounts) |
| `requestAirdrop` | Request an airdrop (testnet/devnet only) | [Docs](https://solana.com/docs/rpc/http/requestAirdrop) |

## Commitment Levels

All methods support optional commitment parameters to specify the level of transaction finality:

- `processed`: Most recent block processed by the node
- `confirmed`: Block confirmed by the cluster (66%+ stake)
- `finalized`: Block finalized by the cluster (>95% stake)

Default: `finalized`

## Making Requests

All HTTP methods use JSON-RPC 2.0 over POST. Example:

```bash
curl -X POST https://basic.rpc.solanavibestation.com \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getBalance",
    "params": ["11111111111111111111111111111111"]
  }'
```

## OpenAPI Specification

The complete OpenAPI specification for all RPC methods is available at `/api-specs/solana-rpc.yaml`. This specification includes detailed parameter schemas, response types, and examples for all supported methods.

## SVS-Specific Behavior

- **Authentication**: Optional via `Authorization` header or `api_key` query parameter (see [Authentication Guide](../getting-started/authentication.md))
- **Rate Limits**: Depend on your service tier (see [RPC Services Overview](./overview.md))
- **Historical Data**: Access via the `/historical` path for fast retrieval of historical blocks and transactions (see [Historical Data](./historical.md))

## Not Supported

The following methods are not currently supported on SVS RPC:

- `accountNotify` (deprecated)
- `programNotify` (deprecated)
- `slotNotify` (deprecated)
- `logsNotify` (deprecated)

Use WebSocket subscriptions instead (see [WebSocket Methods](./websocket-methods.md)).

## Need Help?

For questions about specific methods or integration examples, see the [Support](../support.md) section or refer to the [Solana documentation](https://solana.com/docs/rpc/).

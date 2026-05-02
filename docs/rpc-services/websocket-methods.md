# Supported WebSocket Methods

Solana Vibe Station provides full WebSocket support for real-time subscriptions to blockchain events. WebSocket connections enable efficient streaming of account changes, block notifications, transaction signatures, logs, and more without polling.

## WebSocket Endpoint

Connect to the WebSocket endpoint using the same tier as your HTTP requests:

```
wss://{tier}.rpc.solanavibestation.com
```

Example WebSocket endpoints:
- `wss://public.rpc.solanavibestation.com`
- `wss://basic.rpc.solanavibestation.com`
- `wss://elite.rpc.solanavibestation.com`

## Supported Subscription Methods

### Account Subscriptions

| Method | Description | Reference |
|--------|-------------|-----------|
| `accountSubscribe` | Subscribe to changes on a specific account | [Docs](https://solana.com/docs/rpc/websocket/accountSubscribe) |
| `accountUnsubscribe` | Unsubscribe from an account subscription | [Docs](https://solana.com/docs/rpc/websocket/accountUnsubscribe) |

### Block Subscriptions

| Method | Description | Reference |
|--------|-------------|-----------|
| `blockSubscribe` | Subscribe to block notifications | [Docs](https://solana.com/docs/rpc/websocket/blockSubscribe) |
| `blockUnsubscribe` | Unsubscribe from block notifications | [Docs](https://solana.com/docs/rpc/websocket/blockUnsubscribe) |

### Logs Subscriptions

| Method | Description | Reference |
|--------|-------------|-----------|
| `logsSubscribe` | Subscribe to transaction logs matching a filter | [Docs](https://solana.com/docs/rpc/websocket/logsSubscribe) |
| `logsUnsubscribe` | Unsubscribe from a logs subscription | [Docs](https://solana.com/docs/rpc/websocket/logsUnsubscribe) |

### Program Subscriptions

| Method | Description | Reference |
|--------|-------------|-----------|
| `programSubscribe` | Subscribe to account changes for a specific program | [Docs](https://solana.com/docs/rpc/websocket/programSubscribe) |
| `programUnsubscribe` | Unsubscribe from a program subscription | [Docs](https://solana.com/docs/rpc/websocket/programUnsubscribe) |

### Root Subscriptions

| Method | Description | Reference |
|--------|-------------|-----------|
| `rootSubscribe` | Subscribe to root updates (finalized blocks) | [Docs](https://solana.com/docs/rpc/websocket/rootSubscribe) |
| `rootUnsubscribe` | Unsubscribe from root updates | [Docs](https://solana.com/docs/rpc/websocket/rootUnsubscribe) |

### Signature Subscriptions

| Method | Description | Reference |
|--------|-------------|-----------|
| `signatureSubscribe` | Subscribe to status updates for a specific transaction | [Docs](https://solana.com/docs/rpc/websocket/signatureSubscribe) |
| `signatureUnsubscribe` | Unsubscribe from a signature subscription | [Docs](https://solana.com/docs/rpc/websocket/signatureUnsubscribe) |

### Slot Subscriptions

| Method | Description | Reference |
|--------|-------------|-----------|
| `slotSubscribe` | Subscribe to slot updates | [Docs](https://solana.com/docs/rpc/websocket/slotSubscribe) |
| `slotUnsubscribe` | Unsubscribe from slot updates | [Docs](https://solana.com/docs/rpc/websocket/slotUnsubscribe) |

### Vote Subscriptions

| Method | Description | Reference |
|--------|-------------|-----------|
| `voteSubscribe` | Subscribe to vote notifications | [Docs](https://solana.com/docs/rpc/websocket/voteSubscribe) |
| `voteUnsubscribe` | Unsubscribe from vote notifications | [Docs](https://solana.com/docs/rpc/websocket/voteUnsubscribe) |

## Quick Start: WebSocket Connection

Here's a simple example of connecting to SVS WebSocket and subscribing to slot updates:

```javascript
// Using Node.js or browser with WebSocket support
const WebSocket = require("ws"); // npm install ws

async function subscribeToSlots() {
  // Connect to WebSocket endpoint
  const ws = new WebSocket("wss://basic.rpc.solanavibestation.com");

  ws.on("open", () => {
    console.log("Connected to SVS WebSocket");

    // Subscribe to slot updates
    ws.send(
      JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "slotSubscribe",
      })
    );
  });

  ws.on("message", (data) => {
    const message = JSON.parse(data);

    // Handle subscription result
    if (message.result) {
      console.log("Subscription ID:", message.result);
    }

    // Handle slot updates
    if (message.params) {
      const { slot, parent, root } = message.params.result;
      console.log(`Slot: ${slot}, Parent: ${parent}, Root: ${root}`);
    }
  });

  ws.on("error", (error) => {
    console.error("WebSocket error:", error);
  });

  ws.on("close", () => {
    console.log("Disconnected from SVS WebSocket");
  });
}

subscribeToSlots();
```

## Example: Account Subscription

Monitor an account for changes:

```javascript
const WebSocket = require("ws");

async function watchAccount(accountAddress) {
  const ws = new WebSocket("wss://basic.rpc.solanavibestation.com");

  ws.on("open", () => {
    // Subscribe to account changes
    ws.send(
      JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "accountSubscribe",
        params: [
          accountAddress,
          {
            encoding: "base64",
            commitment: "confirmed",
          },
        ],
      })
    );
  });

  ws.on("message", (data) => {
    const message = JSON.parse(data);

    if (message.params && message.params.result) {
      const { value } = message.params.result;
      console.log(`Account lamports: ${value.lamports}`);
      console.log(`Account owner: ${value.owner}`);
      console.log(`Account data length: ${value.data[0].length}`);
    }
  });
}

watchAccount("11111111111111111111111111111111");
```

## Example: Transaction Signature Subscription

Track confirmation of a specific transaction:

```javascript
const WebSocket = require("ws");

async function trackTransaction(signatureString) {
  const ws = new WebSocket("wss://basic.rpc.solanavibestation.com");

  ws.on("open", () => {
    // Subscribe to signature updates
    ws.send(
      JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "signatureSubscribe",
        params: [
          signatureString,
          {
            commitment: "finalized",
          },
        ],
      })
    );
  });

  ws.on("message", (data) => {
    const message = JSON.parse(data);

    if (message.params && message.params.result) {
      const { err, confirmations } = message.params.result.value;

      if (err) {
        console.log("Transaction failed:", err);
        ws.close();
      } else {
        console.log(`Confirmations: ${confirmations || "finalized"}`);
        if (confirmations === null) {
          console.log("Transaction finalized!");
          ws.close();
        }
      }
    }
  });
}

trackTransaction("YOUR_TRANSACTION_SIGNATURE");
```

## Example: Program Subscription

Monitor all changes to accounts owned by a specific program:

```javascript
const WebSocket = require("ws");

async function watchProgram(programAddress) {
  const ws = new WebSocket("wss://basic.rpc.solanavibestation.com");

  ws.on("open", () => {
    // Subscribe to program account changes
    ws.send(
      JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "programSubscribe",
        params: [
          programAddress,
          {
            encoding: "base64",
            commitment: "confirmed",
          },
        ],
      })
    );
  });

  ws.on("message", (data) => {
    const message = JSON.parse(data);

    if (message.params && message.params.result) {
      const { pubkey, account } = message.params.result.value;
      console.log(`Updated account: ${pubkey}`);
      console.log(`New balance: ${account.lamports} lamports`);
    }
  });
}

watchProgram("11111111111111111111111111111111");
```

## Commitment Levels

WebSocket subscriptions support the same commitment levels as HTTP methods:

- `processed`: Most recent block processed by the node
- `confirmed`: Block confirmed by the cluster
- `finalized`: Block finalized by the cluster (default)

Specify commitment in the params array:

```javascript
ws.send(
  JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "slotSubscribe",
    params: [{ commitment: "confirmed" }],
  })
);
```

## Best Practices

1. **Connection Management**: Implement automatic reconnection with exponential backoff
2. **Error Handling**: Handle connection errors and subscription failures gracefully
3. **Resource Limits**: Monitor the number of active subscriptions; close subscriptions when no longer needed
4. **Message Rate**: Be prepared for high message rates during periods of network activity
5. **Unsubscribe**: Always unsubscribe before closing a connection to free resources

## Connection Limits

Each tier has connection and subscription limits:

- **Public**: Limited connections, suitable for individual development
- **Lite**: Moderate connection limits
- **Basic**: Standard production limits
- **Ultra**: High-frequency application limits
- **Elite**: Enterprise-grade limits

For specific limits on your tier, see [RPC Services Overview](./overview.md) or contact [Support](../support.md).

## Full Documentation

For detailed information about each WebSocket method, parameters, response formats, and examples, refer to the official [Solana WebSocket API documentation](https://solana.com/docs/rpc/websocket/).

## Need Help?

For questions about WebSocket connections or subscription patterns, see [Support](../support.md).

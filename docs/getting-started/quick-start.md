# Quick Start

Get your first Solana Vibe Station API call working in under 5 minutes.

## Step 1: Get Your Endpoint

Solana Vibe Station RPC endpoints are organized by tier. For testing and development, start with the **public** endpoint:

```
https://public.rpc.solanavibestation.com
```

For production workloads, check [Pricing](https://cloud.solanavibestation.com) to choose a tier (lite, basic, ultra, elite, epic) and get your authenticated endpoint.

See [Endpoints](./endpoints.md) for the complete reference of all available endpoints.

## Step 2: Get Your API Key

- **Public Tier**: No API key required
- **Other Tiers**: Get your API key from [cloud.solanavibestation.com](https://cloud.solanavibestation.com)

See [Authentication](./authentication.md) for details on how to use your API key.

## Step 3: Make Your First RPC Call

Choose your language and follow along.

### JavaScript (Web3.js)

Install the Solana web3 library:

```bash
npm install @solana/web3.js
```

Create a file `test.js`:

```javascript
const web3 = require("@solana/web3.js");

const connection = new web3.Connection(
  "https://public.rpc.solanavibestation.com",
  "confirmed"
);

// Example 1: Get balance of a public key
async function getBalance() {
  const publicKey = new web3.PublicKey(
    "TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq"
  );
  const balance = await connection.getBalance(publicKey);
  console.log("Balance:", balance, "lamports");
}

// Example 2: Get latest block hash
async function getLatestBlockhash() {
  const blockHash = await connection.getLatestBlockhash();
  console.log("Latest blockhash:", blockHash.blockhash);
  console.log("Last valid block height:", blockHash.lastValidBlockHeight);
}

async function main() {
  console.log("Connecting to Solana Vibe Station...");
  await getBalance();
  await getLatestBlockhash();
}

main().catch(console.error);
```

Run it:

```bash
node test.js
```

### Python

Install the Solana Python SDK:

```bash
pip install solders solana
```

Create a file `test.py`:

```python
from solders.pubkey import Pubkey
from solana.rpc.api import Client

client = Client("https://public.rpc.solanavibestation.com")

# Example 1: Get balance
def get_balance():
    pubkey = Pubkey("TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq")
    balance = client.get_balance(pubkey)
    print(f"Balance: {balance.value} lamports")

# Example 2: Get latest blockhash
def get_latest_blockhash():
    response = client.get_latest_blockhash()
    print(f"Latest blockhash: {response.value.blockhash}")
    print(f"Last valid block height: {response.value.last_valid_block_height}")

if __name__ == "__main__":
    print("Connecting to Solana Vibe Station...")
    get_balance()
    get_latest_blockhash()
```

Run it:

```bash
python test.py
```

### cURL

Get a balance:

```bash
curl -X POST https://public.rpc.solanavibestation.com \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getBalance",
    "params": ["TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq"]
  }'
```

Get the latest blockhash:

```bash
curl -X POST https://public.rpc.solanavibestation.com \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getLatestBlockhash",
    "params": []
  }'
```

## Next Steps

- **Explore RPC Methods**: Solana Vibe Station supports the full Solana RPC API. See the [Solana RPC documentation](https://docs.solana.com/api) for all available methods.
- **Use WebSocket for Real-Time Data**: See [Endpoints](./endpoints.md) for WebSocket URLs and use `connection.onAccountChange()` or `connection.onLogs()` for subscriptions.
- **Get an API Key**: For production, upgrade to a paid tier at [cloud.solanavibestation.com](https://cloud.solanavibestation.com) and use your API key with the examples above.
- **Learn About Rate Limits**: See [Rate Limits](./rate-limits.md) to understand fair use policies.
- **Use Lightspeed Transactions**: See the transactions guide for priority transaction handling.

You're now connected to Solana Vibe Station! Happy building.

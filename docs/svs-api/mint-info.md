# Mint Info Endpoint

The `/mint_info` endpoint provides comprehensive information for recently launched tokens, including creation details, creator information, and complete trade history. Query up to 36 tokens in a single request.

## Endpoint

```
POST https://beta-api.solanavibestation.com/mint_info
```

## Request

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mints` | array | yes | Array of token mint addresses (max 36 per request) |

### Example Request

```bash
curl -X POST https://beta-api.solanavibestation.com/mint_info \
  -H "Content-Type: application/json" \
  -H "Authorization: YOUR_API_KEY" \
  -d '{
    "mints": [
      "7kXYNH3x8R2c4RqBatUSUhXYqEV4qTKMQ2n8TaGCc2t",
      "9n4nbM75f5Ui33ZbPYRq59NoJd9dsNEUTwuKeS5v5Qo"
    ]
  }'
```

### JavaScript Example

```javascript
async function getMintInfo(mints) {
  const response = await fetch(
    "https://beta-api.solanavibestation.com/mint_info",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "YOUR_API_KEY",
      },
      body: JSON.stringify({ mints }),
    }
  );

  const result = await response.json();

  if (!result.success) {
    console.error("API Error:", result.errors);
    return null;
  }

  return result.data;
}

// Usage
const info = await getMintInfo(["7kXYNH3x8R2c4RqBatUSUhXYqEV4qTKMQ2n8TaGCc2t"]);
console.log(info);
```

## Response

### Response Schema

```json
{
  "success": true,
  "data": {
    "mint_address": {
      "mint": "string",
      "name": "string",
      "symbol": "string",
      "uri": "string",
      "creator": "string",
      "timestamp": number,
      "off_chain_metadata": {
        "image": "string",
        "description": "string",
        "social_links": {
          "twitter": "string",
          "telegram": "string",
          "discord": "string",
          "website": "string"
        }
      },
      "trade_events": [
        {
          "timestamp": number,
          "user": "string",
          "sol_amount": number,
          "token_amount": number,
          "is_buy": boolean
        }
      ]
    }
  },
  "errors": {
    "not_found": ["mint_address"],
    "invalid_format": ["mint_address"]
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `mint` | string | Token mint address |
| `name` | string | Token name |
| `symbol` | string | Token symbol |
| `uri` | string | URI to on-chain metadata |
| `creator` | string | Public key of token creator (pump.fun launcher) |
| `timestamp` | number | Unix timestamp when token was created |
| `off_chain_metadata.image` | string | URL to token logo/image |
| `off_chain_metadata.description` | string | Token description |
| `off_chain_metadata.social_links` | object | Social media and website links |
| `trade_events` | array | Complete trade history for the token |
| `trade_events[].timestamp` | number | Unix timestamp of trade |
| `trade_events[].user` | string | Public key of trader |
| `trade_events[].sol_amount` | number | Amount of SOL in trade |
| `trade_events[].token_amount` | number | Amount of token in trade |
| `trade_events[].is_buy` | boolean | True if buy, false if sell |

## Example Response

```json
{
  "success": true,
  "data": {
    "7kXYNH3x8R2c4RqBatUSUhXYqEV4qTKMQ2n8TaGCc2t": {
      "mint": "7kXYNH3x8R2c4RqBatUSUhXYqEV4qTKMQ2n8TaGCc2t",
      "name": "Example Token",
      "symbol": "EXM",
      "uri": "https://pump.fun/ipfs/QmXxxx",
      "creator": "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6",
      "timestamp": 1708101234,
      "off_chain_metadata": {
        "image": "https://pump.fun/ipfs/QmXxxx/image.png",
        "description": "A brand new token on Solana",
        "social_links": {
          "twitter": "https://twitter.com/exampletoken",
          "telegram": "https://t.me/exampletoken",
          "discord": "https://discord.gg/exampletoken",
          "website": "https://example.com"
        }
      },
      "trade_events": [
        {
          "timestamp": 1708101234,
          "user": "UserABC123...",
          "sol_amount": 2.5,
          "token_amount": 1000000,
          "is_buy": true
        },
        {
          "timestamp": 1708101245,
          "user": "UserDEF456...",
          "sol_amount": 5.0,
          "token_amount": 1500000,
          "is_buy": true
        },
        {
          "timestamp": 1708101256,
          "user": "UserABC123...",
          "sol_amount": 1.2,
          "token_amount": 500000,
          "is_buy": false
        }
      ]
    }
  },
  "errors": {}
}
```

## Token Source Coverage

The `/mint_info` endpoint currently indexes tokens launched via **pump.fun**. Additional launch platforms are added based on customer demand — if you need coverage for another source, let us know via [Contact](../support/contact.md).

## Use Cases

### Analyze Early Trading Activity

```javascript
async function analyzeEarlyTrading(mint) {
  const info = await getMintInfo([mint]);
  const token = info[mint];

  if (!token || !token.trade_events) {
    return null;
  }

  const firstTrade = token.trade_events[0];
  const lastTrade = token.trade_events[token.trade_events.length - 1];

  return {
    createdAt: new Date(token.timestamp * 1000),
    firstTradeAt: new Date(firstTrade.timestamp * 1000),
    totalTrades: token.trade_events.length,
    totalSolVolume: token.trade_events.reduce((sum, e) => sum + e.sol_amount, 0),
    buyCount: token.trade_events.filter((e) => e.is_buy).length,
    sellCount: token.trade_events.filter((e) => !e.is_buy).length,
    timeToFirstTrade: (firstTrade.timestamp - token.timestamp) / 60, // minutes
  };
}
```

### Detect Insider Selling or Holder Lockups

```javascript
async function analyzeHoldings(mint) {
  const info = await getMintInfo([mint]);
  const token = info[mint];

  if (!token || !token.trade_events) {
    return null;
  }

  const userStats = {};

  token.trade_events.forEach((event) => {
    if (!userStats[event.user]) {
      userStats[event.user] = { bought: 0, sold: 0, firstTrade: event.timestamp };
    }

    if (event.is_buy) {
      userStats[event.user].bought += event.token_amount;
    } else {
      userStats[event.user].sold += event.token_amount;
    }
  });

  // Find users still holding
  const holders = Object.entries(userStats)
    .map(([user, stats]) => ({
      user,
      netHolding: stats.bought - stats.sold,
      percentageSold: (stats.sold / stats.bought) * 100,
      holdingTime:
        (token.trade_events[token.trade_events.length - 1].timestamp -
          stats.firstTrade) /
        60, // minutes
    }))
    .filter((h) => h.netHolding > 0)
    .sort((a, b) => b.netHolding - a.netHolding);

  return holders.slice(0, 10); // Top 10 holders
}
```

### Build a Token Price Curve

```javascript
async function getTokenPriceCurve(mint) {
  const info = await getMintInfo([mint]);
  const token = info[mint];

  if (!token || !token.trade_events) {
    return null;
  }

  let cumulativeSol = 0;
  let cumulativeTokens = 0;

  const priceCurve = token.trade_events.map((event) => {
    cumulativeSol += event.sol_amount;
    cumulativeTokens += event.token_amount;

    return {
      timestamp: event.timestamp,
      price: cumulativeSol / cumulativeTokens,
      totalSol: cumulativeSol,
      totalTokens: cumulativeTokens,
      isBuy: event.is_buy,
    };
  });

  return priceCurve;
}
```

### Calculate Volume and Liquidity Metrics

```javascript
async function calculateMetrics(mint) {
  const info = await getMintInfo([mint]);
  const token = info[mint];

  if (!token || !token.trade_events) {
    return null;
  }

  const totalSol = token.trade_events.reduce((sum, e) => sum + e.sol_amount, 0);
  const totalTokens = token.trade_events.reduce(
    (sum, e) => sum + e.token_amount,
    0
  );
  const avgTradeSize = totalSol / token.trade_events.length;
  const priceAtLaunch =
    token.trade_events[0].sol_amount / token.trade_events[0].token_amount;
  const currentPrice =
    token.trade_events[token.trade_events.length - 1].sol_amount /
    token.trade_events[token.trade_events.length - 1].token_amount;

  return {
    createdAt: new Date(token.timestamp * 1000),
    totalTrades: token.trade_events.length,
    totalVolume: totalSol,
    priceAtLaunch: priceAtLaunch.toFixed(8),
    currentPrice: currentPrice.toFixed(8),
    priceChange: (((currentPrice - priceAtLaunch) / priceAtLaunch) * 100).toFixed(
      2
    ),
    avgTradeSize: avgTradeSize.toFixed(4),
  };
}
```

### Identify Pump and Dump Patterns

```javascript
async function detectPumpDump(mint) {
  const info = await getMintInfo([mint]);
  const token = info[mint];

  if (!token || !token.trade_events.length < 10) {
    return null;
  }

  const prices = token.trade_events.map((e) => e.sol_amount / e.token_amount);
  const highPrice = Math.max(...prices);
  const lowPrice = Math.min(...prices);
  const currentPrice = prices[prices.length - 1];

  const pumpPercent = ((highPrice - lowPrice) / lowPrice) * 100;
  const dumpPercent = ((highPrice - currentPrice) / highPrice) * 100;

  return {
    peakPrice: highPrice,
    currentPrice,
    startPrice: prices[0],
    pumpAmount: pumpPercent.toFixed(2) + "%",
    dumpAmount: dumpPercent.toFixed(2) + "%",
    isSuspiciousPattern: pumpPercent > 500 && dumpPercent > 80,
  };
}
```

## Error Handling

The API returns successful responses even when some tokens are not found:

```javascript
const result = await getMintInfo([validMint, invalidMint]);

if (result.errors.not_found) {
  console.log("No data for:", result.errors.not_found);
}

// Access available data
Object.entries(result.data).forEach(([mint, info]) => {
  console.log(`${info.name}: ${info.trade_events.length} trades`);
});
```

## Data Limitations

- **Pump.fun Only**: Currently only supports tokens launched via pump.fun
- **Recent Tokens**: Best data for tokens launched in the last 7 days
- **Trade History**: Complete trade history from token creation
- **Historical Accuracy**: Trade data is sourced from blockchain transactions

## Rate Limits

- **Free Tier**: 25 requests/second
- **Pro Tier**: 100 requests/second
- **Enterprise**: Custom limits

Each request counts as 1 API call regardless of the number of mints (up to 36).

## Best Practices

1. **Batch Requests**: Combine up to 36 mints per request
2. **Cache Results**: Store mint info locally; data changes infrequently
3. **Analyze Trade Patterns**: Look for suspicious pump/dump patterns
4. **Monitor Creator**: Track tokens by the same creator
5. **Validate Data**: Always verify the token address matches expectations
6. **Handle Large Trade Lists**: Trade events can be extensive for popular tokens

## Related Endpoints

- [Token Metadata Endpoint](./token-metadata.md) - Get token basic information
- [Token Price Endpoint](./token-price.md) - Get current pricing data

## API Specification

For complete OpenAPI documentation, see `/api-specs/svs-api.yam
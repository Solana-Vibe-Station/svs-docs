# Token Price Endpoint

The `/price` endpoint provides current and historical pricing data for Solana tokens, including time-based price averages and the latest trade price. Query up to 36 tokens in a single request.

## Endpoint

```
POST https://beta-api.solanavibestation.com/price
```

## Request

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mints` | array | yes | Array of token mint addresses (max 36 per request) |

### Example Request

```bash
curl -X POST https://beta-api.solanavibestation.com/price \
  -H "Content-Type: application/json" \
  -H "Authorization: YOUR_API_KEY" \
  -d '{
    "mints": [
      "EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b",
      "So11111111111111111111111111111111111111112"
    ]
  }'
```

### JavaScript Example

```javascript
async function getTokenPrices(mints) {
  const response = await fetch(
    "https://beta-api.solanavibestation.com/price",
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
const prices = await getTokenPrices([
  "EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b",
]);

console.log(prices);
```

## Response

### Response Schema

```json
{
  "success": true,
  "data": {
    "mint_address": {
      "mint": "string",
      "latest_price": number,
      "latest_timestamp": number,
      "price_1m_avg": number,
      "price_15m_avg": number,
      "price_1h_avg": number,
      "price_24h_avg": number,
      "volume_24h": number,
      "liquidity": number,
      "market_cap": number
    }
  },
  "errors": {
    "no_data": ["mint_address"],
    "invalid_format": ["mint_address"]
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `mint` | string | Token mint address |
| `latest_price` | number | Most recent trade price in SOL |
| `latest_timestamp` | number | Unix timestamp of latest price |
| `price_1m_avg` | number | Average price over the last 1 minute |
| `price_15m_avg` | number | Average price over the last 15 minutes |
| `price_1h_avg` | number | Average price over the last 1 hour |
| `price_24h_avg` | number | Average price over the last 24 hours |
| `volume_24h` | number | Trading volume in the last 24 hours (in SOL) |
| `liquidity` | number | Current liquidity pool value (in SOL) |
| `market_cap` | number | Market capitalization (in SOL) |

All prices are denominated in SOL.

## Example Response

```json
{
  "success": true,
  "data": {
    "EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b": {
      "mint": "EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b",
      "latest_price": 0.05234,
      "latest_timestamp": 1708101234,
      "price_1m_avg": 0.05231,
      "price_15m_avg": 0.05228,
      "price_1h_avg": 0.05215,
      "price_24h_avg": 0.05180,
      "volume_24h": 15234.56,
      "liquidity": 342567.89,
      "market_cap": 5234567.89
    }
  },
  "errors": {}
}
```

## Supported DEXs

Pricing data is aggregated from:

- **pump.fun**: Token launch and trading platform
- **pump.swap**: Pump.fun secondary market
- **Raydium**: Decentralized exchange

## Use Cases

### Monitor Price Changes

```javascript
async function monitorPriceChanges(mints, interval = 5000) {
  let previousPrices = await getTokenPrices(mints);

  setInterval(async () => {
    const currentPrices = await getTokenPrices(mints);

    Object.entries(currentPrices).forEach(([mint, priceData]) => {
      const previous = previousPrices[mint];
      if (!previous) return;

      const change =
        ((priceData.latest_price - previous.latest_price) /
          previous.latest_price) *
        100;

      console.log(
        `${mint}: ${priceData.latest_price} SOL (${change > 0 ? "+" : ""}${change.toFixed(
          2
        )}%)`
      );
    });

    previousPrices = currentPrices;
  }, interval);
}
```

### Detect Price Arbitrage Opportunities

```javascript
async function findArbitrageOpportunities(mints) {
  const prices = await getTokenPrices(mints);

  const opportunities = [];

  Object.entries(prices).forEach(([mint, priceData]) => {
    const spread = priceData.price_1m_avg - priceData.price_15m_avg;
    const spreadPercent = (spread / priceData.price_15m_avg) * 100;

    if (spreadPercent > 2) {
      opportunities.push({
        mint,
        currentPrice: priceData.latest_price,
        spread1m15m: spreadPercent,
        volume24h: priceData.volume_24h,
        liquidity: priceData.liquidity,
      });
    }
  });

  return opportunities.sort((a, b) => b.spread1m15m - a.spread1m15m);
}

// Usage
const arbs = await findArbitrageOpportunities([mint1, mint2, mint3]);
console.log("Potential arbitrage opportunities:", arbs);
```

### Calculate Price Volatility

```javascript
async function calculateVolatility(mint) {
  const prices = await getTokenPrices([mint]);
  const data = prices[mint];

  if (!data) return null;

  const prices_array = [
    data.price_1m_avg,
    data.price_15m_avg,
    data.price_1h_avg,
    data.price_24h_avg,
  ];

  const mean = prices_array.reduce((a, b) => a + b) / prices_array.length;
  const variance =
    prices_array.reduce((acc, p) => acc + Math.pow(p - mean, 2), 0) /
    prices_array.length;
  const stdDev = Math.sqrt(variance);
  const volatility = (stdDev / mean) * 100;

  return {
    volatility: volatility.toFixed(2) + "%",
    prices: {
      latest: data.latest_price,
      avg1m: data.price_1m_avg,
      avg15m: data.price_15m_avg,
      avg1h: data.price_1h_avg,
      avg24h: data.price_24h_avg,
    },
  };
}
```

### Track Volume Leaders

```javascript
async function getVolumeLeaders(mints) {
  const prices = await getTokenPrices(mints);

  const leaders = Object.entries(prices)
    .filter(([_, data]) => data.volume_24h > 0)
    .sort((a, b) => b[1].volume_24h - a[1].volume_24h)
    .slice(0, 10)
    .map(([mint, data]) => ({
      mint,
      volume24h: data.volume_24h,
      price: data.latest_price,
      marketCap: data.market_cap,
    }));

  return leaders;
}
```

## Error Handling

The API returns successful responses even when some tokens don't have pricing data:

```javascript
const result = await getTokenPrices([validMint, newTokenMint]);

if (result.errors.no_data) {
  console.log("No pricing data for:", result.errors.no_data);
}

// Access available pricing data
Object.entries(result.data).forEach(([mint, prices]) => {
  console.log(`${mint}: ${prices.latest_price} SOL`);
});
```

## Data Freshness

- **Latest Price**: Updated within seconds of each trade
- **1-Minute Average**: Calculated from all trades in the last 60 seconds
- **15-Minute Average**: Calculated from all trades in the last 15 minutes
- **1-Hour Average**: Calculated from all trades in the last 60 minutes
- **24-Hour Average**: Calculated from all trades in the last 24 hours

## Rate Limits

- **Free Tier**: 25 requests/second
- **Pro Tier**: 100 requests/second
- **Enterprise**: Custom limits

Each request counts as 1 API call regardless of the number of mints (up to 36).

## Caching and Polling

For optimal performance:

```javascript
const priceCache = new Map();
const CACHE_TTL = 5000; // 5 seconds

async function getCachedPrice(mint) {
  const cached = priceCache.get(mint);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const prices = await getTokenPrices([mint]);
  const data = prices[mint];

  if (data) {
    priceCache.set(mint, { data, timestamp: Date.now() });
  }

  return data;
}
```

## Best Practices

1. **Batch Requests**: Combine up to 36 mints per request
2. **Cache Results**: Implement local caching with appropriate TTL
3. **Monitor Volume**: High volume correlates with liquidity and reliability
4. **Handle Missing Data**: New tokens may not have pricing data yet
5. **Use Time Averages**: Compare price averages across timeframes for better signals
6. **Implement Retry Logic**: Handle rate limits with exponential backoff

## Related Endpoints

- [Token Metadata Endpoint](./token-metadata.md) - Get token information
- [Mint Info Endpoint](./mint-info.md) - Get detailed mint and trade history

## API Specification

For complete OpenAPI documentation, see `/api-specs/svs-api.yaml`.

## Need Help?

For questions about pricing data or integration support, see [Support](../support.md).

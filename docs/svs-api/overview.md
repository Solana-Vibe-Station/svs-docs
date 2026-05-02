# SVS API Overview

The SVS API is a proprietary token intelligence service for Solana that provides real-time market data, metadata, and pricing information for newly launched tokens. Built specifically for token traders, arbitrage bots, and market analysis platforms, SVS API enables fast access to comprehensive token information.

## API Characteristics

- **Specialized Focus**: Real-time data for newly launched tokens and emerging markets
- **High Performance**: Optimized for rapid queries with sub-50ms response times
- **Batch Requests**: Retrieve data for up to 36 tokens in a single request
- **Token Source Support**: Coverage for pump.fun, pump.swap, and Raydium tokens
- **Easy Integration**: Simple REST API with JSON requests and responses

## Base URL

```
https://beta-api.solanavibestation.com
```

All API requests are made to this base URL with standard HTTP methods.

## Authentication

Authentication is optional for the free tier (25 requests/second), but recommended for production use. Authenticate using either method:

### Header Authentication

```bash
curl -X POST https://beta-api.solanavibestation.com/metadata \
  -H "Content-Type: application/json" \
  -H "Authorization: YOUR_API_KEY" \
  -d '{"mints":["..."]}'
```

### Query Parameter Authentication

```bash
curl -X POST "https://beta-api.solanavibestation.com/metadata?api_key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"mints":["..."]}'
```

Replace `YOUR_API_KEY` with your actual API key from the [SVS Cloud Console](https://cloud.solanavibestation.com).

## Available Endpoints

### Health Check

**`GET /health`**

Check API availability and connection status.

```bash
curl https://beta-api.solanavibestation.com/health
```

Response: `{"status":"ok"}`

### Token Metadata

**`POST /metadata`**

Retrieve metadata for up to 36 tokens at once. Returns mint, name, symbol, URI, and creator information.

```bash
curl -X POST https://beta-api.solanavibestation.com/metadata \
  -H "Content-Type: application/json" \
  -d '{"mints":["EPjFWdd5Au...","So11111111..."]}'
```

[Full documentation →](./token-metadata.md)

### Token Price

**`POST /price`**

Get current and historical pricing data with time-based averages (1min, 15min, 1h, 24h).

```bash
curl -X POST https://beta-api.solanavibestation.com/price \
  -H "Content-Type: application/json" \
  -d '{"mints":["EPjFWdd5Au..."]}'
```

[Full documentation →](./token-price.md)

### Mint Info

**`POST /mint_info`**

Comprehensive information for newly launched tokens including trade history and creator data.

```bash
curl -X POST https://beta-api.solanavibestation.com/mint_info \
  -H "Content-Type: application/json" \
  -d '{"mints":["EPjFWdd5Au..."]}'
```

[Full documentation →](./mint-info.md)

## Supported Token Sources

SVS API provides data for tokens from:

- **pump.fun**: The most active token launcher on Solana
- **pump.swap**: Secondary market for pump.fun tokens
- **Raydium**: Decentralized exchange with launch pad integration

## Request Format

All requests (except `/health`) use standard JSON with a `mints` array:

```json
{
  "mints": [
    "mint_address_1",
    "mint_address_2",
    "..."
  ]
}
```

Maximum 36 mints per request. For larger batches, make multiple requests.

## Response Format

Responses are always JSON with a standard structure:

```json
{
  "success": true,
  "data": {
    "mint_address_1": { /* data */ },
    "mint_address_2": { /* data */ }
  },
  "errors": {
    "invalid_mint": ["mint_address"]
  }
}
```

- `success`: Boolean indicating if the request succeeded
- `data`: Object mapping mint addresses to their data
- `errors`: Object listing any errors encountered during processing

## Rate Limits

| Tier | Requests/Second | Burst | Tokens/Month |
|------|-----------------|-------|--------------|
| **Free** | 25 | 50 | Unlimited |
| **Pro** | 100 | 200 | Unlimited |
| **Enterprise** | Custom | Custom | Custom |

Rate limits are applied per API key. Exceeding limits returns HTTP 429 (Too Many Requests).

## Error Handling

Common error responses:

| Status Code | Meaning |
|-------------|---------|
| `200` | Success |
| `400` | Bad request (invalid JSON or parameters) |
| `401` | Unauthorized (invalid API key) |
| `429` | Rate limit exceeded |
| `500` | Server error |

## Quick Start

### 1. Get Your API Key

Visit [SVS Cloud Console](https://cloud.solanavibestation.com) to create an API key.

### 2. Make Your First Request

```bash
curl -X POST https://beta-api.solanavibestation.com/metadata \
  -H "Content-Type: application/json" \
  -H "Authorization: YOUR_API_KEY" \
  -d '{
    "mints": [
      "EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b"
    ]
  }'
```

### 3. Parse the Response

```javascript
const response = await fetch(
  "https://beta-api.solanavibestation.com/metadata",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "YOUR_API_KEY",
    },
    body: JSON.stringify({
      mints: ["EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b"],
    }),
  }
);

const result = await response.json();
console.log(result.data);
```

## Batch Requests Example

Efficiently retrieve data for multiple tokens:

```javascript
const mints = [
  "mint1...",
  "mint2...",
  "mint3...",
  // ... up to 36 tokens
];

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
result.data; // Object with price data for all mints
result.errors; // Any errors encountered
```

## Best Practices

1. **Use Batch Requests**: Combine up to 36 tokens per request to reduce API calls
2. **Handle Errors Gracefully**: Some tokens may not have data available
3. **Cache Results**: Store recent queries to minimize API usage
4. **Implement Retry Logic**: Handle transient errors with exponential backoff
5. **Monitor Rate Limits**: Track your request rate to avoid hitting limits
6. **Use Appropriate Authentication**: Use query parameters for testing, headers for production

## Integration Examples

- **Token Screener**: Analyze newly launched tokens in real-time
- **Arbitrage Bot**: Identify price discrepancies across DEXs
- **Market Dashboard**: Display comprehensive token data
- **Trading Bot**: Access pricing and metadata for trading decisions

## OpenAPI Specification

The complete OpenAPI specification for the SVS API is available at `/api-specs/svs-api.yaml`. This specification includes:

- Detailed request and response schemas
- All parameter types and constraints
- Complete method documentation
- Example requests and responses

## SDK Support

Official SDKs and client libraries are available for:

- JavaScript/TypeScript
- Python
- Rust

See [SDK Documentation](../sdks.md) for more information.

## Need Help?

For questions about API usage, integration support, or technical issues, see [Support](../support.md).

## Changelog

For updates and new features, check the [API Changelog](./changelog.md).

# Token Metadata Endpoint

The `/metadata` endpoint retrieves comprehensive metadata for Solana tokens, including name, symbol, creator information, and off-chain metadata. Query up to 36 tokens in a single request.

## Endpoint

```
POST https://beta-api.solanavibestation.com/metadata
```

## Request

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mints` | array | yes | Array of token mint addresses (max 36 per request) |

### Example Request

```bash
curl -X POST https://beta-api.solanavibestation.com/metadata \
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
async function getTokenMetadata(mints) {
  const response = await fetch(
    "https://beta-api.solanavibestation.com/metadata",
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
const metadata = await getTokenMetadata([
  "EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b",
]);

console.log(metadata);
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
      "fungible": boolean,
      "primary_creator": "string",
      "off_chain_metadata": {
        "image": "string",
        "description": "string",
        "social_links": {
          "twitter": "string",
          "telegram": "string",
          "discord": "string",
          "website": "string"
        }
      }
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
| `name` | string | Token name (e.g., "Solana") |
| `symbol` | string | Token symbol (e.g., "SOL") |
| `uri` | string | URI to off-chain metadata JSON |
| `fungible` | boolean | Whether the token is fungible (true for most tokens) |
| `primary_creator` | string | Public key of the token creator |
| `off_chain_metadata.image` | string | URL to token logo/image |
| `off_chain_metadata.description` | string | Token description |
| `off_chain_metadata.social_links` | object | Social media and website links |

## Example Response

```json
{
  "success": true,
  "data": {
    "EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b": {
      "mint": "EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b",
      "name": "USDC",
      "symbol": "USDC",
      "uri": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b/logo.png",
      "fungible": true,
      "primary_creator": "TokenkegQfeZyiNwAJsyFbPVwwQQfNKVQwV7PydxTqKDMn",
      "off_chain_metadata": {
        "image": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b/logo.png",
        "description": "USD Coin",
        "social_links": {
          "twitter": "https://twitter.com/circle",
          "website": "https://www.circle.com/usdc"
        }
      }
    },
    "So11111111111111111111111111111111111111112": {
      "mint": "So11111111111111111111111111111111111111112",
      "name": "Wrapped SOL",
      "symbol": "SOL",
      "uri": "",
      "fungible": true,
      "primary_creator": "TokenkegQfeZyiNwAJsyFbPVwwQQfNKVQwV7PydxTqKDMn",
      "off_chain_metadata": {
        "image": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
        "description": "Wrapped SOL"
      }
    }
  },
  "errors": {}
}
```

## Use Cases

### Display Token Information in a UI

```javascript
async function displayTokenCard(mint) {
  const metadata = await getTokenMetadata([mint]);
  const token = metadata[mint];

  if (!token) {
    console.log("Token not found");
    return;
  }

  console.log(`
    <div class="token-card">
      <img src="${token.off_chain_metadata.image}" alt="${token.name}">
      <h2>${token.name} (${token.symbol})</h2>
      <p>${token.off_chain_metadata.description}</p>
      <p>Creator: ${token.primary_creator}</p>
    </div>
  `);
}
```

### Verify Token Information

```javascript
async function verifyTokenInfo(mint, expectedName, expectedSymbol) {
  const metadata = await getTokenMetadata([mint]);
  const token = metadata[mint];

  if (!token) {
    return { valid: false, reason: "Token not found" };
  }

  if (token.name !== expectedName || token.symbol !== expectedSymbol) {
    return {
      valid: false,
      reason: "Name or symbol mismatch",
      actual: { name: token.name, symbol: token.symbol },
    };
  }

  return { valid: true };
}

// Usage
const verification = await verifyTokenInfo(
  "EPjFWdd5Au17FBERb55oH3HJ5MtS7NSVQ3w7nxYqo5b",
  "USDC",
  "USDC"
);
```

### Build a Token Registry

```javascript
async function buildTokenRegistry(mints) {
  const registry = {};
  const batchSize = 36;

  // Process in batches of 36
  for (let i = 0; i < mints.length; i += batchSize) {
    const batch = mints.slice(i, i + batchSize);
    const metadata = await getTokenMetadata(batch);

    Object.assign(registry, metadata);
    console.log(`Indexed ${Object.keys(registry).length} tokens...`);
  }

  return registry;
}
```

## Error Handling

The API returns successful responses even when some tokens are not found. Check the `errors` object:

```javascript
const result = await getTokenMetadata([validMint, invalidMint]);

if (result.errors.not_found) {
  console.log("These mints were not found:", result.errors.not_found);
}

if (result.errors.invalid_format) {
  console.log("These mints are invalid:", result.errors.invalid_format);
}

// Access successful results
Object.entries(result.data).forEach(([mint, metadata]) => {
  console.log(`${metadata.name} (${metadata.symbol})`);
});
```

## Rate Limits

- **Free Tier**: 25 requests/second
- **Pro Tier**: 100 requests/second
- **Enterprise**: Custom limits

Each request counts as 1 API call regardless of the number of mints (up to 36).

## Caching

For best performance, cache metadata results locally. Token metadata changes infrequently:

```javascript
const cache = new Map();

async function getTokenMetadataWithCache(mints) {
  const missingMints = mints.filter((m) => !cache.has(m));

  if (missingMints.length > 0) {
    const results = await getTokenMetadata(missingMints);
    Object.entries(results).forEach(([mint, data]) => {
      cache.set(mint, data);
    });
  }

  return mints.reduce((acc, mint) => {
    acc[mint] = cache.get(mint);
    return acc;
  }, {});
}
```

## Best Practices

1. **Batch Requests**: Combine up to 36 mints per request
2. **Handle Missing Data**: Some tokens may not have complete metadata
3. **Cache Results**: Store metadata locally to reduce API calls
4. **Validate Responses**: Always check the `success` field and `errors` object
5. **Use Headers for Auth**: Preferred over query parameters for security

## Related Endpoints

- [Token Price Endpoint](./token-price.md) - Get pricing information
- [Mint Info Endpoint](./mint-info.md) - Get detailed mint information

## API Specification

For complete OpenAPI documentation, see `/api-specs/svs-api.yaml`.

## Need Help?

For questions about the metadata endpoint or troubleshooting, see [Support](../support.md).

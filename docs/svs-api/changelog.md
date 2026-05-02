# SVS API Changelog

Track updates, new features, and improvements to the SVS API. This page is updated regularly as new functionality is released. Check back frequently for the latest changes.

## 2025-02-17 - v1.2.0

### New Features

- **Enhanced Price Data**: Added `liquidity` and `market_cap` fields to `/price` endpoint for better market analysis
- **Volume Metrics**: `/price` endpoint now includes `volume_24h` field with complete 24-hour trading volume

### Improvements

- Reduced `/price` endpoint response times by 30% through optimized data caching
- Improved error handling with more descriptive error messages in the `errors` object
- Added support for larger batch requests (increased from 25 to 36 mints per request)

### Bug Fixes

- Fixed timezone calculation issue in `/mint_info` trade event timestamps
- Resolved occasional duplicate trades in `/mint_info` responses
- Fixed missing social links in `/metadata` responses for some tokens

## 2025-02-10 - v1.1.5

### Improvements

- Added `off_chain_metadata` to all API responses for consistent token information
- Improved data freshness: price updates now every 2-3 seconds (was 5 seconds)
- Enhanced `/mint_info` trade history accuracy for newly launched tokens

### Performance

- Optimized database queries for faster response times across all endpoints
- Implemented intelligent caching to reduce latency for frequently requested tokens

### Documentation

- Updated API documentation with new code examples
- Added best practices guide for batch processing

## 2025-02-03 - v1.1.0

### New Features

- **Mint Info Trade Events**: `/mint_info` now returns complete trade history including individual trades with timestamps and amounts
- **Token Creator Information**: All endpoints now include creator/launcher information
- **Improved Metadata**: Added social links object with Twitter, Telegram, Discord, and website URLs

### Improvements

- `/price` endpoint now includes time-based price averages (1m, 15m, 1h, 24h)
- Better support for new tokens with placeholder data for unavailable fields
- Enhanced error responses with specific error codes

### Rate Limit Changes

- Free tier: 25 requests/second (unchanged)
- Pro tier: 100 requests/second (increased from 75)

## 2025-01-27 - v1.0.5

### Bug Fixes

- Fixed metadata encoding issues for non-ASCII token names
- Resolved intermittent 503 errors during peak traffic
- Fixed API key authentication issue with special characters

### Performance

- Improved response times for batched requests
- Optimized memory usage for large result sets

## 2025-01-20 - v1.0.3

### New Features

- **Query Parameter Auth**: Added support for `?api_key=` in addition to header authentication
- **Health Check Endpoint**: Added `GET /health` for connectivity verification

### Improvements

- Better handling of tokens without metadata
- Improved error messages for invalid mint addresses
- Added request ID tracking for debugging

## 2025-01-15 - v1.0.0 - Initial Release

### Features

- **Token Metadata Endpoint** (`POST /metadata`): Retrieve token name, symbol, URI, and creator information
- **Token Price Endpoint** (`POST /price`): Get current pricing and trading data
- **Mint Info Endpoint** (`POST /mint_info`): Access comprehensive token information
- **Authentication**: Support for header and query parameter authentication
- **Batch Requests**: Process up to 25 tokens per request
- **Error Handling**: Comprehensive error reporting with descriptive messages

### Supported Token Sources

- pump.fun
- pump.swap
- Raydium (limited)

### Rate Limits

- Free tier: 25 requests/second
- Pro tier: 75 requests/second
- Enterprise: Custom limits

### Documentation

- Complete API reference with examples
- Integration guides for common use cases
- OpenAPI specification available

---

## Upcoming Features (Roadmap)

### Q2 2025

- **Historical Price Data**: Access to historical price data and OHLCV candles
- **Token Events**: Real-time notifications for token launches and price movements
- **Advanced Analytics**: Trending tokens and trading pattern analysis

### Q3 2025

- **Additional DEX Support**: Full Raydium and Marinade integration
- **On-Chain Events**: Subscribe to token mint creation and transfer events
- **Custom Alerts**: Webhook-based alerts for price changes and trade volume

### Q4 2025

- **Portfolio Tracking**: Monitor token holdings and portfolio performance
- **Risk Scoring**: Automated risk assessment for newly launched tokens
- **Machine Learning Models**: Predictive analytics for token price movements

---

## API Versioning

SVS API uses semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes requiring client updates
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, no feature changes

Current version: **v1.2.0**

## Breaking Changes

### v1.0.0 → v1.1.0

No breaking changes. All v1.0.x clients remain compatible with v1.1.0.

## Migration Guide

If you're upgrading from an older version:

1. Update any code using deprecated endpoints
2. Test thoroughly with new field additions
3. Implement error handling for new error types
4. Review rate limit changes for your tier

## Support

For questions about API changes or migration assistance:

- Check this changelog for recent updates
- Review the [API Documentation](./overview.md)
- Contact [Support](../support.md) for specific issues
- Visit the community forum for discussion

## How to Stay Updated

- **Subscribe to Updates**: Enable notifications in the [SVS Cloud Console](https://cloud.solanavibestation.com)
- **Follow on Twitter**: [@SolanaVibeStation](https://twitter.com/solanavibestation)
- **Join Discord**: [SVS Community](https://discord.gg/solanavibestation)
- **Check This Page**: New updates appear here first

## Feedback

Have feedback on the API or feature requests? We'd love to hear from you!

- **Feature Requests**: File an issue in the [Community Forum](https://community.solanavibestation.com)
- **Bug Reports**: Report via [Support](../support.md)
- **General Feedback**: Email api-feedback@solanavibestation.com

---

*Last updated: 2025-02-17*
*API Version: 1.2.0*

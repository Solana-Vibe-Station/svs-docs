# Solana Vibe Station Documentation

This repository contains the source content for [docs.solanavibestation.com](https://docs.solanavibestation.com), powered by [GitBook](https://www.gitbook.com/) with Git Sync.

## Repository Structure

```
svs-docs/
├── docs/                          # GitBook content (synced via Git Sync)
│   ├── SUMMARY.md                 # Navigation / table of contents
│   ├── welcome/                   # About, philosophy, benchmarks
│   ├── getting-started/           # Quick start, endpoints, auth, rate limits
│   ├── rpc-services/              # RPC tiers, methods, WebSocket, historical
│   ├── svs-api/                   # Proprietary token intelligence API
│   ├── grpc/                      # Geyser gRPC streaming
│   ├── vps-cloud/                 # VPS hosting and management
│   └── support/                   # Troubleshooting, FAQ, contact
├── api-specs/                     # OpenAPI specifications
│   ├── svs-api.yaml               # SVS proprietary API spec
│   ├── solana-rpc.yaml            # Solana RPC methods spec
│   └── historical-rpc.yaml        # Historical RPC methods spec
├── .github/workflows/             # CI/CD
│   └── validate-specs.yml         # OpenAPI spec validation on push
└── README.md                      # This file
```

## How It Works

This repo is connected to GitBook via **Git Sync**. When you push changes to the `main` branch:

1. GitBook detects the change automatically
2. Documentation pages update from the markdown files in `docs/`
3. OpenAPI specs in `api-specs/` are referenced by the docs and render as interactive API references

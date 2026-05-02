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

## Making Changes

### Editing documentation

1. Edit the relevant `.md` file in `docs/`
2. Commit and push to `main`
3. GitBook picks up the change within minutes

### Adding a new page

1. Create the `.md` file in the appropriate `docs/` subdirectory
2. Add an entry to `docs/SUMMARY.md` (this controls the sidebar navigation)
3. Commit and push

### Updating API specs

1. Edit the relevant `.yaml` file in `api-specs/`
2. The GitHub Action will validate the spec on push
3. GitBook regenerates the API reference pages automatically

### Adding a new API endpoint

1. Add the endpoint definition to the appropriate spec in `api-specs/`
2. If needed, create or update the docs page in `docs/svs-api/`
3. Add an entry to the changelog at `docs/svs-api/changelog.md`
4. Commit and push

## Local Development

To preview changes locally before pushing, you can use GitBook's CLI or any markdown previewer.

### Validate OpenAPI specs locally

```bash
npm install -g @redocly/cli
redocly lint api-specs/svs-api.yaml
redocly lint api-specs/solana-rpc.yaml
redocly lint api-specs/historical-rpc.yaml
```

## GitBook Setup

To connect this repo to GitBook:

1. Go to your GitBook space settings
2. Navigate to **Synchronization** > **Git Sync**
3. Connect your GitHub account and select this repository
4. Set the content directory to `docs/`
5. Choose the `main` branch
6. Save — GitBook will import the content automatically

For OpenAPI specs, use GitBook's OpenAPI block in your markdown pages to reference the spec files.

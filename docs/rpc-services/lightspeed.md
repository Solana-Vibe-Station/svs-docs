# Lightspeed Transactions

Lightspeed Transactions enable faster processing and higher priority inclusion by partnering your transactions with SVS's validator pool. This tip-based system rewards validators for prioritizing your transaction during network congestion.

## How Lightspeed Works

When you submit a transaction with a Lightspeed tip, the transaction is forwarded to SVS's partner validator network with metadata indicating the tip amount. Validators prioritize transactions based on tip size, integrating them into blocks sooner than untipped transactions.

This is the standard Solana validator incentive mechanism and is compatible with any RPC endpoint, though SVS's infrastructure ensures optimal routing to our validator pool.

## Tip Requirements

| Parameter | Value |
|-----------|-------|
| **Minimum Tip** | 0.0001 SOL (100,000 lamports) |
| **Recommended Tip** | 0.001 SOL (1,000,000 lamports) |
| **Effect on Speed** | Higher tips correlate with faster inclusion times |

During normal network conditions, even the minimum tip significantly improves inclusion speed. During high congestion, recommended or higher tips provide the best results.

## Adding a Tip to Your Transaction

### Using Solana Web3.js

Add a priority fee instruction to your transaction before signing:

```javascript
import {
  Connection,
  PublicKey,
  Transaction,
  SystemProgram,
  LAMPORTS_PER_SOL,
  ComputeBudgetProgram,
} from "@solana/web3.js";

const connection = new Connection("https://basic.rpc.solanavibestation.com");

// Create your transaction
const transaction = new Transaction().add(
  SystemProgram.transfer({
    fromPubkey: payer.publicKey,
    toPubkey: recipient,
    lamports: LAMPORTS_PER_SOL * 0.1, // 0.1 SOL
  })
);

// Add priority fee (Lightspeed tip)
// 0.001 SOL = 1,000,000 lamports
const priorityFeeInstruction = ComputeBudgetProgram.setComputeUnitPrice({
  microLamports: 1000, // Adjust based on desired speed
});

transaction.add(priorityFeeInstruction);

// Set recent blockhash and sign
const { blockhash } = await connection.getLatestBlockhash();
transaction.recentBlockhash = blockhash;
transaction.feePayer = payer.publicKey;

await transaction.sign(payer);

// Send transaction
const signature = await connection.sendTransaction(transaction);
```

### Using Anchor (Rust)

If building with Anchor, add the priority fee via the `remaining_accounts` mechanism or use a custom instruction:

```rust
use anchor_lang::solana_program::system_instruction;
use anchor_lang::solana_program::compute_budget;

// Add priority fee instruction
let prioritize_transaction_ix = compute_budget::ComputeBudgetInstruction::set_compute_unit_price(
    1000 // microLamports
);

let tx = Transaction::new_signed_with_payer(
    &[
        prioritize_transaction_ix,
        // ... your other instructions
    ],
    Some(&payer.pubkey()),
    &[payer],
    recent_blockhash,
);
```

### Using Solana CLI

When using `solana program deploy` or similar CLI commands, add the `--with-compute-unit-price` flag:

```bash
solana transfer <RECIPIENT> 0.1 \
  --url https://basic.rpc.solanavibestation.com \
  --with-compute-unit-price 1000
```

## Pricing Recommendations

### Low Congestion (Normal Network Conditions)
- **Recommended Tip**: 0.0001 SOL (minimum)
- **Expected Inclusion**: 1-2 slots (400-800ms)
- **Cost**: < $0.01 per transaction

### Moderate Congestion (Busy Periods)
- **Recommended Tip**: 0.0005 SOL (500,000 lamports)
- **Expected Inclusion**: 1-3 slots (400-1200ms)
- **Cost**: $0.02-0.03 per transaction

### High Congestion (Peak Network Activity)
- **Recommended Tip**: 0.001+ SOL (1,000,000+ lamports)
- **Expected Inclusion**: 1-2 slots (400-800ms)
- **Cost**: $0.05-0.10+ per transaction

Adjust tips based on your application's tolerance for transaction delay and budget constraints.

## Combining with Staked RPC

For maximum priority during high congestion, combine Lightspeed tips with [Staked RPC (SWQoS)](./staked-rpc.md) endpoints:

1. Submit transaction to `https://basic.swqos.rpc.solanavibestation.com`
2. Include a Lightspeed tip (0.001 SOL recommended)
3. Result: Priority connection slot + validator prioritization

This combination provides the fastest inclusion times available on Solana.

## Example: Arbitrage Bot

Here's a complete example of a time-sensitive arbitrage transaction with Lightspeed:

```javascript
async function executeArbitrage(payer, inputMint, outputMint, amount) {
  const connection = new Connection(
    "https://elite.swqos.rpc.solanavibestation.com"
  );

  // Build arbitrage transaction (simplified)
  const transaction = new Transaction().add(
    // ... swap instructions
  );

  // Add high-priority fee for fast inclusion
  const priorityFeeIx = ComputeBudgetProgram.setComputeUnitPrice({
    microLamports: 5000, // High priority for time-sensitive op
  });

  transaction.add(priorityFeeIx);

  // Get fresh blockhash and sign
  const { blockhash } = await connection.getLatestBlockhash("finalized");
  transaction.recentBlockhash = blockhash;
  transaction.feePayer = payer.publicKey;

  await transaction.sign(payer);

  // Send with explicit commitment for faster confirmation
  const signature = await connection.sendTransaction(transaction, [payer], {
    skipPreflight: false,
    preflightCommitment: "processed",
  });

  // Wait for confirmation
  const confirmation = await connection.confirmTransaction(signature);
  return confirmation;
}
```

## Monitoring Tip Effectiveness

Monitor your transaction inclusion times to optimize tip amounts:

```javascript
async function monitorTxInclusion(signature) {
  const connection = new Connection(
    "https://basic.rpc.solanavibestation.com"
  );

  const startTime = Date.now();
  let confirmed = false;

  while (!confirmed) {
    const status = await connection.getSignatureStatus(signature);
    if (status.value?.confirmationStatus === "finalized") {
      confirmed = true;
      const duration = Date.now() - startTime;
      console.log(`Transaction confirmed in ${duration}ms`);
    }
    await new Promise((r) => setTimeout(r, 500));
  }
}
```

## Best Practices

1. **Start conservative**: Begin with minimum tips and increase only if inclusion times are unsatisfactory
2. **Monitor network conditions**: Track recent block times and adjust tips accordingly
3. **Batch when possible**: Combine multiple transactions to amortize tip costs
4. **Use estimated prices**: Query recent transaction fees to estimate optimal tips
5. **Implement fallback logic**: If a transaction doesn't confirm quickly, resubmit with a higher tip
6. **Test thoroughly**: Validate tip amounts with testnet before deploying to mainnet

## Limitations

- Tips do not guarantee transaction inclusion (no blockchain can)
- Very high tips do not proportionally improve inclusion time beyond a certain point
- During extreme network congestion, all transactions experience delays regardless of tip
- Tips are sent to validators; SVS does not collect or retain tip amounts

## Need Help?

For questions about optimal tip amounts for your use case, see [Support](../support.md).

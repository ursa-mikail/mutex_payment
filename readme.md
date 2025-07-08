# Mutex Payment 

2-way mutex-style payment transaction where funds are locked until receipt is confirmed, you can use a smart contract escrow pattern with state locking. The mechanism ensures finality is only reached when both sides fulfill their commitments, deterring double-spending or non-performance.

## 🔐 Concept: Mutex Payment with Escrow Lock
Funds are locked in contract when Bob commits.

Alice sees funds are locked and ships the car.

Funds are not released until Bob confirms receipt.

If Bob never confirms (maliciously or otherwise), a timeout mechanism or a trusted arbitrator may resolve the contract.

## 🛡️ Prevents Double Spending / Lack of Funds
Funds are locked up-front, so insufficient funds or double spending is impossible.

Until both parties act, funds remain locked like a mutex lock.

It requires intent from both parties to reach finality.


| Phase      | Trigger                     | State      | Effect                      |
| ---------- | --------------------------- | ---------- | --------------------------- |
| `Funded`   | Bob sends funds             | `Funded`   | Funds locked in contract    |
| `Shipped`  | Alice confirms shipment     | `Shipped`  | Signals she's sent the item |
| `Received` | Bob confirms receipt        | `Received` | Alice gets the payment      |
| `Refunded` | Timeout reached, no receipt | `Refunded` | Bob gets his funds back     |

## Solidity version

### 🧪 How to Use
Buyer deploys contract → calls initialize(seller, timeout) and sends funds.

Seller calls confirmShipment() when item is shipped.

Buyer calls confirmReceipt() if satisfied → seller gets paid.

If buyer does nothing, anyone can call refundBuyerIfTimeout() after timeout → buyer gets refunded.

### 🛠 Notes
The getBalances() function simulates your Python balance snapshot. In Ethereum, buyer.balance and seller.balance will show total wallet ETH, not just escrow.

This contract mimics the mutex-style lock: only one path can release the funds.

Funds are locked on contract deploy (initialize) and stay so until either confirmReceipt or timeout refund.

refundBuyerIfTimeout() is the "mutex unlock due to timeout" path:

If the buyer fails to confirm (confirmReceipt) after shipment,

And the timeout expires,

Then anyone can trigger this function (not just the buyer), to refund the locked funds to the buyer.

💡 This mimics Python version: if OPT_FAILURE: ... refund_buyer_if_timeout().

### ✅ Outputs of each case
🟩 Case A: Success Path – Buyer Confirms Receipt
Steps:

Buyer calls initialize(seller, timeout) with funds.

Seller calls confirmShipment().

Buyer calls confirmReceipt() before timeout.

Events emitted:

```
[ShipmentConfirmed] Seller confirms shipment.
[ReceiptConfirmed] Buyer confirms receipt.
```

Results:

state = RECEIVED

Seller receives the funds.

fundsLocked = false

getBalances() output (example structure):

```
{
  "buyer": "0xBuyerAddress",
  "seller": "0xSellerAddress",
  "buyerBalance": 0,
  "sellerBalance": [original + escrow amount],
  "contractLocked": 0,
  "state": "RECEIVED"
}
```

🟥 Case B: Failure Path – Buyer Never Confirms
Steps:

Buyer calls initialize(...) with funds.

Seller calls confirmShipment().

Buyer does NOT call confirmReceipt().

After timeout, anyone calls refundBuyerIfTimeout().

Events emitted:
```
[ShipmentConfirmed] Seller confirms shipment.
[RefundedAfterTimeout] Buyer refunded due to timeout.
```

Results:

state = REFUNDED

Buyer gets their funds back.

fundsLocked = false

getBalances() output:

```
{
  "buyer": "0xBuyerAddress",
  "seller": "0xSellerAddress",
  "buyerBalance": [original + escrow amount],
  "sellerBalance": 0,
  "contractLocked": 0,
  "state": "REFUNDED"
}
```

| Path               | Who acts                | State Transition              | Who gets the money | Final State |
| ------------------ | ----------------------- | ----------------------------- | ------------------ | ----------- |
| Happy Path         | Buyer confirms          | `Funded → Shipped → Received` | Seller             | RECEIVED    |
| Failure to Confirm | Timeout triggers refund | `Funded → Shipped → Refunded` | Buyer              | REFUNDED    |



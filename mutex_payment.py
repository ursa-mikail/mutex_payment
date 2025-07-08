# Mutex Payment 
import time

class MutexEscrow:
    def __init__(self, buyer, seller, amount, timeout_secs=10):
        self.buyer = buyer
        self.seller = seller
        self.amount = amount
        self.timeout = timeout_secs
        self.state = 'FUNDED'  # Initial state
        self.last_action_time = time.time()
        self.funds_locked = True
        self.buyer_balance = 0
        self.seller_balance = 0
        print(f"[INFO] Funds locked: {amount} from {buyer} to contract")

    def confirm_shipment(self, user):
        if user != self.seller:
            print("[ERROR] Only seller can confirm shipment.")
            return
        if self.state != 'FUNDED':
            print("[ERROR] Shipment cannot be confirmed in current state.")
            return
        self.state = 'SHIPPED'
        self.last_action_time = time.time()
        print("[ACTION] Shipment confirmed by seller.")

    def confirm_receipt(self, user):
        if user != self.buyer:
            print("[ERROR] Only buyer can confirm receipt.")
            return
        if self.state != 'SHIPPED':
            print("[ERROR] Cannot confirm receipt before shipment.")
            return
        self.state = 'RECEIVED'
        self.funds_locked = False
        self.seller_balance += self.amount
        print(f"[SUCCESS] Buyer confirmed receipt. Funds released to seller ({self.seller}).")

    def refund_buyer_if_timeout(self):
        if self.state != 'SHIPPED':
            print("[INFO] No shipment or still within grace period.")
            return
        if time.time() - self.last_action_time > self.timeout:
            self.state = 'REFUNDED'
            self.funds_locked = False
            self.buyer_balance += self.amount
            print(f"[TIMEOUT] Buyer refunded. Timeout reached.")
        else:
            remaining = round(self.timeout - (time.time() - self.last_action_time), 2)
            print(f"[INFO] Timeout not reached. {remaining}s remaining.")

    def get_balances(self):
        return {
            "buyer": self.buyer_balance,
            "seller": self.seller_balance,
            "contract_locked": self.amount if self.funds_locked else 0,
            "state": self.state
        }

# --------------------------
# Demo Simulation
# --------------------------

if __name__ == "__main__":
    escrow = MutexEscrow(buyer="Bob", seller="Alice", amount=100, timeout_secs=5)

    OPT_SUCCESS = True
    OPT_FAILURE = not OPT_SUCCESS

    print("\nInitial balances:", escrow.get_balances())

    time.sleep(1)
    escrow.confirm_shipment("Alice")

    if OPT_SUCCESS:
      time.sleep(2)
      escrow.confirm_receipt("Bob")  # Happy path
      print("Bob confirmed")

    if OPT_FAILURE: # Or try this instead to simulate timeout refund:
      time.sleep(6)
      escrow.refund_buyer_if_timeout()
      print("Bob has not confirmed")

    print("\nFinal balances:", escrow.get_balances())

""" OPT_SUCCESS = True
[INFO] Funds locked: 100 from Bob to contract

Initial balances: {'buyer': 0, 'seller': 0, 'contract_locked': 100, 'state': 'FUNDED'}
[ACTION] Shipment confirmed by seller.
[SUCCESS] Buyer confirmed receipt. Funds released to seller (Alice).
Bob confirmed

Final balances: {'buyer': 0, 'seller': 100, 'contract_locked': 0, 'state': 'RECEIVED'}
"""
""" OPT_SUCCESS = False
[INFO] Funds locked: 100 from Bob to contract

Initial balances: {'buyer': 0, 'seller': 0, 'contract_locked': 100, 'state': 'FUNDED'}
[ACTION] Shipment confirmed by seller.
[TIMEOUT] Buyer refunded. Timeout reached.
Bob has not confirmed

Final balances: {'buyer': 100, 'seller': 0, 'contract_locked': 0, 'state': 'REFUNDED'}
"""
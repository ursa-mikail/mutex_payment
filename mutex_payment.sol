// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MutexEscrow {
    enum State { Funded, Shipped, Received, Refunded }

    address public buyer;
    address public seller;
    uint256 public amount;
    uint256 public timeout;
    uint256 public lastActionTime;
    State public state;

    bool public fundsLocked;
    bool public initialized;

    constructor() {
        // Prevent accidental deployment with uninitialized state
        initialized = false;
    }

    function initialize(address _seller, uint256 _timeoutSecs) external payable {
        require(!initialized, "Already initialized");
        require(msg.value > 0, "Must send funds");
        buyer = msg.sender;
        seller = _seller;
        amount = msg.value;
        timeout = _timeoutSecs;
        lastActionTime = block.timestamp;
        state = State.Funded;
        fundsLocked = true;
        initialized = true;
    }

    modifier onlyBuyer() {
        require(msg.sender == buyer, "Only buyer can act");
        _;
    }

    modifier onlySeller() {
        require(msg.sender == seller, "Only seller can act");
        _;
    }

    function confirmShipment() external onlySeller {
        require(state == State.Funded, "Shipment not allowed now");
        state = State.Shipped;
        lastActionTime = block.timestamp;
        emit ShipmentConfirmed(seller);
    }

    function confirmReceipt() external onlyBuyer {
        require(state == State.Shipped, "Cannot confirm before shipment");
        state = State.Received;
        fundsLocked = false;
        payable(seller).transfer(amount);
        emit ReceiptConfirmed(buyer);
    }

    function refundBuyerIfTimeout() external {
        require(state == State.Shipped, "Refund not available in current state");
        require(block.timestamp > lastActionTime + timeout, "Timeout not reached");
        state = State.Refunded;
        fundsLocked = false;
        payable(buyer).transfer(amount);
        emit RefundedAfterTimeout(buyer);
    }

    function getBalances() external view returns (
        address _buyer,
        address _seller,
        uint256 buyerBalance,
        uint256 sellerBalance,
        uint256 contractLocked,
        string memory currentState
    ) {
        _buyer = buyer;
        _seller = seller;
        buyerBalance = buyer.balance;
        sellerBalance = seller.balance;
        contractLocked = fundsLocked ? amount : 0;
        currentState = stateToString(state);
    }

    function stateToString(State s) internal pure returns (string memory) {
        if (s == State.Funded) return "FUNDED";
        if (s == State.Shipped) return "SHIPPED";
        if (s == State.Received) return "RECEIVED";
        return "REFUNDED";
    }

    event ShipmentConfirmed(address indexed seller);
    event ReceiptConfirmed(address indexed buyer);
    event RefundedAfterTimeout(address indexed buyer);
}


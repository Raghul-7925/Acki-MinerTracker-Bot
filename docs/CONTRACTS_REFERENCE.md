# 📋 Mobile Verifier Contracts - Developer Reference

## **System Overview**

The Acki Nacki Mobile Verifier System is a tap-mining game where users earn rewards through solving mining puzzles.

### Main Contracts

```
MobileVerifiersContractGameRoot
├── Miner (user contracts)
├── PopitGame
├── Boost
└── PopCoinWallet
```

---

## **1. Miner Contract** ⛏️

**Purpose:** Tracks individual user's taps and mining data

**Location:** Deployed per user (derived address)

### Key State Variables

```solidity
address _mobileVerifiersContractGameRoot;     // Root contract reference
address _owner;                                // User's wallet
address _popitGame;                            // PopitGame contract
address _boost;                                // Boost contract
address _root;                                 // Root reference

// Tap tracking
uint128[] _taps;                              // Tap counts per interval
uint64[] _mbiCurTaps;                         // Current mining state
uint128 _tapSum = 0;                          // TOTAL TAPS ← You need this!
uint128 _tapSum5m = 0;                        // 5-minute tap window
uint128 _modifiedTapSum = 0;                  // Adjusted tap sum
uint128 _miningDurSum = 0;                    // Total mining duration

// Epoch tracking
uint64 _epochStart;                           // Current epoch start
uint64 _epochStartOld;                        // Previous epoch start
uint64 _epochBigStart;                        // Large epoch marker

// Difficulty
uint32 _easyComplexity = 10;                  // Easy mining difficulty
uint32 _hardComplexity = 11;                  // Hard mining difficulty

// Mining state
uint256 _seed;                                // Current random seed
uint256 _seedNext;                            // Next seed
optional(bytes) _commitData;                  // Commit proof
optional(Interval, Interval) _commitInterval; // Commit interval
```

### Main Functions

#### **getDetails()** 🔍 (READ-ONLY)
```solidity
function getDetails() external view returns(
    address mobileVerifiersContractGameRoot,
    address owner,
    address popitGame,
    address boost,
    optional(uint64) mbiCur,
    mapping(uint256=>uint256) owner_pubkey,
    uint64 epochStart,
    uint64 epochStartOld,
    uint128[] oldTaps,
    uint128 oldTapsSize,
    uint64[] oldMbiCurTaps,
    uint128[] taps,
    uint64[] mbiCurTaps,
    uint128 tapsSize,
    uint128 tapSum,              // ← TOTAL TAPS!
    uint128 modifiedTapSum,
    uint128 miningDurSum,
    uint64 epochBigStart,
    uint256 seed,
    uint256 seedNext,
    optional(bytes) commitData,
    optional(Interval, Interval) commitInterval,
    uint32 easyComplexity,       // Easy difficulty
    uint32 hardComplexity        // Hard difficulty
)
```

**Returns:** All user mining data including tap counts!

#### **getVersion()** ℹ️
```solidity
function getVersion() external pure returns(string, string)
```

Returns: Version info

#### **getTap()** (WRITE)
```solidity
function getTap(
    uint64 tap,
    uint64 tapEpochStart,
    address owner,
    uint64 mbiCur,
    uint32 easyComplexity,
    uint32 hardComplexity
)
```
Called by game to register a tap.

#### **setComplexity()** (WRITE)
```solidity
function setComplexity(uint32 easyComplexity, uint32 hardComplexity)
```
Called by root to update difficulty.

---

## **2. MobileVerifiersContractGameRoot** 🎮

**Purpose:** Main game root contract - manages all miners, rewards, and game logic

### Key State Variables

```solidity
// Reward tracking
uint128 _reward_sum = 0;                     // Total rewards distributed
uint128 _reward_adjustment = 0;              // Reward multiplier
uint32 _reward_last_time = 0;               // Last reward calculation
uint32 _reward_period = 520000;             // Reward period (blocks)
uint32 _min_reward_period = 520000;         // Minimum period

// Epoch management
uint64 _epochStart;                         // Current epoch start (seq_no)
mapping(uint64 => TapData) _tapData;        // Global tap data per epoch

// Difficulty
uint32 _easyComplexity = 10;                // Easy difficulty
uint32 _hardComplexity = 11;                // Hard difficulty

// Network
uint32 _networkStart;                       // Network start time
```

### Main Functions

#### **getTap()** (WRITE)
```solidity
function getTap(
    uint64 tap,
    uint64 tapEpochStart,
    address owner,
    uint64 mbiCur,
    uint32 easyComplexity,
    uint32 hardComplexity
)
```
Root receives taps from Miner contracts.

#### **tapReward()** (WRITE)
```solidity
function tapReward(
    TvmCell tapData,
    uint64 epochStart,
    address popitGame,
    address owner,
    uint32 easyComplexity,
    uint32 hardComplexity
)
```
Calculates and distributes rewards based on taps.

#### **setComplexity()** (WRITE)
```solidity
function setComplexity(uint32 easyComplexity, uint32 hardComplexity)
```
Owner updates mining difficulty.

#### **setConfig()** (WRITE)
```solidity
function setConfig(
    uint128 reward_sum,
    uint128 reward_adjustment,
    uint32 reward_period,
    uint32 min_reward_period,
    uint32 reward_last_time,
    uint32 calc_reward_num
)
```
Update game configuration.

#### **getVersion()** ℹ️
```solidity
function getVersion() external pure returns(string, string)
```

---

## **3. PopitGame Contract** 🎪

**Purpose:** Game interface - manages game rounds and user interactions

### Functions
- Game logic
- Round management
- User interactions

---

## **4. Boost Contract** ⚡

**Purpose:** Multiplier system - applies boost to tap rewards

### Features
- Boost multipliers
- Boost rewards
- Activation/deactivation

---

## **Important Constants**

From the contract code:

```
MinerRewardPeriod = 2,200,000 blocks
MinerRewardDelay = 3 epochs
MINING_DUR_TAP = 30 seconds
vectorSize = 256
```

### Epoch Duration
```
One epoch ≈ 2,200,000 blocks
At ~5 seconds/block ≈ 3.3 hours per epoch
```

### Reward Calculation
```solidity
reward = gosh.calcminerreward(
    miningCur,
    globalTapData,
    userTaps,
    basicReward
)
```

---

## **Data Structures**

### TapData
```solidity
struct TapData {
    uint64[] tapData;          // Per-segment tap data
    uint128 basicReward;       // Base reward per tap
}
```

### Interval
```solidity
struct Interval {
    // Mining work interval details
    // Used in commit/reveal scheme
}
```

---

## **Querying Via GraphQL**

### Example: Get Miner Data
```graphql
query {
    accounts(
        filter: {
            id: { eq: "0:abc123..." }
        }
    ) {
        id
        balance
        data
        acc_type_name
    }
}
```

The `data` field contains the contract's state (encoded in hex).

---

## **Events**

### Miner Events
```solidity
event TapSucceed(bytes data, bytes wasmResult);      // Tap accepted
event TapFailed(bytes data, bytes wasmResult);       // Tap rejected
event GetInterval(Interval easy, Interval hard, uint64 workerId);
event NewSeed(uint256 seed, uint256 seednext);       // New random seed
event NewComplexity(uint32 easyComplexity, uint32 hardComplexity);
```

### GameRoot Events
```solidity
event Rewarded(address popitGame, uint128 reward);
event RewardedPopitGame(uint128 reward);
```

---

## **Finding Your Miner Contract Address**

### Method 1: From Mirror Address
Miner address is calculated as:
```
address = address.makeAddrStd(0, BASE_PART * SHIFT + index + 1)
```

Where:
- `index` = your user index
- `BASE_PART` = constant
- `SHIFT` = constant

### Method 2: From Account History
1. Go to block explorer
2. Find your game interaction
3. Look for created contracts
4. Find the Miner-like address

### Method 3: Ask Game Provider
Simplest! They know the formula.

---

## **Key Formulas**

### Tap Sum Calculation
```
tapSum = sum of all _taps[i] values
```

### Mining Duration
```
miningDurSum = total time spent mining (blocks)
```

### Epoch Reset Time
```
epochStart = blockSeqNo - (blockSeqNo % MinerRewardPeriod)
nextEpoch = epochStart + MinerRewardPeriod
```

### Approximate Reset in Hours
```
hoursUntilReset = (MinerRewardPeriod / blockTime) / 3600
                = (2,200,000 / 5) / 3600
                ≈ 3.3 hours
```

---

## **Version Info**

Current contracts:
- **Miner:** v1.0.0
- **MobileVerifiersContractGameRoot:** v1.0.0
- **PopitGame:** TBD
- **Boost:** TBD

---

## **Testing Contract Functions**

### Using tvm-cli

#### Get Miner Details
```bash
tvm-cli run <MINER_ADDRESS> getDetails {} --abi Miner.abi.json
```

#### Get Version
```bash
tvm-cli run <MINER_ADDRESS> getVersion {} --abi Miner.abi.json
```

#### Get Game Root Details (if exists)
```bash
tvm-cli run <GAME_ROOT_ADDRESS> getVersion {} --abi MobileVerifiersContractGameRoot.abi.json
```

---

## **Common Queries**

### "What's my total tap count?"
Answer: `tapSum` from Miner.getDetails()

### "When does the epoch reset?"
Answer: Calculate from `epochStart` + MinerRewardPeriod (≈3.3 hours)

### "What's my current difficulty?"
Answer: `easyComplexity` and `hardComplexity` from Miner.getDetails()

### "How many rewards have I earned?"
Answer: Check rewards distributed to you via events or game dashboard

---

## **Contract Source Files**

From the uploaded mvsystem contracts:

```
├── Miner.sol                              ← User miner (tap tracking)
├── MobileVerifiersContractGameRoot.sol    ← Game root
├── PopitGame.sol                          ← Game logic
├── Boost.sol                              ← Boost multiplier
├── Boost_1.0.1.sol                        ← Boost v1.0.1
├── Mirror.sol                             ← Mirror contract
├── PopCoinRoot.sol                        ← Reward coin root
├── PopCoinWallet.sol                      ← Reward wallet
├── Mvmultifactor.sol                      ← Multi-factor
├── Indexer.sol                            ← Indexing
└── libraries/VerifiersLib.sol             ← Shared library
```

---

## **Deployment Addresses**

You need:
1. **Your Miner Contract Address** - Track YOUR taps
2. **Game Root Address** - Global game data (optional)

Ask your game provider or find on block explorer.

---

## **Further Reading**

- Acki Nacki Docs: https://docs.ackinacki.com
- Contract GitHub: https://github.com/ackinacki/ackinacki/tree/main/contracts/mvsystem
- TVM Solidity: https://ton.org/docs/

---

Good luck tracking those taps! 🎯⛏️

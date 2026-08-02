---
layout: post
title: 'Beyond Raft and Paxos: How Cloudflare Meerkat and QuePaxa Redefine Global
  Consensus'
date: 2026-08-02 14:03:16 +0530
categories: Tech
excerpt: As distributed computing shifts to the global edge, traditional consensus
  protocols like Raft and Paxos fail under WAN network jitter. Cloudflare's Meerkat
  and QuePaxa offer an asynchronous alternative designed for global scale.
cover_image: /assets/images/posts/cloudflare-meerkat-quepaxa-global-consensus-cover.png
cover_caption: An abstract visualization of global edge network nodes interconnected
  across continents.
---

For over a decade, Raft and Paxos have served as the undisputed bedrock of distributed systems. From etcd powering Kubernetes clusters to Spanner coordinating global transactions, modern infrastructure relies heavily on these strong-consistency protocols. They work exceptionally well within the controlled, low-latency environment of a single datacenter or a tight multi-zone deployment. 

However, as computing moves to the edge, the fundamental assumptions underlying classic consensus algorithms begin to crumble. When control planes expand across global Wide Area Networks (WANs), network jitter, fluctuating latencies, transoceanic fiber cuts, and packet loss transform reliable leader elections into catastrophic availability outages.

To solve this challenge at edge scale, Cloudflare designed **Meerkat**, a globally consistent control-plane service powered by a novel consensus algorithm called **QuePaxa**. By abandoning fixed timeouts and leader-centric write bottlenecks, Meerkat demonstrates how asynchronous consensus can deliver linearizable reads and writes across global edge nodes without succumbing to the failure modes of traditional protocols.

---

## The Global Edge Dilemma: Why Classic Consensus Struggles on WANs

Distributed control planes manage critical runtime metadata: feature flags, routing tables, security policy definitions, TLS certificates, and distributed leases. In single-datacenter environments, coordinating this state is straightforward. Round-Trip Times (RTT) are sub-millisecond, packet loss is negligible, and network topology is stable.

When you push a control plane to a global edge network comprising hundreds of Points of Presence (PoPs) across continents, the physical reality of the network changes completely:

```
+-----------------------------------------------------------------------+
|                         GLOBAL WAN ENVIRONMENT                        |
|                                                                       |
|   [PoP: San Jose] <==== trans-pacific ====> [PoP: Tokyo]              |
|        ||  (RTT: ~120ms, Jitter: ±40ms)          ||                   |
|        ||                                        ||                   |
|   trans-atlantic                           trans-indian               |
|  (RTT: ~80ms)                            (RTT: ~180ms)                |
|        ||                                        ||                   |
|        \/                                        \/                   |
|   [PoP: London]   <==== trans-Eurasian ====> [PoP: Singapore]          |
|                   (RTT: ~210ms, Packet Loss: 0.5-2%)                  |
+-----------------------------------------------------------------------+
```

Across wide-area links, modern consensus systems encounter three core physical limitations:

1. **Unpredictable Latency Variance (Jitter):** BGP rerouting, congestion, and underlying hardware faults cause RTTs to swing wildly. A path between London and Tokyo might average 200ms but spike to 1,500ms without total packet loss.
2. **Asymmetric Packet Loss:** WAN connections frequently drop individual packets or experience transient burst loss, delaying acknowledgment vectors without severing the physical TCP connection.
3. **Non-Uniform Node Interconnectivity:** A replica in São Paulo may communicate cleanly with Miami but experience severe degradation when reaching Sydney, creating partial isolation states.

When a global edge service relies on a classic consensus engine for its control plane, network instability directly degrades availability. If the consensus engine halts progress because of network jitter, edge nodes cannot resolve global routing changes, acquire leases, or update security rules. For high-scale edge providers like Cloudflare, a few seconds of control-plane unavailability can stall configuration rollouts or disrupt global request routing.

---

## The Fragility of Partial Synchrony: The Limits of Raft and Paxos

To understand why traditional algorithms struggle on WANs, we must examine their foundational theoretical assumption: **partial synchrony**.

### The Partial Synchrony Assumption

Classic algorithms like Raft, Multi-Paxos, and Viewstamped Replication operate under the partial synchrony network model. They assume that while the network may experience arbitrary delays initially, there exists a *Global Stabilization Time* ($\text{GST}$) after which message transmission delays are bounded by a fixed upper limit ($\Delta$).

To detect failures under this model, these algorithms use **timeout-driven failure detectors**. A follower expects a heartbeat from the leader within a fixed window (e.g., $150\text{ms} - 300\text{ms}$). If no heartbeat arrives before the timer expires, the follower assumes the leader is dead and triggers a new election.

```
Leader                     Follower 1                  Follower 2
  |                            |                           |
  |--- Heartbeat ------------->|                           |
  |    (Delayed by WAN jitter) |                           |
  |                            |                           |
  |                            |-- [Timer Expires!] ------>|
  |                            |   Triggers Election       |
  |                            |<-- RequestVote -----------|
  |                            |                           |
```

### Why Fixed Timeouts Fail Across WANs

On a global WAN, the assumption of a stable bound $\Delta$ constantly fails. If you set the election timeout too low (e.g., $150\text{ms}$), transient network jitter triggers spurious leader elections. Followers falsely suspect healthy leaders, causing constant leadership transitions.

If you set the timeout too high (e.g., $5,000\text{ms}$) to prevent false elections, the cluster becomes unresponsive for five seconds whenever a genuine leader crash occurs.

This design introduces severe failure modes in WAN environments:

* **Election Storms:** When the leader experiences temporary transit delays, multiple followers simultaneously trigger elections. Their vote requests collide over lossy WAN links, causing split votes and repeated election rounds during which the cluster cannot commit writes.
* **Tail-Latency Amplification:** Because all write requests in Raft must be funneled through a single designated leader, a client located in Singapore attempting to write to a leader in Virginia incurs a minimum half-globe RTT ($~180\text{ms}$) just to reach the leader, plus additional RTTs for the leader to replicate the log entry to a quorum.
* **Leader Bottlenecking:** Funneling every mutation through one node creates a centralized CPU and network I/O bottleneck, bottlenecking global system throughput.

---

## Demystifying QuePaxa: Asynchronous Consensus Without Timeouts

To eliminate the vulnerabilities of partial synchrony, researchers and engineers turned toward **fully asynchronous consensus**. 

### The Asynchronous Paradigm

In a fully asynchronous model, no assumptions are made about network delay bounds or clock synchronization. Messages can be delayed arbitrarily, reordered, or duplicated without impacting algorithm correctness or liveness guarantees.

Historically, the **Fischer-Lynch-Paterson (FLP) Impossibility Result** proved that no deterministic asynchronous consensus protocol can guarantee both safety and liveness in a distributed system if even a single process can experience unannounced failure. 

Modern asynchronous algorithms overcome FLP by introducing randomized choices or structure-driven consensus abstractions that guarantee liveness with high probability, without ever relying on clock sync or timeout-driven failure detectors.

### How QuePaxa Eliminates Timeouts

QuePaxa is an asynchronous consensus algorithm engineered specifically to overcome the constraints of WAN infrastructure. Unlike Raft, QuePaxa does not monitor node health using countdown timers or heartbeat loops. 

Instead of asking *"Has the leader responded within $X$ milliseconds?"*, QuePaxa asks *"Have we received a valid, quorum-backed cryptographic progress proof for this consensus round?"*

```
Traditional (Raft/Paxos)          QuePaxa (Asynchronous)
------------------------          ----------------------
Clock / Timeout Dependent         Pure Message / Proof Driven
      |                                 |
 [Start Timer]                          |--> [Propose Value + Vector]
      |                                 |          |
 [Timer Expired?]                       |     [Receive Quorum Proof]
   /        \                           |          |
(Yes)       (No)                        |---> [Advance Log Slot]
  |          |                          (No timeouts or clocks required)
Trigger     Keep
Election    Waiting
```

QuePaxa guarantees both safety and progress under wild latency fluctuations and unpredictable message delivery through three core mechanics:

1. **Timeout-Free Progress:** State transitions occur purely in response to receiving valid sets of messages (quorums), rather than the ticking of a clock. If a link drops packets for 30 seconds, QuePaxa simply waits without altering leadership topology or launching destructive reelection cycles.
2. **Leaderless Write Paths:** Clients or local replicas can initiate proposals without first routing the request to a single global primary node.
3. **Asynchronous Round Escalation:** When a proposal stalls due to competing writes or network isolation, QuePaxa uses randomized, message-driven round escalation to resolve conflicts and select a winning value without relying on synchronized timers.

---

## Inside Cloudflare Meerkat: Architecture of a Global Control Plane

Meerkat is Cloudflare's internal control-plane engine built on top of the QuePaxa algorithm. It translates QuePaxa's theoretical consensus model into a production-grade, state-machine-replicated log service.

### The Slot-Based Replicated Log

Meerkat structures its global consensus state as an append-only log divided into discrete, ordered **slots**. Each slot represents a single consensus decision in the state machine execution sequence.

```
+-------------------------------------------------------------------------+
|                       MEERKAT REPLICATED LOG                            |
|                                                                         |
|   Slot 101       Slot 102       Slot 103       Slot 104 (Active)        |
|  +--------+     +--------+     +--------+     +-------------------+     |
|  | DECIDED| --> | DECIDED| --> | DECIDED| --> |  UNDER CONSENSUS  |     |
|  | (KV-A) |     | (KV-B) |     | (KV-C) |     | (Accepting Props) |     |
|  +--------+     +--------+     +--------+     +-------------------+     |
+-------------------------------------------------------------------------+
```

Log slots in Meerkat exist in two fundamental states:

* **Decided Slots:** Historical entries where consensus has been reached and finalized across a quorum. Decided slots are immutable and can be read locally by edge replicas with strict consistency.
* **Active Slots:** The current slot (or set of uncommitted slots) actively executing the QuePaxa agreement protocol.

### Leaderless Writes and Proposal Rounds

When a client or an edge PoP needs to write a key-value entry or refresh a distributed lease, it does not route the request to a distant leader node. Instead, it submits the write proposal directly to its local Meerkat replica instance.

1. **Proposal Injection:** The local replica acts as the *proposer* for the active log slot.
2. **Phase 1 (Prepare/Payload Distribution):** The proposer broadcasts the proposed log entry to all known replicas across the WAN.
3. **Phase 2 (Asynchronous Accord):** Replicas evaluate the proposal against their current slot index. If no conflicting decision has been reached for that slot, they return a cryptographic vote acknowledgment to the proposer.
4. **Commit Phase:** Once the proposer collects a valid quorum of responses, it emits a commit decision, transitioning the active slot into the **Decided** state and advancing the log head.

If two edge nodes propose different operations for the exact same active slot simultaneously, QuePaxa’s conflict resolution mechanism resolves the collision asynchronously. One proposal wins the slot, while the losing proposal is automatically bumped to the next active log slot without triggering cluster-wide leader elections.

### Log State Pseudocode

The following pseudocode illustrates how a Meerkat replica manages slot progression and evaluates proposals without relying on election timeouts:

```python
class SlotState:
    DECIDED = "DECIDED"
    ACTIVE = "ACTIVE"

class ConsensusSlot:
    def __init__(self, slot_id):
        self.slot_id = slot_id
        self.state = SlotState.ACTIVE
        self.accepted_value = None
        self.votes_received = set()
        self.highest_round = 0

class MeerkatEngine:
    def __init__(self, node_id, cluster_nodes):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.quorum_size = (len(cluster_nodes) // 2) + 1
        self.log = []
        self.current_slot_idx = 0
        self.log.append(ConsensusSlot(0))

    def handle_proposal(self, slot_id, round_num, proposal_value, sender_id):
        slot = self._get_or_create_slot(slot_id)
        
        # If the slot is already decided, ignore new proposals for it
        if slot.state == SlotState.DECIDED:
            return self._send_decided_ack(sender_id, slot.slot_id, slot.accepted_value)

        # Accept proposal if round is greater or equal
        if round_num >= slot.highest_round:
            slot.highest_round = round_num
            slot.accepted_value = proposal_value
            slot.votes_received.add(sender_id)

            # Check if quorum is reached purely based on message count
            if len(slot.votes_received) >= self.quorum_size:
                slot.state = SlotState.DECIDED
                self._advance_log(slot_id)
                return self._broadcast_commit(slot_id, slot.accepted_value)

        return self._send_vote_ack(sender_id, slot_id, slot.highest_round)

    def _advance_log(self, completed_slot_id):
        if completed_slot_id == self.current_slot_idx:
            self.current_slot_idx += 1
            if len(self.log) <= self.current_slot_idx:
                self.log.append(ConsensusSlot(self.current_slot_idx))
```

---

## Architectural Comparison: Raft vs. Multi-Paxos vs. QuePaxa/Meerkat

To highlight the structural differences between these consensus families, consider how each algorithm handles key architectural parameters:

| Metric / Dimension | Raft | Multi-Paxos | QuePaxa / Meerkat |
| :--- | :--- | :--- | :--- |
| **Network Synchrony Model** | Partial Synchrony | Partial Synchrony | Asynchronous |
| **Write Topology** | Leader-centric (Single Proposer) | Leader-centric (Primary) | Leaderless / Multi-Proposer |
| **Failure Detection** | Fixed Timeouts & Heartbeats | Fixed Timeouts & Heartbeats | Message & Quorum Proof Driven |
| **WAN Jitter Impact** | High (Causes election storms) | Moderate (Pipelined, but leader dependent) | Low (No timeout triggers) |
| **Write Latency (Global)** | $1 \text{ RTT (to leader)} + 1 \text{ RTT (to quorum)}$ | $1 \text{ RTT (if leader established)}$ | $1 \text{ RTT (direct to local quorum)}$ |
| **Slot Log Model** | Continuous Sequential Log | Unordered or Ordered Log | Slot-based Replicated Log |
| **Primary Use Case** | Single-DC / Multi-Zone Control | Multi-DC Database Engines | Global WAN / Edge Control Planes |

### Key Trade-Off Analysis

#### 1. Leader Dependency vs. Leaderless Write Paths
In Raft, every client write *must* be processed by the active leader. If a client is in Tokyo and the leader is in Frankfurt, the write incurs a minimum $200\text{ms}$ cross-continental round trip before processing even begins. 

Meerkat's leaderless write model allows any replica to propose writes directly to the active slot log. A node in Tokyo can propose a write locally, gathering votes from nearby regional quorums, reducing initial write propagation latency.

#### 2. Behavior Under Asymmetric Network Partitions
If a Raft leader becomes partially isolated—able to send heartbeats to a minority of nodes but unable to complete quorums—it holds leadership until a follower times out and triggers an election. During this window, client writes sent to the partitioned leader stall indefinitely.

Under QuePaxa, because progress is driven by explicit quorum progress proofs rather than time-based heartbeats, partial partitions do not cause system-wide halts. The unpartitioned majority continues committing entries into upcoming slots without waiting for isolated nodes to check in.

---

## Real-World Feasibility: Proof of Concept and Performance Metrics

Moving asynchronous consensus from academic theory to operational software requires rigorous testing. Cloudflare constructed a proof-of-concept (POC) deployment of Meerkat to evaluate its viability under realistic global conditions.

### Testbed Setup

The POC environment was deployed across **50 globally distributed edge replicas** spanning North America, Europe, Asia-Pacific, South America, and Africa. The deployment was subjected to simulated WAN degradation patterns:

* Random injection of packet loss ($0.5\%$ to $5\%$).
* Synthetic latency spikes ($\pm 300\text{ms}$ phase shifts).
* Transient node isolation events.

```
+------------------------------------------------------------------+
|                   MEERKAT POC TESTBED (50 REPLICAS)              |
|                                                                  |
|    [North America] <---- 5% Loss ----> [Europe]                  |
|          |                                 |                     |
|     +300ms Jitter                     +150ms Jitter              |
|          v                                 v                     |
|    [Asia-Pacific]  <--- 2% Loss ---->  [South America / Africa]  |
+------------------------------------------------------------------+
```

### Empirical Findings

The empirical data from the Meerkat proof-of-concept highlighted key performance characteristics under degraded network conditions:

1. **Tail-Latency Stability ($p99.9$):** While Raft's $p99.9$ commit latency spiked dramatically during high-jitter events due to spurious election timeouts, Meerkat’s $p99.9$ latency scaled smoothly alongside the actual physical network propagation delay.
2. **Throughput Retention Under Packet Loss:** Under a simulated $3\%$ network packet loss across global transit links, traditional timeout-based consensus engines experienced severe throughput drops caused by lost heartbeat packets triggering re-elections. QuePaxa maintained continuous log commit throughput, limited only by underlying TCP retransmission rates.
3. **Recovery Time Objective (RTO):** When nodes were abruptly severed from the network, Meerkat required zero timeout delay to resume progress. The remaining active quorum continued processing writes for subsequent slots without waiting for a failure detector to declare the missing nodes dead.

### Engineering Constraints and Challenges

Despite these advantages, building an asynchronous control plane introduces unique pre-production challenges:

* **Conflict Resolution Overheads:** When write contention is extremely high—such as hundreds of global edge nodes simultaneously writing to the exact same log slot—QuePaxa incurs additional round trips to resolve winning proposals, increasing short-term write latency.
* **Log Compaction and Garbage Collection:** Because slots can be finalized out-of-order internally before being committed sequentially to the state machine, managing log compaction and memory footprint across 50+ heterogeneous nodes requires complex state synchronization mechanisms.

---

## The Future of Distributed Infrastructure: Edge Control Planes Beyond Raft

The introduction of Cloudflare Meerkat and the QuePaxa consensus algorithm represents a significant shift in distributed systems engineering. For years, the industry accepted the operational vulnerabilities of partial synchrony and timeout-driven failure detectors as an unavoidable tax for strong consistency.

As global application architectures become increasingly decentralized, relying on centralized, single-leader consensus models introduces unacceptable latency and availability risks. The success of asynchronous, slot-based architectures points toward a future where:

* **Multi-Region and Edge Platforms** adopt leaderless, timeout-free consensus engines to power transactional key-value platforms, distributed leasing systems, and dynamic service discovery.
* **Open-Source Infrastructure** begins looking beyond standard Raft implementations (like etcd) in favor of flexible consensus engines designed specifically for high-latency, unreliable WAN environments.
* **Consensus Agnosticism** becomes standard in control planes, allowing operations teams to toggle between Raft for single-datacenter deployments and asynchronous protocols like QuePaxa for global edge execution.

By re-evaluating the foundational assumptions of consensus protocols, systems like Meerkat demonstrate that global edge control planes can achieve both linearizable strong consistency and high availability—even across the unpredictable networks that span the globe.

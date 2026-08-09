---
layout: post
title: 'Autonomous Database Remediation: How Stripe Uses Graph Search and State Machines
  for Fleet Health'
date: 2026-08-09 12:35:40 +0530
categories: Tech
excerpt: Imperative runbooks fail when distributed system outages cascade into unpredictable
  states. Learn how Stripe built an algorithmic control plane using stateful graphs
  and state machines to autonomously heal database fleets.
cover_image: /assets/images/posts/stripe-graph-search-database-remediation-cover.png
cover_caption: A visual representation of a distributed database fleet modeled as
  a stateful graph.
---

In large-scale distributed systems, database reliability is rarely about preventing failures entirely. Instead, it is about how gracefully the infrastructure recovers when failures inevitably occur. For years, the industry standard for automated recovery relied on imperative runbooks—complex suites of Python scripts, shell commands, and plugin-driven control planes designed to handle specific failure scenarios. 

However, as database fleets scale into thousands of shards and multi-region deployments, imperative runbook automation reaches its breaking point. Imperative scripts assume a predictable sequence of events: if Condition A occurs, execute Step B, then verify State C. In reality, distributed database failures are rarely linear. A single network micro-partition can trigger a cascading sequence of state changes across primary nodes, secondary replicas, and routing proxies simultaneously.

When an imperative script encounters an unexpected intermediate state during a complex failure cascade, it usually fails in one of two ways: it halts abruptly, requiring human intervention, or it blindly executes actions against a state that no longer matches its hard-coded assumptions, worsening the outage.

At Stripe, managing an extensive database fleet—primarily built on MongoDB—highlighted the severe limitations of legacy runbook automation. Over a single six-month window, operational logs revealed the compounding toll of script-based control planes: **124 misconfigured shard alerts** and **32 single-node failure alerts**. Each alert represented a scenario where rigid automation could not safely reconcile the cluster state, forcing on-call engineers to step in and manually execute recovery steps.

To solve this, Stripe fundamentally rethought control plane design. Rather than writing procedural scripts for every imaginable outage scenario, Stripe transitioned to an **algorithmic control plane**. By modeling the entire database fleet as a stateful graph and leveraging Finite State Machines (FSMs) alongside graph search algorithms like Dijkstra's, the system dynamically calculates the optimal, risk-aware path from any degraded state back to fleet health.

---

## Modeling Distributed Infrastructure as a Stateful Graph

To move away from hard-coded execution paths, an automated system must first understand the complete topology and state of the infrastructure it manages. Stripe achieved this by abstracting its MongoDB database fleet into a stateful, directed graph.

In this model, the physical and logical components of the infrastructure are decoupled from procedural logic and represented as graph primitives:

*   **Nodes (Infrastructure Components):** Every distinct operational entity in the fleet is represented as a node. This includes individual MongoDB replica set members, database shards, and routing proxies (such as `mongos` instances).
*   **Edges (Dependencies and Topology):** Directed edges define the relationships, connectivity, and dependencies between nodes. An edge might represent an active replication stream between a primary and secondary instance, a network adjacency between nodes in the same availability zone, or a proxy route directing client traffic to a specific shard.
*   **Node Attributes (Live Operational State):** Rather than treating nodes as static entities, live operational telemetry is encoded directly into node attributes. A node’s state includes its current role (e.g., `PRIMARY`, `SECONDARY`, `UNREACHABLE`), replication lag, disk utilization, configuration generation, and process health.

```
       +-------------------------------------------------------+
       |                  Shard Topology Graph                 |
       +-------------------------------------------------------+
                                   |
                                   v
                      +-------------------------+
                      |   Router Proxy Node     |
                      |  (State: Routing Active)|
                      +-------------------------+
                               /       \
                              /         \  [Proxy Route Edge]
                             v           v
       +------------------------+     +------------------------+
       | Primary Replica Node   |     | Secondary Replica Node |
       | (State: Health OK)     |     | (State: Degraded/Lag)  |
       +------------------------+     +------------------------+
                    |                             ^
                    +-----------------------------+
                        [Replication Stream Edge]
```

By binding live telemetry to node attributes in real time, static topology diagrams are transformed into a dynamic network of Finite State Machines (FSMs). 

Every component in the graph operates as an FSM with well-defined, valid state transitions. For example, a database node cannot instantly transition from `UNREACHABLE` to `PRIMARY`; it must pass through explicit intermediate states such as `STARTING`, `RECOVERING`, and `SECONDARY_SYNCED`.

```python
# Conceptual representation of a stateful infrastructure graph node
class MongoReplicaNode:
    def __init__(self, node_id: str, zone: str):
        self.node_id = node_id
        self.zone = zone
        # Live Node Attributes (FSM State)
        self.attributes = {
            "health_status": "UNREACHABLE",
            "role": "UNKNOWN",
            "replication_lag_seconds": float("inf"),
            "config_version": 102
        }
        # Graph Relationships (Edges)
        self.edges = {
            "replication_source": None,
            "connected_proxies": []
        }

    def update_telemetry(self, telemetry_data: dict):
        """Ingests live telemetry to update node FSM state."""
        self.attributes["health_status"] = telemetry_data.get("status")
        self.attributes["role"] = telemetry_data.get("role")
        self.attributes["replication_lag_seconds"] = telemetry_data.get("lag", float("inf"))
```

When an incident occurs—such as a network partition or hardware fault—the graph automatically reflects the updated attributes across affected nodes. The operational problem is no longer "Which script do we run for this specific outage?" but rather "What sequence of valid state transitions moves our current graph state to a fully healthy target state?"

---

## Pathfinding for Recovery: From BFS to Dijkstra's Algorithm

Once infrastructure is represented as a stateful graph, calculating a recovery plan becomes a pathfinding problem. The control plane must navigate the graph from Node State $A$ (Degraded) to Node State $B$ (Healthy) through a series of administrative actions (state transitions).

Initially, one might consider using **Breadth-First Search (BFS)** to calculate the shortest recovery path. BFS is well-suited for unweighted graphs, where the goal is simply to minimize the total number of hops (or administrative actions) required to reach the target state. 

### Why Breadth-First Search Fails in Production

In real-world systems engineering, treating all recovery actions as having equal cost is dangerous. BFS evaluates a 1-step action and another 1-step action as identical in weight, regardless of what those actions actually do.

Consider two potential administrative actions available to the control plane:
1. **Restarting a local `mongod` process:** Takes ~10 seconds, carries minimal operational risk, and maintains disk state.
2. **Triggering an initial resync (wiping disk and rebuilding from primary):** Takes ~6 hours, consumes significant network bandwidth, and puts heavy read pressure on the primary node.

Under BFS, both actions are evaluated as a single step ($Cost = 1$). If BFS identifies a 2-step path that includes an initial resync, it will prefer it over a 3-step path that consists of soft process restarts and configuration reloads. In production, executing an unnecessary resync on a core database cluster can severely degrade performance or lead to secondary outages.

```
                            [ Degraded State ]
                                   /  \
            (1 Step, High Risk)   /    \   (1 Step, Low Risk)
                                 v      v
              [ Trigger Initial Resync ]  [ Soft Reload Config ]
                         |                       |
                         | (1 Step)              | (1 Step)
                         v                       v
               [ Complete Recovery ]     [ Step Down Primary ]
                                                 |
                                                 | (1 Step)
                                                 v
                                       [ Complete Recovery ]

  BFS Choice:   Left Path  (2 Steps total) -> Catastrophic Network Load
  Dijkstra Choice: Right Path (Weight: 5+2+1=8) vs Left Path (Weight: 100+1=101)
```

### Formulating Operational Risk with Dijkstra's Algorithm

To fix this, Stripe shifted from unweighted BFS pathfinding to **Dijkstra's algorithm**, which accounts for edge weights. 

In this framework, edge weights represent the **operational cost and risk** of executing a state transition. Operational risk is quantified using several key parameters:
* **Execution Duration:** How long the administrative action takes to complete.
* **Resource Cost:** The CPU, memory, network, and disk I/O load placed on the remaining healthy cluster members.
* **Blast Radius / Availability Impact:** The likelihood of causing temporary write pauses, step-downs, or reduced redundancy during the transition.

By assigning non-negative weights to graph edges based on these factors, the control plane applies Dijkstra's algorithm to compute the absolute lowest-cost path from a degraded state to a healthy target state.

```python
import heapq

class RecoveryPathfinder:
    def __init__(self):
        # Define graph transitions: adjacency list with (neighbor_state, transition_cost, action_name)
        self.transitions = {}

    def add_transition(self, from_state: str, to_state: str, cost: float, action: str):
        if from_state not in self.transitions:
            self.transitions[from_state] = []
        self.transitions[from_state].append((to_state, cost, action))

    def find_lowest_risk_path(self, start_state: str, target_state: str):
        """
        Uses Dijkstra's algorithm to compute the lowest-cost recovery path
        based on operational risk weights.
        """
        # Priority queue stores tuples of (cumulative_cost, current_state, path_taken)
        pq = [(0.0, start_state, [])]
        visited = set()

        while pq:
            cost, current, path = heapq.heappop(pq)

            if current in visited:
                continue
            visited.add(current)

            if current == target_state:
                return cost, path

            for neighbor, weight, action in self.transitions.get(current, []):
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + weight, neighbor, path + [(action, neighbor)]))

        return float("inf"), [] # Return infinity if no valid path exists
```

Using this algorithmic approach, the control plane dynamically balances fast recovery against operational safety. If a 3-step transition path has a combined risk score of $8$, while a 2-step path has a risk score of $101$, Dijkstra's algorithm will always select the 3-step path.

---

## Handling Incomplete Paths with Partial Remediation

In a perfect world, a recovery algorithm would always find a valid path to a $100\%$ healthy target state. But distributed systems frequently experience severe, compound failures—such as concurrent hardware faults, simultaneous disk corruptions, or persistent network isolation.

In these degraded scenarios, a path to `Fully Healthy` may not exist in the graph.

Legacy runbooks typically stall when faced with an unrecoverable node, leaving the entire system unmanaged and generating noisy, continuous alerts until an engineer intervenes. An algorithmic control plane, however, handles these conditions using **Partial Remediation**.

```
              +-------------------------------------------------+
              |            Current Degraded State               |
              +-------------------------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     | Is 'Fully Healthy' Target Reachable?|
                     +-----------------------------------+
                                  /         \
                             No  /           \ Yes
                                /             \
                               v               v
    +----------------------------------+  +------------------------+
    |    Calculate Traversal Distance  |  |  Execute Optimal Path  |
    |    To All Reachable States       |  |   To Fully Healthy     |
    +----------------------------------+  +------------------------+
                               |
                               v
    +----------------------------------+
    | Select Nearest Safe Intermediate |
    |      State (Partial Target)      |
    +----------------------------------+
                               |
                               v
    +----------------------------------+
    | Execute Partial Remediation Path |
    |  & Notify Human for Remainder    |
    +----------------------------------+
```

### Defining Partial Remediation

When Dijkstra's algorithm determines that the primary `Healthy` state is mathematically unreachable, it does not abort. Instead, it evaluates all reachable intermediate states in the graph and selects the state with the minimum distance (lowest accumulated cost) to the target state.

Partial remediation moves the infrastructure into the **least misconfigured, safest intermediate state** possible given current constraints.

For instance, consider a scenario where a three-node MongoDB replica set suffers a failure on Node C (disk failure) while Node B is experiencing severe network degradation:
1. Re-establishing full three-node redundancy (`Healthy Target`) is impossible because Node C cannot write to disk.
2. Rather than doing nothing, the control plane executes a partial remediation path:
   * Demotes Node C from active participation to prevent voting deadlocks.
   * Reconfigures routing proxies (`mongos`) to direct client traffic exclusively to Node A and Node B.
   * Adjusts read/write concerns to ensure remaining nodes maintain data consistency safely.

### Reducing On-Call Fatigue

By executing partial remediation automatically, the control plane stabilizes the cluster and prevents cascading failures across dependent microservices. 

It also changes the nature of on-call response. Instead of waking an engineer at 2:00 AM for a high-priority emergency page because an entire shard is failing, the control plane handles non-critical state dependencies automatically. It brings the cluster into a safe, degraded holding pattern, silences downstream alerts, and files a low-priority ticket for the hardware team to replace Node C's disk during business hours.

---

## Architecture of an Algorithmic Control Plane in Production

Implementing graph search and state-machine transitions at scale requires a decoupled, resilient architecture. Stripe’s algorithmic control plane separates state detection, path calculation, and action execution into distinct, modular layers.

```
 +-----------------------------------------------------------------------+
 |                     Sensing & Telemetry Layer                         |
 |          (Ingests cluster state, replica lag, network health)          |
 +-----------------------------------------------------------------------+
                                     |
                                     v
 +-----------------------------------------------------------------------+
 |                  Dynamic State Graph Reconciliation                   |
 |     (Maps live attributes -> Evaluates FSMs -> Builds Graph)          |
 +-----------------------------------------------------------------------+
                                     |
                                     v
 +-----------------------------------------------------------------------+
 |                     Dijkstra Pathfinding Engine                       |
 |    (Evaluates edge weights -> Calculates optimal state transitions)   |
 +-----------------------------------------------------------------------+
                                     |
                                     v
 +-----------------------------------------------------------------------+
 |                      Safety Guardrail Middleware                      |
 |        (Rate Limit Check | Dry-Run Engine | Emergency Override)       |
 +-----------------------------------------------------------------------+
                                     |
                                     v
 +-----------------------------------------------------------------------+
 |                      Execution Driver Interface                       |
 |      (Applies targeted actions: reconfiguration, restarts, etc.)     |
 +-----------------------------------------------------------------------+
```

### Key Architectural Components

#### 1. Continuous State Reconciliation Loop
The core control plane operates on a continuous loop, similar to Kubernetes controllers:
* **Sense:** Telemetry agents poll database nodes, proxies, and cloud infrastructure APIs to collect metrics, topology mappings, and state attributes.
* **Evaluate:** Telemetry is injected into the state graph. Nodes update their operational states based on explicit state machine definitions.
* **Plan:** The pathfinding engine runs Dijkstra's algorithm against the current graph topology to generate an execution plan.
* **Execute:** The control plane applies targeted actions to transition nodes along the calculated path.

#### 2. Composable Recovery Rules
Recovery rules decouple state detection from state execution. Detection rules inspect node attributes to define current node states, while transition rules define the exact actions required to move between two adjacent states along with their associated risk weights.

Because rules are composable, engineers can add support for new failure modes simply by registering new state transitions and risk weights—without modifying the underlying pathfinding algorithm or execution pipeline.

#### 3. Production Safety Guardrails
Allowing an automated system to execute state transitions on core database infrastructure requires robust safety mechanisms:
* **Rate Limiting:** Prevents global state changes from firing simultaneously across multiple shards during large-scale cloud provider events.
* **Dry-Run Simulation:** Every calculated path can run through a simulation engine prior to execution, validating that proposed actions will not breach quorum or availability SLAs.
* **Emergency Overrides:** On-call engineers can pause autonomous reconciliation across individual shards, regions, or the entire fleet using global feature flags.

### Legacy Runbooks vs. Algorithmic Control Plane

| Feature | Legacy Runbook Scripts | Algorithmic Control Plane (Graph + FSM) |
| :--- | :--- | :--- |
| **Execution Logic** | Imperative (`if/else` scripts) | Declarative Graph Search (Dijkstra's Algorithm) |
| **State Handling** | Assumes linear state sequences | Handles multi-node, non-linear failure cascades |
| **Action Selection** | Fixed sequence of hard-coded steps | Dynamic calculation based on risk-weighted edges |
| **Unrecoverable States**| Script halts or executes invalid steps | **Partial Remediation** to safest intermediate state |
| **Maintainability** | High overhead; prone to script drift | Low overhead; composable rules and transitions |
| **On-Call Impact** | Frequent alerts for unexpected states | 30% reduction in pager alerts across the fleet |

---

## Measured Impact: Operational Gains and Reduced Burnout

Transitioning from imperative runbooks to an algorithmic, graph-based control plane yielded immediate, measurable improvements across Stripe's infrastructure operations.

```
       [ Legacy Control Plane ]               [ Algorithmic Control Plane ]
       ------------------------               -----------------------------
       124 Misconfigured Alerts               30% Overall Pager Reduction
       32 Single-Node Failure Alerts          Zero Script Execution Halts
       12 Days/Yr Unhealthy Shards            12 Days Unhealthy State Eliminated
```

By replacing static scripts with dynamic pathfinding, Stripe achieved significant results across key operational metrics:

*   **30% Overall Reduction in Pager Alerts:** The control plane resolves non-linear intermediate failure states automatically, drastically cutting down night-time alerts for database operations teams.
*   **Elimination of 12 Days of Cumulative Unhealthy Shard States Annually:** By calculating recovery paths using cost-optimized execution steps, the system resolves degraded shard states in minutes rather than hours, regaining the equivalent of 12 full days of cluster degraded time each year.
*   **Reduced Operational Overhead:** SREs no longer need to write, test, and maintain hundreds of procedural runbook scripts. Engineering work shifts from reactive debugging during incidents to declaratively defining state models, edge weights, and guardrails.

---

## Future Outlook: Expanding Graph Traversal Beyond Disaster Recovery

While graph traversal and state machine pathfinding were initially implemented at Stripe for reactive incident response, the paradigm offers broader applications across infrastructure lifecycle management.

Stripe plans to expand this framework beyond disaster recovery to automate routine operational tasks across its global fleet:

*   **Automated Topology Alterations & Shard Rebalancing:** Using Dijkstra's algorithm to plan live shard splitting, topology reshuffling, and database migrations. The pathfinder can calculate migration steps that minimize cross-AZ data transfer costs while preventing bandwidth saturation on active primaries.
*   **Zero-Downtime Blue-Green Cluster Upgrades:** Complex database major-version upgrades can be modeled as multi-stage state machine paths. The control plane can dynamically route client traffic, upgrade read secondaries, execute step-downs, and upgrade remaining nodes automatically, rolling back safely if any step fails validation.
*   **Coordinated Maintenance Mode Planning:** When cloud providers schedule routine hypervisor patching or hardware maintenance, the control plane can ingest maintenance schedules as temporary edge weight adjustments. The graph pathfinder will automatically migrate primary nodes off vulnerable hardware before maintenance windows begin, achieving zero-touch infrastructure patching at global scale.

By modeling distributed infrastructure as stateful graphs and framing operations as pathfinding problems, platforms can move beyond fragile, script-based automation. Algorithmic control planes provide a reliable foundation for self-healing, adaptable systems capable of managing hyper-scale growth securely.

---
layout: post
title: 'Daily DSA: Transceiver Frequency Assignment (Hard)'
date: 2026-11-01 22:04:23 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Transceiver Frequency
  Assignment.'
cover_image: /assets/images/posts/default-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are managing a communication network consisting of $n$ transceivers, indexed from $1$ to $n$. Each transceiver must be configured to operate on one of two available frequency bands: **Band A** or **Band B**.

Due to physical interference and regulatory constraints, there are $m$ pairwise requirements. Each requirement is given as a pair of non-zero integers $[u, v]$, indicating that at least one of the two conditions must be met:
- A positive value $x$ ($1 \le x \le n$) means transceiver $x$ operates on **Band A**.
- A negative value $-x$ ($-n \le -x \le -1$) means transceiver $x$ operates on **Band B** (i.e., NOT Band A).

Determine whether there exists a valid frequency assignment for all $n$ transceivers that satisfies every constraint. If a valid configuration exists, return an array of size $n$ of integers where the $i$-th element is `1` if transceiver $i+1$ operates on **Band A**, or `0` if it operates on **Band B**. If multiple valid configurations exist, return any of them. If it is impossible to satisfy all constraints, return an empty array `[]`.

---

### Examples

**Example 1:**
```text
Input: n = 3, clauses = [[1, 2], [-1, 3], [-2, -3]]
Output: [1, 0, 1]
Explanation:
- [1, 2]: Transceiver 1 is on Band A OR Transceiver 2 is on Band A (1 is on Band A -> Satisfied).
- [-1, 3]: Transceiver 1 is on Band B OR Transceiver 3 is on Band A (3 is on Band A -> Satisfied).
- [-2, -3]: Transceiver 2 is on Band B OR Transceiver 3 is on Band B (2 is on Band B -> Satisfied).
All constraints are satisfied by the configuration [1, 0, 1].
```

**Example 2:**
```text
Input: n = 1, clauses = [[1, 1], [-1, -1]]
Output: []
Explanation:
Clause [1, 1] requires transceiver 1 to operate on Band A.
Clause [-1, -1] requires transceiver 1 to operate on Band B.
Both conditions cannot simultaneously hold, so no valid assignment exists.
```

**Example 3:**
```text
Input: n = 2, clauses = [[1, -2], [-1, 2]]
Output: [1, 1]
Explanation:
- [1, -2]: Transceiver 1 is on Band A OR Transceiver 2 is on Band B.
- [-1, 2]: Transceiver 1 is on Band B OR Transceiver 2 is on Band A.
Setting both transceivers to Band A ([1, 1]) satisfies all clauses.
```

---

### Constraints

- $1 \le n \le 10^5$
- $1 \le m \le 2 \times 10^5$
- `clauses.length == m`
- `clauses[i].length == 2`
- For each clause $[u, v]$: $1 \le |u|, |v| \le n$ and $u, v \ne 0$

---

### Approach

This problem can be directly modeled as the classic **2-Satisfiability (2-SAT)** problem.

1. **Variable Representation:**
   For each transceiver $i$ ($1 \le i \le n$), let boolean variable $x_i = \text{true}$ represent that transceiver $i$ uses Band A, and $x_i = \text{false}$ represent Band B.
   Each variable $x_i$ gives rise to two literals: $x_i$ and $\neg x_i$.
   We can map literal $x_i$ to vertex $2(i - 1)$ and $\neg x_i$ to vertex $2(i - 1) + 1$.

2. **Implication Graph Construction:**
   A clause $(a \lor b)$ is logically equivalent to two implications:
   - $(\neg a \implies b)$
   - $(\neg b \implies a)$
   
   For every clause $[u, v]$, we add two directed edges in our graph:
   - From $\neg u$ to $v$
   - From $\neg v$ to $u$

3. **Strongly Connected Components (SCC):**
   If there is a directed path from $p$ to $q$, then if $p$ is true, $q$ must also be true. Consequently, all literals in the same SCC must share the same truth value.
   - We use **Tarjan's algorithm** to find all SCCs in the implication graph.
   - If any variable $x_i$ and its negation $\neg x_i$ belong to the same SCC, it implies $x_i \implies \neg x_i$ and $\neg x_i \implies x_i$, which is a contradiction. Thus, no valid assignment exists, and we return `[]`.

4. **Truth Assignment:**
   Tarjan's algorithm visits SCCs in reverse topological order (sinks are numbered first). If $\text{scc}[x_i] < \text{scc}[\neg x_i]$, literal $x_i$ is downstream of $\neg x_i$ in the implication DAG, meaning $\neg x_i \implies x_i$. To avoid contradiction, $x_i$ must be assigned `true` (`1`). Conversely, if $\text{scc}[\neg x_i] < \text{scc}[x_i]$, $x_i$ must be assigned `false` (`0`).

---

### C++ Solution

```cpp
#include <vector>
#include <stack>
#include <cmath>
#include <algorithm>

class Solution {
public:
    std::vector<int> solve2SAT(int n, const std::vector<std::vector<int>>& clauses) {
        int num_nodes = 2 * n;
        std::vector<std::vector<int>> adj(num_nodes);

        // Helper to map literal to vertex index
        // Variable i (1-indexed): x_i -> 2*(i-1), ~x_i -> 2*(i-1) + 1
        auto get_id = [](int lit) -> int {
            int var = std::abs(lit) - 1;
            return (lit > 0) ? (2 * var) : (2 * var + 1);
        };

        auto get_neg = [](int id) -> int {
            return id ^ 1;
        };

        // Build implication graph
        for (const auto& clause : clauses) {
            int u = get_id(clause[0]);
            int v = get_id(clause[1]);
            // (u or v) <=> (~u => v) and (~v => u)
            adj[get_neg(u)].push_back(v);
            adj[get_neg(v)].push_back(u);
        }

        // Tarjan's SCC Algorithm
        std::vector<int> dfn(num_nodes, -1);
        std::vector<int> low(num_nodes, -1);
        std::vector<int> scc(num_nodes, -1);
        std::vector<bool> in_stack(num_nodes, false);
        std::stack<int> st;
        int timer = 0, scc_count = 0;

        auto dfs = [&](auto& self, int u) -> void {
            dfn[u] = low[u] = ++timer;
            st.push(u);
            in_stack[u] = true;

            for (int v : adj[u]) {
                if (dfn[v] == -1) {
                    self(self, v);
                    low[u] = std::min(low[u], low[v]);
                } else if (in_stack[v]) {
                    low[u] = std::min(low[u], dfn[v]);
                }
            }

            if (low[u] == dfn[u]) {
                while (true) {
                    int v = st.top();
                    st.pop();
                    in_stack[v] = false;
                    scc[v] = scc_count;
                    if (u == v) break;
                }
                scc_count++;
            }
        };

        for (int i = 0; i < num_nodes; ++i) {
            if (dfn[i] == -1) {
                dfs(dfs, i);
            }
        }

        // Check satisfiability and determine values
        std::vector<int> assignment(n);
        for (int i = 0; i < n; ++i) {
            int pos_node = 2 * i;
            int neg_node = 2 * i + 1;
            
            if (scc[pos_node] == scc[neg_node]) {
                return {}; // Contradiction: x_i and ~x_i are in the same SCC
            }
            
            // In Tarjan's algorithm, smaller SCC IDs correspond to topological sinks.
            // If scc[pos_node] < scc[neg_node], pos_node is a sink relative to neg_node.
            assignment[i] = (scc[pos_node] < scc[neg_node]) ? 1 : 0;
        }

        return assignment;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(n + m)$
  - Building the implication graph takes $\mathcal{O}(m)$ time since each clause adds two directed edges.
  - Tarjan's SCC algorithm runs in linear time with respect to vertices and edges: $\mathcal{O}(V + E) = \mathcal{O}(2n + 2m) = \mathcal{O}(n + m)$.
  - Constructing the final solution iterates through $n$ variables, taking $\mathcal{O}(n)$ time.
  - Total Time Complexity: $\mathcal{O}(n + m)$.

- **Space Complexity:** $\mathcal{O}(n + m)$
  - The adjacency list stores $2n$ vertices and $2m$ directed edges, requiring $\mathcal{O}(n + m)$ space.
  - Auxiliary arrays (`dfn`, `low`, `scc`, `in_stack`) and the stack use $\mathcal{O}(n)$ space.
  - Total Space Complexity: $\mathcal{O}(n + m)$.
{% endraw %}

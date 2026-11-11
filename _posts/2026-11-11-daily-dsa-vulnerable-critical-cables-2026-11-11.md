---
layout: post
title: 'Daily DSA: Vulnerable Critical Cables (Hard)'
date: 2026-11-11 23:09:44 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Vulnerable Critical
  Cables.'
cover_image: /assets/images/posts/daily-dsa-vulnerable-critical-cables-2026-11-11-cover.png
cover_caption: ''
---

{% raw %}
### Problem Description

An IT infrastructure consists of $n$ servers (numbered from $0$ to $n - 1$) connected by $m$ bidirectional communication cables. Each cable connects two distinct servers $u$ and $v$ and has an associated maintenance cost $w$.

In network topology design, a cable is defined as **critical** (or a bridge) if its removal disconnects the server network into two or more separate components.

Given the integer $n$ and a 2D array `edges` where `edges[i] = [u_i, v_i, w_i]`, return the **minimum maintenance cost** among all critical cables in the network. If no critical cables exist in the network, return `-1`.

The initial network is guaranteed to be fully connected, and there are no self-loops or parallel edges.

---

### Examples

**Example 1:**
```
Input: n = 4, edges = [[0, 1, 10], [1, 2, 20], [2, 0, 30], [1, 3, 5]]
Output: 5
Explanation:
- Cable (1, 3) is a critical cable because removing it leaves server 3 isolated.
- Cables (0, 1), (1, 2), and (2, 0) form a cycle (0-1-2-0), so none of them are critical.
- The only critical cable has a cost of 5. The minimum cost is 5.
```

**Example 2:**
```
Input: n = 3, edges = [[0, 1, 5], [1, 2, 5], [2, 0, 5]]
Output: -1
Explanation:
- The graph forms a simple 3-cycle.
- Removing any single cable leaves all servers connected.
- Thus, no critical cables exist, and the answer is -1.
```

**Example 3:**
```
Input: n = 5, edges = [[0, 1, 2], [1, 2, 4], [2, 3, 1], [3, 4, 3], [4, 2, 6]]
Output: 2
Explanation:
- The cycle consists of nodes {2, 3, 4}.
- Cable (0, 1) with weight 2 and Cable (1, 2) with weight 4 are both critical cables.
- The minimum weight among critical cables is min(2, 4) = 2.
```

---

### Constraints

- $2 \le n \le 10^5$
- $1 \le m \le 2 \times 10^5$
- `edges[i] = [u_i, v_i, w_i]`
- $0 \le u_i, v_i < n$
- $u_i \neq v_i$
- $1 \le w_i \le 10^9$
- The given network is connected.
- There are no parallel edges or self-loops.

---

### Approach

To find all critical cables (bridges) in an undirected connected graph efficienty, we can use **Tarjan's Bridge-Finding Algorithm** based on Depth-First Search (DFS).

1. **Discovery Times and Low Values:**
   - Maintain a discovery time array `tin[u]` which records the order/time step at which vertex `u` was first visited during DFS.
   - Maintain a `low[u]` array which stores the smallest `tin` value reachable from `u` using at most one back-edge (an edge to an already-visited ancestor).

2. **Bridge Identification Condition:**
   - For an edge $(u, v)$, after traversing down to child node $v$ in the DFS tree, if `low[v] > tin[u]`, then edge $(u, v)$ is a **bridge** (critical cable).
   - Why? Because `low[v] > tin[u]` means node $v$ and its sub-tree have no path back to $u$ or any ancestor of $u$ except through the edge $(u, v)$ itself. Removing $(u, v)$ completely disconnects node $v$'s sub-tree from $u$.

3. **Tracking Minimum Maintenance Cost:**
   - Whenever a bridge $(u, v)$ with weight $w$ is detected, track `min_cost = min(min_cost, w)`.
   - If after traversing the entire graph no bridges are found, return `-1`.

---

### C++ Solution

```cpp
#include <vector>
#include <algorithm>
#include <climits>

using namespace std;

class Solution {
private:
    struct Edge {
        int to;
        long long weight;
    };

    int timer;
    long long min_critical_weight;
    vector<int> tin, low;
    vector<bool> visited;
    vector<vector<Edge>> adj;

    void dfs(int u, int p = -1) {
        visited[u] = true;
        tin[u] = low[u] = ++timer;
        
        for (const auto& edge : adj[u]) {
            int v = edge.to;
            long long w = edge.weight;
            
            if (v == p) continue; // Skip parent edge
            
            if (visited[v]) {
                // Back-edge encountered
                low[u] = min(low[u], tin[v]);
            } else {
                // Tree-edge
                dfs(v, u);
                low[u] = min(low[u], low[v]);
                
                // Bridge Condition
                if (low[v] > tin[u]) {
                    min_critical_weight = min(min_critical_weight, w);
                }
            }
        }
    }

public:
    long long minCriticalCableCost(int n, vector<vector<int>>& edges) {
        adj.assign(n, vector<Edge>());
        tin.assign(n, 0);
        low.assign(n, 0);
        visited.assign(n, false);
        timer = 0;
        min_critical_weight = LLONG_MAX;

        for (const auto& edge : edges) {
            int u = edge[0];
            int v = edge[1];
            long long w = edge[2];
            adj[u].push_back({v, w});
            adj[v].push_back({u, w});
        }

        // The graph is connected, so one DFS traversal from node 0 visits all vertices.
        dfs(0);

        return (min_critical_weight == LLONG_MAX) ? -1 : min_critical_weight;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(V + E)$, where $V = n$ is the number of servers and $E = m$ is the number of cables. We visit each vertex and traverse each edge exactly once during DFS.
- **Space Complexity:** $\mathcal{O}(V + E)$ to store the adjacency list representation of the graph, alongside $\mathcal{O}(V)$ space for the DFS call stack and helper arrays (`tin`, `low`, `visited`).
{% endraw %}

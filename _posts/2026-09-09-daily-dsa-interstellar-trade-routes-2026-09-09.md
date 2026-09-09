---
layout: post
title: 'Daily DSA: Interstellar Trade Routes (Hard)'
date: 2026-09-09 19:38:03 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Interstellar
  Trade Routes.'
cover_image: /assets/images/posts/daily-dsa-interstellar-trade-routes-2026-09-09-cover.png
cover_caption: ''
---

### Problem Description

In a distant galaxy, there are `n` planets indexed from `0` to `n - 1`. These planets are connected by `m` bidirectional wormholes, represented as a 2D array `connections` where `connections[i] = [u, v]` indicates a wormhole between planet `u` and planet `v`.

A wormhole is considered **critical** if its collapse would result in the trade network becoming disconnected (i.e., some planets would no longer be reachable from others). Your task is to find all critical wormholes and return them in any order.

### Examples

**Example 1:**
**Input:** `n = 4, connections = [[0,1],[1,2],[2,0],[1,3]]`  
**Output:** `[[1,3]]`  
**Explanation:** The wormholes [0,1], [1,2], and [2,0] form a triangle (cycle). Removing any of them still leaves the planets connected. However, removing [1,3] isolates planet 3.

**Example 2:**
**Input:** `n = 2, connections = [[0,1]]`  
**Output:** `[[0,1]]`  
**Explanation:** Removing the only connection leaves the two planets disconnected.

### Constraints

- `2 <= n <= 10^5`
- `n - 1 <= connections.length <= 10^5`
- `0 <= connections[i][0], connections[i][1] <= n - 1`
- `connections[i][0] != connections[i][1]`
- There are no duplicate connections.
- The initial network is guaranteed to be fully connected.

---

### Approach

To find critical connections (bridges) in an undirected graph efficiently, we use **Tarjan's Algorithm** (or a similar DFS-based approach using discovery times and low-link values).

1.  **Discovery Time (`disc`)**: The time at which a node was first visited during a DFS traversal.
2.  **Low-Link Value (`low`)**: The lowest discovery time reachable from the node (including itself) in the DFS tree, possibly using a back-edge (an edge connecting a node to one of its ancestors in the DFS tree).

**Algorithm Steps:**
1.  Perform a DFS starting from any node (e.g., node 0).
2.  For each node `u`, maintain `disc[u]` and `low[u]`.
3.  For every neighbor `v` of `u`:
    - If `v` is the parent of `u`, skip it (don't go back through the same edge).
    - If `v` has already been visited, it's a back-edge. Update `low[u] = min(low[u], disc[v])`.
    - If `v` has not been visited, recursively call DFS for `v`. After the call, update `low[u] = min(low[u], low[v])`.
    - **Bridge Condition**: If `low[v] > disc[u]`, then the edge `(u, v)` is a bridge. This is because there is no back-edge from `v` or its descendants that reaches `u` or any of `u`'s ancestors.

### Complexity Analysis
- **Time Complexity**: $O(V + E)$, where $V$ is the number of planets and $E$ is the number of wormholes. We traverse the graph once using DFS.
- **Space Complexity**: $O(V + E)$ to store the adjacency list and the discovery/low-link arrays.

---

### C++ Implementation

```cpp
#include <vector>
#include <algorithm>

using namespace std;

class Solution {
private:
    vector<vector<int>> bridges;
    vector<vector<int>> adj;
    vector<int> disc;
    vector<int> low;
    int timer;

    void dfs(int u, int p) {
        disc[u] = low[u] = ++timer;
        
        for (int v : adj[u]) {
            if (v == p) continue; // Skip the edge back to parent
            
            if (disc[v]) {
                // v is already visited, this is a back-edge
                low[u] = min(low[u], disc[v]);
            } else {
                // v is not visited, recurse
                dfs(v, u);
                low[u] = min(low[u], low[v]);
                
                // If the lowest node v can reach is still 'deeper' than u,
                // then u-v is a bridge.
                if (low[v] > disc[u]) {
                    bridges.push_back({u, v});
                }
            }
        }
    }

public:
    vector<vector<int>> criticalConnections(int n, vector<vector<int>>& connections) {
        adj.resize(n);
        disc.assign(n, 0);
        low.assign(n, 0);
        timer = 0;
        
        for (const auto& edge : connections) {
            adj[edge[0]].push_back(edge[1]);
            adj[edge[1]].push_back(edge[0]);
        }
        
        // Since the graph is connected, one DFS call from node 0 is enough
        dfs(0, -1);
        
        return bridges;
    }
};
```

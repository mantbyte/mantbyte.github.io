---
layout: post
title: 'Daily DSA: Maximum Path Energy in a Directed Network (Medium)'
date: 2026-08-08 15:56:31 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Maximum Path
  Energy in a Directed Network.'
cover_image: /assets/images/posts/daily-dsa-maximum-path-energy-in-a-directed-network-2026-08-08-cover.png
cover_caption: ''
---

### Problem Description

You are managing an energy network represented as a Directed Acyclic Graph (DAG) with `n` nodes labeled from `0` to `n - 1`.

You are given:
- An integer `n` (the number of nodes).
- A 2D array `edges` where `edges[i] = [u, v, cost]` represents a directed edge from node `u` to node `v` with an energy traversal cost of `cost`.
- An array `gains` of size `n`, where `gains[i]` is the energy bonus added to your pool upon visiting node `i`.
- An integer `initialEnergy`, your starting energy before entering node `0`.

When you start at node `0`, you immediately collect its energy bonus: `energy = initialEnergy + gains[0]`.

To traverse a directed edge `u -> v` with cost `C`:
1. Your current energy at node `u` must be at least `C` (`energy >= C`).
2. Upon reaching node `v`, your energy becomes `energy - C + gains[v]`.

Return the **maximum possible energy** you can possess upon reaching node `n - 1`. If node `n - 1` is unreachable under these conditions, return `-1`.

---

### Examples

**Example 1:**
```
Input: n = 4, edges = [[0,1,3],[0,2,2],[1,3,5],[2,3,1]], gains = [2,8,1,3], initialEnergy = 3
Output: 8
Explanation:
- Start at node 0: Energy = 3 + gains[0] = 3 + 2 = 5.
- Path 1 (0 -> 1 -> 3):
  - Move 0 -> 1 (cost 3 <= 5): Energy = 5 - 3 + gains[1] = 2 + 8 = 10.
  - Move 1 -> 3 (cost 5 <= 10): Energy = 10 - 5 + gains[3] = 5 + 3 = 8.
- Path 2 (0 -> 2 -> 3):
  - Move 0 -> 2 (cost 2 <= 5): Energy = 5 - 2 + gains[2] = 3 + 1 = 4.
  - Move 2 -> 3 (cost 1 <= 4): Energy = 4 - 1 + gains[3] = 3 + 3 = 6.
The maximum energy on reaching node 3 is max(8, 6) = 8.
```

**Example 2:**
```
Input: n = 3, edges = [[0,1,10]], gains = [1,2,3], initialEnergy = 5
Output: -1
Explanation:
- Start at node 0: Energy = 5 + 1 = 6.
- Edge 0 -> 1 requires cost 10, but available energy is only 6. Node 1 cannot be reached.
- Node 2 is not connected, so node 2 (n - 1) is unreachable. Return -1.
```

---

### Constraints

- `1 <= n <= 10^5`
- `0 <= edges.length <= 2 * 10^5`
- `edges[i] = [u, v, cost]` where `0 <= u, v < n` and `u != v`
- `1 <= cost <= 10^9`
- `0 <= gains[i] <= 10^9`
- `0 <= initialEnergy <= 10^9`
- The given graph is guaranteed to be a **Directed Acyclic Graph (DAG)**.

---

### Approach

Since the graph is a **DAG (Directed Acyclic Graph)**, we can process nodes in **Topological Order** using **Kahn's Algorithm (BFS)** to compute the maximum possible energy reaching each node.

1. **Dynamic Programming State:**
   Let `dp[u]` be the maximum energy achievable at node `u` after collecting `gains[u]`. Initialize `dp` array with `-1` for all nodes except `dp[0] = initialEnergy + gains[0]`.

2. **Topological Ordering:**
   - Compute the in-degrees of all nodes.
   - Push all nodes with `in_degree == 0` into a queue.

3. **State Transition:**
   - For each node `u` popped from the queue:
     - If `dp[u] != -1` (i.e., node `u` is reachable):
       - For each neighbor `v` via edge `[u, v, cost]`:
         - Check if current energy is sufficient: `dp[u] >= cost`.
         - If valid, update `dp[v] = max(dp[v], dp[u] - cost + gains[v])`.
     - Decrement `in_degree[v]`. If `in_degree[v] == 0`, push `v` to the queue.

4. **Result:**
   Return `dp[n - 1]`. If it remains `-1`, node `n - 1` is unreachable.

---

### C++ Solution

```cpp
#include <vector>
#include <queue>
#include <algorithm>

using namespace std;

class Solution {
public:
    long long maxPathEnergy(int n, vector<vector<int>>& edges, vector<int>& gains, int initialEnergy) {
        // Adjacency list storing pairs of {neighbor, cost}
        vector<vector<pair<int, int>>> adj(n);
        vector<int> inDegree(n, 0);
        
        for (const auto& edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int cost = edge[2];
            adj[u].push_back({v, cost});
            inDegree[v]++;
        }
        
        // dp[i] stores maximum energy upon reaching node i (after adding gains[i])
        vector<long long> dp(n, -1);
        dp[0] = (long long)initialEnergy + gains[0];
        
        queue<int> q;
        for (int i = 0; i < n; ++i) {
            if (inDegree[i] == 0) {
                q.push(i);
            }
        }
        
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            
            if (dp[u] != -1) {
                for (const auto& [v, cost] : adj[u]) {
                    if (dp[u] >= cost) {
                        long long nextEnergy = dp[u] - cost + gains[v];
                        dp[v] = max(dp[v], nextEnergy);
                    }
                }
            }
            
            for (const auto& [v, cost] : adj[u]) {
                inDegree[v]--;
                if (inDegree[v] == 0) {
                    q.push(v);
                }
            }
        }
        
        return dp[n - 1];
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(V + E)$ where $V = n$ and $E = \text{edges.length}$. Each vertex and edge is processed a constant number of times during topological sorting.
- **Space Complexity:** $\mathcal{O}(V + E)$ to store the adjacency list, in-degree array, queue, and DP table.

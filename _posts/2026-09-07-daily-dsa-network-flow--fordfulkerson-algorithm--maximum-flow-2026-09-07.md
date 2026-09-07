---
layout: post
title: 'Daily DSA: Network Flow - Ford-Fulkerson Algorithm - Maximum Flow (Hard)'
date: 2026-09-07 20:59:21 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Network Flow
  - Ford-Fulkerson Algorithm - Maximum Flow.'
cover_image: /assets/images/posts/daily-dsa-network-flow--fordfulkerson-algorithm--maximum-flow-2026-09-07-cover.png
cover_caption: ''
---

# Problem Statement

You are given a flow network with $N$ vertices (numbered from $0$ to $N-1$) and a list of directed edges. Each edge has a certain capacity. Find the maximum flow from a designated source vertex $S$ to a sink vertex $T$.

# Examples

### Example 1:
**Input:**
```
N = 4
Source = 0, Sink = 3
Edges = [
  [0, 1, 3],
  [0, 2, 2],
  [1, 2, 5],
  [1, 3, 2],
  [2, 3, 3]
]
```
**Output:** `4`
**Explanation:**
- Send 2 units along path 0 -> 1 -> 3 (capacity bottleneck is 2).
- Send 2 units along path 0 -> 2 -> 3 (capacity bottleneck is 2).
- Total maximum flow = 2 + 2 = 4.

### Example 2:
**Input:**
```
N = 3
Source = 0, Sink = 2
Edges = [
  [0, 1, 10],
  [1, 2, 10]
]
```
**Output:** `10`

# Constraints
- $2 \le N \le 200$
- $0 \le \text{Edges.length} \le 5000$
- $0 \le u, v < N$
- $1 \le \text{capacity} \le 10^5$

# Approach / Hint
1. Use the **Ford-Fulkerson method** (specifically implemented via **Edmonds-Karp algorithm** using Breadth-First Search to find augmenting paths).
2. Maintain a residual capacity graph. For every edge $(u, v)$ with capacity $C$, we add forward capacity and allow reverse residual capacity to let the algorithm "undo" greedy choices.
3. Repeatedly find paths from $S$ to $T$ with positive residual capacity using BFS, determine the bottleneck capacity along that path, and augment the flow. Stop when no path exists from $S$ to $T$.

# C++ Solution

```cpp
#include <vector>
#include <queue>
#include <algorithm>
#include <cstring>

using namespace std;

class Solution {
public:
    int maxFlow(int n, int source, int sink, vector<vector<int>>& edges) {
        vector<vector<int>> capacity(n, vector<int>(n, 0));
        for (const auto& edge : edges) {
            int u = edge[0], v = edge[1], cap = edge[2];
            capacity[u][v] += cap; // Handle multiple edges if any
        }

        int flow = 0;
        vector<int> parent(n);

        auto bfs = [&](int s, int t, vector<int>& par) {
            fill(par.begin(), par.end(), -1);
            par[s] = -2;
            queue<pair<int, int>> q;
            q.push({s, 1e9});

            while (!q.empty()) {
                int u = q.front().first;
                int push = q.front().second;
                q.pop();

                for (int v = 0; v < n; ++v) {
                    if (par[v] == -1 && capacity[u][v] > 0) {
                        par[v] = u;
                        int tr_push = min(push, capacity[u][v]);
                        if (v == t)
                            return tr_push;
                        q.push({v, tr_push});
                    }
                }
            }
            return 0;
        };

        int new_flow;
        while ((new_flow = bfs(source, sink, parent)) > 0) {
            flow += new_flow;
            int cur = sink;
            while (cur != source) {
                int prev = parent[cur];
                capacity[prev][cur] -= new_flow;
                capacity[cur][prev] += new_flow;
                cur = prev;
            }
        }

        return flow;
    }
};
```

### Complexity Analysis
- **Time Complexity:** $O(V \cdot E^2)$ using Edmonds-Karp (BFS-based augmenting paths), where $V$ is the number of vertices and $E$ is the number of edges. This guarantees termination and polynomial time execution.
- **Space Complexity:** $O(V^2)$ to store the adjacency/capacity matrix of the residual graph.

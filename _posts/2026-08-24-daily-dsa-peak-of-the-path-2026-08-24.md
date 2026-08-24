---
layout: post
title: 'Daily DSA: Peak of the Path (Hard)'
date: 2026-08-24 16:04:54 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Peak of the Path.'
cover_image: /assets/images/posts/daily-dsa-peak-of-the-path-2026-08-24-cover.png
cover_caption: ''
---

### Problem Description

You are given an undirected tree with `n` nodes labeled from `1` to `n`. The tree contains `n - 1` edges, where each edge has a specific weight representing the 'resistance' between two nodes.

You need to process `q` queries. Each query consists of two nodes `u` and `v`. For each query, find the **maximum weight** of any edge on the unique simple path between node `u` and node `v`.

### Examples

**Example 1:**
**Input:** 
`n = 5` 
`edges = [[1, 2, 10], [2, 3, 5], [1, 4, 20], [4, 5, 2]]` 
`queries = [[3, 5], [2, 4]]` 
**Output:** `[20, 20]` 
**Explanation:** 
- The path from 3 to 5 is: `3 -> 2 -> 1 -> 4 -> 5`. The edge weights are `5, 10, 20, 2`. The maximum is `20`.
- The path from 2 to 4 is: `2 -> 1 -> 4`. The edge weights are `10, 20`. The maximum is `20`.

**Example 2:**
**Input:** 
`n = 3` 
`edges = [[1, 2, 7], [2, 3, 8]]` 
`queries = [[1, 2], [1, 3]]` 
**Output:** `[7, 8]` 
**Explanation:** 
- Path 1-2: Edge weight `7`.
- Path 1-3: Edges `7, 8`. Max is `8`.

### Constraints
- `2 <= n <= 10^5` 
- `1 <= q <= 10^5` 
- `edges[i].length == 3` 
- `1 <= u, v <= n` 
- `1 <= weight <= 10^9` 
- The input is guaranteed to be a valid tree.

### Approach

To efficiently find the maximum edge on a path between two nodes in a tree, we can use **Binary Lifting** (a technique often used for Lowest Common Ancestor - LCA).

1.  **Preprocessing (Binary Lifting Table):**
    - We define `up[u][i]` as the $2^i$-th ancestor of node `u`.
    - We define `max_edge[u][i]` as the maximum edge weight on the path from node `u` to its $2^i$-th ancestor.
    - These tables can be filled using a DFS and the following recurrence:
        - `up[u][i] = up[up[u][i-1]][i-1]`
        - `max_edge[u][i] = max(max_edge[u][i-1], max_edge[up[u][i-1]][i-1])`

2.  **Querying:**
    - For a query `(u, v)`, find the maximum edge weight while moving the deeper node up to the same depth as the shallower node.
    - If the nodes are not the same, move both nodes up simultaneously using the binary lifting table until they reach just below their LCA.
    - Track the maximum weight encountered during all jumps.

### Complexity Analysis
- **Time Complexity:** $O(N \log N)$ to build the lifting table and $O(Q \log N)$ to process queries.
- **Space Complexity:** $O(N \log N)$ to store the lifting tables.

### C++ Solution

```cpp
#include <vector>
#include <algorithm>
#include <cmath>

using namespace std;

class PeakOfThePath {
    int n, LOG;
    vector<vector<pair<int, int>>> adj;
    vector<vector<int>> up;
    vector<vector<int>> max_val;
    vector<int> depth;

    void dfs(int u, int p, int d, int w) {
        depth[u] = d;
        up[u][0] = p;
        max_val[u][0] = w;
        for (int i = 1; i < LOG; i++) {
            up[u][i] = up[up[u][i - 1]][i - 1];
            max_val[u][i] = max(max_val[u][i - 1], max_val[up[u][i - 1]][i - 1]);
        }
        for (auto& edge : adj[u]) {
            if (edge.first != p) {
                dfs(edge.first, u, d + 1, edge.second);
            }
        }
    }

public:
    vector<int> solve(int n, vector<vector<int>>& edges, vector<vector<int>>& queries) {
        this->n = n;
        this->LOG = ceil(log2(n)) + 1;
        adj.assign(n + 1, vector<pair<int, int>>());
        up.assign(n + 1, vector<int>(LOG, 0));
        max_val.assign(n + 1, vector<int>(LOG, 0));
        depth.assign(n + 1, 0);

        for (auto& e : edges) {
            adj[e[0]].push_back({e[1], e[2]});
            adj[e[1]].push_back({e[0], e[2]});
        }

        // Start DFS from root 1
        dfs(1, 1, 0, 0);

        vector<int> results;
        for (auto& q : queries) {
            int u = q[0], v = q[1];
            if (u == v) {
                results.push_back(0);
                continue;
            }
            if (depth[u] < depth[v]) swap(u, v);

            int ans = 0;
            // Lift u to the same depth as v
            for (int i = LOG - 1; i >= 0; i--) {
                if (depth[u] - (1 << i) >= depth[v]) {
                    ans = max(ans, max_val[u][i]);
                    u = up[u][i];
                }
            }

            if (u == v) {
                results.push_back(ans);
                continue;
            }

            // Lift both u and v to just below LCA
            for (int i = LOG - 1; i >= 0; i--) {
                if (up[u][i] != up[v][i]) {
                    ans = max(ans, max(max_val[u][i], max_val[v][i]));
                    u = up[u][i];
                    v = up[v][i];
                }
            }
            // Final step to the parent (LCA)
            ans = max(ans, max(max_val[u][0], max_val[v][0]));
            results.push_back(ans);
        }
        return results;
    }
};
```

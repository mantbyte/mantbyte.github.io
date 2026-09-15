---
layout: post
title: 'Daily DSA: Min Cost to Connect All Nodes Using Prim''s Algorithm (Medium)'
date: 2026-09-15 20:06:45 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Min Cost to
  Connect All Nodes Using Prim''s Algorithm.'
cover_image: /assets/images/posts/daily-dsa-min-cost-to-connect-all-nodes-using-prims-algorithm-2026-09-15-cover.png
cover_caption: ''
---

# Problem Statement

You are given an undirected connected graph with $n$ vertices labeled from $0$ to $n-1$, and a 2D array `edges` where `edges[i] = [u_i, v_i, weight_i]` represents a bidirectional edge between vertex `u_i` and vertex `v_i` with a given `weight_i`.

Return the minimum cost to connect all vertices in the graph. All vertices must be connected, forming a Minimum Spanning Tree (MST).

# Examples

### Example 1:
```
Input: n = 4, edges = [[0,1,1],[1,2,2],[2,3,3],[0,3,4],[0,2,5]]
Output: 6
Explanation:
We can connect the nodes as follows:
0 --(1)-- 1 --(2)-- 2 --(3)-- 3
Total cost = 1 + 2 + 3 = 6.
```

### Example 2:
```
Input: n = 3, edges = [[0,1,5],[1,2,3],[0,2,1]]
Output: 4
Explanation:
We can connect node 0 and 2 with weight 1, and node 1 and 2 with weight 3.
Total cost = 1 + 3 = 4.
```

# Constraints
- $1 \le n \le 1000$
- $0 \le edges.length \le \frac{n(n-1)}{2}$
- `edges[i].length == 3`
- $0 \le u_i, v_i < n$
- $u_i \neq v_i$
- $1 \le weight_i \le 10^4$
- The graph is connected.

# Approach
To find the Minimum Spanning Tree (MST), we can use **Prim's Algorithm** with a priority queue (min-heap).

1. Represent the graph as an adjacency list where each node points to a list of pairs `(neighbor, weight)`.
2. Maintain a boolean array `inMST` of size `n` to track whether a node has been included in the MST.
3. Use a min-heap to store edges `(weight, next_node)` ordered by the smallest weight.
4. Start from an arbitrary node (e.g., node `0`), mark it as visited, and push all its adjacent edges into the min-heap.
5. While the min-heap is not empty and we haven't included all $n$ nodes:
   - Extract the edge with the minimum weight pointing to `next_node`.
   - If `next_node` is already in the MST, skip it.
   - Otherwise, add the weight to our total cost, mark `next_node` as part of the MST, and push all its outgoing edges to unvisited neighbors into the min-heap.
6. Return the total cost once all nodes are connected.

# C++ Solution

```cpp
#include <vector>
#include <queue>

using namespace std;

class Solution {
public:
    int minCostConnectNodes(int n, vector<vector<int>>& edges) {
        vector<vector<pair<int, int>>> adj(n);
        for (const auto& edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int w = edge[2];
            adj[u].push_back({v, w});
            adj[v].push_back({u, w});
        }

        priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> minHeap;
        vector<bool> inMST(n, false);

        // Start from node 0
        minHeap.push({0, 0});
        int totalCost = 0;
        int nodesInMST = 0;

        while (!minHeap.empty() && nodesInMST < n) {
            auto [weight, u] = minHeap.top();
            minHeap.pop();

            if (inMST[u]) continue;

            inMST[u] = true;
            totalCost += weight;
            nodesInMST++;

            for (auto& neighbor : adj[u]) {
                int v = neighbor.first;
                int w = neighbor.second;
                if (!inMST[v]) {
                    minHeap.push({w, v});
                }
            }
        }

        return nodesInMST == n ? totalCost : -1;
    }
};
```

### Complexity Analysis
- **Time Complexity:** $O(E \log E)$, where $E$ is the number of edges. Each edge is pushed into and popped from the priority queue at most once.
- **Space Complexity:** $O(V + E)$, where $V$ is the number of vertices and $E$ is the number of edges, required for the adjacency list and the priority queue.

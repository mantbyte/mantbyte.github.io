---
layout: post
title: 'Daily DSA: Largest Strongly Connected Server Group (Hard)'
date: 2026-09-17 20:06:33 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Largest Strongly
  Connected Server Group.'
cover_image: /assets/images/posts/daily-dsa-largest-strongly-connected-server-group-2026-09-17-cover.png
cover_caption: ''
---

### Problem Statement

You are given `n` servers labeled from `0` to `n-1` and a list of directed connections `edges` where `edges[i] = [u, v]` represents a one-way communication from server `u` to server `v`.

A **Strongly Connected Component (SCC)** is a maximal subset of servers such that for every pair of servers `A` and `B` in the subset, there is a directed path from `A` to `B` and a directed path from `B` to `A`.

Your task is to find the size of the largest Strongly Connected Component in the given graph.

### Examples

**Example 1:**
**Input:** `n = 5`, `edges = [[0,1],[1,2],[2,0],[1,3],[3,4]]`  
**Output:** `3`  
**Explanation:** The graph contains three SCCs: `{0, 1, 2}`, `{3}`, and `{4}`. The largest SCC is `{0, 1, 2}` with a size of 3.

**Example 2:**
**Input:** `n = 4`, `edges = [[0,1],[1,2],[2,3]]`  
**Output:** `1`  
**Explanation:** There are no cycles in the graph. Every server can only reach itself in both directions. Thus, each server forms its own SCC of size 1.

**Example 3:**
**Input:** `n = 3`, `edges = [[0,1],[1,2],[2,0]]`  
**Output:** `3`  
**Explanation:** All servers are part of a single cycle, meaning every server can reach every other server. The entire graph is one SCC of size 3.

### Constraints

- `1 <= n <= 5 * 10^4`
- `0 <= edges.length <= 10^5`
- `edges[i].length == 2`
- `0 <= edges[i][0], edges[i][1] < n`
- All directed edges `[u, v]` are unique.

### Approach

To find the Strongly Connected Components in `O(V + E)` time, we use **Kosaraju's Algorithm**. The algorithm relies on the property that if you reverse all edges in a graph, the SCCs remain the same, but the reachability between different SCCs is reversed.

#### Steps:
1. **DFS for Finishing Times:** Perform a DFS on the original graph. When a node's recursive calls are finished, push it onto a stack. The node at the top of the stack will be one that belongs to an SCC that is a "source" in the condensation graph (the graph where each SCC is a single node).
2. **Transpose the Graph:** Create a reversed version of the adjacency list where every edge `(u, v)` becomes `(v, u)`.
3. **DFS on Transposed Graph:** Pop nodes from the stack one by one. If the node has not been visited, it marks the start of a new SCC. Perform a DFS starting from this node on the **transposed** graph to find all nodes in its SCC.
4. **Track Maximum:** Count the number of nodes visited in each DFS of the second pass and keep track of the maximum size found.

### Complexity Analysis

- **Time Complexity:** `O(V + E)`, where `V` is the number of servers and `E` is the number of edges. We perform two complete traversals of the graph (one on the original and one on the transposed).
- **Space Complexity:** `O(V + E)` to store the adjacency list and its transpose, plus `O(V)` for the stack and the visited array.

### C++ Solution

```cpp
#include <vector>
#include <stack>
#include <algorithm>

class Solution {
public:
    // First DFS to find finishing times
    void findFinishingOrder(int u, const std::vector<std::vector<int>>& adj, 
                           std::vector<bool>& visited, std::stack<int>& st) {
        visited[u] = true;
        for (int v : adj[u]) {
            if (!visited[v]) {
                findFinishingOrder(v, adj, visited, st);
            }
        }
        st.push(u);
    }

    // Second DFS on the transposed graph to extract SCCs
    void collectSCC(int u, const std::vector<std::vector<int>>& revAdj, 
                    std::vector<bool>& visited, int& size) {
        visited[u] = true;
        size++;
        for (int v : revAdj[u]) {
            if (!visited[v]) {
                collectSCC(v, revAdj, visited, size);
            }
        }
    }

    int largestSCC(int n, std::vector<std::vector<int>>& edges) {
        std::vector<std::vector<int>> adj(n);
        std::vector<std::vector<int>> revAdj(n);
        
        // Build original and reversed graphs
        for (const auto& edge : edges) {
            adj[edge[0]].push_back(edge[1]);
            revAdj[edge[1]].push_back(edge[0]);
        }

        std::stack<int> st;
        std::vector<bool> visited(n, false);

        // Step 1: DFS to get nodes in order of finishing times
        for (int i = 0; i < n; ++i) {
            if (!visited[i]) {
                findFinishingOrder(i, adj, visited, st);
            }
        }

        // Step 2: DFS on transposed graph in order of stack
        std::fill(visited.begin(), visited.end(), false);
        int maxSCCSize = 0;

        while (!st.empty()) {
            int u = st.top();
            st.pop();

            if (!visited[u]) {
                int currentSize = 0;
                collectSCC(u, revAdj, visited, currentSize);
                maxSCCSize = std::max(maxSCCSize, currentSize);
            }
        }

        return maxSCCSize;
    }
};
```

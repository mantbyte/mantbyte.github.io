---
layout: post
title: 'Daily DSA: Sum of Distances in Tree (Hard)'
date: 2026-10-15 20:08:01 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Sum of Distances
  in Tree.'
cover_image: /assets/images/posts/daily-dsa-sum-of-distances-in-tree-2026-10-15-cover.png
cover_caption: ''
---

{% raw %}
# Problem Statement

There is an undirected connected tree with `n` nodes labeled from `0` to `n - 1` and `n - 1` edges. You are given the integer `n` and the array `edges` where `edges[i] = [u_i, v_i]` indicates that there is an edge between nodes `u_i` and `v_i` in the tree.

Return an array `answer` of length `n` where `answer[i]` is the sum of the distances between the `i`-th node and all other nodes in the tree.

# Example 1

**Input:** `n = 6`, `edges = [[0,1],[0,2],[2,3],[2,4],[2,5]]`  
**Output:** `[8,12,6,10,10,10]`  
**Explanation:**  
The tree is structured as follows:
- Node 0 is connected to 1 and 2.
- Node 2 is connected to 3, 4, and 5.

Calculation for node 0:
- Distance(0,1) = 1
- Distance(0,2) = 1
- Distance(0,3) = 2
- Distance(0,4) = 2
- Distance(0,5) = 2
Sum = 1+1+2+2+2 = 8.

Calculation for node 2:
- Distance(2,0) = 1
- Distance(2,1) = 2
- Distance(2,3) = 1
- Distance(2,4) = 1
- Distance(2,5) = 1
Sum = 1+2+1+1+1 = 6.

# Example 2

**Input:** `n = 1`, `edges = []`  
**Output:** `[0]`

# Constraints

- `1 <= n <= 3 * 10^4`
- `edges.length == n - 1`
- `0 <= u_i, v_i < n`
- `u_i != v_i`
- The input is guaranteed to be a valid tree.

# Approach

To solve this in $O(n)$, we use a technique called **Re-rooting DP**. A naive $O(n^2)$ BFS/DFS from every node would be too slow.

1. **First DFS (Post-order):** 
   Choose an arbitrary root (e.g., node 0). For each node `u`, calculate:
   - `count[u]`: The total number of nodes in the subtree rooted at `u`.
   - `sub_dist[u]`: The sum of distances from `u` to all nodes in its subtree.
   - Transition: `count[u] = 1 + sum(count[v])` and `sub_dist[u] = sum(sub_dist[v] + count[v])` for all children `v`.

2. **Second DFS (Pre-order):**
   We now have the correct total distance sum for the root (node 0). We can derive the results for its children by shifting the root.
   When moving the root from parent `u` to child `v`:
   - All nodes in the subtree of `v` (count `count[v]`) become 1 unit closer to the root.
   - All nodes NOT in the subtree of `v` (count `n - count[v]`) become 1 unit further away.
   - Formula: `ans[v] = ans[u] - count[v] + (n - count[v])`.

# Complexity Analysis
- **Time Complexity:** $O(n)$ as we perform two DFS traversals.
- **Space Complexity:** $O(n)$ to store the adjacency list, subtree counts, and the result array.

# C++ Solution

```cpp
#include <vector>
using namespace std;

class Solution {
public:
    vector<int> sumOfDistancesInTree(int n, vector<vector<int>>& edges) {
        vector<vector<int>> adj(n);
        for (auto& edge : edges) {
            adj[edge[0]].push_back(edge[1]);
            adj[edge[1]].push_back(edge[0]);
        }

        vector<int> count(n, 1);
        vector<int> ans(n, 0);

        auto dfs1 = [&](auto self, int u, int p) -> void {
            for (int v : adj[u]) {
                if (v == p) continue;
                self(self, v, u);
                count[u] += count[v];
                ans[u] += ans[v] + count[v];
            }
        };

        auto dfs2 = [&](auto self, int u, int p) -> void {
            for (int v : adj[u]) {
                if (v == p) continue;
                ans[v] = ans[u] - count[v] + (n - count[v]);
                self(self, v, u);
            }
        };

        dfs1(dfs1, 0, -1);
        dfs2(dfs2, 0, -1);

        return ans;
    }
};
```
{% endraw %}

---
layout: post
title: 'Daily DSA: Minimum Bandwidth on Tree Paths (Medium)'
date: 2026-10-23 20:09:14 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Minimum Bandwidth
  on Tree Paths.'
cover_image: /assets/images/posts/daily-dsa-minimum-bandwidth-on-tree-paths-2026-10-23-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are given an unrooted, undirected, and connected tree consisting of $n$ servers labeled from $0$ to $n - 1$. The network contains $n - 1$ communication links represented by a 2D integer array `edges`, where `edges[i] = [u_i, v_i, w_i]` indicates a bidirectional link between server $u_i$ and server $v_i$ with bandwidth capacity $w_i$.

You are also given a 2D integer array `queries`, where each `queries[j] = [p_j, q_j]` represents a data transfer request between server $p_j$ and server $q_j$.

The *bottleneck bandwidth* of a communication path is defined as the **minimum** edge capacity among all links along the simple path between the two servers. If $p_j == q_j$, the bottleneck bandwidth is defined to be $0$.

Return an integer array `ans` where `ans[j]` is the bottleneck bandwidth for the $j$-th query.

---

### Examples

**Example 1:**

```
Input: n = 5, edges = [[0,1,10],[0,2,5],[1,3,20],[1,4,15]], queries = [[3,4],[2,3],[0,0]]
Output: [15, 5, 0]
Explanation:
- Path 3 to 4: 3 -> 1 -> 4. Edge weights are 20 and 15. The minimum bandwidth is min(20, 15) = 15.
- Path 2 to 3: 2 -> 0 -> 1 -> 3. Edge weights are 5, 10, 20. The minimum bandwidth is min(5, 10, 20) = 5.
- Path 0 to 0: Both endpoints are the same, so the bottleneck is 0.
```

**Example 2:**

```
Input: n = 4, edges = [[0,1,8],[1,2,6],[2,3,4]], queries = [[0,3],[1,3]]
Output: [4, 4]
Explanation:
- Path 0 to 3: 0 -> 1 -> 2 -> 3 with weights 8, 6, 4. The minimum is 4.
- Path 1 to 3: 1 -> 2 -> 3 with weights 6, 4. The minimum is 4.
```

---

### Constraints

- $1 \le n \le 10^5$
- `edges.length` $== n - 1$
- `edges[i] = [u_i, v_i, w_i]`
- $0 \le u_i, v_i < n$
- $u_i \neq v_i$
- $1 \le w_i \le 10^9$
- The given edges form a valid tree.
- $1 \le queries.length \le 10^5$
- `queries[j] = [p_j, q_j]`
- $0 \le p_j, q_j < n$

---

### Approach

Since the graph is a tree, there is a unique simple path between any pair of nodes $(u, v)$. Finding the bottleneck bandwidth along this path corresponds to finding the minimum edge weight along the path from $u$ to $\text{LCA}(u, v)$ and from $v$ to $\text{LCA}(u, v)$, where $\text{LCA}$ is the Lowest Common Ancestor.

Because there are up to $10^5$ queries, traversing each path naively using BFS or DFS per query would take $O(n)$ time per query, resulting in an overall time complexity of $O(n \times q)$, which will exceed the time limit. We need an approach that preprocesses the tree and answers queries in logarithmic time.

#### Binary Lifting

1. **Root the Tree:** Choose an arbitrary node (e.g., node $0$) as the root and perform a DFS/BFS to determine:
   - `depth[u]`: the distance (number of edges) from the root to node $u$.
   - `up[u][0]`: the immediate parent of node $u$.
   - `min_w[u][0]`: the weight of the edge between $u$ and its immediate parent.

2. **Dynamic Programming Table:**
   We compute jump tables of size $O(n \log n)$:
   - `up[u][k]` stores the $2^k$-th ancestor of node $u$.
   - `min_w[u][k]` stores the minimum edge weight on the path from $u$ up to its $2^k$-th ancestor.
   
   Transitions:
   - `up[u][k] = up[up[u][k - 1]][k - 1]`
   - `min_w[u][k] = min(min_w[u][k - 1], min_w[up[u][k - 1]][k - 1])`

3. **Answering a Query $(u, v)$:**
   - If $u == v$, return $0$.
   - Without loss of generality, assume `depth[u] >= depth[v]`. If not, swap them.
   - Lift $u$ to the same depth as $v$ using powers of $2$, while updating the minimum edge weight seen so far.
   - If $u == v$ after lifting, $v$ was an ancestor of $u$, and we return the accumulated minimum.
   - Otherwise, lift both $u$ and $v$ simultaneously as high as possible without them meeting (checking $2^k$ down to $0$). During each jump, update the accumulated minimum.
   - Finally, include the two edges connecting $u$ and $v$ to their common parent `up[u][0]`.

---

### C++ Solution

```cpp
#include <vector>
#include <algorithm>

using namespace std;

class Solution {
public:
    vector<int> minBandwidthQueries(int n, vector<vector<int>>& edges, vector<vector<int>>& queries) {
        // Build adjacency list: pair<neighbor, weight>
        vector<vector<pair<int, int>>> adj(n);
        for (const auto& edge : edges) {
            adj[edge[0]].push_back({edge[1], edge[2]});
            adj[edge[1]].push_back({edge[0], edge[2]});
        }

        const int LOG = 18; // 2^17 = 131072 > 10^5
        vector<vector<int>> up(n, vector<int>(LOG, 0));
        vector<vector<int>> min_w(n, vector<int>(LOG, 1e9 + 7));
        vector<int> depth(n, 0);

        // DFS to initialize depth, parent (up[u][0]), and min_w[u][0]
        auto dfs = [&](auto self, int u, int p, int d, int w) -> void {
            depth[u] = d;
            up[u][0] = p;
            min_w[u][0] = w;

            for (const auto& [v, weight] : adj[u]) {
                if (v != p) {
                    self(self, v, u, d + 1, weight);
                }
            }
        };

        // Root the tree at node 0
        dfs(dfs, 0, 0, 0, 1e9 + 7);

        // Fill the binary lifting tables
        for (int k = 1; k < LOG; ++k) {
            for (int i = 0; i < n; ++i) {
                up[i][k] = up[up[i][k - 1]][k - 1];
                min_w[i][k] = min(min_w[i][k - 1], min_w[up[i][k - 1]][k - 1]);
            }
        }

        // Function to query the bottleneck along the path between u and v
        auto query = [&](int u, int v) -> int {
            if (u == v) return 0;

            int res = 1e9 + 7;

            // Ensure depth[u] >= depth[v]
            if (depth[u] < depth[v]) {
                swap(u, v);
            }

            // Lift u to the same depth as v
            int diff = depth[u] - depth[v];
            for (int k = 0; k < LOG; ++k) {
                if ((diff >> k) & 1) {
                    res = min(res, min_w[u][k]);
                    u = up[u][k];
                }
            }

            if (u == v) return res;

            // Lift both nodes until they are just below their LCA
            for (int k = LOG - 1; k >= 0; --k) {
                if (up[u][k] != up[v][k]) {
                    res = min(res, min_w[u][k]);
                    res = min(res, min_w[v][k]);
                    u = up[u][k];
                    v = up[v][k];
                }
            }

            // Include the edges to their immediate parent (the LCA)
            res = min(res, min_w[u][0]);
            res = min(res, min_w[v][0]);

            return res;
        };

        vector<int> ans;
        ans.reserve(queries.size());
        for (const auto& q : queries) {
            ans.push_back(query(q[0], q[1]));
        }

        return ans;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:**
  - **Preprocessing:** Building the graph takes $O(n)$ time. The DFS runs in $O(n)$, and filling the binary lifting table takes $O(n \log n)$.
  - **Query Processing:** Each query performs at most $O(\log n)$ operations to find the LCA and calculate the minimum along the path.
  - **Total Time Complexity:** $O((n + q) \log n)$, which easily handles $10^5$ nodes and $10^5$ queries within $0.2$ seconds in C++.

- **Space Complexity:**
  - The adjacency list takes $O(n)$ memory.
  - The `up` and `min_w` tables take $O(n \log n)$ space.
  - **Total Space Complexity:** $O(n \log n)$.
{% endraw %}

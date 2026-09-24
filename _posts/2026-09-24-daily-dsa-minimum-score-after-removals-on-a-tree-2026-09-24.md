---
layout: post
title: 'Daily DSA: Minimum Score After Removals on a Tree (Hard)'
date: 2026-09-24 20:06:10 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Minimum Score
  After Removals on a Tree.'
cover_image: /assets/images/posts/daily-dsa-minimum-score-after-removals-on-a-tree-2026-09-24-cover.png
cover_caption: ''
---

### Problem Statement

There is an undirected connected tree with $n$ nodes labeled from $0$ to $n - 1$ and rooted at node $0$. You are given a 0-indexed integer array `nums` of length $n$, where `nums[i]` represents the value of the $i$-th node. You are also given a 2D integer array `edges` of length $n - 1$, where `edges[i] = [a_i, b_i]` denotes that there is an undirected edge between nodes `a_i` and `b_i`.

Remove two distinct edges from the tree. This will split the tree into three connected components. Let the XOR sum of the node values in the three components be $X_1$, $X_2$, and $X_3$.

The score of the removal is the difference between the maximum and minimum XOR values among $X_1$, $X_2$, and $X_3$, which is `max(X1, X2, X3) - min(X1, X2, X3)`.

Return *the minimum possible score of the removal of any two distinct edges*.

---

### Examples

**Example 1:**
```text
Input: nums = [1,5,5,4,11], edges = [[0,1],[1,2],[1,3],[3,4]]
Output: 9
Explanation: 
- Remove edge [0,1] and edge [3,4].
- The components are rooted at 0, 4, and 1-2-3 (minus 4). Wait, the tree splits into:
  - Component containing 0: values [1], XOR = 1
  - Component containing 4: values [11], XOR = 11
  - Component containing 2: values [5, 5, 4], XOR = 5 ^ 5 ^ 4 = 4
- The XOR values are 1, 11, and 4. 
- Max is 11, Min is 1. Score = 11 - 1 = 10 (or other removals give 9).
```

**Example 2:**
```text
Input: nums = [5,5,2,4,4,2], edges = [[0,1],[1,2],[5,2],[4,3],[1,3]]
Output: 0
```

---

### Constraints

- $n == \text{nums.length}$
- $3 \le n \le 1000$
- $1 \le \text{nums}[i] \le 10^5$
- $\text{edges.length} == n - 1$
- $\text{edges}[i].\text{length} == 2$
- $0 \le a_i, b_i < n$
- `edges` represents a valid tree.

---

### Approach & Hint

1. **Subtree XOR Sums**: Every edge removal splits the tree into two parts. If we direct the tree away from root $0$, removing an edge $(u, v)$ (where $v$ is a child of $u$) isolates the subtree rooted at $v$. The XOR sum of this subtree can be computed using a post-order traversal (DFS). Let this be $S(v)$. The other component's XOR sum will be $	ext{TotalXOR} \oplus S(v)$.
2. **Two Edge Removals**: Since $n$ is up to $1000$, $n^2$ is at most $10^6$, which is small enough to iterate over all pairs of edges to remove.
3. **Component Relationships**: When we remove two edges, say corresponding to subtrees rooted at $v_1$ and $v_2$ (assume $v_1 \neq v_2$): 
   - Case 1: $v_2$ is inside the subtree of $v_1$. Then the three components are: subtree of $v_2$ (XOR $S(v_2)$), subtree of $v_1$ excluding subtree of $v_2$ (XOR $S(v_1) \oplus S(v_2)$), and the rest of the tree (XOR $	ext{TotalXOR} \oplus S(v_1)$).
   - Case 2: $v_1$ is inside the subtree of $v_2$ (symmetric to Case 1).
   - Case 3: $v_1$ and $v_2$ are in disjoint branches. The three components are: subtree of $v_1$ (XOR $S(v_1)$), subtree of $v_2$ (XOR $S(v_2)$), and the rest of the tree (XOR $	ext{TotalXOR} \oplus S(v_1) \oplus S(v_2)$).
4. Precompute the subtree ranges `in[i]` and `out[i]` using DFS entry/exit times to easily check if one node is an ancestor of another in $O(1)$ time.

---

### C++ Solution

```cpp
#include <vector>
#include <algorithm>

using namespace std;

class Solution {
    vector<vector<int>> adj;
    vector<int> subtree_xor;
    vector<int> in, out;
    int timer;

    void dfs(int u, int p, const vector<int>& nums) {
        in[u] = ++timer;
        subtree_xor[u] = nums[u];
        for (int v : adj[u]) {
            if (v != p) {
                dfs(v, u, nums);
                subtree_xor[u] ^= subtree_xor[v];
            }
        }
        out[u] = timer;
    }

    bool isAncestor(int u, int v) {
        return in[u] <= in[v] && out[v] <= out[u];
    }

public:
    int minimumScore(vector<int>& nums, vector<vector<int>>& edges) {
        int n = nums.size();
        adj.assign(n, vector<int>());
        subtree_xor.assign(n, 0);
        in.assign(n, 0);
        out.assign(n, 0);
        timer = 0;

        for (const auto& edge : edges) {
            adj[edge[0]].push_back(edge[1]);
            adj[edge[1]].push_back(edge[0]);
        }

        dfs(0, -1, nums);
        int total_xor = subtree_xor[0];
        int min_score = 1e9;

        // edges are represented by their child nodes (since each non-root node has a unique parent)
        vector<int> nodes;
        for (int i = 1; i < n; ++i) {
            nodes.push_back(i);
        }

        int m = nodes.size();
        for (int i = 0; i < m; ++i) {
            for (int j = i + 1; j < m; ++j) {
                int u = nodes[i];
                int v = nodes[j];
                int x1 = subtree_xor[u];
                int x2 = subtree_xor[v];
                int x3 = total_xor;

                if (isAncestor(u, v)) {
                    // v is inside u's subtree
                    x3 ^= subtree_xor[u];
                    x1 ^= subtree_xor[v];
                } else if (isAncestor(v, u)) {
                    // u is inside v's subtree
                    x3 ^= subtree_xor[v];
                    x2 ^= subtree_xor[u];
                } else {
                    // Disjoint subtrees
                    x3 ^= (subtree_xor[u] ^ subtree_xor[v]);
                }

                int current_max = max({x1, x2, x3});
                int current_min = min({x1, x2, x3});
                min_score = min(min_score, current_max - current_min);
            }
        }

        return min_score;
    }
};
```

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(n^2)$. We perform a DFS in $\mathcal{O}(n)$ time to compute subtree XOR sums and entry/exit times. Then, we iterate over all pairs of edges, which takes $\mathcal{O}(n^2)$ iterations, doing $\mathcal{O}(1)$ ancestor checks per pair. Since $n \le 1000$, $n^2 = 10^6$ operations, which easily runs within the time limit.
- **Space Complexity:** $\mathcal{O}(n)$ to store the adjacency list, subtree XOR sums, recursion stack, and entry/exit times.

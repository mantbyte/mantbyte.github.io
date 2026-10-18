---
layout: post
title: 'Daily DSA: Subtree Value Range Queries (Medium)'
date: 2026-10-18 19:14:02 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Subtree Value
  Range Queries.'
cover_image: /assets/images/posts/daily-dsa-subtree-value-range-queries-2026-10-18-cover.png
cover_caption: ''
---

{% raw %}
### Problem Description

You are given a tree consisting of $n$ nodes numbered from $0$ to $n - 1$, rooted at node $0$. The tree is represented by an array of edges `edges` where `edges[i] = [u_i, v_i]` indicates an undirected edge between nodes $u_i$ and $v_i$, and an array `values` where `values[i]` is the initial value assigned to node $i$.

You are also given a list of queries `queries`, where each query is of one of two types:
- `[1, u, val]`: Add `val` to the value of node `u`.
- `[2, u]`: Compute and return the sum of values of all nodes in the subtree rooted at `u`.

Return an array containing the results of all type `2` queries in the order they appear.

---

### Examples

**Example 1:**

```
Input:
n = 5
edges = [[0, 1], [0, 2], [1, 3], [1, 4]]
values = [1, 2, 3, 4, 5]
queries = [
  [2, 1],
  [1, 3, 6],
  [2, 1],
  [2, 0]
]
Output: [11, 17, 21]
Explanation:
- The tree structure:
        0 (val: 1)
       / \
(val: 2) 1   2 (val: 3)
        / \
 (val: 4) 3 4 (val: 5)
- Query 1: Type 2 on node 1. Subtree of 1 consists of {1, 3, 4}. Sum = 2 + 4 + 5 = 11.
- Query 2: Type 1 on node 3. values[3] becomes 4 + 6 = 10.
- Query 3: Type 2 on node 1. Subtree of 1 sum = 2 + 10 + 5 = 17.
- Query 4: Type 2 on node 0. Subtree of 0 is the whole tree. Sum = 1 + 2 + 3 + 10 + 5 = 21.
```

**Example 2:**

```
Input:
n = 3
edges = [[0, 1], [1, 2]]
values = [5, -2, 10]
queries = [
  [2, 2],
  [1, 1, 3],
  [2, 0]
]
Output: [10, 16]
Explanation:
- Query 1: Subtree rooted at 2 is just {2}, sum = 10.
- Query 2: values[1] becomes -2 + 3 = 1.
- Query 3: Subtree rooted at 0 sum = 5 + 1 + 10 = 16.
```

---

### Constraints

- $1 \le n \le 10^5$
- `edges.length` $== n - 1$
- `edges[i].length` $== 2$
- $0 \le u_i, v_i < n$
- The given edges form a valid tree.
- `values.length` $== n$
- $-10^9 \le values[i] \le 10^9$
- $1 \le queries.length \le 10^5$
- For type `1` query: $0 \le u < n$ and $-10^9 \le val \le 10^9$
- For type `2` query: $0 \le u < n$

---

### Approach

1. **Euler Tour Technique (Tree Flattening)**:
   - When traversing a tree with Depth First Search (DFS), we can assign each node an entry timestamp `tin[u]` and an exit timestamp `tout[u]`.
   - Any node $v$ inside the subtree of $u$ is visited strictly between the entry and exit times of $u$. Thus, the entire subtree rooted at $u$ corresponds to a contiguous range $[tin[u], tout[u]]$ in the flattened array of size $n$.

2. **Fenwick Tree (Binary Indexed Tree)**:
   - With the tree flattened into an array of indices $1$ to $n$, the two operations become standard array operations:
     - **Type 1 (Point Update)**: Add `val` at index `tin[u]`.
     - **Type 2 (Range Sum Query)**: Query the prefix sum up to `tout[u]` and subtract the prefix sum up to `tin[u] - 1`.
   - A Fenwick Tree provides both operations in $O(\log n)$ time with $O(n)$ space.

3. **Initial State**:
   - We initialize the Fenwick Tree with the initial values positioned at `tin[u]` for each node $u$.

---

### C++ Solution

```cpp
#include <vector>

using namespace std;

class FenwickTree {
private:
    int n;
    vector<long long> tree;

public:
    FenwickTree(int n) : n(n), tree(n + 1, 0) {}

    void add(int i, long long delta) {
        for (; i <= n; i += i & -i) {
            tree[i] += delta;
        }
    }

    long long query(int i) {
        long long sum = 0;
        for (; i > 0; i -= i & -i) {
            sum += tree[i];
        }
        return sum;
    }

    long long queryRange(int l, int r) {
        return query(r) - query(l - 1);
    }
};

class Solution {
private:
    int timer = 0;
    void dfs(int u, int parent, const vector<vector<int>>& adj, vector<int>& tin, vector<int>& tout) {
        tin[u] = ++timer;
        for (int v : adj[u]) {
            if (v != parent) {
                dfs(v, u, adj, tin, tout);
            }
        }
        tout[u] = timer;
    }

public:
    vector<long long> subtreeQueries(int n, vector<vector<int>>& edges, vector<int>& values, vector<vector<int>>& queries) {
        vector<vector<int>> adj(n);
        for (const auto& edge : edges) {
            adj[edge[0]].push_back(edge[1]);
            adj[edge[1]].push_back(edge[0]);
        }

        vector<int> tin(n), tout(n);
        timer = 0;
        dfs(0, -1, adj, tin, tout);

        FenwickTree bit(n);
        for (int i = 0; i < n; ++i) {
            bit.add(tin[i], values[i]);
        }

        vector<long long> results;
        for (const auto& q : queries) {
            if (q[0] == 1) {
                int u = q[1];
                long long val = q[2];
                bit.add(tin[u], val);
            } else if (q[0] == 2) {
                int u = q[1];
                results.push_back(bit.queryRange(tin[u], tout[u]));
            }
        }

        return results;
    }
};
```

---

### Complexity Analysis

- **Time Complexity**:
  - **Tree Flattening (DFS)**: $O(n)$ to traverse all vertices and edges.
  - **Fenwick Tree Initialization**: $O(n \log n)$ to insert initial node values.
  - **Query Processing**: Each type `1` or type `2` query takes $O(\log n)$ via the Fenwick Tree. For $q$ queries, this takes $O(q \log n)$.
  - **Total Time Complexity**: $O((n + q) \log n)$, which is optimal and runs in around $0.1$s for $10^5$ operations.

- **Space Complexity**:
  - The adjacency list requires $O(n)$ space.
  - `tin` and `tout` arrays require $O(n)$ space.
  - The Fenwick Tree requires $O(n)$ space.
  - Recursion stack in DFS requires $O(n)$ space in the worst case (skewed tree).
  - **Total Space Complexity**: $O(n)$ auxiliary space (excluding the output array).
{% endraw %}

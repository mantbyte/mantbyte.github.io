---
layout: post
title: 'Daily DSA: Dynamic Connected Components with Max Weight (Medium)'
date: 2026-08-13 16:27:36 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Dynamic Connected
  Components with Max Weight.'
cover_image: /assets/images/posts/daily-dsa-dynamic-connected-components-with-max-weight-2026-08-13-cover.png
cover_caption: ''
---

### Problem Description

You are given $n$ nodes numbered from $0$ to $n - 1$, where each node $i$ has an associated integer weight specified by `weights[i]`. Initially, there are no edges between any of the nodes, so each node forms its own isolated connected component.

You are given a list of operations called `queries`, where each query is represented as a 3-element array `[type, u, v]`:
- **Type 1 (`[1, u, v]`)**: Add an undirected edge between node `u` and node `v`. If they are already in the same connected component, this operation has no effect on component structure.
- **Type 2 (`[2, u, -1]`)**: Query the maximum weight among all nodes in the connected component containing node `u`. The third value `v` is set to `-1` and should be ignored.

Return an array of integers containing the answers to all **Type 2** queries in the order they appear.

---

### Examples

#### Example 1:
```text
Input:
n = 5
weights = [10, 20, 15, 30, 5]
queries = [
  [2, 0, -1],
  [1, 0, 1],
  [2, 0, -1],
  [1, 1, 2],
  [2, 2, -1],
  [1, 3, 4],
  [2, 4, -1]
]
Output: [10, 20, 20, 30]
```

**Explanation:**
1. `[2, 0, -1]`: Component containing node 0 has nodes `{0}` with max weight `10`.
2. `[1, 0, 1]`: Add edge `(0, 1)`. Component becomes `{0, 1}` with weights `[10, 20]`.
3. `[2, 0, -1]`: Component containing node 0 is `{0, 1}`. Max weight is `20`.
4. `[1, 1, 2]`: Add edge `(1, 2)`. Component becomes `{0, 1, 2}` with weights `[10, 20, 15]`.
5. `[2, 2, -1]`: Component containing node 2 is `{0, 1, 2}`. Max weight is `20`.
6. `[1, 3, 4]`: Add edge `(3, 4)`. Component becomes `{3, 4}` with weights `[30, 5]`.
7. `[2, 4, -1]`: Component containing node 4 is `{3, 4}`. Max weight is `30`.

#### Example 2:
```text
Input:
n = 3
weights = [50, 10, 40]
queries = [
  [1, 0, 1],
  [1, 1, 2],
  [2, 1, -1]
]
Output: [50]
```

**Explanation:**
After merging all 3 nodes into a single component `{0, 1, 2}`, the weights present are `[50, 10, 40]`. Querying node 1 yields the maximum weight `50`.

---

### Constraints

- $1 \le n \le 10^5$
- `weights.length` $== n$
- $1 \le \text{weights}[i] \le 10^9$
- $1 \le \text{queries.length} \le 10^5$
- Each query is formatted as `[type, u, v]` where `type` $\in \{1, 2\}$, $0 \le u, v < n$.
- For `type == 2`, $v = -1$.

---

### Approach

This problem can be efficiently solved using the **Disjoint Set Union (DSU)** (or Union-Find) data structure:

1. **DSU Initialization:**
   - Maintain a `parent` array where `parent[i] = i` initially.
   - Maintain a `max_weight` array initialized with `max_weight[i] = weights[i]` for each representative root.
   - Optionally use union by rank/size for optimal time complexity.

2. **Path Compression:**
   - Implement the `find(u)` operation with path compression to achieve near $O(1)$ amortized lookup time.

3. **Union Operation (`[1, u, v]`):**
   - Find the roots `root_u` and `root_v` of `u` and `v`.
   - If they belong to different components, merge them by setting `parent[root_v] = root_u`.
   - Update `max_weight[root_u] = max(max_weight[root_u], max_weight[root_v])`.

4. **Query Operation (`[2, u, -1]`):**
   - Find the root of node `u`: `root_u = find(u)`.
   - The maximum weight for this component is directly stored at `max_weight[root_u]`.

#### Complexity Analysis:
- **Time Complexity:** $O(n + q \cdot \alpha(n))$, where $q$ is the number of queries and $\alpha$ is the Inverse Ackermann function. This is effectively $O(n + q)$ in practice.
- **Space Complexity:** $O(n)$ auxiliary space to store the DSU parent pointers and maximum weights.

---

### C++ Source Code

```cpp
#include <vector>
#include <algorithm>
#include <numeric>

class DSU {
private:
    std::vector<int> parent;
    std::vector<int> max_weight;
    std::vector<int> rank;

public:
    DSU(int n, const std::vector<int>& weights) {
        parent.resize(n);
        std::iota(parent.begin(), parent.end(), 0);
        max_weight = weights;
        rank.assign(n, 0);
    }

    int find(int i) {
        if (parent[i] == i)
            return i;
        return parent[i] = find(parent[i]);
    }

    void unite(int i, int j) {
        int root_i = find(i);
        int root_j = find(j);

        if (root_i != root_j) {
            if (rank[root_i] < rank[root_j]) {
                std::swap(root_i, root_j);
            }
            parent[root_j] = root_i;
            max_weight[root_i] = std::max(max_weight[root_i], max_weight[root_j]);
            if (rank[root_i] == rank[root_j]) {
                rank[root_i]++;
            }
        }
    }

    int getMaxWeight(int i) {
        int root = find(i);
        return max_weight[root];
    }
};

class Solution {
public:
    std::vector<int> processQueries(int n, std::vector<int>& weights, std::vector<std::vector<int>>& queries) {
        DSU dsu(n, weights);
        std::vector<int> result;

        for (const auto& query : queries) {
            int type = query[0];
            int u = query[1];
            int v = query[2];

            if (type == 1) {
                dsu.unite(u, v);
            } else if (type == 2) {
                result.push_back(dsu.getMaxWeight(u));
            }
        }

        return result;
    }
};
```

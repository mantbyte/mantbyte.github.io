---
layout: post
title: 'Daily DSA: Consistent Relative Positions (Medium)'
date: 2026-10-13 01:04:48 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Consistent
  Relative Positions.'
cover_image: /assets/images/posts/daily-dsa-consistent-relative-positions-2026-10-12-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are given an integer `n`, representing `n` landmarks indexed from `0` to `n - 1` along a straight East-West road.

You are also given a 2D integer array `relations`, where `relations[i] = [u, v, d]`. Each entry represents an observation claiming that landmark `v` is located exactly `d` units to the East of landmark `u` (i.e., `pos(v) - pos(u) == d`). Note that `d` can be positive, negative, or zero.

We process the relations sequentially in the given order:
- If an observation does **not** contradict any previously accepted observations, it is considered **valid** and is accepted.
- If an observation contradicts any previously accepted observations, it is considered **invalid** and is discarded.

Return a boolean array `ans` of length equal to `relations.length`, where `ans[i]` is `true` if `relations[i]` is accepted, or `false` if it is rejected.

---

### Examples

**Example 1:**
```
Input: n = 4, relations = [[0, 1, 10], [1, 2, 5], [0, 2, 15], [0, 2, 20]]
Output: [true, true, true, false]
Explanation:
- [0, 1, 10]: Sets pos(1) - pos(0) = 10. Valid.
- [1, 2, 5]: Sets pos(2) - pos(1) = 5. Now pos(2) - pos(0) = 15. Valid.
- [0, 2, 15]: Observation claims pos(2) - pos(0) = 15, which matches our existing deductions. Valid.
- [0, 2, 20]: Observation claims pos(2) - pos(0) = 20, contradicting pos(2) - pos(0) = 15. Invalid.
```

**Example 2:**
```
Input: n = 3, relations = [[0, 1, 4], [0, 0, 5], [1, 0, -4]]
Output: [true, false, true]
Explanation:
- [0, 1, 4]: Sets pos(1) - pos(0) = 4. Valid.
- [0, 0, 5]: Claims pos(0) - pos(0) = 5 != 0. Invalid.
- [1, 0, -4]: Claims pos(0) - pos(1) = -4, which is equivalent to pos(1) - pos(0) = 4. Valid.
```

**Example 3:**
```
Input: n = 4, relations = [[0, 1, 3], [2, 3, 4], [1, 2, -2], [0, 3, 5]]
Output: [true, true, true, true]
Explanation:
- [0, 1, 3]: pos(1) - pos(0) = 3.
- [2, 3, 4]: pos(3) - pos(2) = 4.
- [1, 2, -2]: Connects the two components. Now pos(3) - pos(0) = (pos(1) - pos(0)) + (pos(2) - pos(1)) + (pos(3) - pos(2)) = 3 + (-2) + 4 = 5.
- [0, 3, 5]: Matches pos(3) - pos(0) = 5. Valid.
```

---

### Constraints

- `1 <= n <= 10^5`
- `1 <= relations.length <= 10^5`
- `relations[i].length == 3`
- `0 <= u, v < n`
- `-10^9 <= d <= 10^9`

---

### Approach

This problem can be modeled as maintaining relative offsets in connected components, which is best solved using a **Disjoint Set Union (DSU) with Potential (Weighted DSU)**.

#### Key Idea
In a standard DSU, each element points to a parent, eventually leading to a representative root. In a weighted DSU, we also maintain a `dist[x]` array representing the relative displacement from `parent[x]` to `x`: `pos(x) - pos(parent[x]) = dist[x]`.

1. **Path Compression with Offset Accumulation:**
   When querying `find(x)`, we recursively find the root of `parent[x]`. As the recursion unwinds, we update `dist[x] += dist[parent[x]]` and redirect `parent[x] = root`. After path compression, `dist[x]` directly represents `pos(x) - pos(root)`.

2. **Evaluating an Observation `(u, v, d)`:**
   - Find the roots of `u` and `v`: `rootU = find(u)` and `rootV = find(v)`.
   - **Case 1: `rootU == rootV`**
     Both nodes already belong to the same component, so their relative position is fixed.
     The known displacement is `pos(v) - pos(u) = dist[v] - dist[u]`.
     - If `dist[v] - dist[u] == d`, the observation is consistent and accepted (`true`).
     - Otherwise, it is a contradiction and rejected (`false`).
   - **Case 2: `rootU != rootV`**
     The two components are not yet connected, so no contradiction is possible. The relation is accepted (`true`).
     We merge the components by setting `parent[rootV] = rootU`.
     To find `dist[rootV]` (displacement of `rootV` relative to `rootU`), we use the relation:
     $$pos(v) - pos(u) = d$$
     $$(pos(rootV) + dist[v]) - (pos(rootU) + dist[u]) = d$$
     $$pos(rootV) - pos(rootU) = d + dist[u] - dist[v]$$
     Thus, we assign `dist[rootV] = d + dist[u] - dist[v]`.

#### Precision Note
Distances can accumulate across multiple additions, potentially exceeding standard 32-bit integers. We use 64-bit integers (`long long` in C++) for all distance offsets.

---

### C++ Implementation

```cpp
#include <vector>

using namespace std;

class Solution {
    struct WeightedDSU {
        vector<int> parent;
        vector<long long> dist; // dist[i] = pos(i) - pos(parent[i])

        WeightedDSU(int n) {
            parent.resize(n);
            dist.assign(n, 0LL);
            for (int i = 0; i < n; ++i) {
                parent[i] = i;
            }
        }

        int find(int i) {
            if (parent[i] == i) {
                return i;
            }
            int originalParent = parent[i];
            parent[i] = find(parent[i]);
            dist[i] += dist[originalParent];
            return parent[i];
        }

        bool addRelation(int u, int v, long long d) {
            int rootU = find(u);
            int rootV = find(v);

            if (rootU == rootV) {
                // Both are in the same component, check consistency
                return (dist[v] - dist[u]) == d;
            }

            // Merge rootV into rootU
            parent[rootV] = rootU;
            dist[rootV] = d + dist[u] - dist[v];
            return true;
        }
    };

public:
    vector<bool> validateRelations(int n, vector<vector<int>>& relations) {
        WeightedDSU dsu(n);
        int m = relations.size();
        vector<bool> ans(m);

        for (int i = 0; i < m; ++i) {
            int u = relations[i][0];
            int v = relations[i][1];
            long long d = relations[i][2];
            ans[i] = dsu.addRelation(u, v, d);
        }

        return ans;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}((N + M) \log N)$ or $\mathcal{O}((N + M) \alpha(N))$ nearly linear time, where $N$ is the number of landmarks and $M$ is the number of relations. Path compression keeps tree depth minimal.
- **Space Complexity:** $\mathcal{O}(N)$ auxiliary space for storing the `parent` and `dist` arrays in the DSU, plus $\mathcal{O}(M)$ for the output array.
{% endraw %}

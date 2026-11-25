---
layout: post
title: 'Daily DSA: Kruskal''s Algorithm - Minimum Spanning Tree (Medium)'
date: 2026-11-26 01:12:48 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Kruskal''s
  Algorithm - Minimum Spanning Tree.'
cover_image: /assets/images/posts/daily-dsa-kruskals-algorithm--minimum-spanning-tree-2026-11-25-cover.png
cover_caption: ''
---

{% raw %}
# Problem Statement

Given an undirected, connected, and weighted graph with $N$ vertices and $M$ edges, find the weight of the **Minimum Spanning Tree (MST)** of the graph. A spanning tree is a subset of all the edges of the graph that forms a tree and connects all the vertices together, without any cycles, with the minimum possible total edge weight.

# Examples

### Example 1:
```
Input: N = 4, edges = [[0, 1, 10], [0, 2, 6], [0, 3, 5], [1, 3, 15], [2, 3, 4]]
Output: 19
Explanation:
The edges selected in the MST are:
- (2, 3) with weight 4
- (0, 3) with weight 5
- (0, 1) with weight 10
Total weight = 4 + 5 + 10 = 19.
```

### Example 2:
```
Input: N = 3, edges = [[0, 1, 1], [1, 2, 2], [0, 2, 3]]
Output: 3
Explanation:
The edges selected in the MST are:
- (0, 1) with weight 1
- (1, 2) with weight 2
Total weight = 1 + 2 = 3.
```

# Constraints
- $1 \le N \le 10^5$
- $1 \le M \le 2 \times 10^5$
- $0 \le u, v < N$
- $1 \le \text{weight} \le 10^4$

# Approach

To find the Minimum Spanning Tree, we can use **Kruskal's Algorithm**:
1. **Sort all the edges** in non-decreasing order of their weight.
2. **Initialize a Disjoint Set Union (DSU)** data structure with $N$ elements, where each vertex is its own parent initially.
3. Iterate through the sorted edges:
   - For each edge $(u, v, w)$, find the set representatives (roots) of $u$ and $v$ using the DSU `find` operation.
   - If $u$ and $v$ belong to different sets (i.e., adding the edge does not form a cycle), include this edge in the MST, add its weight to the total cost, and union the two sets using `unionSet`.
4. Stop when we have included $N - 1$ edges in the MST.

# C++ Code

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

class DSU {
    vector<int> parent, rank;
public:
    DSU(int n) {
        parent.resize(n);
        rank.resize(n, 0);
        for (int i = 0; i < n; i++) parent[i] = i;
    }

    int find(int i) {
        if (parent[i] == i)
            return i;
        return parent[i] = find(parent[i]);
    }

    bool unite(int i, int j) {
        int root_i = find(i);
        int root_j = find(j);
        if (root_i != root_j) {
            if (rank[root_i] < rank[root_j])
                parent[root_i] = root_j;
            else if (rank[root_i] > rank[root_j])
                parent[root_j] = root_i;
            else {
                parent[root_j] = root_i;
                rank[root_i]++;
            }
            return true;
        }
        return false;
    }
};

class Solution {
public:
    int minSpanningTree(int N, vector<vector<int>>& edges) {
        // Sort edges based on weight
        sort(edges.begin(), edges.end(), [](const vector<int>& a, const vector<int>& b) {
            return a[2] < b[2];
        });

        DSU dsu(N);
        int totalWeight = 0;
        int edgesCount = 0;

        for (const auto& edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int w = edge[2];

            if (dsu.unite(u, v)) {
                totalWeight += w;
                edgesCount++;
                if (edgesCount == N - 1) break;
            }
        }

        return totalWeight;
    }
};
```

# Complexity Analysis
- **Time Complexity:** $O(M \log M + M \alpha(N))$, where $M$ is the number of edges and $N$ is the number of vertices. Sorting the edges takes $O(M \log M)$ time, and processing each edge with DSU takes nearly constant time $O(\alpha(N))$ due to path compression and union by rank.
- **Space Complexity:** $O(N + M)$ to store the DSU structure and the edge list.
{% endraw %}

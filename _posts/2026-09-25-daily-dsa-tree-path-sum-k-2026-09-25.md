---
layout: post
title: 'Daily DSA: Tree Path Sum K (Hard)'
date: 2026-09-25 20:27:43 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Tree Path Sum
  K.'
cover_image: /assets/images/posts/default-cover.png
cover_caption: ''
---

### Problem Statement

You are given a tree with $n$ nodes and $n-1$ edges. Each edge has an associated integer weight. A path between two nodes $u$ and $v$ is defined as the unique simple path connecting them. The weight of a path is the sum of the weights of all edges on that path.

Your task is to find the total number of unique pairs of nodes $(u, v)$ such that $u < v$ and the weight of the path between them is exactly $K$.

### Examples

**Example 1:**
**Input:** 
`n = 5, k = 3`  
`edges = [[1, 2, 1], [1, 3, 2], [2, 4, 2], [2, 5, 1]]`  
**Output:** `3`  
**Explanation:** 
- Path (3, 1, 2): weight 2 + 1 = 3.
- Path (1, 2, 4): weight 1 + 2 = 3.
- Path (4, 2, 5): weight 2 + 1 = 3.
Total paths with sum 3 are 3.

**Example 2:**
**Input:** 
`n = 4, k = 5`  
`edges = [[1, 2, 10], [2, 3, 5], [3, 4, 1]]`  
**Output:** `0`  
**Explanation:** No path in the tree has a sum of exactly 5.

### Constraints

- $1 \le n \le 10^5$
- $1 \le k \le 10^6$
- $1 \le u, v \le n$
- $1 \le weight \le 10^5$

---

### Approach

The problem asks for paths in a tree with a specific property (path sum). Standard Tree DP might be difficult because path sums can be large. Centroid Decomposition is the ideal technique for path-related problems in trees.

1. **Centroid Decomposition**: Find the centroid of the current tree. The centroid is a node whose removal splits the tree into components, each with at most half the nodes of the original tree.
2. **Counting Paths**: For a chosen centroid $C$, any path in the tree either:
   - Passes through $C$.
   - Lies entirely within one of the subtrees formed by removing $C$.
3. **Processing the Centroid**: To count paths passing through $C$:
   - Maintain a frequency array `cnt` where `cnt[s]` stores the number of nodes found so far in previously processed subtrees of $C$ that are at distance `s` from $C$.
   - For each child of $C$, perform a DFS to find all node distances `d` from $C$ within that child's subtree.
   - For each distance `d`, if `d <= K`, add `cnt[K - d]` to the total answer.
   - After processing a child's subtree, update the `cnt` array with the distances found in that subtree.
4. **Divide and Conquer**: Mark the centroid as visited (effectively removing it) and recursively apply the same logic to the remaining components.

**Time Complexity:** $O(N \log N)$ because the tree is decomposed into $\log N$ levels, and each node is processed once per level.
**Space Complexity:** $O(N + K)$ for the adjacency list and the frequency array.

---

### C++ Solution

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

const int MAXN = 100005;
const int MAXK = 1000005;

struct Edge {
    int to, weight;
};

vector<Edge> adj[MAXN];
int sz[MAXN];
bool vis[MAXN];
int cnt[MAXK];
long long total_paths = 0;
int max_k;

void get_sz(int u, int p) {
    sz[u] = 1;
    for (auto& edge : adj[u]) {
        if (edge.to != p && !vis[edge.to]) {
            get_sz(edge.to, u);
            sz[u] += sz[edge.to];
        }
    }
}

int get_centroid(int u, int p, int n) {
    for (auto& edge : adj[u]) {
        if (edge.to != p && !vis[edge.to] && sz[edge.to] > n / 2)
            return get_centroid(edge.to, u, n);
    }
    return u;
}

void get_distances(int u, int p, int dist, int K, vector<int>& dists) {
    if (dist > K) return;
    dists.push_back(dist);
    for (auto& edge : adj[u]) {
        if (edge.to != p && !vis[edge.to]) {
            get_distances(edge.to, u, dist + edge.weight, K, dists);
        }
    }
}

void decompose(int u, int K) {
    get_sz(u, -1);
    int centroid = get_centroid(u, -1, sz[u]);
    vis[centroid] = true;

    cnt[0] = 1;
    int current_max_d = 0;

    for (auto& edge : adj[centroid]) {
        if (!vis[edge.to]) {
            vector<int> dists;
            get_distances(edge.to, centroid, edge.weight, K, dists);
            
            for (int d : dists) {
                if (K >= d) total_paths += cnt[K - d];
            }
            for (int d : dists) {
                cnt[d]++;
                current_max_d = max(current_max_d, d);
            }
        }
    }

    // Reset cnt array for next centroid efficiently
    for (int i = 0; i <= current_max_d; ++i) cnt[i] = 0;

    for (auto& edge : adj[centroid]) {
        if (!vis[edge.to]) {
            decompose(edge.to, K);
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    if (!(cin >> n >> k)) return 0;

    for (int i = 0; i < n - 1; ++i) {
        int u, v, w;
        cin >> u >> v >> w;
        adj[u].push_back({v, w});
        adj[v].push_back({u, w});
    }

    decompose(1, k);
    cout << total_paths << endl;

    return 0;
}
```"

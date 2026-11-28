---
layout: post
title: 'Daily DSA: Network Flow - Dinic''s Algorithm - Maximum Flow (Hard)'
date: 2026-11-28 23:24:45 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Network Flow
  - Dinic''s Algorithm - Maximum Flow.'
cover_image: /assets/images/posts/daily-dsa-network-flow--dinics-algorithm--maximum-flow-2026-11-28-cover.png
cover_caption: ''
---

{% raw %}
# Problem Statement

You are given a directed network of conduits (edges) represented as a flow network with $N$ nodes (labeled $1$ to $N$) and $M$ directed edges. Each edge has a certain capacity that limits the maximum amount of flow that can pass through it.

Your task is to find the **Maximum Flow** from a designated source node $S$ (node $1$) to a designated sink node $T$ (node $N$).

# Examples

**Example 1:**
* **Input:**
  * $N = 4, M = 5, S = 1, T = 4$
  * Edges: 
    * $(1, 2, 3)$
    * $(1, 3, 2)$
    * $(2, 3, 1)$
    * $(2, 4, 2)$
    * $(3, 4, 3)$
* **Output:** `5`
* **Explanation:** 
  * Send 3 units along $1 \to 2 \to 4$
  * Send 2 units along $1 \to 3 \to 4$
  * Total flow = $3 + 2 = 5$.

**Example 2:**
* **Input:**
  * $N = 3, M = 3, S = 1, T = 3$
  * Edges:
    * $(1, 2, 10)$
    * $(2, 3, 10)$
    * $(1, 3, 5)$
* **Output:** `15`
* **Explanation:** 
  * Send 10 units through $1 \to 2 \to 3$.
  * Send 5 units through $1 \to 3$.
  * Total flow = $10 + 5 = 15$.

# Constraints
* $2 \le N \le 500$
* $1 \le M \le 2000$
* $1 \le u, v \le N$
* $0 \le \text{capacity} \le 10^9$
* The source and sink are distinct ($S \neq T$).

# Approach / Hint
To solve the Maximum Flow problem efficiently, we can use **Dinic's Algorithm**, which runs in $O(V^2 E)$ time in the worst case and much faster on typical networks. 
1. **Level Graph (BFS):** Use Breadth-First Search from the source node $S$ to assign levels (shortest distance in terms of edges) to all reachable nodes in the residual graph. If the sink $T$ cannot be reached, the algorithm terminates.
2. **Blocking Flow (DFS):** Use Depth-First Search to find a *blocking flow* in the level graph, pushing flow only from nodes at level $l$ to nodes at level $l+1$. Optimizations like the *pointer/cur array* ensure we don't revisit dead-end edges.
3. Repeat the BFS and DFS phases until no augmenting path to $T$ remains in the residual graph.

# C++ Solution

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>

using namespace std;

const long long INF = 1e18;

struct Edge {
    int to;
    long long cap;
    long long flow;
    int rev;
};

class Dinic {
    int n;
    vector<vector<Edge>> adj;
    vector<int> level;
    vector<int> ptr;

public:
    Dinic(int n) : n(n), adj(n + 1), level(n + 1), ptr(n + 1) {}

    void add_edge(int from, int to, long long cap) {
        adj[from].push_back({to, cap, 0, (int)adj[to].size()});
        adj[to].push_back({from, 0, 0, (int)adj[from].size() - 1});
    }

    bool bfs(int s, int t) {
        fill(level.begin(), level.end(), -1);
        level[s] = 0;
        queue<int> q;
        q.push(s);
        while (!q.empty()) {
            int v = q.front();
            q.pop();
            for (auto& edge : adj[v]) {
                if (edge.cap - edge.flow > 0 && level[edge.to] == -1) {
                    level[edge.to] = level[v] + 1;
                    q.push(edge.to);
                }
            }
        }
        return level[t] != -1;
    }

    long long dfs(int v, int t, long long pushed) {
        if (pushed == 0) return 0;
        if (v == t) return pushed;
        for (int& cid = ptr[v]; cid < adj[v].size(); ++cid) {
            auto& edge = adj[v][cid];
            int tr = edge.to;
            if (level[v] + 1 != level[tr] || edge.cap - edge.flow == 0) continue;
            long long tr_pushed = dfs(tr, t, min(pushed, edge.cap - edge.flow));
            if (tr_pushed == 0) continue;
            edge.flow += tr_pushed;
            adj[tr][edge.rev].flow -= tr_pushed;
            return tr_pushed;
        }
        return 0;
    }

    long long max_flow(int s, int t) {
        long long flow = 0;
        while (bfs(s, t)) {
            fill(ptr.begin(), ptr.end(), 0);
            while (long long pushed = dfs(s, t, INF)) {
                flow += pushed;
            }
        }
        return flow;
    }
};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    if (!(cin >> n >> m)) return 0;

    int s = 1, t = n;
    Dinic dinic(n);

    for (int i = 0; i < m; ++i) {
        int u, v;
        long long cap;
        cin >> u >> v >> cap;
        dinic.add_edge(u, v, cap);
    }

    cout << dinic.max_flow(s, t) << "\n";

    return 0;
}
```

### Complexity Analysis
- **Time Complexity:** $O(V^2 E)$, where $V$ is the number of vertices and $E$ is the number of edges. Due to the layer graph property in Dinic's algorithm, the number of augmentations is bounded efficiently.
- **Space Complexity:** $O(V + E)$ to store the adjacency list representation of the network graph along with level and pointer arrays.
{% endraw %}

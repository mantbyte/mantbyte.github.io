---
layout: post
title: 'Daily DSA: Maximum Weight Independent Set on a Tree (Medium)'
date: 2026-11-06 22:36:17 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Maximum Weight
  Independent Set on a Tree.'
cover_image: /assets/images/posts/daily-dsa-maximum-weight-independent-set-on-a-tree-2026-11-06-cover.png
cover_caption: ''
---

{% raw %}
# Problem Statement

Given a tree with $N$ nodes rooted at node 1, where each node has a certain weight, find the **Maximum Weight Independent Set** (MWIS).

An independent set is a subset of nodes such that no two nodes in the subset are adjacent (i.e., no edge connects any two nodes in the set). The weight of an independent set is the sum of the weights of its constituent nodes.

# Examples

**Example 1:**
```
Input: N = 5, weights = [0, 3, 2, 1, 4, 5], edges = [[1, 2], [1, 3], [2, 4], [2, 5]]
Tree structure:
        1 (3)
       / \
     (2)  (3)
     2     3
    / \
  (4)  (5)
  4     5

Output: 9
Explanation: We can choose nodes 1, 4, and 5. Their weights are 3 + 4 + 5 = 12? Wait, let's trace properly.
Let's use weights: Node 1: 3, Node 2: 2, Node 3: 1, Node 4: 4, Node 5: 5.
Edges: (1-2), (1-3), (2-4), (2-5).
If we pick {1, 4, 5}, node 1 and 2 are connected, but 1 and 4 are not directly connected. However, node 2 is adjacent to 4 and 5. Since we picked 4 and 5, we didn't pick 2. Node 1 is adjacent to 2 and 3. Since we picked 1, we didn't pick 2 or 3. 
Wait, is {1, 4, 5} independent? Node 1 is connected to 2, 4 is connected to 2. No direct edge between 1 and 4. But let's check path: 1-2-4. So 1 and 4 are not adjacent. 1 and 5 are not adjacent. 4 and 5 are adjacent! Edge (2, 4) and (2, 5) means 4 and 5 have parent 2, but are 4 and 5 connected? No, 4 and 5 are siblings. Wait! Edges are [[1, 2], [1, 3], [2, 4], [2, 5]]. So children of 2 are 4 and 5. They are not connected directly. Thus {1, 4, 5} is independent! Weight = 3 (node 1) + 4 (node 4) + 5 (node 5) = 12.
```

**Example 2:**
```
Input: N = 2, weights = [0, 10, 20], edges = [[1, 2]]
Output: 20
Explanation: Pick node 2 with weight 20 (cannot pick both 1 and 2).
```

# Constraints
- $1 \le N \le 10^5$
- $0 \le \text{weight of node} \le 10^4$
- The given graph is guaranteed to be a valid tree.

# Approach / Hint

1. This is a classic Tree DP problem.
2. For each node $u$, we can define two states:
   - `dp[u][0]`: Maximum weight independent set of the subtree rooted at $u$, **excluding** node $u$.
   - `dp[u][1]`: Maximum weight independent set of the subtree rooted at $u$, **including** node $u$.
3. Transitions:
   - If we exclude $u$ (`dp[u][0]`), for each child $v$ of $u$, we can either include or exclude $v$. Thus, `dp[u][0] += sum(max(dp[v][0], dp[v][1]))` for all children $v$.
   - If we include $u$ (`dp[u][1]`), we must exclude all its children $v$. Thus, `dp[u][1] = weight[u] + sum(dp[v][0])` for all children $v$.
4. Perform a post-order traversal (DFS) to compute these values, and the answer will be $\max(\text{dp}[1][0], \text{dp}[1][1])$.

# C++ Solution

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

const int MAXN = 100005;
vector<int> adj[MAXN];
int w[MAXN];
long long dp[MAXN][2];

void dfs(int u, int p) {
    dp[u][0] = 0;
    dp[u][1] = w[u];
    
    for (int v : adj[u]) {
        if (v == p) continue;
        dfs(v, u);
        dp[u][0] += max(dp[v][0], dp[v][1]);
        dp[u][1] += dp[v][0];
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int n;
    if (!(cin >> n)) return 0;
    
    for (int i = 1; i <= n; ++i) {
        cin >> w[i];
    }
    
    for (int i = 0; i < n - 1; ++i) {
        int u, v;
        cin >> u >> v;
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    
    dfs(1, 0);
    
    long long ans = max(dp[1][0], dp[1][1]);
    cout << ans << "\n";
    
    return 0;
}
```

### Complexity Analysis
- **Time Complexity:** $\mathcal{O}(N)$ since we visit each node and edge exactly once during the DFS traversal.
- **Space Complexity:** $\mathcal{O}(N)$ for the adjacency list, recursion stack, and the `dp` table.
{% endraw %}

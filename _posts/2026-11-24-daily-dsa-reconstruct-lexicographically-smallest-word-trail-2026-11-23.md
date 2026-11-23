---
layout: post
title: 'Daily DSA: Reconstruct Lexicographically Smallest Word Trail (Hard)'
date: 2026-11-24 03:35:33 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Reconstruct Lexicographically
  Smallest Word Trail.'
cover_image: /assets/images/posts/daily-dsa-reconstruct-lexicographically-smallest-word-trail-2026-11-23-cover.png
cover_caption: ''
---

{% raw %}
### Problem Description

You are given a list of directed character pairs `pairs`, where `pairs[i] = [from_i, to_i]` represents a directed edge from character `from_i` to character `to_i`. Both characters are lowercase English letters.

You must construct a single string `S` of length `N + 1` (where `N` is the number of pairs) such that every pair `[u, v]` in `pairs` is traversed **exactly once** as a contiguous two-character substring `u` + `v` at some position in `S`.

If there are multiple valid strings `S` that traverse all `N` pairs, return the one that is **lexicographically smallest**.

If it is impossible to traverse all pairs in a single continuous path, return an empty string `""`.

---

### Examples

**Example 1:**
```
Input: pairs = [["b","a"], ["a","c"], ["c","b"], ["b","d"]]
Output: "bacbd"
Explanation:
The 4 contiguous 2-character substrings of "bacbd" are "ba", "ac", "cb", and "bd", which match all the input pairs exactly once.
"bacbd" is the lexicographically smallest among all valid sequences.
```

**Example 2:**
```
Input: pairs = [["a","b"], ["b","c"], ["c","a"]]
Output: "abca"
Explanation:
The sequence forms a cycle "abca" covering "ab", "bc", and "ca".
```

**Example 3:**
```
Input: pairs = [["a","b"], ["c","d"]]
Output: ""
Explanation:
The graph consists of two disconnected components, making it impossible to traverse all pairs in a single continuous trail.
```

---

### Constraints

- `1 <= pairs.length <= 10^5`
- `pairs[i].length == 2`
- `pairs[i][0]` and `pairs[i][1]` are lowercase English letters (`'a'` to `'z'`).

---

### Approach

This problem asks us to find a sequence of nodes (characters) that uses every directed edge exactly once. This is equivalent to finding a **Directed Eulerian Path** (or Eulerian Circuit) in a multigraph.

#### 1. Necessary Conditions for an Eulerian Path:
- **Degree Balance**:
  - At most one node can have $\text{out-degree} - \text{in-degree} = 1$ (the **start node**).
  - At most one node can have $\text{in-degree} - \text{out-degree} = 1$ (the **end node**).
  - All other nodes with edges must have $\text{in-degree} == \text{out-degree}$.
  - If no node has $\text{out-degree} - \text{in-degree} = 1$, any node with $\text{out-degree} > 0$ can serve as the start node. To minimize lexicographically, we choose the smallest character with $\text{out-degree} > 0$.

- **Connectivity**:
  - All edges must belong to a single weakly connected component.

#### 2. Hierholzer's Algorithm:
To find the Eulerian Path and ensure lexicographical minimality:
1. Count in-degrees and out-degrees for all 26 character nodes.
2. Determine the unique start node according to degree balance rules.
3. Sort all adjacency lists in **ascending order** so that lexicographically smaller outgoing edges are prioritized.
4. Perform a post-order Depth-First Search (DFS) using **Hierholzer's algorithm**:
   - As you traverse an edge `u -> v`, remove it from the graph to avoid re-visiting.
   - When a vertex `u` has no more outgoing edges, push `u` to the `path` stack.
5. Reverse the resulting `path` stack.
6. Check if the path length is equal to `N + 1`. If it is, convert the path to a string; otherwise, return `""` (indicating the graph was disconnected).

---

### C++ Source Code

```cpp
#include <vector>
#include <string>
#include <algorithm>
#include <cmath>

using namespace std;

class Solution {
public:
    string reconstructTrail(vector<vector<string>>& pairs) {
        int n = pairs.size();
        vector<vector<int>> adj(26);
        vector<int> in_degree(26, 0);
        vector<int> out_degree(26, 0);
        vector<bool> present(26, false);

        for (const auto& pair : pairs) {
            int u = pair[0][0] - 'a';
            int v = pair[1][0] - 'a';
            adj[u].push_back(v);
            out_degree[u]++;
            in_degree[v]++;
            present[u] = true;
            present[v] = true;
        }

        // Sort outgoing edges in ascending order for lexicographical priority
        for (int i = 0; i < 26; ++i) {
            sort(adj[i].begin(), adj[i].end());
        }

        int start_nodes = 0;
        int end_nodes = 0;
        int start_node = -1;

        for (int i = 0; i < 26; ++i) {
            int diff = out_degree[i] - in_degree[i];
            if (abs(diff) > 1) return ""; // Invalid degree difference
            if (diff == 1) {
                start_nodes++;
                start_node = i;
            } else if (diff == -1) {
                end_nodes++;
            }
        }

        // Check degree constraints for Eulerian Path / Circuit
        if (!((start_nodes == 0 && end_nodes == 0) || (start_nodes == 1 && end_nodes == 1))) {
            return "";
        }

        // If Eulerian Circuit, pick the lexicographically smallest node with out-degree > 0
        if (start_nodes == 0) {
            for (int i = 0; i < 26; ++i) {
                if (out_degree[i] > 0) {
                    start_node = i;
                    break;
                }
            }
        }

        if (start_node == -1) return "";

        vector<int> path;
        vector<int> edge_idx(26, 0); // Pointer to avoid repeatedly erasing elements

        // Hierholzer's Algorithm (Iterative or Recursive DFS)
        auto dfs = [&](auto& self, int u) -> void {
            while (edge_idx[u] < adj[u].size()) {
                int v = adj[u][edge_idx[u]++];
                self(self, v);
            }
            path.push_back(u);
        };

        dfs(dfs, start_node);

        // All N edges must be visited, path must contain N + 1 nodes
        if (path.size() != n + 1) {
            return "";
        }

        reverse(path.begin(), path.end());

        string result = "";
        for (int node : path) {
            result += (char)('a' + node);
        }

        return result;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(N \log (\text{deg}_{max})) = \mathcal{O}(N)$ where $N$ is the number of pairs. Sorting adjacency lists takes $\mathcal{O}(V \cdot K \log K)$ where $V = 26$ and $K \le N$. Traversing each edge takes $\mathcal{O}(N)$ amortized time.
- **Space Complexity:** $\mathcal{O}(N + V) = \mathcal{O}(N)$ to store adjacency lists, degrees, recursion stack, and the final output path.
{% endraw %}

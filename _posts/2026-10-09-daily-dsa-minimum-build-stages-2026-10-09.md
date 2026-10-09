---
layout: post
title: 'Daily DSA: Minimum Build Stages (Medium)'
date: 2026-10-09 22:17:02 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Minimum Build
  Stages.'
cover_image: /assets/images/posts/default-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are an engineer designing an automated build system for a large software project. The project consists of `n` modules, labeled from `0` to `n - 1`. 

Some modules have dependencies: if module `u` must be compiled before module `v`, this is represented as a dependency `[u, v]`. 

Your build system can compile multiple modules simultaneously, provided that all their respective prerequisites have already been completed in previous stages. Each compilation stage takes exactly 1 unit of time. 

Return the **minimum number of stages** required to compile all modules. If it is impossible to complete the project due to circular dependencies, return `-1`.

### Examples

**Example 1:**
**Input:** `n = 3, dependencies = [[0, 1], [1, 2]]`  
**Output:** `3`  
**Explanation:**  
- Stage 1: Compile module 0.  
- Stage 2: Compile module 1 (requires 0).  
- Stage 3: Compile module 2 (requires 1).  

**Example 2:**
**Input:** `n = 4, dependencies = [[0, 2], [1, 2], [2, 3]]`  
**Output:** `3`  
**Explanation:**  
- Stage 1: Compile modules 0 and 1 simultaneously.  
- Stage 2: Compile module 2 (requires 0 and 1).  
- Stage 3: Compile module 3 (requires 2).  

**Example 3:**
**Input:** `n = 2, dependencies = [[0, 1], [1, 0]]`  
**Output:** `-1`  
**Explanation:** Module 0 depends on 1, and 1 depends on 0. This circular dependency makes it impossible to start.

### Constraints

- `1 <= n <= 10^5`
- `0 <= dependencies.length <= 2 * 10^5`
- `dependencies[i].length == 2`
- `0 <= u, v < n`
- `u != v`
- All dependency pairs `[u, v]` are unique.

---

### Approach

The problem asks for the minimum time to complete all tasks where tasks can be done in parallel. This is equivalent to finding the number of levels in a **Topological Sort** or the length of the longest path in a Directed Acyclic Graph (DAG).

1.  **Graph Representation:** Represent the dependencies as an adjacency list where `adj[u]` contains all modules `v` that depend on `u`. Simultaneously, maintain an `inDegree` array where `inDegree[v]` counts how many prerequisites module `v` has.
2.  **Kahn's Algorithm (BFS Variation):** 
    - Initialize a queue with all modules that have an `inDegree` of `0` (modules with no prerequisites).
    - Process the queue level by level (similar to BFS for tree depth).
    - For each level, increment the `stages` counter.
    - For every module processed in the current level, iterate through its neighbors in the adjacency list and decrement their `inDegree`.
    - If a neighbor's `inDegree` reaches `0`, add it to the queue for the next stage.
3.  **Cycle Detection:** Keep track of the total number of modules processed. If the number of processed modules is less than `n` after the queue is empty, a cycle exists, and we return `-1`.

### C++ Solution

```cpp
#include <vector>
#include <queue>
#include <algorithm>

using namespace std;

class Solution {
public:
    int minBuildStages(int n, vector<vector<int>>& dependencies) {
        vector<vector<int>> adj(n);
        vector<int> inDegree(n, 0);
        
        // Build the adjacency list and calculate in-degrees
        for (const auto& dep : dependencies) {
            int u = dep[0];
            int v = dep[1];
            adj[u].push_back(v);
            inDegree[v]++;
        }
        
        // Queue for Kahn's algorithm
        queue<int> q;
        for (int i = 0; i < n; ++i) {
            if (inDegree[i] == 0) {
                q.push(i);
            }
        }
        
        int stages = 0;
        int processedCount = 0;
        
        // Process the graph level by level
        while (!q.empty()) {
            int size = q.size();
            stages++;
            for (int i = 0; i < size; ++i) {
                int curr = q.front();
                q.pop();
                processedCount++;
                
                for (int neighbor : adj[curr]) {
                    inDegree[neighbor]--;
                    if (inDegree[neighbor] == 0) {
                        q.push(neighbor);
                    }
                }
            }
        }
        
        // If we couldn't process all nodes, there is a cycle
        return (processedCount == n) ? stages : -1;
    }
};
```

### Complexity Analysis

- **Time Complexity:** O(V + E), where V is the number of modules (`n`) and E is the number of dependencies. We traverse every node and every edge exactly once.
- **Space Complexity:** O(V + E) to store the adjacency list and the in-degree array.
{% endraw %}

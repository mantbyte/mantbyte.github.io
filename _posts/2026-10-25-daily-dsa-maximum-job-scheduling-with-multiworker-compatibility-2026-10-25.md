---
layout: post
title: 'Daily DSA: Maximum Job Scheduling with Multi-Worker Compatibility (Hard)'
date: 2026-10-25 19:36:17 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Maximum Job Scheduling
  with Multi-Worker Compatibility.'
cover_image: /assets/images/posts/daily-dsa-maximum-job-scheduling-with-multiworker-compatibility-2026-10-25-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are managing a production facility with $N$ workers (indexed $0$ to $N - 1$) and $M$ jobs (indexed $0$ to $M - 1$). Each job requires exactly one worker, and each worker can be assigned to at most one job.

You are given a 2D integer array `compatibility` where `compatibility[i]` is a list of job IDs that worker $i$ is qualified to perform.

Due to scheduling efficiency, your goal is to find the maximum number of jobs that can be simultaneously assigned to qualified workers such that no worker takes more than one job, and no job is assigned to more than one worker.

Return the maximum number of job assignments possible.

---

### Examples

**Example 1:**
```text
Input: N = 4, M = 4, compatibility = [[0, 1], [1, 2], [2, 3], []]
Output: 3
Explanation:
Worker 0 can do Job 0.
Worker 1 can do Job 1.
Worker 2 can do Job 2.
Worker 3 has no compatible jobs.
A total of 3 jobs can be assigned.
```

**Example 2:**
```text
Input: N = 3, M = 3, compatibility = [[0, 1, 2], [0], [0]]
Output: 2
Explanation:
Worker 1 can do Job 0.
Worker 0 can do Job 1 (or Job 2).
Worker 2 can only do Job 0, which is already assigned.
The maximum number of assigned jobs is 2.
```

**Example 3:**
```text
Input: N = 2, M = 2, compatibility = [[], []]
Output: 0
Explanation:
No worker has any compatible jobs, so 0 jobs are assigned.
```

---

### Constraints

- $1 \le N, M \le 5 \times 10^4$
- $0 \le \sum \text{compatibility}[i].\text{length} \le 1.5 \times 10^5$
- $0 \le \text{compatibility}[i][j] < M$
- All job IDs in `compatibility[i]` are distinct.

---

### Approach

This problem can be modeled as finding the **Maximum Bipartite Matching** in a bipartite graph where the left set of vertices represents the workers and the right set of vertices represents the jobs. An edge exists from worker $u$ to job $v$ if worker $u$ is qualified to perform job $v$.

While standard augmenting path algorithms like Kuhn's algorithm run in $O(V \cdot E)$ time—which could TLE under $N, M \le 50,000$ and $E \le 1.5 \times 10^5$—the **Hopcroft-Karp algorithm** achieves this in $O(E \sqrt{V})$ time.

#### Hopcroft-Karp Algorithm
1. **BFS Phase**:
   - Find the shortest augmenting paths from unmatched left vertices to unmatched right vertices.
   - Assign level numbers (`dist`) to vertices on the left partition to construct a layered directed graph of shortest paths.
   - If no unmatched right vertex can be reached, terminate.
2. **DFS Phase**:
   - Find a maximal set of vertex-disjoint shortest augmenting paths using DFS.
   - For each augmenting path found, toggle the matching edges along the path to increase the matching size.
3. Repeat the BFS and DFS phases until no augmenting paths exist.

---

### C++ Source Code

```cpp
#include <vector>
#include <queue>

class Solution {
    static const int INF = 1e9;
    int n, m;
    std::vector<std::vector<int>> adj;
    std::vector<int> matchL, matchR, dist;

    bool bfs() {
        std::queue<int> q;
        for (int u = 0; u < n; ++u) {
            if (matchL[u] == -1) {
                dist[u] = 0;
                q.push(u);
            } else {
                dist[u] = INF;
            }
        }

        bool foundAugmentingPath = false;
        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (int v : adj[u]) {
                int nextU = matchR[v];
                if (nextU == -1) {
                    foundAugmentingPath = true;
                } else if (dist[nextU] == INF) {
                    dist[nextU] = dist[u] + 1;
                    q.push(nextU);
                }
            }
        }
        return foundAugmentingPath;
    }

    bool dfs(int u) {
        for (int v : adj[u]) {
            int nextU = matchR[v];
            if (nextU == -1 || (dist[nextU] == dist[u] + 1 && dfs(nextU))) {
                matchL[u] = v;
                matchR[v] = u;
                return true;
            }
        }
        dist[u] = INF; // Prune visited dead-ends
        return false;
    }

public:
    int maximumJobAssignments(int N, int M, const std::vector<std::vector<int>>& compatibility) {
        n = N;
        m = M;
        adj = compatibility;

        matchL.assign(n, -1);
        matchR.assign(m, -1);
        dist.assign(n, INF);

        int maxMatching = 0;
        while (bfs()) {
            for (int u = 0; u < n; ++u) {
                if (matchL[u] == -1 && dfs(u)) {
                    maxMatching++;
                }
            }
        }

        return maxMatching;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $O(E \sqrt{V})$ where $V = N + M$ and $E = \sum \text{compatibility}[i].\text{length}$. In each phase, the length of the shortest augmenting path strictly increases, guaranteeing at most $O(\sqrt{V})$ iterations of BFS/DFS. Each iteration processes edges in $O(E)$.
- **Space Complexity:** $O(V + E)$ to store the bipartite graph representation, matching tables, and queue/distance structures.
{% endraw %}

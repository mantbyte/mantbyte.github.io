---
layout: post
title: 'Daily DSA: Strategic Hub Selection (Medium)'
date: 2026-08-22 15:49:12 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Strategic Hub
  Selection.'
cover_image: /assets/images/posts/daily-dsa-strategic-hub-selection-2026-08-22-cover.png
cover_caption: ''
---

### Problem Statement

A logistics company is looking to establish a strategic headquarters in one of $n$ cities. The cities are connected by $m$ bidirectional roads, each with a specific travel time (weight). 

To ensure efficiency, the company defines an **inconvenience score** for each city. The inconvenience score of city $i$ is the **maximum shortest-path distance** from city $i$ to any other city that is reachable within a given `distanceThreshold`. If a city cannot reach any other city within the threshold, its inconvenience score is $0$.

Your task is to find the city with the **minimum inconvenience score**. If there are multiple cities with the same minimum score, return the city with the **smallest index**.

### Examples

**Example 1:**
**Input:** `n = 3`, `edges = [[0,1,10],[1,2,5]]`, `distanceThreshold = 15`
**Output:** `1`
**Explanation:**
- Shortest paths from City 0: to City 1 is 10, to City 2 is 15. All are $\le 15$. Max distance = 15.
- Shortest paths from City 1: to City 0 is 10, to City 2 is 5. All are $\le 15$. Max distance = 10.
- Shortest paths from City 2: to City 1 is 5, to City 0 is 15. All are $\le 15$. Max distance = 15.
The minimum inconvenience score is 10, which belongs to City 1.

**Example 2:**
**Input:** `n = 3`, `edges = [[0,1,10],[1,2,5]]`, `distanceThreshold = 12`
**Output:** `2`
**Explanation:**
- Shortest paths from City 0: to City 1 is 10. City 2 is unreachable within the threshold (15 > 12). Max distance = 10.
- Shortest paths from City 1: to City 0 is 10, to City 2 is 5. Max distance = 10.
- Shortest paths from City 2: to City 1 is 5. City 0 is unreachable within the threshold. Max distance = 5.
The minimum inconvenience score is 5, which belongs to City 2.

### Constraints

- $2 \le n \le 200$
- $1 \le edges.length \le n \times (n - 1) / 2$
- `edges[i] = [u, v, weight]`
- $0 \le u, v < n$
- $1 \le weight, distanceThreshold \le 10^6$
- The graph may not be fully connected.

### Approach

1.  **All-Pairs Shortest Path:** Since we need the shortest path from every city to every other city and $n$ is small ($n \le 200$), the **Floyd-Warshall algorithm** is ideal. It computes all-pairs shortest paths in $O(n^3)$ time.
2.  **Distance Matrix Initialization:** Initialize a 2D array `dist` where `dist[i][j]` is the weight of the edge between $i$ and $j$, or infinity if no edge exists. Set `dist[i][i] = 0`.
3.  **Dynamic Programming (Floyd-Warshall):** Iterate through all possible intermediate nodes $k$, and for every pair of nodes $(i, j)$, update `dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])`.
4.  **Score Calculation:** For each city $i$, iterate through all other cities $j$. If `dist[i][j]` is less than or equal to the `distanceThreshold`, update the city's `currentMax` distance.
5.  **Result Selection:** Keep track of the minimum `currentMax` found across all cities and the corresponding index. Since we iterate from index $0$ to $n-1$, we naturally pick the smallest index in case of ties.

### Complexity Analysis

- **Time Complexity:** $O(n^3)$ due to the triple nested loops in the Floyd-Warshall algorithm. With $n=200$, $n^3 = 8 \times 10^6$, which comfortably fits within a 1-second time limit.
- **Space Complexity:** $O(n^2)$ to store the distance matrix.

### C++ Solution

```cpp
#include <vector>
#include <algorithm>

using namespace std;

class Solution {
public:
    int findBestCity(int n, vector<vector<int>>& edges, int distanceThreshold) {
        const int INF = 1e9; // Sufficiently large value to represent infinity
        vector<vector<int>> dist(n, vector<int>(n, INF));

        // Initialize distances based on edges
        for (int i = 0; i < n; ++i) {
            dist[i][i] = 0;
        }
        for (const auto& edge : edges) {
            int u = edge[0], v = edge[1], w = edge[2];
            dist[u][v] = min(dist[u][v], w);
            dist[v][u] = min(dist[v][u], w);
        }

        // Floyd-Warshall Algorithm
        for (int k = 0; k < n; ++k) {
            for (int i = 0; i < n; ++i) {
                for (int j = 0; j < n; ++j) {
                    if (dist[i][k] != INF && dist[k][j] != INF) {
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
                    }
                }
            }
        }

        int minInconvenience = INF;
        int bestCity = 0;

        // Calculate inconvenience score for each city
        for (int i = 0; i < n; ++i) {
            int currentMax = 0;
            for (int j = 0; j < n; ++j) {
                if (i != j && dist[i][j] <= distanceThreshold) {
                    currentMax = max(currentMax, dist[i][j]);
                }
            }

            // Update result if we find a smaller score
            if (currentMax < minInconvenience) {
                minInconvenience = currentMax;
                bestCity = i;
            }
        }

        return bestCity;
    }
};
```

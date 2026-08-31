---
layout: post
title: 'Daily DSA: Currency Arbitrage Detection (Medium)'
date: 2026-08-31 22:52:45 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Currency Arbitrage
  Detection.'
cover_image: /assets/images/posts/daily-dsa-currency-arbitrage-detection-2026-08-31-cover.png
cover_caption: ''
---

### Problem Statement

In the world of finance, **arbitrage** is the practice of taking advantage of a price difference between two or more markets. In the context of currency exchange, an arbitrage opportunity exists if there is a sequence of currency exchanges that starts and ends with the same currency, resulting in a net gain (i.e., you end up with more money than you started with).

You are given an integer `n`, representing the number of different currencies (labeled from `0` to `n-1`). You are also given a 2D array `exchanges`, where each `exchanges[i] = [u, v, rate]` indicates that you can exchange 1 unit of currency `u` for `rate` units of currency `v`.

Return `true` if an arbitrage opportunity exists, and `false` otherwise.

### Examples

**Example 1:**
**Input:** `n = 3`, `exchanges = [[0, 1, 0.9], [1, 2, 0.8], [2, 0, 1.5]]`  
**Output:** `true`  
**Explanation:** If you start with 1 unit of currency 0:  
1. Exchange 0 for 1: $1 \times 0.9 = 0.9$ units of currency 1.  
2. Exchange 1 for 2: $0.9 \times 0.8 = 0.72$ units of currency 2.  
3. Exchange 2 for 0: $0.72 \times 1.5 = 1.08$ units of currency 0.  
Since $1.08 > 1.0$, an arbitrage opportunity exists.

**Example 2:**
**Input:** `n = 3`, `exchanges = [[0, 1, 0.5], [1, 2, 0.5], [2, 0, 2.0]]`  
**Output:** `false`  
**Explanation:** $0.5 \times 0.5 \times 2.0 = 0.5$. Since $0.5 < 1.0$, there is no profit cycle.

### Constraints

*   `2 <= n <= 100`
*   `1 <= exchanges.length <= 2000`
*   `exchanges[i] = [u, v, rate]`
*   `0 <= u, v < n`, `u != v`
*   `0.0001 <= rate <= 1000.0`

---

### Approach

An arbitrage opportunity exists if there is a cycle of currencies $c_1, c_2, \dots, c_k$ such that:
$$R_{12} \times R_{23} \times \dots \times R_{k1} > 1$$

Multiplying rates is difficult to handle with standard shortest-path algorithms. However, we can transform this product into a sum using logarithms:
$$\ln(R_{12} \times R_{23} \times \dots \times R_{k1}) > \ln(1)$$
$$\ln(R_{12}) + \ln(R_{23}) + \dots + \ln(R_{k1}) > 0$$

To find a cycle with a sum greater than 0, we can negate the values and look for a **negative cycle**:
$$(-\ln(R_{12})) + (-\ln(R_{23})) + \dots + (-\ln(R_{k1})) < 0$$

#### Algorithm:
1.  **Graph Construction**: Create a directed graph where each edge $(u, v)$ has a weight $w = -\ln(rate)$.
2.  **Negative Cycle Detection**: Use the **Bellman-Ford algorithm** to detect if a negative cycle exists.
3.  **Initialization**: Since we want to detect a cycle anywhere in the graph (not necessarily reachable from a specific source), we initialize all distances `dist[i] = 0`.
4.  **Relaxation**: Relax all edges $n-1$ times. On the $n$-th iteration, if any edge can still be relaxed (i.e., `dist[v] > dist[u] + weight`), then a negative cycle exists.

### Complexity
*   **Time Complexity**: $O(V \cdot E)$, where $V$ is the number of currencies and $E$ is the number of exchange rates. This is efficient for $V=100$ and $E=2000$.
*   **Space Complexity**: $O(V)$ to store the distances.

---

### C++ Solution

```cpp
#include <vector>
#include <cmath>
#include <iostream>

using namespace std;

class Solution {
public:
    bool isArbitragePossible(int n, vector<vector<double>>& exchanges) {
        // dist[i] represents the minimum path cost to currency i.
        // Initializing with 0 allows us to detect cycles regardless of source.
        vector<double> dist(n, 0.0);
        const double EPS = 1e-10;

        // Relax edges n-1 times
        for (int i = 0; i < n - 1; ++i) {
            bool any_change = false;
            for (const auto& edge : exchanges) {
                int u = (int)edge[0];
                int v = (int)edge[1];
                double rate = edge[2];
                double weight = -log(rate);

                if (dist[v] > dist[u] + weight + EPS) {
                    dist[v] = dist[u] + weight;
                    any_change = true;
                }
            }
            // If no distance changed during an entire pass, no negative cycle exists
            if (!any_change) return false;
        }

        // Perform the n-th pass to detect negative cycles
        for (const auto& edge : exchanges) {
            int u = (int)edge[0];
            int v = (int)edge[1];
            double rate = edge[2];
            double weight = -log(rate);

            if (dist[v] > dist[u] + weight + EPS) {
                return true; // Negative cycle found -> Arbitrage exists
            }
        }

        return false;
    }
};
```

---
layout: post
title: 'Daily DSA: Currency Arbitrage Detection (Medium)'
date: 2026-11-05 23:19:35 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Currency Arbitrage
  Detection.'
cover_image: /assets/images/posts/daily-dsa-currency-arbitrage-detection-2026-11-05-cover.png
cover_caption: ''
---

{% raw %}
### Problem Description

You are given a list of $n$ currencies (labeled from $0$ to $n-1$) and $m$ exchange rates. Each exchange rate is represented as a triplet `[u, v, rate]`, meaning that 1 unit of currency `u` can be converted into `rate` units of currency `v`.

Your task is to determine if there exists a sequence of exchanges that starts with some currency $i$ and ends back at currency $i$ such that the final amount is strictly greater than the starting amount (i.e., you have made a profit).

### Examples

**Example 1:**
**Input:** `n = 3`, `rates = [[0, 1, 0.5], [1, 2, 4.0], [2, 0, 0.6]]`
**Output:** `true`
**Explanation:** 
Starting with 1 unit of currency 0:
1. Exchange 0 to 1: $1 \times 0.5 = 0.5$
2. Exchange 1 to 2: $0.5 \times 4.0 = 2.0$
3. Exchange 2 to 0: $2.0 \times 0.6 = 1.2$
Since $1.2 > 1.0$, an arbitrage opportunity exists.

**Example 2:**
**Input:** `n = 2`, `rates = [[0, 1, 2.0], [1, 0, 0.4]]`
**Output:** `false`
**Explanation:** 
Starting with 1 unit of currency 0:
1. Exchange 0 to 1: $1 \times 2.0 = 2.0$
2. Exchange 1 to 0: $2.0 \times 0.4 = 0.8$
Since $0.8 \le 1.0$, no profit is made in this cycle.

### Constraints

* $2 \le n \le 100$
* $1 \le m \le n \times (n-1)$
* $0.001 \le rate \le 1000.0$
* There are no self-loops (exchange from $u$ to $u$).

### Approach

An arbitrage opportunity exists if there is a cycle of currencies $c_1, c_2, \dots, c_k$ such that:
$rate(c_1, c_2) \times rate(c_2, c_3) \times \dots \times rate(c_k, c_1) > 1$

To solve this using standard shortest-path algorithms, we can transform the multiplication into addition using logarithms. 
Taking the negative logarithm of both sides:
$-\log(rate_1 \times rate_2 \times \dots \times rate_k) < -\log(1)$
$-(\log(rate_1) + \log(rate_2) + \dots + \log(rate_k)) < 0$
$\sum (-\log(rate_i)) < 0$

This transforms the problem into finding a **negative cycle** in a directed graph where the weight of an edge $(u, v)$ is $-\log(rate(u, v))$. 

We can use the **Bellman-Ford algorithm**:
1. Initialize distances from a source to all vertices as infinity, and source distance as 0.
2. Since the graph might not be fully connected, we can either use a dummy source connected to all nodes or simply initialize all distances to 0 and run the relaxation $n-1$ times.
3. On the $n$-th iteration, if any edge can still be relaxed ($dist[v] > dist[u] + weight$), then a negative cycle exists.

### C++ Solution

```cpp
#include <vector>
#include <cmath>
#include <iostream>

using namespace std;

class Solution {
public:
    bool isArbitragePossible(int n, vector<vector<double>>& rates) {
        // dist[i] represents the shortest path from an implicit source to node i
        // Initialize with 0 to handle disconnected components simultaneously
        vector<double> dist(n, 0.0);

        // Relax all edges n-1 times
        for (int i = 0; i < n - 1; ++i) {
            bool relaxed = false;
            for (const auto& edge : rates) {
                int u = (int)edge[0];
                int v = (int)edge[1];
                double weight = -log(edge[2]);
                
                if (dist[u] + weight < dist[v]) {
                    dist[v] = dist[u] + weight;
                    relaxed = true;
                }
            }
            // If no edge was relaxed in an iteration, no negative cycle exists
            if (!relaxed) return false;
        }

        // n-th iteration to detect negative cycle
        for (const auto& edge : rates) {
            int u = (int)edge[0];
            int v = (int)edge[1];
            double weight = -log(edge[2]);
            
            // If we can still relax, a negative cycle (arbitrage) is present
            if (dist[u] + weight < dist[v] - 1e-9) {
                return true;
            }
        }

        return false;
    }
};
```

### Complexity Analysis

* **Time Complexity:** $O(V \times E)$, where $V$ is the number of currencies ($n$) and $E$ is the number of exchange rates ($m$). In the worst case, $E = O(V^2)$, making it $O(V^3)$.
* **Space Complexity:** $O(V)$ to store the distance array.
{% endraw %}

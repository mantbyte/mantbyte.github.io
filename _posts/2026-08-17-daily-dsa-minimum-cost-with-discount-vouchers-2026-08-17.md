---
layout: post
title: 'Daily DSA: Minimum Cost with Discount Vouchers (Medium)'
date: 2026-08-17 15:56:39 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Minimum Cost
  with Discount Vouchers.'
cover_image: /assets/images/posts/daily-dsa-minimum-cost-with-discount-vouchers-2026-08-17-cover.png
cover_caption: ''
---

### Problem Description

You are given an integer `n` representing the number of cities numbered from `0` to `n - 1`, and a 2D integer array `flights` where `flights[i] = [u_i, v_i, cost_i]` indicates a directed flight from city `u_i` to city `v_i` with a specific `cost_i`.

You are also given two integers `src` and `dst`, representing the starting and destination cities, and an integer `k`, representing the maximum number of discount vouchers you have. Each voucher allows you to take any single flight at half price, rounded down (i.e., `cost // 2`). You can use at most one voucher per flight leg, and you can use at most `k` vouchers during the entire journey.

Return *the minimum total cost to travel from* `src` *to* `dst`. If it is impossible to reach `dst` from `src`, return `-1`.

---

### Examples

**Example 1:**
```
Input: n = 4, flights = [[0,1,100],[1,2,100],[2,3,100],[0,2,500]], src = 0, dst = 3, k = 1
Output: 250
Explanation:
The optimal route is 0 -> 1 -> 2 -> 3 with costs 100, 100, 100.
Apply the voucher on leg 0 -> 1 (cost becomes 50), total cost = 50 + 100 + 100 = 250.
Alternatively, applying it to any of the 100-cost legs gives 250.
```

**Example 2:**
```
Input: n = 3, flights = [[0,1,10],[1,2,20],[0,2,100]], src = 0, dst = 2, k = 2
Output: 15
Explanation:
Take route 0 -> 1 -> 2. Apply vouchers to both legs:
- 0 -> 1: cost 10 // 2 = 5
- 1 -> 2: cost 20 // 2 = 10
Total cost = 5 + 10 = 15.
```

**Example 3:**
```
Input: n = 3, flights = [[0,1,10]], src = 0, dst = 2, k = 1
Output: -1
Explanation:
There is no path from city 0 to city 2.
```

---

### Constraints

- `1 <= n <= 10^4`
- `0 <= flights.length <= 5 * 10^4`
- `flights[i].length == 3`
- `0 <= u_i, v_i < n`
- `u_i != v_i`
- `1 <= cost_i <= 10^5`
- `0 <= src, dst < n`
- `0 <= k <= 10`

---

### Approach

This problem can be modeled as finding the shortest path on a **layered graph (state-space graph)** using Dijkstra's Algorithm.

1. **State Representation:**
   - Each state can be defined as `(cost, u, used_vouchers)`, where:
     - `cost`: Total cost accumulated so far.
     - `u`: Current city.
     - `used_vouchers`: Number of discount vouchers used so far (`0 <= used_vouchers <= k`).

2. **Transitions from state `(u, used)`:**
   - For every outgoing flight `(u -> v, price)`:
     - **Without using a voucher:** Move to `(v, used)` with cost `current_cost + price`.
     - **Using a voucher (if `used < k`):** Move to `(v, used + 1)` with cost `current_cost + (price / 2)`.

3. **Data Structures:**
   - A 2D distance array `dist[u][used]` initialized to infinity, storing the minimal cost to reach city `u` with `used` vouchers.
   - A min-heap (priority queue) storing tuples of `(cost, u, used)` ordered by `cost`.

4. **Termination:**
   - The first time we pop destination city `dst` from the priority queue, the associated cost is guaranteed to be minimal.
   - If the queue becomes empty and `dst` was never reached, return `-1`.

---

### C++ Solution

```cpp
#include <vector>
#include <queue>
#include <tuple>

using namespace std;

class Solution {
public:
    int minimumCostWithVouchers(int n, vector<vector<int>>& flights, int src, int dst, int k) {
        // Build adjacency list: u -> vector of {v, cost}
        vector<vector<pair<int, int>>> adj(n);
        for (const auto& flight : flights) {
            adj[flight[0]].emplace_back(flight[1], flight[2]);
        }

        // dist[city][vouchers_used]
        const long long INF = 1e18;
        vector<vector<long long>> dist(n, vector<long long>(k + 1, INF));

        // Min-heap storing {cost, u, vouchers_used}
        priority_queue<tuple<long long, int, int>, 
                       vector<tuple<long long, int, int>>, 
                       greater<tuple<long long, int, int>>> pq;

        dist[src][0] = 0;
        pq.emplace(0, src, 0);

        while (!pq.empty()) {
            auto [d, u, used] = pq.top();
            pq.pop();

            if (u == dst) return d;
            if (d > dist[u][used]) continue;

            for (const auto& [v, cost] : adj[u]) {
                // Option 1: Do not use a voucher
                if (d + cost < dist[v][used]) {
                    dist[v][used] = d + cost;
                    pq.emplace(dist[v][used], v, used);
                }

                // Option 2: Use a voucher (if available)
                if (used < k) {
                    int discounted_cost = cost / 2;
                    if (d + discounted_cost < dist[v][used + 1]) {
                        dist[v][used + 1] = d + discounted_cost;
                        pq.emplace(dist[v][used + 1], v, used + 1);
                    }
                }
            }
        }

        return -1;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}((N \cdot K + M \cdot K) \log(N \cdot K))$, where $N$ is the number of cities, $M$ is the number of flights, and $K$ is the maximum number of vouchers.
- **Space Complexity:** $\mathcal{O}(N \cdot K + M)$ to store the distance table, graph adjacency list, and priority queue.

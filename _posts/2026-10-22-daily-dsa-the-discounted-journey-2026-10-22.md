---
layout: post
title: 'Daily DSA: The Discounted Journey (Hard)'
date: 2026-10-22 20:20:30 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: The Discounted
  Journey.'
cover_image: /assets/images/posts/daily-dsa-the-discounted-journey-2026-10-22-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are a traveler in a country with $N$ cities, numbered from 1 to $N$. There are $M$ directed flights connecting these cities, each with a specific cost. 

You have been given $K$ discount coupons. Each coupon allows you to reduce the cost of a single flight to half its original value (using integer division, i.e., $\lfloor \text{cost} / 2 \rfloor$). You can use at most one coupon per flight, and you can use a maximum of $K$ coupons during your entire journey.

Your task is to find the minimum total cost to travel from city 1 to city $N$. If it is impossible to reach city $N$, return -1.

### Examples

**Example 1:**
**Input:** 
$N = 3, M = 2, K = 1$
Flights: `[[1, 2, 10], [2, 3, 10]]` 
**Output:** `15` 
**Explanation:** 
You can travel $1 \to 2 \to 3$. 
- Use a coupon on the first flight: $\lfloor 10/2 \rfloor + 10 = 5 + 10 = 15$.
- Or use a coupon on the second flight: $10 + \lfloor 10/2 \rfloor = 10 + 5 = 15$.
The minimum cost is 15.

**Example 2:**
**Input:** 
$N = 3, M = 2, K = 2$
Flights: `[[1, 2, 10], [2, 3, 10]]` 
**Output:** `10` 
**Explanation:** 
You can use coupons on both flights: $\lfloor 10/2 \rfloor + \lfloor 10/2 \rfloor = 5 + 5 = 10$.

**Example 3:**
**Input:** 
$N = 3, M = 1, K = 1$
Flights: `[[1, 2, 10]]` 
**Output:** `-1` 
**Explanation:** 
City 3 cannot be reached from city 1.

### Constraints

- $2 \le N \le 10^5$
- $1 \le M \le 2 \cdot 10^5$
- $0 \le K \le 10$
- $1 \le u, v \le N$
- $1 \le \text{cost} \le 10^9$

### Approach

This problem can be modeled as finding the shortest path in an **augmented state-space graph**. A simple Dijkstra algorithm finds the shortest path based on nodes alone, but here, our "state" depends on two factors:
1. The current city $u$.
2. The number of coupons $k$ already used.

We define `dist[u][k]` as the minimum cost to reach city $u$ using exactly $k$ coupons. 

**Transitions:**
For each directed flight from $u$ to $v$ with cost $w$:
1. **Without using a coupon:** Transition from $(u, k)$ to $(v, k)$ with weight $w$.
   `dist[v][k] = min(dist[v][k], dist[u][k] + w)`
2. **Using a coupon (if $k < K$):** Transition from $(u, k)$ to $(v, k+1)$ with weight $\lfloor w/2 \rfloor$.
   `dist[v][k+1] = min(dist[v][k+1], dist[u][k] + floor(w/2))`

Since all edge weights are non-negative, we use Dijkstra's algorithm with a priority queue to explore these states. The priority queue will store tuples of `(cost, u, k)`, and we always expand the state with the minimum cost first.

### Complexity Analysis

- **Time Complexity:** $O(K \cdot M \log(K \cdot N))$. There are $N \times (K+1)$ states and each of the $M$ edges can result in two transitions (using or not using a coupon) for each level of $K$.
- **Space Complexity:** $O(N \cdot K + M)$ to store the distance array and the adjacency list.

### C++ Solution

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>

using namespace std;

const long long INF = 1e18;

struct State {
    int u, k;
    long long d;

    // Min-priority queue based on distance
    bool operator>(const State& other) const {
        return d > other.d;
    }
};

struct Edge {
    int to;
    int weight;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m, k_limit;
    if (!(cin >> n >> m >> k_limit)) return 0;

    vector<vector<Edge>> adj(n + 1);
    for (int i = 0; i < m; ++i) {
        int u, v, w;
        cin >> u >> v >> w;
        adj[u].push_back({v, w});
    }

    // dist[node][coupons_used]
    vector<vector<long long>> dist(n + 1, vector<long long>(k_limit + 1, INF));
    priority_queue<State, vector<State>, greater<State>> pq;

    // Starting point: City 1, 0 coupons used, 0 cost
    dist[1][0] = 0;
    pq.push({1, 0, 0});

    while (!pq.empty()) {
        State curr = pq.top();
        pq.pop();

        if (curr.d > dist[curr.u][curr.k]) continue;

        for (const auto& edge : adj[curr.u]) {
            // Option 1: Move to next city without using a coupon
            if (dist[edge.to][curr.k] > curr.d + edge.weight) {
                dist[edge.to][curr.k] = curr.d + edge.weight;
                pq.push({edge.to, curr.k, dist[edge.to][curr.k]});
            }

            // Option 2: Move to next city using a coupon
            if (curr.k < k_limit) {
                long long discounted_w = edge.weight / 2;
                if (dist[edge.to][curr.k + 1] > curr.d + discounted_w) {
                    dist[edge.to][curr.k + 1] = curr.d + discounted_w;
                    pq.push({edge.to, curr.k + 1, dist[edge.to][curr.k + 1]});
                }
            }
        }
    }

    long long min_total_cost = INF;
    for (int i = 0; i <= k_limit; ++i) {
        min_total_cost = min(min_total_cost, dist[n][i]);
    }

    if (min_total_cost == INF) {
        cout << -1 << endl;
    } else {
        cout << min_total_cost << endl;
    }

    return 0;
}
```
{% endraw %}

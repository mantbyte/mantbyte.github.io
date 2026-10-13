---
layout: post
title: 'Daily DSA: Project Deadline Management (Medium)'
date: 2026-10-13 22:48:56 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Project Deadline
  Management.'
cover_image: /assets/images/posts/daily-dsa-project-deadline-management-2026-10-13-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are a project manager with $N$ potential projects. Each project $i$ is characterized by two integers: a deadline $d_i$ and a profit $p_i$. 

- Each project takes exactly **1 unit of time** to complete.
- For a project to yield profit, it must be completed by its deadline. Specifically, if a project has a deadline $d_i$, it must be finished at or before time $d_i$. 
- Time starts at $T = 0$. This means a project with deadline $d=1$ can be completed in the time slot $[0, 1)$. A project with deadline $d=2$ can be completed in either $[0, 1)$ or $[1, 2)$.

Your goal is to determine the maximum total profit you can achieve by strategically choosing which projects to complete and in what order.

### Examples

**Example 1:**
**Input:** `projects = [[2, 50], [1, 20], [2, 100], [1, 30]]`  
**Output:** `150`  
**Explanation:** 
- We can perform the project with profit 30 in the slot [0, 1) and the project with profit 100 in the slot [1, 2). Total = 130.
- Alternatively, we can perform the project with profit 50 in the slot [0, 1) and the project with profit 100 in the slot [1, 2). Total = 150. This is the maximum.

**Example 2:**
**Input:** `projects = [[1, 10], [1, 20], [1, 30]]`  
**Output:** `30`  
**Explanation:** All projects have a deadline of 1. You can only complete one project before time $T=1$. You choose the one with the highest profit.

### Constraints

- $1 \le N \le 10^5$
- $1 \le d_i \le 10^9$
- $1 \le p_i \le 10^9$

---

### Approach

Since each project takes 1 unit of time and we want to maximize profit, a greedy approach combined with a priority queue is optimal.

1. **Sort Projects:** First, sort all projects based on their deadlines in ascending order. This allows us to process projects as their time constraints become relevant.
2. **Tentative Selection:** Use a **min-priority queue** (min-heap) to store the profits of the projects we have currently decided to undertake.
3. **Iterate and Adjust:** For each project $(d_i, p_i)$:
   - If the number of projects currently in our min-heap is less than the current project's deadline $d_i$, we have enough time to add this project to our schedule. Push $p_i$ into the heap.
   - If the number of projects in our heap is equal to $d_i$, we cannot simply add another project because we've already filled $d_i$ slots. However, we can replace one of our previously selected projects if the current project's profit $p_i$ is higher than the minimum profit in our heap. If $p_i > heap.top()$, we remove the minimum profit and add $p_i$.
4. **Final Result:** The sum of all profits remaining in the min-heap is our maximum total profit.

### C++ Solution

```cpp
#include <vector>
#include <algorithm>
#include <queue>

class Solution {
public:
    long long maxProfit(std::vector<std::vector<int>>& projects) {
        // Sort projects by deadline
        std::sort(projects.begin(), projects.end(), [](const std::vector<int>& a, const std::vector<int>& b) {
            return a[0] < b[0];
        });

        // Min-heap to keep track of the profits of selected projects
        std::priority_queue<int, std::vector<int>, std::greater<int>> pq;

        for (const auto& project : projects) {
            int deadline = project[0];
            int profit = project[1];

            if (pq.size() < (size_t)deadline) {
                // We have a free slot before or at this deadline
                pq.push(profit);
            } else if (!pq.empty() && profit > pq.top()) {
                // Swap the least profitable project with the current one
                pq.pop();
                pq.push(profit);
            }
        }

        long long totalProfit = 0;
        while (!pq.empty()) {
            totalProfit += pq.top();
            pq.pop();
        }

        return totalProfit;
    }
};
```

### Complexity Analysis

- **Time Complexity:** $O(N \log N)$, where $N$ is the number of projects. Sorting the projects takes $O(N \log N)$, and each of the $N$ projects is pushed/popped from the priority queue at most once, which takes $O(\log N)$ per operation.
- **Space Complexity:** $O(N)$ to store the projects in the priority queue in the worst case (though practically it's limited by the maximum deadline).
{% endraw %}

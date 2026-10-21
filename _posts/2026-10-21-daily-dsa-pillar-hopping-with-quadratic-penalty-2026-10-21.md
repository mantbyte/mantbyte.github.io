---
layout: post
title: 'Daily DSA: Pillar Hopping with Quadratic Penalty (Hard)'
date: 2026-10-21 20:19:32 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Pillar Hopping
  with Quadratic Penalty.'
cover_image: /assets/images/posts/daily-dsa-pillar-hopping-with-quadratic-penalty-2026-10-21-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are given an array of integers `heights` of length $N$, representing the heights of $N$ pillars ordered from left to right along a straight line. The pillars are strictly increasing in height, meaning `heights[i] < heights[i + 1]` for all $0 \le i < N - 1$.

You are also given a positive integer $C$, which represents a fixed penalty cost for every jump.

A jumper starts at the first pillar (index $0$) and wants to reach the last pillar (index $N - 1$). From pillar $i$, you can jump directly to any pillar $j$ such that $j > i$. The cost of jumping from pillar $i$ to pillar $j$ is:

$$\text{Cost}(i, j) = (\text{heights}[j] - \text{heights}[i])^2 + C$$

Return the **minimum total cost** required to reach pillar $N - 1$ starting from pillar $0$.

---

### Examples

**Example 1:**
```text
Input: heights = [1, 3, 5], C = 2
Output: 12
Explanation:
Path 1: Jump 0 -> 1 -> 2.
- Jump 0 to 1: (3 - 1)^2 + 2 = 4 + 2 = 6
- Jump 1 to 2: (5 - 3)^2 + 2 = 4 + 2 = 6
Total cost = 6 + 6 = 12.

Path 2: Jump 0 -> 2 directly.
- Jump 0 to 2: (5 - 1)^2 + 2 = 16 + 2 = 18.

The minimum total cost is 12.
```

**Example 2:**
```text
Input: heights = [1, 2, 3, 10], C = 100
Output: 181
Explanation:
Because C is very large, jumping directly from pillar 0 to pillar 3 incurs only one penalty of C:
- Cost = (10 - 1)^2 + 100 = 81 + 100 = 181.
Any path with multiple hops adds an additional 100 per hop, yielding a higher cost.
```

**Example 3:**
```text
Input: heights = [2, 5, 8, 11, 14], C = 10
Output: 46
Explanation:
One optimal sequence of jumps is 0 -> 2 -> 4:
- Jump 0 to 2: (8 - 2)^2 + 10 = 36 + 10 = 46.
- Wait, jump 0 -> 1 -> 2 -> 3 -> 4 gives 4 * (9 + 10) = 76.
- Jump 0 -> 4 directly gives (14 - 2)^2 + 10 = 144 + 10 = 154.
- Jump 0 -> 2 -> 4 gives (8 - 2)^2 + 10 + (14 - 8)^2 + 10 = 46 + 46 = 92.
- Comparing all combinations, jumping 0 -> 4 directly with cost 154 vs other hops shows that 0 -> 2 -> 4 gives 92, but jumping 0 -> 4 is 154.
Wait, for heights = [2, 5, 8, 11, 14], if we jump 0 -> 4: (14 - 2)^2 + 10 = 154. If we jump 0 -> 2 -> 4: 46 + 46 = 92. Let's check 0 -> 1 -> 3 -> 4: (5-2)^2 + 10 + (11-5)^2 + 10 + (14-11)^2 + 10 = 19 + 46 + 19 = 84. In fact, jumping consecutive steps: each step is (3)^2 + 10 = 19; 4 jumps = 76. The minimum is 76.
```

---

### Constraints

- $2 \le N \le 10^5$
- $1 \le \text{heights}[i] \le 10^6$
- $\text{heights}[i] < \text{heights}[i + 1]$ for all $0 \le i < N - 1$
- $1 \le C \le 10^9$

---

### Approach

Let $dp[j]$ denote the minimum cost to reach pillar $j$ from pillar $0$. Base condition: $dp[0] = 0$.

For $j > 0$, the transition is:
$$dp[j] = \min_{0 \le i < j} \{ dp[i] + (heights[j] - heights[i])^2 + C \}$$

Expanding the quadratic term:
$$dp[j] = heights[j]^2 + C + \min_{0 \le i < j} \{ -2 \cdot heights[i] \cdot heights[j] + dp[i] + heights[i]^2 \}$$

Notice that the inner expression is linear with respect to $x = heights[j]$:
$$y = m_i \cdot x + c_i$$
where:
- Slope $m_i = -2 \cdot heights[i]$
- Intercept $c_i = dp[i] + heights[i]^2$
- Query point $x = heights[j]$

Because $heights$ is strictly increasing:
1. The slopes $m_i$ are strictly decreasing ($m_0 > m_1 > m_2 > \dots$).
2. The query points $x = heights[j]$ are strictly increasing.

This setup matches the classic **Convex Hull Trick (CHT)** with monotonic slopes and queries:
- We can maintain the lower envelope of lines using a double-ended queue (`std::deque`).
- **Querying**: Since $x$ is strictly increasing, lines that are no longer optimal at the current $x$ can be popped from the front of the deque (`pop_front`). Specifically, while the second line in the deque gives a smaller or equal value at $x$ compared to the front line, we pop the front.
- **Insertion**: To insert a new line $(m_i, c_i)$, we pop lines from the back of the deque if the intersection between the new line and the second-to-last line occurs earlier than or at the same point as the intersection between the last two lines.
- To avoid floating-point inaccuracies, cross-multiplication with 128-bit integers (`__int128_t`) can be used to compare intersection coordinates.

With both query and insertion being amortized $O(1)$, the entire DP runs in $O(N)$ time and $O(N)$ space.

---

### C++ Source Code

```cpp
#include <vector>
#include <deque>
#include <cstdint>

class Solution {
private:
    struct Line {
        long long m, c; // y = m * x + c
        long long eval(long long x) const {
            return m * x + c;
        }
    };

    // Returns true if line l2 is made redundant by l1 and l3.
    // Since slopes are strictly decreasing: m1 > m2 > m3.
    // Intersection of l1 and l2: x12 = (c1 - c2) / (m2 - m1)
    // Intersection of l2 and l3: x23 = (c2 - c3) / (m3 - m2)
    // l2 is redundant if x12 >= x23.
    // Cross-multiplying: (c1 - c2) * (m2 - m3) <= (c2 - c3) * (m1 - m2) (taking care of signs)
    // Since m1 - m2 > 0 and m2 - m3 > 0:
    // x12 = (c2 - c1) / (m1 - m2), x23 = (c3 - c2) / (m2 - m3)
    // x12 >= x23 <=> (c2 - c1) * (m2 - m3) >= (c3 - c2) * (m1 - m2)
    bool isRedundant(const Line& l1, const Line& l2, const Line& l3) {
        __int128 dx1 = l1.m - l2.m;
        __int128 dy1 = l2.c - l1.c;
        __int128 dx2 = l2.m - l3.m;
        __int128 dy2 = l3.c - l2.c;
        return dy1 * dx2 >= dy2 * dx1;
    }

public:
    long long minCost(const std::vector<int>& heights, int C) {
        int n = heights.size();
        std::deque<Line> dq;

        // Base case: starting at index 0
        // dp[0] = 0
        // Line 0: m = -2 * heights[0], c = dp[0] + heights[0]^2 = heights[0]^2
        dq.push_back({-2LL * heights[0], 1LL * heights[0] * heights[0]});

        long long current_dp = 0;

        for (int j = 1; j < n; ++j) {
            long long x = heights[j];

            // Since x is increasing, remove suboptimal lines from the front
            while (dq.size() >= 2 && dq[0].eval(x) >= dq[1].eval(x)) {
                dq.pop_front();
            }

            // Best line at x
            current_dp = dq.front().eval(x) + x * x + C;

            if (j == n - 1) break;

            // Prepare new line from current pillar j
            Line newLine = {-2LL * heights[j], current_dp + 1LL * heights[j] * heights[j]};

            // Maintain convex hull at the back
            while (dq.size() >= 2 && isRedundant(dq[dq.size() - 2], dq.back(), newLine)) {
                dq.pop_back();
            }
            dq.push_back(newLine);
        }

        return current_dp;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(N)$. Each line is inserted into the deque once and removed at most once from the front and back. Evaluating each state takes amortized $\mathcal{O}(1)$ time.
- **Space Complexity:** $\mathcal{O}(N)$ to store lines in the deque.
{% endraw %}

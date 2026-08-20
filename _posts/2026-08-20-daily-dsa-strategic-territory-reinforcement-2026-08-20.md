---
layout: post
title: 'Daily DSA: Strategic Territory Reinforcement (Medium)'
date: 2026-08-20 15:54:50 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Strategic Territory
  Reinforcement.'
cover_image: /assets/images/posts/daily-dsa-strategic-territory-reinforcement-2026-08-20-cover.png
cover_caption: ''
---

### Problem Statement

You are a military strategist managing a rectangular territory divided into an $n \times m$ grid of sectors. Initially, all sectors have a reinforcement level of 0.

You are given a series of $Q$ reinforcement commands. Each command is represented as an array `[r1, c1, r2, c2, val]`, which indicates that every sector $(r, c)$ such that $r1 \le r \le r2$ and $c1 \le c \le c2$ should have its reinforcement level increased by `val` (where `val` can be negative, indicating a reduction).

After processing all commands, return the final reinforcement levels of all sectors in the $n \times m$ grid.

### Examples

**Example 1:**
**Input:** `n = 3, m = 3, queries = [[0,0,1,1,2]]`  
**Output:** `[[2,2,0],[2,2,0],[0,0,0]]`  
**Explanation:** The command adds 2 to the subgrid from (0,0) to (1,1). The sectors (0,0), (0,1), (1,0), and (1,1) become 2, while others remain 0.

**Example 2:**
**Input:** `n = 3, m = 3, queries = [[0,0,1,1,2], [1,1,2,2,3]]`  
**Output:** `[[2,2,0],[2,5,3],[0,3,3]]`  
**Explanation:** 
- After the first command: `[[2,2,0],[2,2,0],[0,0,0]]` 
- After the second command (adding 3 to subgrid (1,1) to (2,2)): 
  - Sector (1,1) was 2, now 2 + 3 = 5.
  - Sectors (1,2), (2,1), (2,2) were 0, now 0 + 3 = 3.
  - Final grid: `[[2,2,0],[2,5,3],[0,3,3]]`.

### Constraints

- $1 \le n, m \le 1000$
- $1 \le queries.length \le 10^5$
- $queries[i] = [r1, c1, r2, c2, val]$
- $0 \le r1 \le r2 < n$
- $0 \le c1 \le c2 < m$
- $-10^4 \le val \le 10^4$

---

### Approach

A naive approach would be to iterate through every cell in the subgrid for every query. In the worst case, this would take $O(Q \times n \times m)$, which is $10^5 \times 10^6 = 10^{11}$ operations—far too slow for a 1-second time limit.

To solve this efficiently, we use a **2D Difference Array** (also known as a 2D prefix sum array). 

1. **Difference Array Logic:** In 1D, to add $v$ to $[L, R]$, we set $D[L] += v$ and $D[R+1] -= v$. In 2D, to add $v$ to the rectangle defined by $(r1, c1)$ and $(r2, c2)$, we perform four updates on a difference matrix $D$:
   - $D[r1][c1] += val$
   - $D[r1][c2+1] -= val$
   - $D[r2+1][c1] -= val$
   - $D[r2+1][c2+1] += val$

2. **Reconstruction:** After applying all $Q$ updates, the value of any cell $(i, j)$ in the final grid is the 2D prefix sum of the difference array from $(0,0)$ to $(i, j)$. This is calculated using the inclusion-exclusion principle:
   $S[i][j] = D[i][j] + S[i-1][j] + S[i][j-1] - S[i-1][j-1]$

This approach reduces the complexity to $O(Q + n \times m)$.

### C++ Solution

```cpp
#include <vector>

using namespace std;

class Solution {
public:
    vector<vector<long long>> solveReinforcements(int n, int m, vector<vector<int>>& queries) {
        // Initialize a difference array with extra padding to handle boundary conditions (r2+1, c2+1)
        // Use long long to prevent overflow during prefix sum calculation
        vector<vector<long long>> diff(n + 2, vector<long long>(m + 2, 0));

        for (const auto& q : queries) {
            int r1 = q[0], c1 = q[1], r2 = q[2], c2 = q[3], val = q[4];
            
            // Apply 2D difference array updates (using 1-based indexing for simpler prefix sum logic)
            diff[r1 + 1][c1 + 1] += val;
            diff[r1 + 1][c2 + 2] -= val;
            diff[r2 + 2][c1 + 1] -= val;
            diff[r2 + 2][c2 + 2] += val;
        }

        vector<vector<long long>> result(n, vector<long long>(m));
        for (int i = 1; i <= n; ++i) {
            for (int j = 1; j <= m; ++j) {
                // Compute the 2D prefix sum in-place or into the result grid
                // Current value = current diff + top sum + left sum - diagonal sum
                diff[i][j] += diff[i - 1][j] + diff[i][j - 1] - diff[i - 1][j - 1];
                result[i - 1][j - 1] = diff[i][j];
            }
        }

        return result;
    }
};
```

### Complexity Analysis

- **Time Complexity:** $O(Q + n \times m)$, where $Q$ is the number of queries. We process each query in $O(1)$ and then iterate over the grid once in $O(n \times m)$.
- **Space Complexity:** $O(n \times m)$ to store the difference array and the resulting grid.

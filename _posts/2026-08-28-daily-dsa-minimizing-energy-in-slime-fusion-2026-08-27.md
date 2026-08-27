---
layout: post
title: 'Daily DSA: Minimizing Energy in Slime Fusion (Hard)'
date: 2026-08-28 01:36:58 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Minimizing Energy
  in Slime Fusion.'
cover_image: /assets/images/posts/daily-dsa-minimizing-energy-in-slime-fusion-2026-08-27-cover.png
cover_caption: ''
---

### Problem Statement

You are given $n$ slimes arranged in a row. Each slime has a specific size given in an integer array `slimes`. 

In each step, you can choose two **adjacent** slimes and merge them into a single slime. The cost of merging two slimes of size $x$ and $y$ is $x + y$. The resulting slime will have a size of $x + y$. 

Your goal is to find the minimum total cost to merge all the slimes into one single slime.

### Examples

**Example 1:**
**Input:** `slimes = [1, 3, 2]`
**Output:** `10`
**Explanation:**
- Option 1: Merge index 0 and 1 (1+3=4). Cost: 4. Slimes become [4, 2]. Then merge 4 and 2 (4+2=6). Cost: 6. Total cost: 4 + 6 = 10.
- Option 2: Merge index 1 and 2 (3+2=5). Cost: 5. Slimes become [1, 5]. Then merge 1 and 5 (1+5=6). Cost: 6. Total cost: 5 + 6 = 11.
The minimum cost is 10.

**Example 2:**
**Input:** `slimes = [10, 10, 10, 10]`
**Output:** `80`
**Explanation:**
- One optimal sequence: Merge [10, 10] into 20 (cost 20), merge the other [10, 10] into 20 (cost 20). Current slimes: [20, 20]. Merge [20, 20] into 40 (cost 40). Total cost: 20 + 20 + 40 = 80.

### Constraints

- $1 \le n \le 400$
- $1 \le slimes[i] \le 10^6$

### Approach

This problem is a classic variation of **Interval Dynamic Programming**, similar to the Matrix Chain Multiplication problem.

1.  **State Definition**: Let `dp[i][j]` be the minimum cost to merge the sub-segment of slimes from index `i` to index `j` into a single slime.
2.  **Base Case**: If `i == j`, there is only one slime, so no merge is needed. `dp[i][i] = 0`.
3.  **Recursive Step**: To compute `dp[i][j]`, we assume the very last step was merging two blocks of slimes: one block from `i` to `k` and another from `k+1` to `j` (where $i \le k < j$).
    - The cost to form the first block is `dp[i][k]`.
    - The cost to form the second block is `dp[k+1][j]`.
    - The cost of the final merge is the sum of all elements in the range `[i, j]`.
    - Thus: `dp[i][j] = min(dp[i][k] + dp[k+1][j]) + sum(slimes[i...j])` for all $i \le k < j$.
4.  **Optimization**: To calculate `sum(slimes[i...j])` efficiently in $O(1)$, precompute a **prefix sum** array.
5.  **Execution Order**: Iterate through all possible interval lengths from 2 up to $n$, then iterate through all possible starting positions $i$ for each length.

### C++ Solution

```cpp
#include <vector>
#include <climits>
#include <algorithm>

using namespace std;

class Solution {
public:
    long long minMergeCost(vector<int>& slimes) {
        int n = slimes.size();
        if (n <= 1) return 0;

        // dp[i][j] stores the minimum cost to merge slimes from index i to j
        vector<vector<long long>> dp(n, vector<long long>(n, 0));

        // Precompute prefix sums for O(1) range sum queries
        vector<long long> prefixSum(n + 1, 0);
        for (int i = 0; i < n; i++) {
            prefixSum[i + 1] = prefixSum[i] + slimes[i];
        }

        // len is the length of the interval being processed
        for (int len = 2; len <= n; len++) {
            for (int i = 0; i <= n - len; i++) {
                int j = i + len - 1;
                dp[i][j] = LLONG_MAX;

                // The total sum of the current range [i, j]
                long long currentRangeSum = prefixSum[j + 1] - prefixSum[i];

                // Try all possible split points k between i and j-1
                for (int k = i; k < j; k++) {
                    long long totalCost = dp[i][k] + dp[k + 1][j] + currentRangeSum;
                    if (totalCost < dp[i][j]) {
                        dp[i][j] = totalCost;
                    }
                }
            }
        }

        return dp[0][n - 1];
    }
};
```

### Complexity Analysis

- **Time Complexity**: $O(n^3)$ because there are $O(n^2)$ states in the DP table, and calculating each state requires iterating over $O(n)$ possible split points.
- **Space Complexity**: $O(n^2)$ to store the DP table.

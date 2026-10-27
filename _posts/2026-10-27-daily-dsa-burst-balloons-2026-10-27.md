---
layout: post
title: 'Daily DSA: Burst Balloons (Hard)'
date: 2026-10-27 21:11:49 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Burst Balloons.'
cover_image: /assets/images/posts/default-cover.png
cover_caption: ''
---

{% raw %}
### Problem Description

You are given `n` balloons, indexed from `0` to `n - 1`. Each balloon is painted with a number on it represented by an array `nums`. You are asked to burst all the balloons.

If you burst the `i`-th balloon, you will get `nums[i - 1] * nums[i] * nums[i + 1]` coins. After the burst, the `(i - 1)`-th and `(i + 1)`-th then become adjacent.

Find the maximum coins you can collect by bursting the balloons wisely.

**Note:**
- You may imagine `nums[-1] = nums[n] = 1`. They are not real, therefore you cannot burst them.
- `0 <= n <= 300`
- `0 <= nums[i] <= 100`

### Examples

**Example 1:**
**Input:** `nums = [3, 1, 5, 8]`
**Output:** `167`
**Explanation:**
`nums = [3, 1, 5, 8] --> [3, 5, 8] --> [3, 8] --> [8] --> []` 
`coins =  3*1*5    +   3*5*8   +   1*3*8   +   1*8*1   = 167`.

**Example 2:**
**Input:** `nums = [1, 5]`
**Output:** `10`
**Explanation:**
`nums = [1, 5] --> [5] --> []` 
`coins = 1*1*5 + 1*5*1 = 10`.

### Constraints

- `n == nums.length`
- `1 <= n <= 300`
- `0 <= nums[i] <= 100`

---

### Approach

This problem can be solved using **Interval Dynamic Programming**. 

If we try to simulate bursting balloons from first to last, the subproblems become dependent on which balloons were burst previously, because the neighbors of a balloon change. However, if we think in reverse—**which balloon is the last one to burst in a given range**—the subproblems become independent.

1.  **Define the DP State:** Let `dp[i][j]` be the maximum coins we can collect by bursting all balloons in the open interval `(i, j)`. The balloons at indices `i` and `j` are not burst; they act as boundaries.
2.  **Base Case:** If `j <= i + 1`, there are no balloons to burst between `i` and `j`, so `dp[i][j] = 0`.
3.  **Transitions:** To calculate `dp[i][j]`, we iterate through every possible balloon `k` that could be the **last** one to burst in the interval `(i, j)`. 
    - If `k` is the last balloon to burst in `(i, j)`, then all balloons in `(i, k)` and `(k, j)` must have already been burst.
    - The coins gained from bursting `k` last will be `nums[i] * nums[k] * nums[j]`.
    - Therefore: `dp[i][j] = max(dp[i][j], dp[i][k] + dp[k][j] + nums[i] * nums[k] * nums[j])` for all `i < k < j`.
4.  **Final Answer:** The answer will be `dp[0][n+1]` after padding the original array with `1` at both ends.

### Complexity Analysis
- **Time Complexity:** $O(N^3)$, where $N$ is the number of balloons. There are $O(N^2)$ states, and each state takes $O(N)$ to compute.
- **Space Complexity:** $O(N^2)$ to store the DP table.

---

### C++ Solution

```cpp
#include <vector>
#include <algorithm>

using namespace std;

class Solution {
public:
    int maxCoins(vector<int>& nums) {
        int n = nums.size();
        // Pad the array with 1s at the boundaries
        vector<int> vals(n + 2);
        vals[0] = 1;
        vals[n + 1] = 1;
        for (int i = 0; i < n; ++i) {
            vals[i + 1] = nums[i];
        }

        // dp[i][j] means max coins for bursting balloons in open interval (i, j)
        int m = n + 2;
        vector<vector<int>> dp(m, vector<int>(m, 0));

        // len is the length of the interval (j - i)
        for (int len = 2; len < m; ++len) {
            for (int i = 0; i < m - len; ++i) {
                int j = i + len;
                // Try each balloon k in (i, j) as the last one to burst
                for (int k = i + 1; k < j; ++k) {
                    int current_coins = vals[i] * vals[k] * vals[j];
                    dp[i][j] = max(dp[i][j], dp[i][k] + dp[k][j] + current_coins);
                }
            }
        }

        return dp[0][m - 1];
    }
};
```
{% endraw %}

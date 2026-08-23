---
layout: post
title: 'Daily DSA: Optimal Candy Distribution (Hard)'
date: 2026-08-23 15:48:53 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Optimal Candy
  Distribution.'
cover_image: /assets/images/posts/daily-dsa-optimal-candy-distribution-2026-08-23-cover.png
cover_caption: ''
---

### Problem Statement
There are `n` children standing in a line. Each child is assigned a rating value given in the integer array `ratings`.

You are giving candies to these children subjected to the following requirements:
1. Each child must have at least one candy.
2. Children with a higher rating must get more candies than their neighbors.

Return the *minimum number of candies* you need to have to distribute the candies to the children while satisfying both conditions.

### Examples
**Example 1:**
- **Input:** `ratings = [1, 0, 2]`
- **Output:** `5`
- **Explanation:** You can allocate to the first, second, and third child with 2, 1, 2 candies respectively. This satisfies all rules.

**Example 2:**
- **Input:** `ratings = [1, 2, 2]`
- **Output:** `4`
- **Explanation:** You can allocate to the first, second, and third child with 1, 2, 1 candies respectively. The third child gets 1 candy because it satisfies the conditions (it is not higher than the second child's rating).

### Constraints
- `n == ratings.length`
- `1 <= n <= 5 * 10^4`
- `0 <= ratings[i] <= 5 * 10^4`

### Approach: Two-Pass Greedy
The distribution of candies for any child depends on both their left and right neighbors. To satisfy the conditions with the minimum number of candies, we can break the problem into two greedy sub-problems:

1.  **Left-to-Right Pass:** Ensure every child has more candies than their left neighbor if their rating is higher. 
    - Initialize a `candies` array of size `n` with all `1`s.
    - Iterate from `i = 1` to `n-1`. If `ratings[i] > ratings[i-1]`, set `candies[i] = candies[i-1] + 1`.

2.  **Right-to-Left Pass:** Ensure every child has more candies than their right neighbor if their rating is higher, while maintaining the property established in the first pass.
    - Iterate from `i = n-2` down to `0`. If `ratings[i] > ratings[i+1]`, set `candies[i] = max(candies[i], candies[i+1] + 1)`.

3.  **Result:** The sum of the `candies` array represents the global minimum required.

This works because the first pass handles all increasing slopes from the left, and the second pass handles all increasing slopes from the right (decreasing from the left) without invalidating the first pass's results due to the `max()` function.

### C++ Solution
```cpp
#include <vector>
#include <algorithm>
#include <numeric>

class Solution {
public:
    int candy(std::vector<int>& ratings) {
        int n = ratings.size();
        if (n <= 1) return n;

        // Step 1: Every child gets at least one candy
        std::vector<int> candies(n, 1);

        // Step 2: Left-to-Right pass
        // Higher rating than left neighbor -> more candies than left neighbor
        for (int i = 1; i < n; ++i) {
            if (ratings[i] > ratings[i - 1]) {
                candies[i] = candies[i - 1] + 1;
            }
        }

        // Step 3: Right-to-Left pass
        // Higher rating than right neighbor -> more candies than right neighbor
        // Use max to ensure we don't break the Left-to-Right condition
        for (int i = n - 2; i >= 0; --i) {
            if (ratings[i] > ratings[i + 1]) {
                candies[i] = std::max(candies[i], candies[i + 1] + 1);
            }
        }

        // Step 4: Sum up the candies
        int total_candies = 0;
        for (int count : candies) {
            total_candies += count;
        }

        return total_candies;
    }
};
```

### Complexity Analysis
- **Time Complexity:** O(n), where n is the length of the ratings array. We perform two linear passes over the array.
- **Space Complexity:** O(n) to store the candy count for each child.

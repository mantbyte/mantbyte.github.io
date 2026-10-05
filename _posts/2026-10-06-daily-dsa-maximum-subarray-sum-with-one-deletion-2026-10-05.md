---
layout: post
title: 'Daily DSA: Maximum Subarray Sum with One Deletion (Medium)'
date: 2026-10-06 00:34:48 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Maximum Subarray
  Sum with One Deletion.'
cover_image: /assets/images/posts/daily-dsa-maximum-subarray-sum-with-one-deletion-2026-10-05-cover.png
cover_caption: ''
---

{% raw %}
# Problem Statement

Given an array of integers, find the maximum subarray sum possible after performing **at most one** deletion of an element. That is, you can choose to delete any single element from the array (or none at all), and then find the maximum sum of a contiguous subarray in the remaining elements. The remaining subarray must contain at least one element.

# Examples

### Example 1:
- **Input:** `arr = [1, -2, 0, 3]`
- **Output:** `4`
- **Explanation:** By deleting `-2`, the array becomes `[1, 0, 3]`. The maximum subarray sum is `1 + 0 + 3 = 4`.

### Example 2:
- **Input:** `arr = [1, -2, -2, 3]`
- **Output:** `3`
- **Explanation:** By deleting the first `-2`, the array becomes `[1, -2, 3]`. The subarray `[3]` or `[1, -2, 3]` gives the max sum, but the max contiguous sum of a subsegment is `3` (from `[3]`). Wait, if we take `[1, -2, 3]`, sum is `2`. If we delete the second `-2`, array becomes `[1, -2, 3]`, sum is `2`. If we delete both? We can only delete at most one. If we delete `-2`, max sum is `3` (taking just `[3]`).

### Example 3:
- **Input:** `arr = [-1, -1, -1, -1]`
- **Output:** `-1`
- **Explanation:** We must choose a non-empty subarray. Deleting any `-1` leaves three `-1`s, and the maximum subarray of length 1 has a sum of `-1`.

# Constraints
- $1 \le arr.length \le 10^5$
- $-10^4 \le arr[i] \le 10^4$

# Approach / Hint
This is a variation of Kadane's algorithm. For every index $i$, we can track two states:
1. `noDelete[i]`: The maximum subarray ending at index $i$ **without** any deletions. This is the classic Kadane's state: `max(arr[i], noDelete[i-1] + arr[i])`.
2. `oneDelete[i]`: The maximum subarray ending at index $i$ **with** at most one deletion. This can come from two scenarios:
   - We deleted the current element `arr[i]`, meaning the state equals the maximum subarray ending at `i-1` **without** any deletions (`noDelete[i-1]`).
   - We deleted an element *before* the current index, meaning we extend the previous `oneDelete[i-1]` state with the current element: `oneDelete[i-1] + arr[i]`.
   
Thus, `oneDelete[i] = max(noDelete[i-1], oneDelete[i-1] + arr[i])`.
We can optimize space from $O(N)$ to $O(1)$ since each state only depends on the previous indices.

# C++ Solution

```cpp
#include <vector>
#include <algorithm>

class Solution {
public:
    int maximumSum(std::vector<int>& arr) {
        int n = arr.size();
        if (n == 1) return arr[0];

        int noDelete = arr[0];
        int oneDelete = 0; // At start, deleting arr[0] leaves empty sum 0, but we need non-empty
        int maxSum = arr[0];
        
        // Base initializations
        int prevNoDelete = arr[0];
        int prevOneDelete = arr[0]; // If we delete arr[0], we need to handle carefully. 
        
        // Let's reformulate with standard DP states:
        // noDelete: max subarray ending at i with 0 deletions
        // oneDelete: max subarray ending at i with 1 deletion
        
        int curNoDelete = arr[0];
        int curOneDelete = arr[0]; // If we delete arr[0], max sum so far (technically empty, but constraint requires non-empty)
        
        // Better approach: initialize for i = 0
        // noDelete[0] = arr[0]
        // oneDelete[0] = arr[0] (effectively treating deletion of nothing or handling edge cases)
        
        int ans = arr[0];
        int nd = arr[0]; // no delete
        int od = arr[0]; // one delete
        
        for (int i = 1; i < n; ++i) {
            // od can be:
            // 1. the max sum ending at i-1 with NO deletion (meaning we delete arr[i] now)
            // 2. the max sum ending at i-1 with ONE deletion + current element arr[i]
            int next_od = std::max(nd, od + arr[i]);
            
            // nd is standard Kadane
            int next_nd = std::max(arr[i], nd + arr[i]);
            
            nd = next_nd;
            od = next_od;
            
            ans = std::max({ans, nd, od});
        }
        
        return ans;
    }
};
```

### Complexity Analysis
- **Time Complexity:** $O(N)$ since we iterate through the array of size $N$ once.
- **Space Complexity:** $O(1)$ as we only maintain a few variables for the states.
{% endraw %}

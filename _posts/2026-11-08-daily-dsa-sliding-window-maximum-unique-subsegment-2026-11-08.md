---
layout: post
title: 'Daily DSA: Sliding Window Maximum Unique Subsegment (Medium)'
date: 2026-11-08 21:58:59 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Sliding Window
  Maximum Unique Subsegment.'
cover_image: /assets/images/posts/daily-dsa-sliding-window-maximum-unique-subsegment-2026-11-08-cover.png
cover_caption: ''
---

{% raw %}
# Problem Statement

You are given an array of integers `nums` and an integer `k`. Your goal is to find the maximum sum of a contiguous subsegment (subarray) of `nums` of length **at most** `k` such that all elements within the subsegment are **distinct**. If no such subsegment exists, return `0`.

# Examples

### Example 1:
- **Input:** `nums = [1, 2, 1, 3, 2]`, `k = 3`
- **Output:** `6`
- **Explanation:** The subsegment `[1, 3, 2]` has length 3 (which is $\le 3$), all elements are unique, and its sum is `1 + 3 + 2 = 6`. Another valid subsegment is `[2, 1, 3]` with sum `2 + 1 + 3 = 6`.

### Example 2:
- **Input:** `nums = [4, 4, 4, 4]`, `k = 2`
- **Output:** `4`
- **Explanation:** Subsegments of length at most 2 with all distinct elements are single elements like `[4]`. The maximum sum is `4`.

### Example 3:
- **Input:** `nums = [1, 2, 3, 4, 5]`, `k = 3`
- **Output:** `12`
- **Explanation:** The subsegment `[3, 4, 5]` has length 3, distinct elements, and a sum of `3 + 4 + 5 = 12`.

# Constraints
- $1 \le nums.length \le 10^5$
- $1 \le k \le nums.length$
- $-10^4 \le nums[i] \le 10^4$

# Approach / Hint
1. **Sliding Window + Hash Map:** Use a variable-size sliding window defined by a left pointer `L` and a right pointer `R`. Maintain a frequency map or hash table to track the elements currently inside the window.
2. **Window Constraints:** 
   - The window size (`R - L + 1`) must not exceed `k`.
   - All elements in the window must be unique (i.e., no element's frequency exceeds `1`).
3. **Shrinking Strategy:** As you expand `R` and add `nums[R]` to the window and its sum, if the window size exceeds `k` or if `nums[R]` already appears more than once, increment `L` (subtracting `nums[L]` from the sum and updating the frequency map) until both conditions are satisfied.
4. **Tracking Maximum:** Keep a running maximum of the window sums whenever the window satisfies all conditions.

# C++ Solution

```cpp
#include <vector>
#include <unordered_map>
#include <algorithm>

class Solution {
public:
    long long maximumUniqueSubarraySum(std::vector<int>& nums, int k) {
        std::unordered_map<int, int> count;
        long long max_sum = 0;
        long long current_sum = 0;
        int L = 0;

        for (int R = 0; R < nums.size(); ++R) {
            count[nums[R]]++;
            current_sum += nums[R];

            // Shrink window if it violates the maximum length k
            // or contains duplicate elements
            while ((R - L + 1) > k || count[nums[R]] > 1) {
                count[nums[L]]--;
                current_sum -= nums[L];
                L++;
            }

            max_sum = std::max(max_sum, current_sum);
        }

        return max_sum;
    }
};
```

### Complexity Analysis
- **Time Complexity:** $\mathcal{O}(N)$ where $N$ is the number of elements in `nums`. Each element is visited at most twice (once by `R` and once by `L`).
- **Space Complexity:** $\mathcal{O}(min(N, k))$ to store the frequency map of elements in the current window.
{% endraw %}

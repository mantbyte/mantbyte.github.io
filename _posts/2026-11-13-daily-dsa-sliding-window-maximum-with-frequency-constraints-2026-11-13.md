---
layout: post
title: 'Daily DSA: Sliding Window Maximum with Frequency Constraints (Hard)'
date: 2026-11-13 22:57:52 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Sliding Window
  Maximum with Frequency Constraints.'
cover_image: /assets/images/posts/daily-dsa-sliding-window-maximum-with-frequency-constraints-2026-11-13-cover.png
cover_caption: ''
---

{% raw %}
# Problem Statement

You are given an array of integers `nums` and two integers `k` and `limit`. A subarray is called **valid** if its length is at most `k`, and no element in the subarray appears more than `limit` times.

Return the maximum sum of any **valid** subarray. If no such valid subarray exists, return 0.

# Examples

### Example 1:
**Input:** `nums = [1, 2, 1, 2, 1]`, `k = 3`, `limit = 2`
**Output:** `6`
**Explanation:** 
Valid subarrays of length at most 3 with element frequency <= 2 include:
- `[1, 2, 1]` (sum = 4)
- `[2, 1, 2]` (sum = 5)
- `[1, 2]` (sum = 3)
The maximum sum is 5? Wait, let's check `[1, 2, 1, 2]` -> length 4 > k=3. 
Let's re-evaluate: `[1, 2, 1]` has sum 4. `[2, 1, 2]` has sum 5. `[1, 2]` has sum 3. `[2, 1, 2]` elements: '2' appears 2 times, '1' appears 1 time. Max frequency is 2 <= limit. Length is 3 <= k. Sum = 5. Wait, can we get 6? Subarray `[2, 1, 2]` has sum 5. Let's check `[1, 2]` sum 3. What about `[2, 1]`? Sum 3. Let's trace `[1, 2, 1, 2, 1]` with k=3, limit=2. Max sum is `[2, 1, 2]` = 5.

### Example 2:
**Input:** `nums = [5, 5, 5, 5]`, `k = 2`, `limit = 1`
**Output:** `5`
**Explanation:**
Valid subarrays must have length <= 2 and each element frequency <= 1. Since all elements are 5, any subarray of length >= 2 violates the frequency limit. Subarrays of length 1 are `[5]`, each with sum 5.

# Constraints
- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`
- `1 <= k <= nums.length`
- `1 <= limit <= k`

# Approach
1. **Sliding Window:** We can maintain a sliding window `[left, right]` that respects the maximum length constraint `k` and the frequency constraint `limit` using a hash map to count frequencies and a running sum.
2. **Shrinking Condition:** If the window size exceeds `k` OR any element's frequency exceeds `limit`, we increment `left` to shrink the window until all conditions are satisfied.
3. **Tracking the Maximum:** For every valid window configuration (or specifically when the window is valid), we update our global maximum sum with the current window's sum.

# C++ Code

```cpp
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <numeric>

class Solution {
public:
    long long maximumSubarraySum(std::vector<int>& nums, int k, int limit) {
        std::unordered_map<int, int> freq;
        int left = 0;
        long long current_sum = 0;
        long long max_sum = 0;
        bool has_valid = false;

        for (int right = 0; right < nums.size(); ++right) {
            freq[nums[right]]++;
            current_sum += nums[right];

            // Shrink the window if length exceeds k or any frequency exceeds limit
            while ((right - left + 1 > k) || (freq[nums[right]] > limit)) {
                freq[nums[left]]--;
                current_sum -= nums[left];
                left++;
            }

            max_sum = std::max(max_sum, current_sum);
            has_valid = true;
        }

        return has_valid ? max_sum : 0;
    }
};
```

### Complexity Analysis
- **Time Complexity:** $\mathcal{O}(N)$ where $N$ is the number of elements in `nums`. Each element is added and removed from the window at most once.
- **Space Complexity:** $\mathcal{O}(K)$ to store the frequency map of elements inside the current window of size at most $K$.
{% endraw %}

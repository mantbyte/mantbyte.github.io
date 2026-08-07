---
layout: post
title: 'Daily DSA: Longest Subarray with At Most K Distinct Even Numbers (Medium)'
date: 2026-08-08 00:39:52 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Longest Subarray
  with At Most K Distinct Even Numbers.'
cover_image: /assets/images/posts/daily-dsa-longest-subarray-with-at-most-k-distinct-even-numbers-2026-08-07-cover.png
cover_caption: ''
---

## Problem Description

Given an array of positive integers `nums` and an integer `k`, return the **maximum length** of a contiguous subarray that contains at most `k` **distinct even numbers**.

An even number is an integer that is divisible by `2`. Odd numbers do not count towards the distinct even numbers limit.

---

### Examples

**Example 1:**

```
Input: nums = [1, 2, 4, 2, 3, 6, 8], k = 2
Output: 5
Explanation: The longest valid subarray is [1, 2, 4, 2, 3].
The distinct even numbers in this subarray are {2, 4}, which is 2 distinct even numbers (<= k).
The length of this subarray is 5.
```

**Example 2:**

```
Input: nums = [2, 4, 6, 8], k = 1
Output: 1
Explanation: Any subarray of length 2 or more contains at least 2 distinct even numbers. Thus, the maximum length is 1 (e.g., [2], [4], [6], or [8]).
```

**Example 3:**

```
Input: nums = [1, 3, 5, 7, 2, 9, 11], k = 0
Output: 3
Explanation: With k = 0, no even numbers are allowed. The subarray [1, 3, 5] (or [3, 5, 7]) contains 0 distinct even numbers and has length 3.
```

---

### Constraints

- `1 <= nums.length <= 10^5`
- `1 <= nums[i] <= 10^9`
- `0 <= k <= nums.length`

---

### Approach & Explanation

This problem can be efficiently solved using the **Sliding Window (Two Pointers)** technique:

1. **Window Definition**: Maintain a window `[left, right]` and a hash map `even_freq` to keep track of the frequencies of **even** numbers within the current window.
2. **Expand Window**: Iterate `right` from `0` to `nums.length - 1`. If `nums[right]` is even, increment its frequency count in `even_freq`.
3. **Shrink Window**: If the number of distinct even elements (i.e., `even_freq.size()`) exceeds `k`, shrink the window from the left by incrementing `left` until `even_freq.size() <= k`. If `nums[left]` is even, decrement its frequency in `even_freq` and remove the key if its count reaches `0`.
4. **Update Result**: At each step where the window is valid (`even_freq.size() <= k`), update the maximum length as `max_len = max(max_len, right - left + 1)`.

---

### C++ Source Code

```cpp
#include <vector>
#include <unordered_map>
#include <algorithm>

class Solution {
public:
    int maxSubarrayLength(std::vector<int>& nums, int k) {
        std::unordered_map<int, int> even_freq;
        int left = 0;
        int max_len = 0;

        for (int right = 0; right < nums.size(); ++right) {
            // If the element is even, track its frequency
            if (nums[right] % 2 == 0) {
                even_freq[nums[right]]++;
            }

            // Shrink window if distinct even count exceeds k
            while (even_freq.size() > k) {
                if (nums[left] % 2 == 0) {
                    even_freq[nums[left]]--;
                    if (even_freq[nums[left]] == 0) {
                        even_freq.erase(nums[left]);
                    }
                }
                left++;
            }

            // Update maximum length
            max_len = std::max(max_len, right - left + 1);
        }

        return max_len;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(N)$, where $N$ is the length of `nums`. Each element is processed at most twice (once when expanded by `right`, once when shrunk by `left`). Hash map lookup and insertion are $\mathcal{O}(1)$ on average.
- **Space Complexity:** $\mathcal{O}(N)$ in the worst case (or $\mathcal{O}(K)$) to store frequencies of distinct even integers in the hash map.

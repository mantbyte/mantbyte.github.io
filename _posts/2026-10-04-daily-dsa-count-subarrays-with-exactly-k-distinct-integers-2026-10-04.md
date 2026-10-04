---
layout: post
title: 'Daily DSA: Count Subarrays with Exactly K Distinct Integers (Hard)'
date: 2026-10-04 20:36:25 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Count Subarrays
  with Exactly K Distinct Integers.'
cover_image: /assets/images/posts/daily-dsa-count-subarrays-with-exactly-k-distinct-integers-2026-10-04-cover.png
cover_caption: ''
---

{% raw %}
### Problem Description

Given an integer array `nums` and an integer `k`, return the number of **good subarrays** of `nums`.

A **good subarray** is an array where the number of different integers in that array is exactly `k`.

*   A **subarray** is a contiguous part of an array.

### Examples

**Example 1:**
**Input:** `nums = [1,2,1,2,3], k = 2`  
**Output:** `7`  
**Explanation:** Subarrays formed with exactly 2 different integers: `[1,2]`, `[2,1]`, `[1,2]`, `[2,3]`, `[1,2,1]`, `[2,1,2]`, `[1,2,1,2]`.

**Example 2:**
**Input:** `nums = [1,2,1,3,4], k = 3`  
**Output:** `3`  
**Explanation:** Subarrays formed with exactly 3 different integers: `[1,2,1,3]`, `[2,1,3]`, `[1,3,4]`.

### Constraints

*   `1 <= nums.length <= 2 * 10^4`
*   `1 <= nums[i] <= nums.length`
*   `1 <= k <= nums.length`

---

### Approach

Counting subarrays with **exactly** `k` distinct elements directly is challenging because a sliding window typically finds ranges that satisfy a "less than or equal to" condition easily, but not an "exactly" condition.

#### The "At Most" Trick
We can define a helper function `countAtMost(k)` which returns the number of subarrays with **at most** `k` distinct elements. 
If we have this function, the number of subarrays with **exactly** `k` distinct elements is simply:
`Exactly(K) = AtMost(K) - AtMost(K - 1)`

#### Sliding Window for At Most K
1.  Maintain a sliding window `[left, right]` and a frequency map of elements within the window.
2.  Expand the window by moving `right` and adding `nums[right]` to the map.
3.  If the number of distinct elements in the map exceeds `k`, shrink the window from the `left` until the count of distinct elements is `k` or less.
4.  At each step, the number of subarrays ending at `right` that have at most `k` distinct elements is `(right - left + 1)`. Add this to your total.

### C++ Solution

```cpp
#include <vector>
#include <vector>

using namespace std;

class Solution {
public:
    /**
     * Helper function to count subarrays with at most 'k' distinct integers.
     */
    int countAtMost(vector<int>& nums, int k) {
        if (k == 0) return 0;
        int n = nums.size();
        // Using a vector as a frequency map for optimization since nums[i] <= n
        vector<int> freq(n + 1, 0);
        int left = 0, distinctCount = 0, result = 0;

        for (int right = 0; right < n; ++right) {
            if (freq[nums[right]] == 0) {
                distinctCount++;
            }
            freq[nums[right]]++;

            // Shrink window if distinct elements exceed k
            while (distinctCount > k) {
                freq[nums[left]]--;
                if (freq[nums[left]] == 0) {
                    distinctCount--;
                }
                left++;
            }

            // All subarrays ending at 'right' and starting between 'left' and 'right'
            // have at most k distinct elements.
            result += (right - left + 1);
        }
        return result;
    }

    int subarraysWithKDistinct(vector<int>& nums, int k) {
        return countAtMost(nums, k) - countAtMost(nums, k - 1);
    }
};
```

### Complexity Analysis

*   **Time Complexity:** O(N), where N is the length of the array. The `countAtMost` function is called twice. In each call, both the `left` and `right` pointers traverse the array at most once.
*   **Space Complexity:** O(N) to store the frequency map (in the worst case, all elements are distinct).
{% endraw %}

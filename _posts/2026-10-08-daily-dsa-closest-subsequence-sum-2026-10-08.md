---
layout: post
title: 'Daily DSA: Closest Subsequence Sum (Hard)'
date: 2026-10-08 22:37:55 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Closest Subsequence
  Sum.'
cover_image: /assets/images/posts/daily-dsa-closest-subsequence-sum-2026-10-08-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are given an integer array `nums` and an integer `target`. You want to choose a subsequence of `nums` such that the sum of its elements is as close to `target` as possible. 

Return the minimum absolute difference between the sum of the subsequence and `target`. 

A subsequence of an array is an array that can be derived from another array by deleting some or no elements without changing the order of the remaining elements. (e.g., `[2,3,5]` is a subsequence of `[1,2,3,4,5]` while `[1,5,2]` is not).

### Examples

**Example 1:**
- **Input:** `nums = [5, -7, 35, 4], target = 6` 
- **Output:** `1` 
- **Explanation:** The subsequence `[5]` has a sum of 5, which is at a distance of 1 from 6. This is the minimum possible difference.

**Example 2:**
- **Input:** `nums = [7, -9, 15, -2], target = -5` 
- **Output:** `1` 
- **Explanation:** The subsequence `[7, -9, -2]` has a sum of -4, which is at a distance of 1 from -5.

**Example 3:**
- **Input:** `nums = [1, 2, 3], target = -7` 
- **Output:** `7` 
- **Explanation:** The empty subsequence has a sum of 0, which is the closest to -7 (difference of 7).

### Constraints
- `1 <= nums.length <= 40`
- `-10^7 <= nums[i] <= 10^7`
- `-10^9 <= target <= 10^9`

---

### Approach: Meet-in-the-Middle

With `nums.length` up to 40, a standard brute-force approach to check all $2^{40}$ subsequences is impossible ($2^{40} \approx 10^{12}$). However, we can use the **Meet-in-the-middle** technique:

1. **Split the Array:** Divide the array into two halves: `left` (size $N/2$) and `right` (size $N - N/2$).
2. **Generate All Sums:** Generate all possible subsequence sums for both halves. For each half of size 20, there are $2^{20} \approx 10^6$ sums, which is manageable.
3. **Sort the Second Half:** Sort the sums of the `right` half to enable binary search.
4. **Binary Search for the Target:** Iterate through every sum $S_L$ in the `left` sums. We want to find a sum $S_R$ from the `right` sums such that $S_L + S_R$ is as close to `target` as possible. This is equivalent to finding $S_R$ closest to `target - S_L`.
5. **Optimization:** Use `std::lower_bound` in C++ to find the closest values in the sorted `right` sums for each $S_L$.

### Time & Space Complexity
- **Time Complexity:** $O(N \cdot 2^{N/2})$, where $N$ is the length of the array. Generating sums takes $O(2^{N/2})$, sorting takes $O(2^{N/2} \log 2^{N/2})$, and binary search takes $O(2^{N/2} \log 2^{N/2})$.
- **Space Complexity:** $O(2^{N/2})$ to store the generated subsequence sums for the two halves.

---

### C++ Solution

```cpp
#include <vector>
#include <algorithm>
#include <cmath>

using namespace std;

class Solution {
public:
    void generateSums(int index, int end, long long currentSum, const vector<int>& nums, vector<long long>& sums) {
        if (index == end) {
            sums.push_back(currentSum);
            return;
        }
        // Choice 1: Include nums[index]
        generateSums(index + 1, end, currentSum + nums[index], nums, sums);
        // Choice 2: Exclude nums[index]
        generateSums(index + 1, end, currentSum, nums, sums);
    }

    int minAbsDifference(vector<int>& nums, int target) {
        int n = nums.size();
        vector<long long> leftSums, rightSums;

        // Generate all possible sums for the first half
        generateSums(0, n / 2, 0, nums, leftSums);
        // Generate all possible sums for the second half
        generateSums(n / 2, n, 0, nums, rightSums);

        // Sort right half to perform binary search
        sort(rightSums.begin(), rightSums.end());

        long long minDiff = abs(target);

        for (long long sL : leftSums) {
            long long remaining = target - sL;

            // Find the first element in rightSums >= remaining
            auto it = lower_bound(rightSums.begin(), rightSums.end(), remaining);

            if (it != rightSums.end()) {
                minDiff = min(minDiff, abs(remaining - *it));
            }
            if (it != rightSums.begin()) {
                // Check the element just smaller than remaining
                minDiff = min(minDiff, abs(remaining - *prev(it)));
            }
            
            if (minDiff == 0) return 0; // Early exit
        }

        return (int)minDiff;
    }
};
```
{% endraw %}

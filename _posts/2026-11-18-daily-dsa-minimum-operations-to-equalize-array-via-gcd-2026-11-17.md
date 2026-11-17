---
layout: post
title: 'Daily DSA: Minimum Operations to Equalize Array via GCD (Medium)'
date: 2026-11-18 00:25:24 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Minimum Operations
  to Equalize Array via GCD.'
cover_image: /assets/images/posts/daily-dsa-minimum-operations-to-equalize-array-via-gcd-2026-11-17-cover.png
cover_caption: ''
---

{% raw %}
# Problem Statement

You are given an array of positive integers `nums`. In one operation, you can choose any two elements `nums[i]` and `nums[j]` ($i \neq j$) and replace one of them with their greatest common divisor (GCD). 

Return the *minimum* number of operations required to make all elements in the array equal to `1`. If it is impossible to make all elements equal to `1`, return `-1`.

# Examples

### Example 1:
**Input:** `nums = [2, 6, 3, 4]`
**Output:** `4`
**Explanation:** 
- Replace `nums[1]` (6) with `gcd(nums[1], nums[0]) = gcd(6, 2) = 2`. Array becomes `[2, 2, 3, 4]`.
- Replace `nums[2]` (3) with `gcd(nums[2], nums[1]) = gcd(3, 2) = 1`. Array becomes `[2, 2, 1, 4]`.
- Replace `nums[0]` (2) with `gcd(nums[0], nums[2]) = gcd(2, 1) = 1`. Array becomes `[1, 2, 1, 4]`.
- Replace `nums[1]` (2) with `gcd(nums[1], nums[0]) = gcd(2, 1) = 1`. Array becomes `[1, 1, 1, 4]`.
- Replace `nums[3]` (4) with `gcd(nums[3], nums[2]) = gcd(4, 1) = 1`. Array becomes `[1, 1, 1, 1]`.
Total operations: 4.

### Example 2:
**Input:** `nums = [2, 10, 6, 14]`
**Output:** `-1`
**Explanation:** The overall GCD of the array is 2, which is greater than 1. It is impossible to reduce the elements to 1.

# Constraints
- `1 <= nums.length <= 50`
- `1 <= nums[i] <= 10^9`

# Approach & Hints
1. **Check Base Cases**: 
   - If the array already contains all `1`s, the answer is the count of elements that are not `1` (which is `0`).
   - If the overall GCD of the entire array is greater than `1` and there are no existing `1`s, it's impossible to create a `1`, so return `-1`.
2. **Count Existing Ones**: If there is at least one `1` in the array, say there are $C$ ones, we can convert every other element to `1` using one operation per element. Thus, the answer is `n - count_ones`.
3. **Find Subarrays with GCD = 1**: If there are no `1`s initially, we must find the shortest contiguous subarray whose GCD is `1`. Suppose the minimum length of such a subarray is $L$. We can reduce this subarray to a single `1` using $L - 1$ operations. Then, we can propagate this `1` to the rest of the $n - 1$ elements using an additional $n - 1$ operations. Total operations = $(L - 1) + (n - 1) = n + L - 2$.

# C++ Solution
```cpp
#include <vector>
#include <numeric>
#include <algorithm>

class Solution {
public:
    int minOperations(std::vector<int>& nums) {
        int n = nums.size();
        int ones = 0;
        int overall_gcd = 0;
        
        for (int x : nums) {
            if (x == 1) ones++;
            overall_gcd = std::gcd(overall_gcd, x);
        }
        
        // If there are already 1s, we just need to convert the non-1 elements.
        if (ones > 0) {
            return n - ones;
        }
        
        // If the total GCD is not 1, we can never produce a 1.
        if (overall_gcd > 1) {
            return -1;
        }
        
        // Find the shortest subarray with GCD equal to 1
        int min_len = n + 1;
        for (int i = 0; i < n; ++i) {
            int current_gcd = 0;
            for (int j = i; j < n; ++j) {
                current_gcd = std::gcd(current_gcd, nums[j]);
                if (current_gcd == 1) {
                    min_len = std::min(min_len, j - i + 1);
                    break;
                }
            }
        }
        
        // Operations to form the first 1: min_len - 1
        // Operations to spread the 1 to all other elements: n - 1
        return (min_len - 1) + (n - 1);
    }
};
```

### Complexity Analysis
- **Time Complexity:** $O(n^2 \log(\text{MAX}))$, where $n$ is the size of the array and $\text{MAX}$ is the maximum element in `nums`. The nested loops check all subarrays, taking logarithmic time for each GCD computation.
- **Space Complexity:** $O(1)$ auxiliary space.
{% endraw %}

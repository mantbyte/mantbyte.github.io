---
layout: post
title: 'Daily DSA: Sum of Subarray Minimums (Medium)'
date: 2026-08-26 16:01:06 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Sum of Subarray
  Minimums.'
cover_image: /assets/images/posts/daily-dsa-sum-of-subarray-minimums-2026-08-26-cover.png
cover_caption: ''
---

### Problem Statement

Given an array of integers `arr`, find the sum of `min(b)`, where `b` ranges over every (contiguous) subarray of `arr`. Since the answer may be large, return the answer **modulo** $10^9 + 7$.

### Examples

**Example 1:**
- **Input:** `arr = [3, 1, 2, 4]`
- **Output:** `17`
- **Explanation:** 
  Subarrays are [3], [1], [2], [4], [3,1], [1,2], [2,4], [3,1,2], [1,2,4], [3,1,2,4].
  Minimums are 3, 1, 2, 4, 1, 1, 2, 1, 1, 1.
  Sum is 17.

**Example 2:**
- **Input:** `arr = [11, 81, 94, 43]`
- **Output:** `444`

### Constraints

- `1 <= arr.length <= 3 * 10^4`
- `1 <= arr[i] <= 3 * 10^4`

---

### Approach

Instead of calculating the minimum for every possible subarray (which would be $O(N^2)$), we use the **Contribution Technique**. We determine for each element `arr[i]`, how many subarrays have `arr[i]` as their minimum value.

#### 1. Contribution Logic
For an element `arr[i]`, let:
- `L` be the number of consecutive elements to the left that are strictly greater than `arr[i]`.
- `R` be the number of consecutive elements to the right that are greater than or equal to `arr[i]`.

The number of subarrays where `arr[i]` is the minimum is `(L + 1) * (R + 1)`. 
*Note: We use strictly greater on one side and greater-than-or-equal on the other to avoid double-counting subarrays when duplicate elements exist.*

#### 2. Monotonic Stack
We can find the nearest smaller element to the left and right efficiently using a **Monotonic Stack**. 
- As we iterate through the array, we maintain a stack of indices where the values are in increasing order.
- When we encounter an element smaller than the stack top, the stack top element has found its "right boundary."
- The element currently below it in the stack is its "left boundary."

### Time Complexity
- **Time:** $O(N)$, as each element is pushed and popped from the stack exactly once.
- **Space:** $O(N)$, to store the stack.

---

### C++ Solution

```cpp
#include <vector>
#include <stack>

using namespace std;

class Solution {
public:
    int sumSubarrayMins(vector<int>& arr) {
        int n = arr.size();
        long long total_sum = 0;
        const int MOD = 1e9 + 7;
        stack<int> s; // Monotonic increasing stack storing indices

        // We iterate up to n to process remaining elements in the stack
        for (int i = 0; i <= n; ++i) {
            // Use a value smaller than any possible element to flush the stack at i == n
            int current_val = (i == n) ? -1 : arr[i];

            while (!s.empty() && arr[s.top()] > current_val) {
                int mid = s.top();
                s.pop();
                
                // The element at 'mid' is the minimum for all subarrays 
                // starting after 'left' and ending before or at 'i'
                int left = s.empty() ? -1 : s.top();
                int right = i;
                
                long long count = (long long)(mid - left) * (right - mid);
                total_sum = (total_sum + (count * arr[mid])) % MOD;
            }
            s.push(i);
        }

        return (int)total_sum;
    }
};
```

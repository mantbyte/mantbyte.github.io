---
layout: post
title: 'Daily DSA: Next Greater Element in a Circular Array (Medium)'
date: 2026-10-28 21:57:37 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Next Greater
  Element in a Circular Array.'
cover_image: /assets/images/posts/daily-dsa-next-greater-element-in-a-circular-array-2026-10-28-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

Given a circular integer array `nums` (i.e., the next element of `nums[nums.length - 1]` is `nums[0]`), return the **next greater number** for every element in `nums`.

The **next greater number** of a number `x` is the first greater number to its traversing-order next in the array, which means you could search circularly to find its next greater number. If it doesn't exist, return `-1` for this number.

### Examples

**Example 1:**
**Input:** `nums = [1, 2, 1]`
**Output:** `[2, -1, 2]`
**Explanation:** 
- The first 1's next greater number is 2.
- The number 2 has no next greater number.
- The second 1's next greater number needs to be searched circularly, which is also 2.

**Example 2:**
**Input:** `nums = [3, 8, 4, 1, 2]`
**Output:** `[8, -1, 8, 2, 3]`

### Constraints

- `1 <= nums.length <= 10^4`
- `-10^9 <= nums[i] <= 10^9`

---

### Approach

To solve this efficiently, we can use a **Monotonic Stack**. 

1.  **Circular Property:** Since the array is circular, we can simulate traversing the array twice (using indices `i % n`). This ensures that for any element, we check all other elements in the array to find a potential 'next greater' value.
2.  **Monotonic Decreasing Stack:** We maintain a stack of indices whose values are in non-increasing order. 
3.  **Traversing:** As we iterate through the simulated $2N$ length array:
    - While the stack is not empty and the current element `nums[i % n]` is greater than the element at the index stored at the top of the stack (`nums[stack.top()]`):
        - We have found the next greater element for `stack.top()`. 
        - Update `result[stack.top()] = nums[i % n]`.
        - Pop from the stack.
    - If we are in the first pass ($i < n$), push the current index `i` onto the stack.
4.  **Result:** Any index remaining in the stack after the two passes will have no next greater element, so those values remain `-1` (initialized default).

### Complexity Analysis

- **Time Complexity:** $O(N)$, where $N$ is the length of the array. Each index is pushed and popped from the stack at most once.
- **Space Complexity:** $O(N)$ to store the stack and the result array.

### C++ Solution

```cpp
#include <vector>
#include <stack>

using namespace std;

class Solution {
public:
    vector<int> nextGreaterElements(vector<int>& nums) {
        int n = nums.size();
        vector<int> res(n, -1);
        stack<int> st;

        // Traverse the array twice to simulate circularity
        for (int i = 0; i < 2 * n; ++i) {
            int currentVal = nums[i % n];
            
            // While current element is greater than the element at the index on top of stack
            while (!st.empty() && nums[st.top()] < currentVal) {
                res[st.top()] = currentVal;
                st.pop();
            }
            
            // Only push indices during the first pass
            if (i < n) {
                st.push(i);
            }
        }

        return res;
    }
};
```
{% endraw %}

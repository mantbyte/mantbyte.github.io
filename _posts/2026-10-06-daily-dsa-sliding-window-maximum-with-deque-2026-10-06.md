---
layout: post
title: 'Daily DSA: Sliding Window Maximum with Deque (Hard)'
date: 2026-10-06 21:57:08 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Sliding Window
  Maximum with Deque.'
cover_image: /assets/images/posts/daily-dsa-sliding-window-maximum-with-deque-2026-10-06-cover.png
cover_caption: ''
---

{% raw %}
# Problem Statement

You are given an array of integers `nums`, and there is a sliding window of size `k` which is moving from the very left of the array to the very left. You can only see the `k` numbers in the window. Each time the sliding window moves right by one position.

Return the max sliding window.

## Examples

### Example 1:
**Input:** `nums = [1,3,-1,-3,5,3,6,7], k = 3`
**Output:** `[3,3,5,5,6,7]`
**Explanation:**
```
Window position                Max
----------------ִ------------- -----
[1  3  -1] -3  5  3  6  7       3
 1 [3  -1  -3] 5  3  6  7       3
 1  3 [-1  -3  5] 3  6  7       5
 1  3  -1 [-3  5  3] 6  7       5
 1  3  -1  -3 [5  3  6] 7       6
 1  3  -1  -3  5 [3  6  7]      7
```

### Example 2:
**Input:** `nums = [1], k = 1`
**Output:** `[1]`

## Constraints:
- $1 \le \text{nums.length} \le 10^5$
- $-10^4 \le \text{nums}[i] \le 10^4$
- $1 \le k \le \text{nums.length}$

## Approach & Intuition
To solve this efficiently, we need a data structure that can provide the maximum element in the current window in $O(1)$ amortized time.
1. We can use a **Monotonic Decreasing Deque** (double-ended queue) to store the indices of the elements in the window.
2. The elements in the deque are kept in descending order of their values. This ensures that the front of the deque always contains the index of the maximum element for the current window.
3. As we slide the window:
   - **Remove elements outside the window:** From the front of the deque, pop indices that are less than `i - k + 1`.
   - **Maintain decreasing order:** From the back of the deque, pop indices whose corresponding values are less than or equal to `nums[i]`, as they cannot be the maximum.
   - **Push current index:** Push `i` to the back of the deque.
   - **Record the maximum:** Once the first window is formed (`i >= k - 1`), the front of the deque gives the maximum for the current window.

## C++ Solution

```cpp
#include <vector>
#include <deque>

class Solution {
public:
    std::vector<int> maxSlidingWindow(std::vector<int>& nums, int k) {
        std::deque<int> dq;
        std::vector<int> result;
        
        for (int i = 0; i < nums.size(); ++i) {
            // Remove elements out of the current window
            if (!dq.empty() && dq.front() <= i - k) {
                dq.pop_front();
            }
            
            // Maintain monotonic decreasing property
            while (!dq.empty() && nums[dq.back()] <= nums[i]) {
                dq.pop_back();
            }
            
            // Push current element index
            dq.push_back(i);
            
            // The first window is fully formed at i = k - 1
            if (i >= k - 1) {
                result.push_back(nums[dq.front()]);
            }
        }
        
        return result;
    }
};
```

## Complexity Analysis
- **Time Complexity:** $\mathcal{O}(N)$ where $N$ is the number of elements in `nums`. Each element is pushed and popped from the deque at most once.
- **Space Complexity:** $\mathcal{O}(k)$ to store indices in the deque for the window of size $k$.
{% endraw %}

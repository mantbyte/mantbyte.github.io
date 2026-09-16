---
layout: post
title: 'Daily DSA: Static Range GCD (Medium)'
date: 2026-09-16 20:03:28 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Static Range
  GCD.'
cover_image: /assets/images/posts/daily-dsa-static-range-gcd-2026-09-16-cover.png
cover_caption: ''
---

### Problem Statement

You are given an array of $n$ positive integers `nums` and a 2D array `queries` where `queries[i] = [L_i, R_i]`. For each query, calculate the **Greatest Common Divisor (GCD)** of all elements in the subarray `nums[L_i...R_i]` (inclusive).

Since the array is static (no updates), you should aim for an efficient solution that can handle a large number of queries.

### Examples

**Example 1:**
**Input:** `nums = [12, 18, 24, 36]`, `queries = [[0, 1], [1, 3], [0, 3]]`  
**Output:** `[6, 6, 6]`  
**Explanation:**
- `gcd(12, 18) = 6`
- `gcd(18, 24, 36) = 6`
- `gcd(12, 18, 24, 36) = 6`

**Example 2:**
**Input:** `nums = [7, 5, 11]`, `queries = [[0, 1], [0, 2]]`  
**Output:** `[1, 1]`  
**Explanation:**
- `gcd(7, 5) = 1`
- `gcd(7, 5, 11) = 1`

### Constraints

- $1 \le n, q \le 10^5$
- $1 \le nums[i] \le 10^9$
- $0 \le L_i \le R_i < n$

---

### Approach

To solve this problem efficiently, we can use a **Sparse Table**. 

1.  **Idempotency Property**: The GCD operation is idempotent, meaning $gcd(x, x) = x$. More importantly, $gcd(a, b, c) = gcd(gcd(a, b), gcd(b, c))$. This property allows us to compute the GCD of a range $[L, R]$ by combining the results of two overlapping sub-ranges that cover the entire range, as long as each sub-range has a length that is a power of 2.

2.  **Preprocessing**: 
    - We build a 2D table `st[k][n]`, where `st[j][i]` stores the GCD of the subarray starting at index `i` with length $2^j$.
    - Base case: `st[0][i] = nums[i]`.
    - Recursive step: `st[j][i] = gcd(st[j-1][i], st[j-1][i + 2^{j-1}])`.
    - This takes $O(n \log n)$ time.

3.  **Querying**:
    - For a range $[L, R]$, let $len = R - L + 1$.
    - Find the largest power of 2, $2^j$, such that $2^j \le len$.
    - The result is $gcd(st[j][L], st[j][R - 2^j + 1])$.
    - This takes $O(\log(\max(nums)))$ per query due to the GCD calculation.

### Complexity Analysis

- **Time Complexity**: $O(n \log n \cdot \log(\max(nums)))$ for preprocessing and $O(q \cdot \log(\max(nums)))$ for querying. Given the constraints, this fits well within the time limit.
- **Space Complexity**: $O(n \log n)$ to store the Sparse Table.

### C++ Implementation

```cpp
#include <vector>
#include <numeric>
#include <algorithm>

using namespace std;

class Solution {
public:
    vector<int> solveRangeGCD(vector<int>& nums, vector<vector<int>>& queries) {
        int n = nums.size();
        if (n == 0) return {};

        // Precompute logs for O(1) retrieval of largest power of 2
        vector<int> lg(n + 1, 0);
        for (int i = 2; i <= n; i++) {
            lg[i] = lg[i / 2] + 1;
        }

        int max_log = lg[n];
        // st[j][i] stores gcd of range [i, i + 2^j - 1]
        vector<vector<int>> st(max_log + 1, vector<int>(n));

        for (int i = 0; i < n; i++) {
            st[0][i] = nums[i];
        }

        for (int j = 1; j <= max_log; j++) {
            for (int i = 0; i + (1 << j) <= n; i++) {
                st[j][i] = std::gcd(st[j - 1][i], st[j - 1][i + (1 << (j - 1))]);
            }
        }

        vector<int> results;
        results.reserve(queries.size());

        for (const auto& q : queries) {
            int L = q[0];
            int R = q[1];
            int j = lg[R - L + 1];
            results.push_back(std::gcd(st[j][L], st[j][R - (1 << j) + 1]));
        }

        return results;
    }
};
```

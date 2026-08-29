---
layout: post
title: 'Daily DSA: Number of Non-Coprime Pairs (Hard)'
date: 2026-08-29 20:25:15 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Number of Non-Coprime
  Pairs.'
cover_image: /assets/images/posts/daily-dsa-number-of-noncoprime-pairs-2026-08-29-cover.png
cover_caption: ''
---

### Problem Statement

Given an array of integers `nums`, return the number of pairs `(i, j)` such that `0 <= i < j < nums.length` and the greatest common divisor $\text{gcd}(nums[i], nums[j]) > 1$.

### Examples

**Example 1:**

**Input:** `nums = [2, 4, 6]`
**Output:** `3`
**Explanation:** The pairs are:
- `(2, 4)` with $\text{gcd} = 2$
- `(2, 6)` with $\text{gcd} = 2$
- `(4, 6)` with $\text{gcd} = 2$
All 3 pairs have $\text{gcd} > 1$.

**Example 2:**

**Input:** `nums = [2, 3, 5]`
**Output:** `0`
**Explanation:** All pairs `(2, 3)`, `(2, 5)`, and `(3, 5)` have $\text{gcd} = 1$.

**Example 3:**

**Input:** `nums = [10, 6, 15, 4]`
**Output:** `5`
**Explanation:** The pairs with $\text{gcd} > 1$ are (10, 6), (10, 15), (10, 4), (6, 15), and (6, 4).

### Constraints

- `1 <= nums.length <= 10^5`
- `1 <= nums[i] <= 10^5`

### Approach

Calculating the GCD for every pair would result in an $O(N^2)$ solution, which is too slow for $N = 10^5$. Instead, we use a frequency-based counting approach with the principle of inclusion-exclusion.

1. **Count Frequencies**: Create a frequency array `freq` where `freq[x]` is the count of number `x` in `nums`.
2. **Count Multiples**: For each integer $g$ from 1 up to the maximum value $V$ in the array, calculate $C[g]$, the total number of elements in `nums` that are multiples of $g$. This is computed in $O(V \log V)$ using a sieve-like harmonic sum (iterating over multiples of $g$).
3. **Inclusion-Exclusion**: Let $P[g]$ be the number of pairs $(i, j)$ such that $\text{gcd}(nums[i], nums[j])$ is **exactly** $g$.
   - The number of pairs whose GCD is a **multiple** of $g$ is $M[g] = \frac{C[g](C[g]-1)}{2}$.
   - Using inclusion-exclusion, we find $P[g]$ by subtracting the counts of its proper multiples: $P[g] = M[g] - \sum_{k=2, 3, \dots} P[k \cdot g]$.
   - This calculation must be performed in decreasing order from $g = V$ down to 1 to ensure that $P[k \cdot g]$ is already computed when calculating $P[g]$.
4. **Final Result**: The answer is the sum of $P[g]$ for all $g > 1$.

### Complexity Analysis

- **Time Complexity**: $O(N + V \log V)$, where $N$ is the length of `nums` and $V$ is the maximum value in `nums` ($10^5$). The $V \log V$ part comes from the harmonic series $\sum_{g=1}^{V} \frac{V}{g}$.
- **Space Complexity**: $O(V)$ to store the frequency, multiples count, and pair count arrays.

### C++ Solution

```cpp
#include <vector>
#include <algorithm>

using namespace std;

class Solution {
public:
    long long countNonCoprimePairs(vector<int>& nums) {
        if (nums.empty()) return 0;
        
        int max_val = 0;
        for (int x : nums) {
            if (x > max_val) max_val = x;
        }
        
        vector<int> freq(max_val + 1, 0);
        for (int x : nums) {
            freq[x]++;
        }
        
        vector<long long> C(max_val + 1, 0);
        for (int i = 1; i <= max_val; ++i) {
            for (int j = i; j <= max_val; j += i) {
                C[i] += (long long)freq[j];
            }
        }
        
        vector<long long> P(max_val + 1, 0);
        long long totalNonCoprime = 0;
        for (int i = max_val; i >= 1; --i) {
            P[i] = (long long)C[i] * (C[i] - 1) / 2;
            for (int j = 2 * i; j <= max_val; j += i) {
                P[i] -= P[j];
            }
            if (i > 1) {
                totalNonCoprime += P[i];
            }
        }
        
        return totalNonCoprime;
    }
};
```

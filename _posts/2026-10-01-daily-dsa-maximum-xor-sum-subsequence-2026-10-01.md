---
layout: post
title: 'Daily DSA: Maximum XOR Sum Subsequence (Hard)'
date: 2026-10-01 22:21:03 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Maximum XOR Sum
  Subsequence.'
cover_image: /assets/images/posts/daily-dsa-maximum-xor-sum-subsequence-2026-10-01-cover.png
cover_caption: ''
---

### Problem Statement

You are given an array `nums` of $n$ non-negative integers. Your task is to find a subsequence (possibly empty) of the given array such that the bitwise XOR sum of its elements is maximized. 

A **subsequence** is a sequence that can be derived from another sequence by deleting zero or more elements without changing the order of the remaining elements. Since the bitwise XOR operation is commutative and associative, the order of elements does not matter.

### Examples

**Example 1:**
- **Input:** `nums = [3, 4, 5]`
- **Output:** `7`
- **Explanation:** 
    - Subsequences and their XOR sums:
        - `[3]` -> 3
        - `[4]` -> 4
        - `[5]` -> 5
        - `[3, 4]` -> 7 (011 ^ 100 = 111)
        - `[3, 5]` -> 6 (011 ^ 101 = 110)
        - `[4, 5]` -> 1 (100 ^ 101 = 001)
        - `[3, 4, 5]` -> 2 (011 ^ 100 ^ 101 = 010)
    - The maximum XOR sum is 7.

**Example 2:**
- **Input:** `nums = [8, 1, 2, 12, 7, 6]`
- **Output:** `15`
- **Explanation:** 
    - By picking the subsequence `[8, 7]`, we get `8 ^ 7 = 15` (1000 ^ 0111 = 1111).

### Constraints

- $1 \le n \le 10^5$
- $0 \le nums[i] \le 10^{18}$

---

### Approach: Linear Basis using Gaussian Elimination

To solve this problem efficiently, we use the concept of a **Linear Basis** (also known as XOR Basis). 

1.  **What is a Linear Basis?**
    A linear basis of a set of numbers is a small set of numbers that can represent the XOR sum of any subset of the original set. For numbers up to $10^{18}$ (which fit in 60-64 bits), the basis will contain at most 64 numbers.

2.  **How to build the Basis?**
    We iterate through each number $x$ in the input array. For each $x$, we try to insert it into the basis by iterating from the most significant bit (MSB) to the least significant bit:
    - If the $i$-th bit of $x$ is set:
        - If the basis doesn't have a value for the $i$-th bit (`basis[i] == 0`), we set `basis[i] = x` and stop.
        - If the basis already has a value `basis[i]`, we update $x = x \oplus basis[i]$ and continue to the next bit.

3.  **Finding the Maximum XOR Sum:**
    Once the basis is constructed, we start with a variable `max_xor = 0`. We iterate through the basis from the highest bit to the lowest. For each `basis[i]`, if XORing `max_xor` with `basis[i]` results in a larger value, we update `max_xor = max_xor ^ basis[i]`.

### Complexity Analysis

- **Time Complexity:** $O(n \cdot \log(\max(nums)))$. With $n = 10^5$ and $\log(\max(nums)) \approx 60$, this is roughly $6 \cdot 10^6$ operations, which easily fits within the time limit.
- **Space Complexity:** $O(\log(\max(nums)))$ to store the basis (at most 64 integers).

---

### C++ Solution

```cpp
#include <vector>
#include <algorithm>

using namespace std;

class Solution {
public:
    /**
     * @param nums: Vector of long long integers
     * @return: The maximum possible XOR sum of any subsequence
     */
    long long maximumXORSum(vector<long long>& nums) {
        // basis[i] stores a number whose highest set bit is the i-th bit
        vector<long long> basis(64, 0);

        for (long long x : nums) {
            for (int i = 62; i >= 0; i--) {
                // If the i-th bit of x is not set, skip it
                if (!(x & (1LL << i))) continue;

                if (!basis[i]) {
                    // If no number in basis has the i-th bit as MSB, insert x
                    basis[i] = x;
                    break;
                }

                // Otherwise, XOR x with the existing basis element and continue
                x ^= basis[i];
            }
        }

        long long max_xor = 0;
        // Greedy selection: start from the highest bit to maximize the result
        for (int i = 62; i >= 0; i--) {
            if ((max_xor ^ basis[i]) > max_xor) {
                max_xor ^= basis[i];
            }
        }

        return max_xor;
    }
};
```

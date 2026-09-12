---
layout: post
title: 'Daily DSA: Total Coprime Count (Medium)'
date: 2026-09-12 18:49:37 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Total Coprime
  Count.'
cover_image: /assets/images/posts/daily-dsa-total-coprime-count-2026-09-12-cover.png
cover_caption: ''
---

### Problem Description

Given an integer `n`, find the sum of Euler's totient function values for all integers from 1 to `n`. 

The Euler's totient function, denoted as $\phi(i)$, counts the number of positive integers up to $i$ that are relatively prime to $i$ (i.e., $\text{gcd}(i, k) = 1$ for $1 \le k \le i$).

### Examples

**Example 1:**
- **Input:** `n = 3`
- **Output:** `4`
- **Explanation:** 
  - $\phi(1) = 1$ (1 is coprime to 1)
  - $\phi(2) = 1$ (1 is coprime to 2)
  - $\phi(3) = 2$ (1 and 2 are coprime to 3)
  - Total sum: $1 + 1 + 2 = 4$.

**Example 2:**
- **Input:** `n = 10`
- **Output:** `32`
- **Explanation:** 
  - $\phi(1..10) = [1, 1, 2, 2, 4, 2, 6, 4, 6, 4]$
  - Total sum: $1+1+2+2+4+2+6+4+6+4 = 32$.

### Constraints

- $1 \le n \le 10^6$

### Approach

To solve this problem efficiently for $n$ up to $10^6$, we cannot calculate $\phi(i)$ for each $i$ independently using prime factorization, as that would take $O(n\sqrt{n})$ time. Instead, we use a **Linear Sieve** (also known as a multiplicative sieve) to precompute all $\phi$ values in $O(n)$ time.

**Properties of $\phi(i)$ used in the sieve:**
1. If $p$ is prime, $\phi(p) = p - 1$.
2. If $p$ divides $i$ (i.e., $i \% p == 0$), then $\phi(i \cdot p) = \phi(i) \cdot p$.
3. If $p$ does not divide $i$, then $\phi(i \cdot p) = \phi(i) \cdot (p - 1)$ (using the property that $\phi$ is a multiplicative function).

By iterating through numbers and maintaining a list of primes, we can calculate each $\phi(i)$ exactly once.

### Complexity Analysis
- **Time Complexity:** $O(n)$, as the linear sieve ensures each number is visited a constant number of times.
- **Space Complexity:** $O(n)$, required to store the $\phi$ values and the sieve arrays.

### C++ Solution

```cpp
#include <vector>
#include <iostream>

class Solution {
public:
    long long totalCoprimeCount(int n) {
        if (n < 1) return 0;
        
        std::vector<int> phi(n + 1);
        std::vector<int> primes;
        std::vector<char> is_prime(n + 1, 1);
        
        phi[1] = 1;
        for (int i = 2; i <= n; ++i) {
            if (is_prime[i]) {
                primes.push_back(i);
                phi[i] = i - 1;
            }
            for (int p : primes) {
                if (1LL * i * p > n) break;
                is_prime[i * p] = 0;
                if (i % p == 0) {
                    // p is a factor of i
                    phi[i * p] = phi[i] * p;
                    break;
                } else {
                    // p is not a factor of i
                    phi[i * p] = phi[i] * (p - 1);
                }
            }
        }
        
        long long total_sum = 0;
        for (int i = 1; i <= n; ++i) {
            total_sum += phi[i];
        }
        
        return total_sum;
    }
};
```

---
layout: post
title: 'Daily DSA: Count Alternating-Parity Integers with Divisible Digit Sum (Hard)'
date: 2026-10-20 20:08:21 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Count Alternating-Parity
  Integers with Divisible Digit Sum.'
cover_image: /assets/images/posts/daily-dsa-count-alternatingparity-integers-with-divisible-digit-sum-2026-10-20-cover.png
cover_caption: ''
---

{% raw %}
## Problem Statement

You are given two large positive integers represented as strings `low` and `high`, and a positive integer `k`.

An integer is defined as **valid** if it satisfies both of the following conditions:
1. **Alternating Parity:** No two adjacent decimal digits have the same parity. That is, if a digit is even, the immediately following digit must be odd, and if a digit is odd, the immediately following digit must be even. Single-digit numbers trivially satisfy this condition.
2. **Divisible Digit Sum:** The sum of all its digits is divisible by `k`.

Return the number of valid integers in the inclusive range `[low, high]`.

Since the answer may be very large, return it modulo $10^9 + 7$.

---

### Example 1

```text
Input: low = "10", high = "30", k = 3
Output: 5
Explanation: 
The valid integers between 10 and 30 are:
- 12: parities are [odd, even], sum = 1 + 2 = 3 (divisible by 3)
- 18: parities are [odd, even], sum = 1 + 8 = 9 (divisible by 3)
- 21: parities are [even, odd], sum = 2 + 1 = 3 (divisible by 3)
- 27: parities are [even, odd], sum = 2 + 7 = 9 (divisible by 3)
- 30: parities are [odd, even], sum = 3 + 0 = 3 (divisible by 3)
Total count is 5.
```

### Example 2

```text
Input: low = "1", high = "9", k = 2
Output: 4
Explanation: 
Single-digit integers trivially satisfy the alternating parity condition.
The integers with an even digit sum are 2, 4, 6, and 8. Thus, there are 4 valid integers.
```

### Example 3

```text
Input: low = "50", high = "100", k = 5
Output: 6
Explanation:
The valid integers are 50 (sum=5), 69 (sum=15), 78 (sum=15), 87 (sum=15), 96 (sum=15), and 104 is out of range. 
Among integers up to 100, the valid ones in [50, 100] are 50, 69, 78, 87, 96. Note: 100 has adjacent digits '0' and '0' (both even), so it is invalid.
```

---

### Constraints

- $1 \le \text{low.length} \le \text{high.length} \le 500$
- `low` and `high` consist only of decimal digits and do not contain leading zeros.
- Numerically, $\text{low} \le \text{high}$.
- $1 \le k \le 50$

---

## Approach / Hints

1. **Range Query Decomposition:**
   Instead of counting directly in the range `[low, high]`, compute `f(high)` which counts valid numbers in `[1, high]`, and `f(low)` which counts valid numbers in `[1, low]`. The answer is `(f(high) - f(low) + isValid(low)) % MOD`.

2. **Digit DP State Representation:**
   Process the digits from the most significant to the least significant (index $0$ to $N - 1$).
   We define our DP state as `dp(idx, sum_mod, last_parity, is_less)`:
   - `idx`: Current digit position we are placing ($0$ to $N-1$).
   - `sum_mod`: Sum of chosen digits modulo $k$ ($0$ to $k - 1$).
   - `last_parity`: Parity of the previous non-leading-zero digit. We can represent this with `0` (even), `1` (odd), or `2` (no digit placed yet / leading zeros).
   - `is_less`: A boolean flag indicating whether the prefix placed so far is strictly less than the prefix of the boundary string.

3. **Transitions:**
   - The upper bound for the current digit $d$ is $9$ if `is_less` is true, or the digit in the boundary string otherwise.
   - If we haven't started forming the number yet (`last_parity == 2`):
     - We can place $0$, remaining in the non-started state (`last_parity = 2`, `sum_mod = 0`).
     - Or place $d \in [1, \text{limit}]$, transitioning to `last_parity = d % 2` and `sum_mod = d % k`.
   - If the number has started (`last_parity` is 0 or 1):
     - We can place any digit $d$ where $d \% 2 \ne \text{last\_parity}$.
     - The new `sum_mod` becomes `(sum_mod + d) % k` and `last_parity` becomes `d % 2`.

4. **Base Case:**
   - When `idx == N`, we return $1$ if `last_parity != 2` and `sum_mod == 0`, otherwise $0$.

5. **Complexity:**
   - Total number of states: $N \times k \times 3 \times 2$.
   - For $N = 500$ and $k = 50$, the number of states is $500 \times 50 \times 3 \times 2 = 150{,}000$.
   - From each state, we iterate over at most 10 digits. Total transitions $\approx 1.5 \times 10^6$, which easily runs well within the 1-second time limit in C++.

---

## C++ Solution

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cstring>

using namespace std;

class Solution {
    static const int MOD = 1e9 + 7;
    int memo[505][55][3][2];

    int solve(int idx, int sum_mod, int last_parity, bool is_less, const string& S, int k) {
        if (idx == (int)S.size()) {
            return (last_parity != 2 && sum_mod == 0) ? 1 : 0;
        }

        if (memo[idx][sum_mod][last_parity][is_less] != -1) {
            return memo[idx][sum_mod][last_parity][is_less];
        }

        int limit = is_less ? 9 : (S[idx] - '0');
        long long ans = 0;

        for (int d = 0; d <= limit; ++d) {
            bool next_less = is_less || (d < limit);

            if (last_parity == 2) {
                if (d == 0) {
                    // Still leading zero
                    ans = (ans + solve(idx + 1, 0, 2, next_less, S, k)) % MOD;
                } else {
                    // First non-zero digit
                    ans = (ans + solve(idx + 1, d % k, d % 2, next_less, S, k)) % MOD;
                }
            } else {
                // Must alternate parity
                if (d % 2 != last_parity) {
                    ans = (ans + solve(idx + 1, (sum_mod + d) % k, d % 2, next_less, S, k)) % MOD;
                }
            }
        }

        return memo[idx][sum_mod][last_parity][is_less] = ans;
    }

    int countUpTo(const string& S, int k) {
        memset(memo, -1, sizeof(memo));
        return solve(0, 0, 2, false, S, k);
    }

    bool isValid(const string& S, int k) {
        int sum = 0;
        for (int i = 0; i < (int)S.size(); ++i) {
            sum += (S[i] - '0');
            if (i > 0 && (S[i] - '0') % 2 == (S[i - 1] - '0') % 2) {
                return false;
            }
        }
        return (sum % k == 0);
    }

public:
    int countAlternatingParity(string low, string high, int k) {
        long long count_high = countUpTo(high, k);
        long long count_low = countUpTo(low, k);
        long long ans = (count_high - count_low + (isValid(low, k) ? 1 : 0)) % MOD;
        if (ans < 0) {
            ans += MOD;
        }
        return ans;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(N \times k \times D)$, where $N$ is the number of digits in `high` ($N \le 500$), $k$ is the divisor ($k \le 50$), and $D = 10$ is the base size. Total operations $\le 1.5 \times 10^6$, running in under $50\text{ ms}$.
- **Space Complexity:** $\mathcal{O}(N \times k)$ for the 4-dimensional memoization table and recursion stack.
{% endraw %}

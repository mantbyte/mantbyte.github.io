---
layout: post
title: 'Daily DSA: Count Parity-Alternating Integers in Range (Hard)'
date: 2026-08-21 15:54:26 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Count Parity-Alternating
  Integers in Range.'
cover_image: /assets/images/posts/daily-dsa-count-parityalternating-integers-in-range-2026-08-21-cover.png
cover_caption: ''
---

### Problem Description

An integer is called **parity-alternating** if for every pair of adjacent digits in its standard decimal representation (without leading zeros), one digit is even and the other is odd. Single-digit numbers are trivially parity-alternating.

For example:
- `2385`, `703`, and `4` are parity-alternating integers.
- `248` (adjacent evens), `135` (adjacent odds), and `1223` are not parity-alternating integers.

Given two positive integers represented as strings `low` and `high`, return the total number of parity-alternating integers $x$ such that $\text{low} \le x \le \text{high}$.

Since the answer can be very large, return it modulo $10^9 + 7$.

---

### Examples

**Example 1:**
```
Input: low = "1", high = "15"
Output: 12
Explanation: 
- The numbers 1 through 9 are all single digits and thus alternating (9 numbers).
- In the range 10-15: 10, 12, and 14 are alternating (3 numbers).
- 11, 13, and 15 have adjacent odd digits, so they are not alternating.
Total count = 9 + 3 = 12.
```

**Example 2:**
```
Input: low = "20", high = "35"
Output: 8
Explanation:
The alternating numbers in this range are: 21, 23, 25, 27, 29, 30, 32, and 34 (8 numbers).
```

**Example 3:**
```
Input: low = "88", high = "105"
Output: 6
Explanation:
The valid numbers are 89, 90, 92, 94, 96, 98.
```

---

### Constraints

- $1 \le \text{low.length} \le \text{high.length} \le 1000$
- `low` and `high` consist only of decimal digits `'0'` - `'9'`.
- `low` and `high` do not have leading zeros.
- The integer represented by `low` is less than or equal to the integer represented by `high`.

---

### Approach

To find the count of valid numbers in the range $[\text{low}, \text{high}]$, we can use the prefix technique:
$$\text{Count}([\text{low}, \text{high}]) = \text{Count}([1, \text{high}]) - \text{Count}([1, \text{low}]) + \text{isAlternating}(\text{low})$$

To compute $\text{Count}([1, S])$ for any string $S$, we apply **Digit DP** (Digit Dynamic Programming):

1. **DP State Representation**:
   `dp(idx, last_parity, is_less, is_started)`
   - `idx`: Current digit position in string $S$ (from $0$ to $N-1$).
   - `last_parity`: Parity of the previous placed digit (`0` for even, `1` for odd, `2` for unassigned / leading zeros).
   - `is_less`: Boolean flag indicating whether the current prefix is already strictly smaller than the prefix of $S$.
   - `is_started`: Boolean flag indicating whether we have placed at least one non-zero digit (to handle variable length numbers).

2. **Transitions**:
   - Determine the upper bound for the current digit: `limit = is_less ? 9 : (S[idx] - '0')`.
   - Iterate through every possible digit $d \in [0, \text{limit}]$:
     - If `!is_started && d == 0`: We continue placing leading zeros. The state transitions to `(idx + 1, 2, is_less || (d < limit), false)`.
     - Otherwise (placing an actual digit): The parity of $d$ is $p = d \pmod 2$.
     - If `is_started && p == last_parity`, this digit choice is invalid (same parity adjacent).
     - If valid, transition to `(idx + 1, p, is_less || (d < limit), true)`.

3. **Base Case**:
   - When `idx == N`, return `1` if `is_started` is `true`, otherwise `0`.

4. **Complexity**:
   - **Time Complexity**: $O(N \times 3 \times 2 \times 2 \times 10) = O(N)$ where $N$ is the number of digits in $S$. For $N \le 1000$, this executes in a few milliseconds.
   - **Space Complexity**: $O(N)$ for the memoization table and recursion stack.

---

### C++ Solution

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cstring>

class Solution {
private:
    static const int MOD = 1e9 + 7;
    int memo[1005][3][2][2];

    int solveDP(int idx, int last_parity, bool is_less, bool is_started, const std::string& s) {
        if (idx == (int)s.length()) {
            return is_started ? 1 : 0;
        }

        if (memo[idx][last_parity][is_less][is_started] != -1) {
            return memo[idx][last_parity][is_less][is_started];
        }

        int limit = is_less ? 9 : (s[idx] - '0');
        long long total = 0;

        for (int digit = 0; digit <= limit; ++digit) {
            bool next_less = is_less || (digit < limit);
            
            if (!is_started && digit == 0) {
                // Still in leading zero state
                total = (total + solveDP(idx + 1, 2, next_less, false, s)) % MOD;
            } else {
                int cur_parity = digit % 2;
                if (!is_started || cur_parity != last_parity) {
                    total = (total + solveDP(idx + 1, cur_parity, next_less, true, s)) % MOD;
                }
            }
        }

        return memo[idx][last_parity][is_less][is_started] = total;
    }

    int countUpTo(const std::string& s) {
        std::memset(memo, -1, sizeof(memo));
        return solveDP(0, 2, false, false, s);
    }

    bool isValid(const std::string& s) {
        for (size_t i = 1; i < s.length(); ++i) {
            if ((s[i] - '0') % 2 == (s[i - 1] - '0') % 2) {
                return false;
            }
        }
        return true;
    }

public:
    int countAlternatingIntegers(std::string low, std::string high) {
        int count_high = countUpTo(high);
        int count_low = countUpTo(low);
        int is_low_valid = isValid(low) ? 1 : 0;

        int result = (count_high - count_low + is_low_valid) % MOD;
        if (result < 0) {
            result += MOD;
        }
        return result;
    }
};
```

---
layout: post
title: 'Daily DSA: Count Orthogonal Bitwise Pairs (Hard)'
date: 2026-10-17 18:55:28 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Count Orthogonal
  Bitwise Pairs.'
cover_image: /assets/images/posts/daily-dsa-count-orthogonal-bitwise-pairs-2026-10-17-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are given an integer array `nums` of length `n`.

A pair of indices `(i, j)` is called **orthogonal** if:
- `0 <= i < j < n`
- `nums[i] & nums[j] == 0`

where `&` denotes the bitwise AND operator.

Return the total number of orthogonal pairs in `nums`.

---

### Examples

**Example 1:**
```text
Input: nums = [1, 2, 4]
Output: 3
Explanation: 
The binary representations are:
- 1 = 001_2
- 2 = 010_2
- 4 = 100_2

Pair evaluations:
- (0, 1): 1 & 2 = 0
- (0, 2): 1 & 4 = 0
- (1, 2): 2 & 4 = 0
All 3 pairs have a bitwise AND equal to 0.
```

**Example 2:**
```text
Input: nums = [0, 1, 2, 3]
Output: 4
Explanation:
The orthogonal pairs are:
- (0, 1): 0 & 1 = 0
- (0, 2): 0 & 2 = 0
- (0, 3): 0 & 3 = 0
- (1, 2): 1 & 2 = 0
Pairs (1, 3) and (2, 3) are not orthogonal because 1 & 3 = 1 and 2 & 3 = 2.
Total orthogonal pairs = 4.
```

**Example 3:**
```text
Input: nums = [3, 5, 7]
Output: 0
Explanation:
- 3 & 5 = 1
- 3 & 7 = 3
- 5 & 7 = 5
There are no orthogonal pairs.
```

---

### Constraints

- `1 <= nums.length <= 10^5`
- `0 <= nums[i] < 2^18` (i.e., `0 <= nums[i] <= 262143`)

---

### Approach

#### 1. Algebraic Reformulation
Two numbers $x$ and $y$ satisfy $x \ \& \ y = 0$ if and only if for every bit set in $x$, the corresponding bit in $y$ is $0$. 
In bitmask terms, if we consider all numbers within $B = 18$ bits, $y$ must be a **submask** of the bitwise complement of $x$:
$$
y \subseteq ((2^B - 1) \oplus x)
$$

Thus, for each number $x$, we need to count how many elements in `nums` are submasks of its complement $\sim x$.

#### 2. Sum Over Subsets (SOS DP)
Let $freq[mask]$ be the frequency of $mask$ in `nums`.
We want to compute for every mask $M$:
$$F[M] = \sum_{sub \subseteq M} freq[sub]$$

A naive iteration over all submasks for each mask takes $O(3^B)$ time, which is too slow for $B = 18$ ($3^{18} \approx 3.87 \times 10^8$).

Instead, we can use **SOS DP** (Sum Over Subsets Dynamic Programming) which computes this prefix sum over the hypercube in $O(B \cdot 2^B)$ time:
- Iterate over each bit $i$ from $0$ to $B - 1$.
- For every mask where bit $i$ is set, add $F[mask \oplus 2^i]$ to $F[mask]$.

#### 3. Counting Pairs and Handling Edge Cases
After computing $F[mask]$ for all $mask < 2^B$:
- For each element $x \in nums$, the number of elements $y$ such that $x \ \& \ y = 0$ is $F[\sim x]$.
- Note that if $x = 0$, $\sim x = 2^B - 1$, so $0 \subseteq \sim 0$, meaning $x = 0$ counts itself. For $x > 0$, $x$ cannot be a submask of $\sim x$ because $x \ \& \ x \ne 0$.
- Therefore, if $x == 0$, we subtract $1$ from $F[\sim x]$ to avoid pairing an element with itself.
- Sum these counts for all elements and divide by $2$ because each pair $(i, j)$ is counted twice.

---

### C++ Source Code

```cpp
#include <vector>

class Solution {
public:
    long long countOrthogonalPairs(std::vector<int>& nums) {
        const int B = 18;
        const int MAX_VAL = 1 << B;
        const int FULL_MASK = MAX_VAL - 1;

        // Step 1: Count frequency of each number
        std::vector<int> F(MAX_VAL, 0);
        for (int x : nums) {
            F[x]++;
        }

        // Step 2: Sum Over Subsets (SOS) DP
        for (int i = 0; i < B; ++i) {
            for (int mask = 0; mask < MAX_VAL; ++mask) {
                if (mask & (1 << i)) {
                    F[mask] += F[mask ^ (1 << i)];
                }
            }
        }

        // Step 3: Count total matching pairs
        long long total_matches = 0;
        for (int x : nums) {
            int comp = FULL_MASK ^ x;
            long long valid_candidates = F[comp];
            
            // An element can only pair with itself if x & x == 0 (which means x == 0)
            if (x == 0) {
                valid_candidates--;
            }
            
            total_matches += valid_candidates;
        }

        // Each unordered pair (i, j) was counted twice (once for i, once for j)
        return total_matches / 2;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $O(n + B \cdot 2^B)$, where $n$ is the size of `nums` and $B = 18$.
  - Frequency count: $O(n)$.
  - SOS DP transitions: $18 \times 2^{18} \approx 4.7 \times 10^6$ operations, which easily runs in $\approx 20$ ms.
  - Final summation: $O(n)$.
  - Overall runtime is well within the 1-second limit.

- **Space Complexity:** $O(2^B)$ auxiliary space for the DP array `F`, which requires $2^{18} \times 4$ bytes $\approx 1\text{ MB}$ of memory.
{% endraw %}

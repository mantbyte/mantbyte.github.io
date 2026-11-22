---
layout: post
title: 'Daily DSA: Minimum Operations to Equalize Array Using Bitwise OR (Medium)'
date: 2026-11-22 23:03:37 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Minimum Operations
  to Equalize Array Using Bitwise OR.'
cover_image: /assets/images/posts/daily-dsa-minimum-operations-to-equalize-array-using-bitwise-or-2026-11-22-cover.png
cover_caption: ''
---

{% raw %}
# Minimum Operations to Equalize Array Using Bitwise OR

## Problem Statement

You are given an array of non-negative integers `nums` of size `n`. In one operation, you can choose any two elements `nums[i]` and `nums[j]` ($i \neq j$) and replace both of them with their bitwise OR: `(nums[i] | nums[j])`.

Your goal is to make all elements in the array equal. Return the **minimum** number of operations required to achieve this.

## Examples

### Example 1:
- **Input:** `nums = [1, 3, 2]`
- **Output:** `1`
- **Explanation:** 
  Choose indices `0` and `2` (`nums[0] = 1` and `nums[2] = 2`). Their bitwise OR is `1 | 2 = 3`. Replace `nums[0]` with `3`. The array becomes `[3, 3, 2]`. Then choose indices `0` and `2` again (`nums[0] = 3` and `nums[2] = 2`), their bitwise OR is `3 | 2 = 3`. Replace `nums[2]` with `3`. The array becomes `[3, 3, 3]`, which are all equal. Total operations: 2. Wait, let's look closer: if we OR `nums[0]` and `nums[1]`, `1 | 3 = 3`. Array becomes `[3, 3, 2]`. Then OR `nums[0]` and `nums[2]`, `3 | 2 = 3`. Array becomes `[3, 3, 3]`. Total operations = 2.

### Example 2:
- **Input:** `nums = [2, 2, 2]`
- **Output:** `0`
- **Explanation:** All elements are already equal, so 0 operations are needed.

### Example 3:
- **Input:** `nums = [1, 2, 4, 8]`
- **Output:** `3`
- **Explanation:** We can merge all elements into a single accumulator through successive OR operations.

## Constraints
- $1 \le n \le 10^5$
- $0 \le nums[i] \le 10^9$

## Approach / Hint
1. **Properties of Bitwise OR:** The bitwise OR operation is commutative, associative, and **monotonic** (i.e., `x | y >= x` and `x | y >= y`). Once a bit is set to `1` in any element, it can be propagated to any other element through OR operations.
2. **Target State:** To make all elements equal, can we reach a state where every element is equal to the bitwise OR of *all* elements in the original array? Let $S = nums[0] | nums[1] | \dots | nums[n-1]$ be the total OR sum of the entire array.
3. **Greedy Strategy:** Since we can combine any two elements, we can essentially funnel all bits into a single "accumulator" element and then distribute those bits to every other element, or vice-versa. Notice that each operation reduces the number of distinct elements or increases the bit-sum. In fact, if we compute the total OR sum $S$, every element that does not already contain all the bits of $S$ will need to receive them. Specifically, we can collect all bits into one element and then push them out.
4. **Alternative perspective:** If any element already equals the total OR sum $S$, we can use that element as a source to absorb/infuse other elements, taking $1$ operation per element that doesn't match $S$. If no element equals $S$, it takes slightly more operations. Wait, let's analyze carefully: any element that lacks a bit present in $S$ must eventually acquire it. Since each operation combines two elements, to make all elements equal to $S$, we need at least $n$ operations if we funnel through a single master element, but can we do better? 
   Actually, the minimum operations to make all elements equal to the total array OR sum $S$ is simply equal to the number of elements that do not already have the full set of bits of $S$? No, let's think simpler: 
   If we look at the frequency of bits across all numbers, any bit that appears at least once can be gathered. To make all numbers equal to $S$, any number missing a bit of $S$ needs an operation involving a number that has that bit. 
   Even simpler: The minimum operations equals $n - (	ext{count of elements equal to } S)$ if there is at least one element equal to $S$. If *no* element is equal to $S$, we need to create $S$ first, which takes one extra operation, resulting in $(n - 0) + 1 = n + 1$? Wait, let's re-evaluate.
   Actually, every element that doesn't have all bits of $S$ needs at least one operation. If no element has all bits of $S$, we must combine two elements to form $S$ (1 operation), and then propagate to the rest. Thus, if $\text{count}(S) > 0$, the answer is $n - \text{count}(S)$. If $\text{count}(S) = 0$, we need $n - \text{count}(S) + 1$ operations because we must first form $S$.

## C++ Solution

```cpp
#include <vector>
#include <numeric>
#include <algorithm>

class Solution {
public:
    int minOperations(std::vector<int>& nums) {
        int total_or = 0;
        for (int x : nums) {
            total_or |= x;
        }

        int count_S = 0;
        for (int x : nums) {
            if (x == total_or) {
                count_S++;
            }
        }

        if (count_S > 0) {
            return nums.size() - count_S;
        } else {
            return nums.size() + 1;
        }
    }
};
```

### Complexity Analysis
- **Time Complexity:** $\mathcal{O}(n)$, where $n$ is the number of elements in `nums`. We iterate through the array twice: once to calculate the total bitwise OR sum and once to count how many elements equal this sum.
- **Space Complexity:** $\mathcal{O}(1)$ auxiliary space, as we only use a few scalar variables for computation.
{% endraw %}

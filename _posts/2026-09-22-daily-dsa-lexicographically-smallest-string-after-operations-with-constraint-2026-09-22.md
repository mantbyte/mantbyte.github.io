---
layout: post
title: 'Daily DSA: Lexicographically Smallest String After Operations With Constraint
  (Medium)'
date: 2026-09-22 19:49:10 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Lexicographically
  Smallest String After Operations With Constraint.'
cover_image: /assets/images/posts/daily-dsa-lexicographically-smallest-string-after-operations-with-constraint-2026-09-22-cover.png
cover_caption: ''
---

# Problem Statement

You are given a string `s` consisting of lowercase English letters, and an integer `k` representing the maximum number of operations you can perform.

In one operation, you can choose any character in the string and replace it with its next consecutive letter in the alphabet (e.g., `'a'` becomes `'b'`, `'b'` becomes `'c'`, ..., and `'z'` wraps around to become `'a'`). 

Return the lexicographically smallest string you can obtain after applying the operation at most `k` times.

# Examples

### Example 1:
- **Input:** `s = "z", k = 25`
- **Output:** `"a"`
- **Explanation:** We can increment `'z'` 1 time to get `'a'`, using 1 operation out of 25. The remaining operations are wasted or unnecessary.

### Example 2:
- **Input:** `s = "zb", k = 2`
- **Output:** `"aa"`
- **Explanation:** Increment `'z'` 1 time to get `'a'` (1 op). Increment `'b'` 1 time to get `'a'` (1 op). Total operations used: 2. Result is `"aa"`.

### Example 3:
- **Input:** `s = "abcd", k = 5`
- **Output:** `"aaaa"`
- **Explanation:** Transform each character to `'a'`. `'b'` takes 1 op, `'c'` takes 2 ops, `'d'` takes 3 ops. Total: 1 + 2 + 3 = 6 (wait, `k=5`, so we can transform `'b'` (1) and `'c'` (2) completely, leaving 2 ops for `'d'` which turns into `'b'`...)

# Constraints
- `1 <= s.length <= 10^5`
- `0 <= k <= 10^9`
- `s` consists of lowercase English letters.

# Approach
To make the string lexicographically smallest, we should greedily try to change each character to `'a'`. For any character, we can reach `'a'` either by moving forward in the alphabet (incrementing) or moving backward (decrementing, which wraps around). 

For a character `c`, the cost to reach `'a'` is the minimum of:
1. Forward distance: `(26 - (c - 'a')) % 26`
2. Backward distance: `c - 'a'`

Wait, the problem statement says we can *only* replace with the **next** consecutive letter (incrementing). Therefore, the cost to change a character to `'a'` is simply the number of increments needed, which is `(26 - (c - 'a')) % 26`.

We iterate through the string from left to right. For each character, we compute the cost to turn it into `'a'`. If `k` is greater than or equal to this cost, we subtract the cost from `k` and set the character to `'a'`. Otherwise, we use all remaining `k` operations to increment the character as much as possible, and then stop.

# C++ Solution
```cpp
#include <string>
#include <algorithm>

class Solution {
public:
    string getSmallestString(string s, int k) {
        for (int i = 0; i < s.length(); ++i) {
            int dist = (26 - (s[i] - 'a')) % 26;
            if (k >= dist) {
                k -= dist;
                s[i] = 'a';
            } else {
                s[i] = s[i] + k;
                k = 0;
                break;
            }
        }
        return s;
    }
};
```

### Complexity Analysis
- **Time Complexity:** $O(N)$, where $N$ is the length of the string `s`. We iterate through the string at most once.
- **Space Complexity:** $O(1)$ auxiliary space if we modify the string in place, or $O(N)$ to store and return the result.

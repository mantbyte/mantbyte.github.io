---
layout: post
title: 'Daily DSA: Lexicographically Smallest String After Operations With Constraint
  (Medium)'
date: 2026-09-08 19:36:58 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Lexicographically
  Smallest String After Operations With Constraint.'
cover_image: /assets/images/posts/daily-dsa-lexicographically-smallest-string-after-operations-with-constraint-2026-09-08-cover.png
cover_caption: ''
---

# Problem Statement

You are given a string `s` consisting of lowercase English letters and an integer `k`.

You are allowed to perform the following operation on `s` any number of times:
- Choose any character in `s` and change it to either the immediately preceding letter in the alphabet (with 'a' preceding 'z') or the immediately following letter (with 'z' following 'a').

However, you have a total budget of `k` operations. Specifically, changing a character from `c1` to `c2` costs the minimum number of cyclic steps in the alphabet between `c1` and `c2`.

Return the lexicographically smallest string you can obtain after using **at most** `k` operations.

---

## Examples

### Example 1:
- **Input:** `s = "zba", k = 3`
- **Output:** "aaa"
- **Explanation:** 
  - Change 'z' to 'a' using 1 operation (cost: 1, since z -> a is 1 step).
  - 'b' is already 'a' or can be changed to 'a' using 1 operation.
  - 'a' requires 0 operations.
  - Total operations used: 1 + 1 + 0 = 2 <= 3. The resulting string is "aaa".

### Example 2:
- **Input:** `s = "leetcode", k = 5`
- **Output:** "aeatcode"
- **Explanation:** 
  - Change 'l' (12th letter) towards 'a' (1st letter). The minimum cyclic distance is `min(12 - 1, 26 - 12 + 1) = min(11, 15) = 11`. But we only have $k = 5$ operations, so we can decrease 'l' by 5 to get 'g'. Wait, we want the lexicographically smallest. For each character, we should greedily try to turn it into 'a' if we have enough budget. If we don't have enough budget, we reduce it as much as possible.

---

## Constraints
- `1 <= s.length <= 100`
- `0 <= k <= 2000`
- `s` consists of lowercase English letters.

---

## Approach

To find the lexicographically smallest string, we should process the characters from left to right (greedy approach) and try to make each character as small as possible ('a') using the available budget `k`.

For each character `c` in `s`:
1. Calculate the cost to change `c` to 'a'. The cost is `min(c - 'a', 'z' - c + 1)`.
2. If `k` is greater than or equal to this cost, we can afford to change `c` to 'a'. We subtract the cost from `k` and set `c = 'a'`.
3. If `k` is less than the cost, we cannot reach 'a'. To make it as small as possible, we should decrease it by `k` steps (i.e., `c = c - k`) and set `k = 0`, since our budget is now exhausted.

---

## C++ Code

```cpp
#include <string>
#include <algorithm>

class Solution {
public:
    string getSmallestString(string s, int k) {
        for (int i = 0; i < s.length(); ++i) {
            int dist_to_a = std::min(s[i] - 'a', 'z' - s[i] + 1);
            if (k >= dist_to_a) {
                k -= dist_to_a;
                s[i] = 'a';
            } else {
                s[i] = s[i] - k;
                k = 0;
                break;
            }
        }
        return s;
    }
};
```

## Complexity Analysis
- **Time Complexity:** $O(N)$, where $N$ is the length of the string `s`. We iterate through the string at most once.
- **Space Complexity:** $O(1)$ auxiliary space if we modify the string in-place, or $O(N)$ to return the new string.

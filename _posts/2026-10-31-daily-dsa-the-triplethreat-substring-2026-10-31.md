---
layout: post
title: 'Daily DSA: The Triple-Threat Substring (Medium)'
date: 2026-10-31 21:06:22 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: The Triple-Threat
  Substring.'
cover_image: /assets/images/posts/default-cover.png
cover_caption: ''
---

{% raw %}
### Problem Description

Given a string `s`, find the longest substring `t` that satisfies the following three conditions:
1. `t` is a **prefix** of `s`.
2. `t` is a **suffix** of `s`.
3. `t` appears elsewhere in `s` as a **middle occurrence**. 

An occurrence is considered "middle" if it starts at an index `i > 0` and ends at an index `j < s.length() - 1`. In other words, the occurrence must not be the prefix starting at index 0 and must not be the suffix ending at index `n-1`.

If no such substring exists, return an empty string.

### Examples

**Example 1:**
- **Input:** `s = "fixprefixsuffix"`
- **Output:** `"fix"`
- **Explanation:** "fix" is a prefix (indices 0-2), a suffix (indices 12-14), and also appears in the middle starting at index 9 (indices 9-11).

**Example 2:**
- **Input:** `s = "aaaaa"`
- **Output:** `"aaa"`
- **Explanation:** "aaa" is a prefix (0-2), a suffix (2-4), and appears in the middle (indices 1-3).

**Example 3:**
- **Input:** `s = "abcdabc"`
- **Output:** `""`
- **Explanation:** Although "abc" is a prefix and a suffix, it does not appear anywhere in the middle of the string.

### Constraints

- `1 <= s.length() <= 10^6`
- `s` consists of lowercase English letters.

### Approach

To solve this problem in $O(N)$ time, we can use the **Z-Algorithm**.

The Z-array `z[i]` stores the length of the longest common prefix (LCP) between the original string `s` and the suffix of `s` starting at index `i`.

1. **Compute the Z-array**: Using the standard Z-algorithm, we can find all prefix matches in linear time.
2. **Identify Middle Occurrences**: For any index $i > 0$, `z[i]` tells us that the prefix of length `z[i]` occurs starting at index $i$. 
   - If $i + z[i] < n$, the entire prefix of length `z[i]` is contained within the middle/suffix part. Since it doesn't reach the end, it is a "middle" occurrence.
   - If $i + z[i] == n$, the occurrence is a suffix. However, the prefix of length `z[i] - 1` starting at $i$ would end at $n-2$, making it a "middle" occurrence.
   - We track the maximum such length as `max_mid`.
3. **Identify Suffixes**: A length $L$ is a suffix candidate if there exists an index $i$ such that $i + z[i] == n$ and $z[i] = L$.
4. **Selection**: The result is the largest $L$ that is a suffix candidate and satisfies $L \le max\_mid$.

### Solution (C++)

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

class Solution {
public:
    string longestTripleThreat(string s) {
        int n = s.length();
        if (n < 3) return "";

        // Compute Z-array
        vector<int> z(n, 0);
        int l = 0, r = 0;
        for (int i = 1; i < n; i++) {
            if (i <= r) 
                z[i] = min(r - i + 1, z[i - l]);
            while (i + z[i] < n && s[z[i]] == s[i + z[i]]) 
                z[i]++;
            if (i + z[i] - 1 > r) {
                l = i;
                r = i + z[i] - 1;
            }
        }

        // Find the maximum length of any prefix that appears in the middle.
        // A prefix starting at i is 'middle' if it ends before index n-1.
        int max_mid = 0;
        for (int i = 1; i < n; i++) {
            if (i + z[i] == n) {
                // If it's a suffix, the prefix of length z[i]-1 is middle.
                max_mid = max(max_mid, z[i] - 1);
            } else {
                // If it's not a suffix, the whole z[i] is middle.
                max_mid = max(max_mid, z[i]);
            }
        }

        // Find the longest suffix length L such that L <= max_mid.
        int best_l = 0;
        for (int i = 1; i < n; i++) {
            if (i + z[i] == n) {
                if (z[i] <= max_mid) {
                    best_l = max(best_l, z[i]);
                }
            }
        }

        if (best_l == 0) return "";
        return s.substr(0, best_l);
    }
};
```

### Complexity Analysis

- **Time Complexity:** $O(N)$, where $N$ is the length of the string. The Z-algorithm and the subsequent loops each process the string in linear time.
- **Space Complexity:** $O(N)$ to store the Z-array.
{% endraw %}

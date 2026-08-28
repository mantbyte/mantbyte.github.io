---
layout: post
title: 'Daily DSA: String Score via Z-Algorithm (Hard)'
date: 2026-08-29 02:36:20 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: String Score
  via Z-Algorithm.'
cover_image: /assets/images/posts/daily-dsa-string-score-via-zalgorithm-2026-08-28-cover.png
cover_caption: ''
---

### Problem Statement

You are building a string `s` of length `n`. The **score** of the string is defined as the sum of the lengths of the **Longest Common Prefix (LCP)** between `s` and all its suffixes $S[i \dots n-1]$ for $i = 0$ to $n-1$.

Given a string `s`, return its total score.

### Examples

**Example 1:**
**Input:** `s = "babab"`  
**Output:** `9`  
**Explanation:**  
- Suffix starting at index 0: "babab", LCP with "babab" is 5.  
- Suffix starting at index 1: "abab", LCP with "babab" is 0.  
- Suffix starting at index 2: "bab", LCP with "babab" is 3.  
- Suffix starting at index 3: "ab", LCP with "babab" is 0.  
- Suffix starting at index 4: "b", LCP with "babab" is 1.  
Total score = 5 + 0 + 3 + 0 + 1 = 9.

**Example 2:**
**Input:** `s = "azbazbazba"`  
**Output:** `22`  
**Explanation:**  
Sum of LCPs: 10 + 0 + 0 + 7 + 0 + 0 + 4 + 0 + 0 + 1 = 22.

### Constraints

- `1 <= s.length <= 10^5`
- `s` consists of lowercase English letters.

### Approach

To solve this efficiently, we use the **Z-algorithm**, which computes an array `Z` in $O(n)$ time. For a string $S$, `Z[i]` is the length of the longest common prefix between $S$ and the suffix of $S$ starting at index $i$.

#### How Z-algorithm works:
1. We maintain a window $[L, R]$ (called a **Z-box**) which is the rightmost interval such that $S[L \dots R]$ is a prefix of $S$.
2. For each index $i$ from 1 to $n-1$:
   - If $i > R$, we cannot use previous information. We compare $S[i \dots]$ with $S[0 \dots]$ to find the new $Z[i]$ and update $L$ and $R$.
   - If $i \le R$, we are inside the current Z-box. The character at $S[i]$ corresponds to $S[i-L]$ in the prefix. We can initialize $Z[i]$ as $\min(R - i + 1, Z[i - L])$. If the value $Z[i-L]$ doesn't hit the boundary $R$, we are done. Otherwise, we attempt to expand the Z-box by manual character comparison starting from $R+1$.
3. The score for the suffix at index 0 is always $n$. The total score is $n + \sum_{i=1}^{n-1} Z[i]$.

### Complexity Analysis

- **Time Complexity:** $O(n)$, as the right boundary $R$ of the Z-box only moves forward, and each character comparison either increases $R$ or results in a mismatch (ending the loop for that $i$).
- **Space Complexity:** $O(n)$ to store the Z-array.

### C++ Solution

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

class Solution {
public:
    long long sumScores(string s) {
        int n = s.length();
        if (n == 0) return 0;
        
        // z[i] stores the length of the longest common prefix 
        // between s and the suffix starting at index i.
        vector<int> z(n, 0);
        long long totalScore = n; // LCP of the string with itself (index 0)
        
        int l = 0, r = 0;
        for (int i = 1; i < n; ++i) {
            // If i is within the current Z-box [l, r], initialize z[i] using symmetry
            if (i <= r) {
                z[i] = min(r - i + 1, z[i - l]);
            }
            
            // Attempt to extend the Z-box by comparing characters manually
            while (i + z[i] < n && s[z[i]] == s[i + z[i]]) {
                z[i]++;
            }
            
            // If the new Z-box extends further than the current one, update l and r
            if (i + z[i] - 1 > r) {
                l = i;
                r = i + z[i] - 1;
            }
            
            totalScore += z[i];
        }
        
        return totalScore;
    }
};
```

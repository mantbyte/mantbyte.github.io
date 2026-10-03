---
layout: post
title: 'Daily DSA: Distinct Echo Substrings (Hard)'
date: 2026-10-03 20:01:28 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Distinct Echo
  Substrings.'
cover_image: /assets/images/posts/daily-dsa-distinct-echo-substrings-2026-10-03-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

Given a string `text`, return the number of **distinct** non-empty substrings that can be written as the concatenation of some string with itself (i.e., it can be written as $a + a$ where $a$ is some string).

A substring is a contiguous sequence of characters within a string.

### Examples

**Example 1:**
**Input:** `text = "abcabcabc"`  
**Output:** `3`  
**Explanation:** The 3 substrings are "abcabc", "bcabca", and "cabcab". "abcabc" appears twice, but we only count distinct occurrences.

**Example 2:**
**Input:** `text = "leelee"`  
**Output:** `2`  
**Explanation:** The 2 substrings are "ee" (from "e"+"e") and "leelee" (from "lee"+"lee").

### Constraints

- `1 <= text.length <= 2000`
- `text` consists only of lowercase English letters.

---

### Approach

To solve this efficiently, we need to identify all substrings of the form $S[i \dots i+2L-1]$ such that the first half $S[i \dots i+L-1]$ is identical to the second half $S[i+L \dots i+2L-1]$. Since the string length $N$ is up to 2000, an $O(N^2)$ approach is feasible.

1.  **Rolling Hash:** Comparing two substrings character by character takes $O(L)$ time. To check the "echo" property in $O(1)$, we can use a **Rolling Hash** (Rabin-Karp algorithm). We precompute the prefix hashes and powers of a base (e.g., 131) to allow any substring hash to be calculated in constant time.
2.  **Iteration:** We iterate through all possible half-lengths $L$ from 1 up to $N/2$. For each $L$, we slide a window of size $2L$ across the string.
3.  **Validation:** For each window starting at index $i$, we extract the hash of the first half and the second half. If `hash(i, i+L-1) == hash(i+L, i+2L-1)`, the substring $S[i \dots i+2L-1]$ is an "echo" substring.
4.  **Uniqueness:** To ensure we only count distinct substrings, we store the hash of the entire echo substring (length $2L$) in a hash set (`std::unordered_set`). The size of the set at the end is our answer.

### Complexity Analysis
- **Time Complexity:** $O(N^2)$, where $N$ is the length of the string. We iterate through all possible lengths and starting positions, performing $O(1)$ hash checks.
- **Space Complexity:** $O(N^2)$ in the worst case to store the hashes of unique echo substrings in the hash set.

---

### C++ Solution

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_set>

using namespace std;

typedef unsigned long long ull;

class Solution {
public:
    int distinctEchoSubstrings(string text) {
        int n = text.length();
        const ull base = 131;
        
        // Precompute prefix hashes and powers of base
        vector<ull> h(n + 1, 0);
        vector<ull> p(n + 1, 1);
        
        for (int i = 0; i < n; ++i) {
            h[i + 1] = h[i] * base + (text[i] - 'a' + 1);
            p[i + 1] = p[i] * base;
        }

        // Lambda to get hash of substring text[l...r] inclusive
        auto get_hash = [&](int l, int r) {
            return h[r + 1] - h[l] * p[r - l + 1];
        };

        unordered_set<ull> unique_echoes;

        // Iterate over all possible half-lengths L
        for (int len = 1; len <= n / 2; ++len) {
            for (int i = 0; i <= n - 2 * len; ++i) {
                ull hash1 = get_hash(i, i + len - 1);
                ull hash2 = get_hash(i + len, i + 2 * len - 1);
                
                // If the two halves are identical
                if (hash1 == hash2) {
                    // Store the hash of the full echo substring (length 2*len)
                    unique_echoes.insert(get_hash(i, i + 2 * len - 1));
                }
            }
        }

        return unique_echoes.size();
    }
};
```
{% endraw %}

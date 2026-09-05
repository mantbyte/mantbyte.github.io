---
layout: post
title: 'Daily DSA: Palindromic Length Inventory (Hard)'
date: 2026-09-05 18:45:46 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Palindromic Length
  Inventory.'
cover_image: /assets/images/posts/daily-dsa-palindromic-length-inventory-2026-09-05-cover.png
cover_caption: ''
---

### Problem Description

Given a string `s` of length `n`, calculate the frequency of every possible palindromic substring length. Specifically, return an array `ans` of size `n`, where `ans[i]` represents the total number of palindromic substrings in `s` that have a length of exactly `i + 1`.

A **palindrome** is a string that reads the same forward and backward.

### Examples

**Example 1:**
- **Input:** `s = "aba"`
- **Output:** `[3, 0, 1]`
- **Explanation:** 
    - Palindromes of length 1: "a", "b", "a" (Total 3)
    - Palindromes of length 2: None (Total 0)
    - Palindromes of length 3: "aba" (Total 1)

**Example 2:**
- **Input:** `s = "aaaa"`
- **Output:** `[4, 3, 2, 1]`
- **Explanation:** 
    - Length 1: "a", "a", "a", "a" (4)
    - Length 2: "aa", "aa", "aa" (3)
    - Length 3: "aaa", "aaa" (2)
    - Length 4: "aaaa" (1)

### Constraints
- `1 <= s.length <= 10^5`
- `s` consists of lowercase English letters.

---

### Approach

1.  **Manacher's Algorithm**: Finding all palindromic substrings in $O(n^2)$ is too slow. Instead, we use Manacher's Algorithm, which finds the maximum expansion radius of palindromes centered at every character (odd length) and every gap between characters (even length) in $O(n)$ time.
    - Let `d1[i]` be the radius of the largest odd palindrome centered at `s[i]`. The length is $2 \times d1[i] - 1$.
    - Let `d2[i]` be the radius of the largest even palindrome centered between `s[i-1]` and `s[i]`. The length is $2 \times d2[i]$.

2.  **Counting Overlapping Palindromes**: If a center has a maximum palindromic radius $R$, it also contains palindromes of radii $R-1, R-2, \dots, 1$ sharing the same center. For example, if "abcba" (radius 3) is a palindrome, then "bcb" (radius 2) and "c" (radius 1) are also palindromes.

3.  **Difference Array Optimization**: 
    - For each center, we know the maximum length $L$. We need to increment the count for lengths $L, L-2, L-4, \dots$.
    - We can use two separate difference-style arrays (one for even lengths and one for odd lengths). For a maximum length $L$, we increment `diff[L]`. After processing all centers, we iterate backwards: `diff[i-2] += diff[i]`. This propagates the count of a larger palindrome to all smaller nested palindromes with the same center.

### Complexity Analysis
- **Time Complexity**: $O(n)$, as Manacher's algorithm and the linear scan for the difference array both run in linear time.
- **Space Complexity**: $O(n)$ to store the radii and the frequency arrays.

---

### C++ Solution

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

class Solution {
public:
    vector<long long> countPalindromicLengths(string s) {
        int n = s.length();
        if (n == 0) return {};

        // d1[i]: radius of odd palindrome centered at i (e.g., "aba" radius is 2)
        vector<int> d1(n);
        for (int i = 0, l = 0, r = -1; i < n; i++) {
            int k = (i > r) ? 1 : min(d1[l + r - i], r - i + 1);
            while (0 <= i - k && i + k < n && s[i - k] == s[i + k]) k++;
            d1[i] = k--;
            if (i + k > r) {
                l = i - k;
                r = i + k;
            }
        }

        // d2[i]: radius of even palindrome centered between i-1 and i
        vector<int> d2(n);
        for (int i = 0, l = 0, r = -1; i < n; i++) {
            int k = (i > r) ? 0 : min(d2[l + r - i + 1], r - i + 1);
            while (0 <= i - k - 1 && i + k < n && s[i - k - 1] == s[i + k]) k++;
            d2[i] = k--;
            if (i + k > r) {
                l = i - k - 1;
                r = i + k;
            }
        }

        // Use a difference-like array to count frequencies
        // diff[i] counts palindromes of length i.
        // A palindrome of length L implies palindromes of length L-2, L-4... at same center.
        vector<long long> diff(n + 2, 0);
        for (int i = 0; i < n; i++) {
            if (d1[i] > 0) {
                diff[2 * d1[i] - 1]++;
            }
            if (d2[i] > 0) {
                diff[2 * d2[i]]++;
            }
        }

        // Propagate counts from length L to L-2
        for (int i = n; i >= 2; i--) {
            diff[i - 2] += diff[i];
        }

        vector<long long> result;
        for (int i = 1; i <= n; i++) {
            result.push_back(diff[i]);
        }

        return result;
    }
};
```

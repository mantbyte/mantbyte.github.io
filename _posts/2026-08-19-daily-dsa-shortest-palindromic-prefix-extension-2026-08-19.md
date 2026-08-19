---
layout: post
title: 'Daily DSA: Shortest Palindromic Prefix Extension (Hard)'
date: 2026-08-19 15:53:29 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Shortest Palindromic
  Prefix Extension.'
cover_image: /assets/images/posts/daily-dsa-shortest-palindromic-prefix-extension-2026-08-19-cover.png
cover_caption: ''
---

### Problem Description

You are given a string `s`. You can convert `s` to a palindrome by adding characters in front of it. Find and return the shortest palindrome you can find by performing this transformation.

### Examples

**Example 1:**
- **Input:** `s = "aacecaaa"` 
- **Output:** `"aaacecaaa"` 
- **Explanation:** The longest prefix of "aacecaaa" that is a palindrome is "aacecaa". We take the remaining suffix "a", reverse it, and prepend it to get "aaacecaaa".

**Example 2:**
- **Input:** `s = "abcd"` 
- **Output:** `"dcbabcd"` 
- **Explanation:** The longest palindromic prefix is "a". The remaining suffix is "bcd". Reversing "bcd" gives "dcb", resulting in "dcbabcd".

### Constraints

- `0 <= s.length <= 5 * 10^4` 
- `s` consists of lowercase English letters only.

### Approach

To solve this problem efficiently, we need to find the **longest prefix** of `s` that is already a palindrome. If we find this prefix, we can take the remaining characters (the suffix), reverse them, and add them to the beginning of the string.

**Algorithm using KMP Prefix Function:**

1.  **Construct a Helper String:** Create a new string `temp = s + "#" + reverse(s)`. The `#` separator is crucial because it ensures that the KMP prefix function does not match a prefix that spans across the boundary of the original and reversed strings.
2.  **Compute the Prefix Function (pi array):** In the KMP algorithm, the prefix function `pi[i]` stores the length of the longest proper prefix of the substring `temp[0...i]` that is also a suffix of `temp[0...i]`.
3.  **Extract the Result:** The last value of the `pi` array, `pi[temp.length() - 1]`, tells us the length of the longest prefix of `s` that matches the end of `reverse(s)`. This match is exactly the longest palindromic prefix of `s`.
4.  **Final Construction:** Identify the suffix of `s` that is not part of this palindromic prefix, reverse it, and prepend it to `s`.

### Complexity Analysis
- **Time Complexity:** O(N), where N is the length of the string `s`. We perform string concatenation, reversal, and a single pass to compute the KMP prefix function, all of which are linear.
- **Space Complexity:** O(N), as we store the modified string and the `pi` array of size approximately 2N.

### C++ Solution

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

class Solution {
public:
    std::string shortestPalindrome(std::string s) {
        if (s.empty()) return s;
        
        // Step 1: Create the reversed version of s
        std::string rev_s = s;
        std::reverse(rev_s.begin(), rev_s.end());
        
        // Step 2: Combine strings with a separator to avoid overlap
        std::string combined = s + "#" + rev_s;
        int n = combined.length();
        
        // Step 3: Compute the KMP Prefix Function (pi array)
        std::vector<int> pi(n, 0);
        for (int i = 1; i < n; i++) {
            int j = pi[i - 1];
            // Standard KMP logic to find the longest prefix-suffix match
            while (j > 0 && combined[i] != combined[j]) {
                j = pi[j - 1];
            }
            if (combined[i] == combined[j]) {
                j++;
            }
            pi[i] = j;
        }
        
        // Step 4: The last value in pi array is the length of the palindromic prefix
        int longest_pal_len = pi[n - 1];
        
        // Step 5: Prepend the reversed suffix to the original string
        std::string suffix_to_add = s.substr(longest_pal_len);
        std::reverse(suffix_to_add.begin(), suffix_to_add.end());
        
        return suffix_to_add + s;
    }
};
```

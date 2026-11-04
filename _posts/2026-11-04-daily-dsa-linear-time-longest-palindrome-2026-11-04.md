---
layout: post
title: 'Daily DSA: Linear Time Longest Palindrome (Hard)'
date: 2026-11-04 23:13:48 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Linear Time Longest
  Palindrome.'
cover_image: /assets/images/posts/daily-dsa-linear-time-longest-palindrome-2026-11-04-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

Given a string `s` of length up to $10^6$, find the longest substring that is a palindrome. A palindrome is a string that reads the same forward and backward.

While this problem is often solved in $O(N^2)$ using Dynamic Programming or Center Expansion, the constraints here require a linear time $O(N)$ solution.

### Examples

**Example 1:**
- **Input:** `s = "babad"` 
- **Output:** `"bab"` 
- **Explanation:** `"aba"` is also a valid answer.

**Example 2:**
- **Input:** `s = "cbbd"` 
- **Output:** `"bb"` 

**Example 3:**
- **Input:** `s = "a"` 
- **Output:** `"a"` 

### Constraints

- `1 <= s.length <= 1,000,000` 
- `s` consists of lowercase English letters.
- Time Limit: 1.0s

### Approach: Manacher's Algorithm

Manacher's Algorithm is a sophisticated approach to find all palindromic radii in linear time. 

1. **Preprocessing:** Palindromes can be odd-length (`aba`) or even-length (`abba`). To handle both uniformly, we transform the string by inserting a special character (like `#`) between every character and at both ends. For example, `aba` becomes `#a#b#a#` (length 7) and `abba` becomes `#a#b#b#a#` (length 9). Every palindrome in the transformed string now has an odd length.

2. **State Variables:** 
   - `P[i]`: The radius of the palindrome centered at index `i` in the transformed string.
   - `C`: The center of the palindrome that reaches the furthest to the right.
   - `R`: The right boundary of this palindrome (`R = C + P[C]`).

3. **Mirroring:** For a current index `i`, we find its mirror index `i_mirror = 2*C - i` relative to the current center `C`. 
   - If `i < R`, we can initialize `P[i]` as `min(R - i, P[i_mirror])`. This is the core optimization that avoids redundant character comparisons.
   - We then attempt to expand around `i` manually.
   - If the expanded palindrome centered at `i` goes beyond `R`, we update `C = i` and `R = i + P[i]`.

4. **Extracting Result:** The maximum value in `P` corresponds to the length of the longest palindrome in the original string. The starting index can be derived from the position in the transformed string.

### Complexity Analysis

- **Time Complexity:** $O(N)$. Although there is a nested `while` loop for expansion, the right boundary `R` only moves forward, and each character comparison either increases `R` or finishes the expansion for that center.
- **Space Complexity:** $O(N)$ to store the transformed string and the radii array.

### C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

string solve() {
    string s;
    if (!(cin >> s)) return "";
    
    // Preprocess the string
    string t = "#";
    for (char c : s) {
        t += c;
        t += "#";
    }
    
    int n = t.length();
    vector<int> p(n, 0);
    int center = 0, right = 0;
    int maxLen = 0, startIdx = 0;
    
    for (int i = 0; i < n; i++) {
        // Use mirroring property
        if (i < right) {
            p[i] = min(right - i, p[2 * center - i]);
        }
        
        // Attempt to expand around i
        int left_ptr = i - (p[i] + 1);
        int right_ptr = i + (p[i] + 1);
        while (left_ptr >= 0 && right_ptr < n && t[left_ptr] == t[right_ptr]) {
            p[i]++;
            left_ptr--;
            right_ptr++;
        }
        
        // Update center and right boundary
        if (i + p[i] > right) {
            center = i;
            right = i + p[i];
        }
        
        // Track maximum
        if (p[i] > maxLen) {
            maxLen = p[i];
            startIdx = (i - maxLen) / 2;
        }
    }
    
    return s.substr(startIdx, maxLen);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    cout << solve() << endl;
    return 0;
}
```
{% endraw %}

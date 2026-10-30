---
layout: post
title: 'Daily DSA: Longest Substring Containing Vowels in Even Counts (Medium)'
date: 2026-10-30 21:59:34 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Longest Substring
  Containing Vowels in Even Counts.'
cover_image: /assets/images/posts/default-cover.png
cover_caption: ''
---

{% raw %}
# Problem Statement

Given a string `s`, return the size of the longest substring where every vowel ('a', 'e', 'i', 'o', 'u') appears an even number of times.

# Examples

**Example 1:**
- **Input:** `s = "eleetminicoworoep"` 
- **Output:** `13` 
- **Explanation:** The longest substring is `"leetminicowor"` which contains 'e':2, 'i':2, 'o':2 and 'a', 'u':0. Each vowel appears an even number of times.

**Example 2:**
- **Input:** `s = "leetcodeisgreat"` 
- **Output:** `5` 
- **Explanation:** The longest substring is `"leetc"` which contains 'e':2.

**Example 3:**
- **Input:** `s = "bcbcbc"` 
- **Output:** `6` 
- **Explanation:** In this case, the given string `"bcbcbc"` is the longest because all vowels appear zero times (which is even).

# Constraints

- `1 <= s.length <= 5 * 10^5` 
- `s` contains only lowercase English letters.

# Approach

1.  **Parity Tracking**: We need to determine if the count of each vowel is even or odd. Since there are only 5 vowels and 2 states (even/odd) per vowel, we can represent the entire state of vowel parities using a **5-bit integer (bitmask)**.
2.  **Bitmask Representation**:
    - Bit 0 ($2^0$): Parity of 'a'
    - Bit 1 ($2^1$): Parity of 'e'
    - Bit 2 ($2^2$): Parity of 'i'
    - Bit 3 ($2^3$): Parity of 'o'
    - Bit 4 ($2^4$): Parity of 'u'
    When we encounter a vowel, we flip its corresponding bit in our mask using the XOR operator (`mask ^= bit_value`). Non-vowel characters do not affect the mask.
3.  **Prefix State Pattern**: 
    - This problem follows the same logic as finding the longest subarray with a sum of 0. If the bitmask at index $i$ is identical to the bitmask at index $j$ ($j > i$), it implies that the change in vowel counts between $i$ and $j$ resulted in an even number of occurrences for every vowel (XORing a bit twice returns it to its original state).
    - We maintain an array `first_occurrence` of size 32 (since $2^5 = 32$) to store the index of the first time we encountered each specific mask.
    - Initialize `first_occurrence[0] = -1` to handle cases where a valid substring starts from index 0.
4.  **Algorithm**:
    - Iterate through the string, updating the current bitmask.
    - If the mask has been seen before, update the global maximum length using `current_index - first_occurrence[mask]`.
    - If the mask is new, record its current index.

# Code (C++)

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

class Solution {
public:
    int findTheLongestSubstring(string s) {
        // first_occurrence stores the earliest index for each of the 32 possible vowel parity masks.
        // Initialize with -2 to indicate the mask hasn't been seen yet.
        vector<int> first_occurrence(32, -2);
        first_occurrence[0] = -1; // Base case: mask 0 (all even) is seen before the string starts.
        
        int mask = 0;
        int max_len = 0;
        
        for (int i = 0; i < (int)s.length(); ++i) {
            // Update the mask if the current character is a vowel.
            if (s[i] == 'a') mask ^= (1 << 0);
            else if (s[i] == 'e') mask ^= (1 << 1);
            else if (s[i] == 'i') mask ^= (1 << 2);
            else if (s[i] == 'o') mask ^= (1 << 3);
            else if (s[i] == 'u') mask ^= (1 << 4);
            
            // If the current mask has been seen before, the substring between 
            // the first occurrence and now has even counts of all vowels.
            if (first_occurrence[mask] != -2) {
                max_len = max(max_len, i - first_occurrence[mask]);
            } else {
                // Store the first time we see this mask.
                first_occurrence[mask] = i;
            }
        }
        
        return max_len;
    }
};
```

# Complexity Analysis

- **Time Complexity**: $O(N)$, where $N$ is the length of the string. We perform a single linear scan of the input.
- **Space Complexity**: $O(1)$, as the auxiliary storage (`first_occurrence`) is fixed at 32 integers regardless of the input size.
{% endraw %}

---
layout: post
title: 'Daily DSA: Lexicographical String Merging via Suffix Automaton Transitions
  (Hard)'
date: 2026-09-11 19:30:35 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Lexicographical
  String Merging via Suffix Automaton Transitions.'
cover_image: /assets/images/posts/daily-dsa-lexicographical-string-merging-via-suffix-automaton-transitions-2026-09-11-cover.png
cover_caption: ''
---

# Problem Statement

You are given two strings, $S$ and $T$, consisting of lowercase English letters. You need to construct a new string $P$ by interleaving (merging) $S$ and $T$ such that the relative order of characters from each string is preserved.

Among all possible valid merged strings, you must find the **lexicographically smallest** one.

# Examples

### Example 1:
- **Input:** $S = "bba"$, $T = "ab"$
- **Output:** $"abbba"$
- **Explanation:** The valid merges include "bbaab", "babab", "abbba", etc. The lexicographically smallest among them is "abbba".

### Example 2:
- **Input:** $S = "ab"$, $T = "ba"$
- **Output:** $"aabb"$

# Constraints
- $1 \le |S|, |T| \le 3000$
- $S$ and $T$ contain only lowercase English letters.

# Approach

To find the lexicographically smallest merged string efficiently, we can use greedy choices backed by suffix structures, or state-space traversal. A standard dynamic programming approach with state $(i, j)$ representing the prefixes $S[0 \dots i-1]$ and $T[0 \dots j-1]$ takes $O(|S| \times |T|)$ time. 

However, to optimize or decide local optimality when choices are tied, we can inspect which suffix is lexicographically smaller. If $S[i:] < T[j:]$, we should greedily pick from $S$; otherwise, we pick from $T$.

# C++ Solution

```cpp
#include <iostream>
#include <string>
#include <vector>

using namespace std;

class Solution {
public:
    string smallestMerge(string S, string T) {
        int n = S.length(), m = T.length();
        int i = 0, j = 0;
        string result = "";
        
        while (i < n && j < m) {
            if (S.substr(i) < T.substr(j)) {
                result += S[i++];
            } else {
                result += T[j++];
            }
        }
        
        while (i < n) result += S[i++];
        while (j < m) result += T[j++];
        
        return result;
    };
};

int main() {
    Solution sol;
    cout << sol.smallestMerge("bba", "ab") << endl;
    return 0;
}
```

### Complexity Analysis
- **Time Complexity:** $O((N + M) \cdot (N + M))$ due to substring comparisons in the worst case, which can be optimized to $O((N+M)^2)$ with precomputed suffix comparisons.
- **Space Complexity:** $O(N + M)$ to store the result string.

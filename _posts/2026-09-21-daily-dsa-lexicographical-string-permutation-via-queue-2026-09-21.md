---
layout: post
title: 'Daily DSA: Lexicographical String Permutation via Queue (Medium)'
date: 2026-09-21 21:40:05 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Lexicographical
  String Permutation via Queue.'
cover_image: /assets/images/posts/daily-dsa-lexicographical-string-permutation-via-queue-2026-09-21-cover.png
cover_caption: ''
---

# Problem Statement

You are given a string `s` consisting of lowercase English letters. You need to construct a new string `result` by repeatedly performing the following operations:

1. Remove the first character from `s` and append it to a queue.
2. You may at any time remove the smallest character available at the front of the queue and append it to `result`.

Return the lexicographically smallest string `result` that can be formed after all characters from `s` are processed and the queue is emptied.

# Examples

**Example 1:**
```
Input: s = "cab"
Output: "abc"
Explanation:
- Pop 'c' from s, push to queue. Queue: ['c']
- Pop 'a' from s, push to queue. Queue: ['c', 'a']
- Pop 'a' (smallest) from queue, append to result. Result: "a", Queue: ['c']
- Pop 'b' from s, push to queue. Queue: ['c', 'b']
- Pop 'b' (smallest) from queue, append to result. Result: "ab", Queue: ['c']
- Pop 'c' from queue, append to result. Result: "abc", Queue: []
```

**Example 2:**
```
Input: s = "acbdb"
Output: "abbdc"
```

# Constraints
- `1 <= s.length <= 10^5`
- `s` consists of lowercase English letters.

# Approach / Hint
1. We want to output the lexicographically smallest characters as early as possible.
2. We can use a frequency array to keep track of the count of each character remaining in `s`.
3. As we iterate through `s`, we push characters into a queue.
4. Before pushing or after pushing each character, we can greedily pop from the queue and add to our result if the front of the queue is smaller than or equal to the smallest available character remaining in `s` (which can be found by checking our frequency array).

# C++ Code

```cpp
#include <string>
#include <queue>
#include <vector>

class Solution {
public:
    string robotWithString(string s) {
        vector<int> count(26, 0);
        for (char c : s) {
            count[c - 'a']++;
        }

        string result = "";
        queue<char> q;
        char min_available = 'a';

        for (char c : s) {
            q.push(c);
            count[c - 'a']--;

            // Find the smallest available character remaining in 's'
            while (min_available <= 'z' && count[min_available - 'a'] == 0) {
                min_available++;
            }

            // Greedily pop from queue if the front is smaller or equal to the minimum remaining
            while (!q.empty() && q.front() <= min_available) {
                result += q.front();
                q.pop();
            }
        }

        // Empty the remaining queue
        while (!q.empty()) {
            result += q.front();
            q.pop();
        }

        return result;
    }
};
```

# Complexity Analysis
- **Time Complexity:** $O(N)$, where $N$ is the length of the string `s`. Each character is pushed and popped from the queue at most once, and the `min_available` character pointer only advances forward from `'a'` to `'z'`. 
- **Space Complexity:** $O(N)$ to store the queue and the result string.

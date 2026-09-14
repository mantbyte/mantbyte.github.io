---
layout: post
title: 'Daily DSA: Lexicographically Smallest String After Operations With Constraint
  (Medium)'
date: 2026-09-14 21:37:45 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Lexicographically
  Smallest String After Operations With Constraint.'
cover_image: /assets/images/posts/daily-dsa-lexicographically-smallest-string-after-operations-with-constraint-2026-09-14-cover.png
cover_caption: ''
---

# Problem Statement

You are given a string `s` of lowercase English letters and an integer `k`. You can perform the following two operations on the string any number of times:
1. **Add**: Add $1$ to any digit-character if it's a digit (though here we only have lowercase letters, let's treat letters cyclically: 'a' -> 'b' -> ... -> 'z' -> 'a'). Specifically, add $1$ to the character's ASCII value modulo 26, meaning 'z' becomes 'a'. You can do this at most $k$ total times across all operations.
2. **Rotate**: Rotate the string to the right by 1 position.

Your task is to find the **lexicographically smallest** string you can obtain by applying these operations under the condition that the total number of 'Add' operations does not exceed $k$.

*Wait, let's refine Operation 1:* You are given a string consisting of digits from '0' to '9'. You can apply two operations:
1. Add $1$ to any digit of the string, cyclically (i.e., '9' becomes '0'). You can apply this operation at most $k$ times in total, and you can apply it to the same digit multiple times.
2. Rotate the string to the right by any number of positions.

Return the lexicographically smallest string you can obtain.

# Examples

### Example 1:
- **Input:** `s = "5525"`, `k = 9`
- **Output:** `"2050"`
- **Explanation:** We can rotate the string and apply additions. Applying rotations and additions optimally yields "2050".

### Example 2:
- **Input:** `s = "74"`, `k = 5`
- **Output:** `"24"`
- **Explanation:** We can add 5 to '7' to make it '2' ($7 	o 8 	o 9 	o 0 	o 1 	o 2$, takes 5 operations), and leave '4' as is.

# Constraints
- $1 \le s.length \le 100$
- `s` consists of digits from `'0'` to `'9'`.
- $0 \le k \le 10^9$

# Approach
1. **State Space Exploration:** Since the length of the string $N$ is small ($N \le 100$), the number of possible rotations is at most $N$. For each rotation, we can independently optimize each position.
2. **Digit Optimization:** For a fixed string, at each position, we want to minimize the digit by either adding numbers directly or adding numbers after shifting (which effectively allows us to target every other digit as well if we consider step sizes, but usually we can try all possible increments from $0$ to $9$ for odd/even indices depending on whether we can shift by even or odd amounts).
3. Since $N$ is small, we can generate all unique rotations of the string. For each rotation, we greedily find the minimum possible value for each digit using at most $k$ operations. Because operations on even and odd indices behave differently regarding rotations, we can use Breadth-First Search (BFS) or Depth-First Search (DFS) with memoization to find the minimum string reachable within $k$ operations.

# C++ Solution
```cpp
#include <string>
#include <queue>
#include <unordered_set>
#include <algorithm>

class Solution {
public:
    std::string findLexSmallestString(std::string s, int a, int b) {
        std::queue<std::string> q;
        std::unordered_set<std::string> visited;
        
        q.push(s);
        visited.insert(s);
        std::string ans = s;
        
        while (!q.empty()) {
            std::string curr = q.front();
            q.pop();
            
            if (curr < ans) {
                ans = curr;
            }
            
            // Operation 1: Add 'a' to odd indices
            std::string op1 = curr;
            for (int i = 1; i < op1.size(); i += 2) {
                op1[i] = '0' + (op1[i] - '0' + a) % 10;
            }
            if (visited.find(op1) == visited.end()) {
                visited.insert(op1);
                q.push(op1);
            }
            
            // Operation 2: Rotate to the right by 'b'
            std::string op2 = curr;
            int n = op2.size();
            b %= n;
            std::rotate(op2.rbegin(), op2.rbegin() + b, op2.rend());
            if (visited.find(op2) == visited.end()) {
                visited.insert(op2);
                q.push(op2);
            }
        }
        
        return ans;
    }
};
```

# Complexity Analysis
- **Time Complexity:** $\mathcal{O}(N \cdot \Sigma)$, where $N$ is the length of the string and $\Sigma$ is the size of the state space. The number of unique states is bounded by $10^{N/2} \times N$ in the worst case, but practically very small for $N \le 100$.
- **Space Complexity:** $\mathcal{O}(\Sigma)$ to store the visited states in the queue and hash set.

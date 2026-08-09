---
layout: post
title: 'Daily DSA: Evaluate Expression with Custom Precedence (Medium)'
date: 2026-08-09 15:58:17 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Evaluate Expression
  with Custom Precedence.'
cover_image: /assets/images/posts/daily-dsa-evaluate-expression-with-custom-precedence-2026-08-09-cover.png
cover_caption: ''
---

### Problem Statement

You are given a string `s` representing a valid mathematical expression containing non-negative integers and two binary operators: addition (`'+'`) and a custom max operator (`'@'`).

The operations are defined as follows:
- Addition `a + b`: Calculates the sum of `a` and `b`.
- Custom Max `a @ b`: Calculates the maximum of `a` and `b` (i.e., $\max(a, b)$).

The custom operator `'@'` has **higher precedence** than standard addition `'+'`. Operators of equal precedence are evaluated from **left to right**.

Return the final integer result after evaluating the expression.

---

### Examples

**Example 1:**
```text
Input: s = "3+5@2+4"
Output: 12
Explanation: 
1. First evaluate higher-precedence '@' operator: 5 @ 2 = max(5, 2) = 5.
2. The expression becomes: "3 + 5 + 4".
3. Evaluate addition from left to right: 3 + 5 + 4 = 12.
```

**Example 2:**
```text
Input: s = "10@20+5@15"
Output: 35
Explanation:
1. Evaluate '@' operators: 10 @ 20 = 20 and 5 @ 15 = 15.
2. Expression becomes: "20 + 15".
3. Result = 35.
```

**Example 3:**
```text
Input: s = "8@3@7+2"
Output: 10
Explanation:
1. Evaluate '@' operators from left to right: (8 @ 3) @ 7 = 8 @ 7 = 8.
2. Expression becomes: "8 + 2".
3. Result = 10.
```

---

### Constraints

- `1 <= s.length <= 10^5`
- `s` consists only of digits (`'0'` - `'9'`), `'+'`, and `'@'`.
- Numbers in `s` are positive integers between `1` and `10^6` (no leading zeros except for the single digit `0`).
- `s` is a valid mathematical expression with no spaces or parentheses.
- The answer is guaranteed to fit within a standard 64-bit signed integer (`long long` in C++).

---

### Approach

To handle operator precedence, we can simulate the evaluation using a **Stack** data structure in two logical steps:

1. **First Pass (High Precedence `'@'`):**
   - Parse the first operand and push it onto the stack.
   - Iterate through the remaining operators and numbers in the expression.
   - If the operator is `'@'`, pop the top number from the stack, evaluate `max(top_number, current_number)`, and push the result back onto the stack.
   - If the operator is `'+'`, push the `current_number` directly onto the stack.

2. **Second Pass (Low Precedence `'+'`):**
   - After processing all `'@'` operators, all remaining numbers in the stack represent terms separated by `'+'`.
   - Sum all elements in the stack to get the final evaluated result.

---

### C++ Solution

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cctype>

class Solution {
public:
    long long evaluateExpression(std::string s) {
        std::vector<long long> numStack;
        int n = s.length();
        int i = 0;
        
        // Parse the first number
        long long currentNum = 0;
        while (i < n && std::isdigit(s[i])) {
            currentNum = currentNum * 10 + (s[i] - '0');
            i++;
        }
        numStack.push_back(currentNum);
        
        // Process remaining operators and numbers
        while (i < n) {
            char op = s[i];
            i++; // Move past operator
            
            long long nextNum = 0;
            while (i < n && std::isdigit(s[i])) {
                nextNum = nextNum * 10 + (s[i] - '0');
                i++;
            }
            
            if (op == '@') {
                long long prevNum = numStack.back();
                numStack.pop_back();
                numStack.push_back(std::max(prevNum, nextNum));
            } else if (op == '+') {
                numStack.push_back(nextNum);
            }
        }
        
        // Sum all reduced terms
        long long totalSum = 0;
        for (long long num : numStack) {
            totalSum += num;
        }
        
        return totalSum;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(N)$, where $N$ is the length of the string `s`. We traverse the string once to parse numbers and operators, performing $\mathcal{O}(1)$ stack operations per token.
- **Space Complexity:** $\mathcal{O}(N)$, to store the numbers in the stack in the worst-case scenario (e.g., when the expression consists entirely of addition operations).

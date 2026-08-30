---
layout: post
title: 'Daily DSA: The Grand Staircase Challenge (Hard)'
date: 2026-08-30 20:09:17 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: The Grand Staircase
  Challenge.'
cover_image: /assets/images/posts/daily-dsa-the-grand-staircase-challenge-2026-08-30-cover.png
cover_caption: ''
---

### Problem Description

You are standing at the base of a staircase with $n$ steps. You want to reach the top by taking steps of size 1, 2, or 3. 

Since $n$ can be extremely large, you need to find the number of distinct ways to reach the $n$-th step. Two ways are considered different if the sequence of step sizes taken is different.

Because the answer can be very large, return it **modulo $10^9 + 7$**.

### Examples

**Example 1:**
- **Input:** `n = 3`
- **Output:** `4`
- **Explanation:** There are 4 ways to reach the 3rd step:
  1. `1 + 1 + 1`
  2. `1 + 2`
  3. `2 + 1`
  4. `3`

**Example 2:**
- **Input:** `n = 4`
- **Output:** `7`
- **Explanation:** The ways are: `1+1+1+1`, `1+1+2`, `1+2+1`, `2+1+1`, `2+2`, `1+3`, `3+1`.

**Example 3:**
- **Input:** `n = 10`
- **Output:** `274`

### Constraints

- $1 \le n \le 10^{18}$

### Approach

1.  **Recurrence Relation:**
    Let $f(n)$ be the number of ways to reach the $n$-th step. To reach step $n$, you could have come from step $n-1$ (with a 1-step), step $n-2$ (with a 2-step), or step $n-3$ (with a 3-step). Therefore:
    $f(n) = f(n-1) + f(n-2) + f(n-3)$
    Base cases: $f(0) = 1, f(1) = 1, f(2) = 2$.

2.  **Matrix Form:**
    For large $n$, we cannot use standard Dynamic Programming ($O(n)$). We use Matrix Exponentiation ($O(\log n)$).
    We can represent the recurrence as:
    $$\begin{bmatrix} f(n) \\ f(n-1) \\ f(n-2) \end{bmatrix} = \begin{bmatrix} 1 & 1 & 1 \\ 1 & 0 & 0 \\ 0 & 1 & 0 \end{bmatrix} \times \begin{bmatrix} f(n-1) \\ f(n-2) \\ f(n-3) \end{bmatrix}$$
    Let $T = \begin{bmatrix} 1 & 1 & 1 \\ 1 & 0 & 0 \\ 0 & 1 & 0 \end{bmatrix}$. Then:
    $$\begin{bmatrix} f(n) \\ f(n-1) \\ f(n-2) \end{bmatrix} = T^{n-2} \times \begin{bmatrix} f(2) \\ f(1) \\ f(0) \end{bmatrix}$$

3.  **Binary Exponentiation:**
    Compute $T^{n-2}$ in $O(3^3 \log n)$ time using the binary exponentiation algorithm (also known as exponentiation by squaring).

### C++ Solution

```cpp
#include <iostream>
#include <vector>
#include <cstring>

using namespace std;

class Solution {
    long long MOD = 1e9 + 7;

    struct Matrix {
        long long mat[3][3];
        Matrix() {
            memset(mat, 0, sizeof(mat));
        }
    };

    Matrix multiply(Matrix A, Matrix B) {
        Matrix C;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                for (int k = 0; k < 3; k++) {
                    C.mat[i][j] = (C.mat[i][j] + A.mat[i][k] * B.mat[k][j]) % MOD;
                }
            }
        }
        return C;
    }

    Matrix power(Matrix A, long long p) {
        Matrix res;
        for (int i = 0; i < 3; i++) res.mat[i][i] = 1;
        while (p > 0) {
            if (p & 1) res = multiply(res, A);
            A = multiply(A, A);
            p >>= 1;
        }
        return res;
    }

public:
    int countWays(long long n) {
        if (n == 0) return 1;
        if (n == 1) return 1;
        if (n == 2) return 2;
        if (n == 3) return 4;

        Matrix T;
        T.mat[0][0] = 1; T.mat[0][1] = 1; T.mat[0][2] = 1;
        T.mat[1][0] = 1; T.mat[1][1] = 0; T.mat[1][2] = 0;
        T.mat[2][0] = 0; T.mat[2][1] = 1; T.mat[2][2] = 0;

        // We want f(n). Using the relation V_n = T^(n-2) * V_2
        // V_2 = [f(2), f(1), f(0)] = [2, 1, 1]
        T = power(T, n - 2);

        long long ans = (T.mat[0][0] * 2 + T.mat[0][1] * 1 + T.mat[0][2] * 1) % MOD;
        return (int)ans;
    }
};
```

### Complexity Analysis

- **Time Complexity:** $O(K^3 \log n)$, where $K=3$ is the dimension of the transition matrix. This simplifies to $O(\log n)$.
- **Space Complexity:** $O(K^2)$ to store the matrix, which is $O(1)$ constant space.

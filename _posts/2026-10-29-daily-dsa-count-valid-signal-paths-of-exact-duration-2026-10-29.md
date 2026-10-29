---
layout: post
title: 'Daily DSA: Count Valid Signal Paths of Exact Duration (Hard)'
date: 2026-10-29 22:08:06 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Count Valid Signal
  Paths of Exact Duration.'
cover_image: /assets/images/posts/daily-dsa-count-valid-signal-paths-of-exact-duration-2026-10-29-cover.png
cover_caption: ''
---

{% raw %}
### Problem Description

You are designing a secure communication protocol across a network of $N$ transmission nodes, labeled from $0$ to $N - 1$. 

A signal transmission starts at node $0$ at time $t = 0$. In each step, if a signal is currently at node $u$, it can be transmitted along a directed channel to an adjacent node $v$. Each channel has an associated integer delay of either $1$ millisecond or $2$ milliseconds.

You are given:
- An integer $N$, the number of nodes in the network.
- A 2D integer array `channels`, where `channels[i] = [u, v, delay]` indicates a directed channel from node $u$ to node $v$ taking `delay` milliseconds ($1 \le \text{delay} \le 2$). Multiple channels can exist between the same pair of nodes.
- An integer $T$, the exact target duration in milliseconds.
- An integer `target`, the destination node.

A signal path is considered valid if it starts at node $0$ at time $0$, traverses one or more channels, and arrives at node `target` at **exactly** time $T$.

Return the total number of valid signal paths from node $0$ to node `target` of duration exactly $T$. Since the answer can be very large, return it modulo $10^9 + 7$.

---

### Examples

#### Example 1:
```
Input: N = 3, channels = [[0, 1, 1], [1, 2, 1], [0, 2, 2]], T = 2, target = 2
Output: 2
Explanation: 
There are 2 valid paths from node 0 to node 2 that take exactly 2 milliseconds:
1. 0 -> 1 -> 2: delay is 1 + 1 = 2 ms.
2. 0 -> 2: delay is 2 ms.
```

#### Example 2:
```
Input: N = 2, channels = [[0, 0, 1], [0, 1, 1], [1, 0, 1]], T = 3, target = 1
Output: 3
Explanation:
The valid paths of duration 3 ms from node 0 to node 1 are:
1. 0 -> 0 -> 0 -> 1 (1 + 1 + 1 = 3 ms)
2. 0 -> 1 -> 0 -> 1 (1 + 1 + 1 = 3 ms)
3. 0 -> 0 -> 1 does not take 3 ms, but traversing 0 -> 0 -> 0 -> 1 works.
Total valid paths = 3.
```

#### Example 3:
```
Input: N = 2, channels = [[0, 1, 2]], T = 3, target = 1
Output: 0
Explanation: The only path takes 2 ms, and there is no way to reach node 1 at exactly 3 ms.
```

---

### Constraints

- $1 \le N \le 30$
- $1 \le \text{channels.length} \le 200$
- `channels[i] = [u, v, delay]` where $0 \le u, v < N$ and $\text{delay} \in \{1, 2\}$.
- $1 \le T \le 10^{18}$
- $0 \le \text{target} < N$

---

### Approach and Intuition

#### 1. Why Standard Dynamic Programming Fails
Let $dp[t][u]$ be the number of paths from node $0$ to node $u$ taking exactly $t$ milliseconds. The recurrence would be:
$$dp[t][v] = \sum_{(u, v, d) \in channels} dp[t - d][u]$$
However, $T$ can be as large as $10^{18}$. A linear scan over time $O(T \cdot (|V| + |E|))$ is far too slow.

#### 2. State Expansion for Unit Delays
Matrix exponentiation is typically used when transitions take $1$ unit of time. Here, delays are either $1$ or $2$. We can eliminate delays of $2$ by introducing "virtual nodes":
- For each original node $u$, we can introduce a helper node $u'$.
- A delay-2 transition from $u$ to $v$ can be represented as two consecutive 1-millisecond transitions: $u \xrightarrow{1} v'$ and $v' \xrightarrow{1} v$.
- Equivalently, let the state at time $t$ consist of $2N$ components:
  - For $0 \le u < N$: number of paths reaching node $u$ at time $t$.
  - For $N \le u + N < 2N$: number of paths that arrived at node $u$ at time $t - 1$ (acting as a memory buffer for delay-2 incoming paths).

More systematically, assign each node $u$ two states:
1. State $u$: the signal is at node $u$ at current time $t$.
2. State $u + N$: a buffer state holding signals that will arrive at node $u$ at time $t + 1$.

Then in one time step (from $t$ to $t+1$):
- If there is a channel $(u, v)$ with delay $1$: add a transition from state $u$ to state $v$.
- If there is a channel $(u, v)$ with delay $2$: add a transition from state $u$ to state $v + N$.
- Automatically, any signal buffered at $v + N$ progresses to $v$: add a transition from state $v + N$ to state $v$.

This gives an augmented system with $M = 2N$ total states (since $N \le 30$, $M \le 60$).

#### 3. Transition Matrix Formulation
Construct an $M \times M$ matrix $A$, where $A[j][i]$ represents the number of ways to transition from state $i$ to state $j$ in $1$ millisecond:
1. Initialize $A$ with all zeros.
2. For each channel $(u, v, 1)$: $A[v][u] = (A[v][u] + 1) \pmod{10^9 + 7}$.
3. For each channel $(u, v, 2)$: $A[v + N][u] = (A[v + N][u] + 1) \pmod{10^9 + 7}$.
4. For each $u \in [0, N-1]$: $A[u][u + N] = (A[u][u + N] + 1) \pmod{10^9 + 7}$.

The initial state vector at $t = 0$ is $X_0 = [1, 0, 0, \dots, 0]^T$ (with $1$ at index $0$, and $0$ elsewhere).
The state vector at time $T$ is:
$$X_T = A^T \cdot X_0$$
The answer will be $X_T[\text{target}]$, which is precisely $(A^T)[\text{target}][0]$.

#### 4. Matrix Exponentiation
Using binary exponentiation, $A^T$ can be computed in $O(M^3 \log T)$ time.
Since $M \le 60$, $M^3 = 216,000$ operations per multiplication, and $\log_2(10^{18}) \approx 60$. The total operations are around $60 \times 216,000 \approx 1.3 \times 10^7$, which easily runs in under $0.05$ seconds in C++.

---

### C++ Solution

```cpp
#include <vector>
#include <iostream>

class Solution {
private:
    static constexpr int MOD = 1'000'000'007;

    // Multiply two square matrices of size sz x sz modulo MOD
    std::vector<std::vector<long long>> multiply(
        const std::vector<std::vector<long long>>& A,
        const std::vector<std::vector<long long>>& B,
        int sz
    ) {
        std::vector<std::vector<long long>> C(sz, std::vector<long long>(sz, 0));
        for (int i = 0; i < sz; ++i) {
            for (int k = 0; k < sz; ++k) {
                if (A[i][k] == 0) continue;
                for (int j = 0; j < sz; ++j) {
                    C[i][j] = (C[i][j] + A[i][k] * B[k][j]) % MOD;
                }
            }
        }
        return C;
    }

    // Compute (base^exp) modulo MOD for a square matrix of size sz x sz
    std::vector<std::vector<long long>> matrixPower(
        std::vector<std::vector<long long>> base,
        long long exp,
        int sz
    ) {
        std::vector<std::vector<long long>> res(sz, std::vector<long long>(sz, 0));
        for (int i = 0; i < sz; ++i) {
            res[i][i] = 1; // Identity matrix
        }

        while (exp > 0) {
            if (exp & 1) {
                res = multiply(res, base, sz);
            }
            base = multiply(base, base, sz);
            exp >>= 1;
        }
        return res;
    }

public:
    int countValidPaths(int N, const std::vector<std::vector<int>>& channels, long long T, int target) {
        int M = 2 * N;
        std::vector<std::vector<long long>> transition(M, std::vector<long long>(M, 0));

        // Buffer to target node transition: (u + N) -> u
        for (int u = 0; u < N; ++u) {
            transition[u][u + N] = (transition[u][u + N] + 1) % MOD;
        }

        // Edge transitions
        for (const auto& ch : channels) {
            int u = ch[0];
            int v = ch[1];
            int delay = ch[2];

            if (delay == 1) {
                // Direct transition from u to v in 1 step
                transition[v][u] = (transition[v][u] + 1) % MOD;
            } else if (delay == 2) {
                // Intermediate transition: from u to buffer (v + N) in 1 step
                transition[v + N][u] = (transition[v + N][u] + 1) % MOD;
            }
        }

        // Compute transition^T
        std::vector<std::vector<long long>> resultMatrix = matrixPower(transition, T, M);

        // The answer is the number of ways to reach 'target' starting from node '0'
        return resultMatrix[target][0];
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}((2N)^3 \log T)$. With $N \le 30$, the matrix dimension is $M = 2N \le 60$. Multiplication takes $M^3 = 216,000$ operations, and exponentiation performs $\approx 60$ multiplications. Total operations $\approx 1.3 \times 10^7$, well within the 1-second limit.
- **Space Complexity:** $\mathcal{O}((2N)^2) = \mathcal{O}(N^2)$ auxiliary space to store the $60 \times 60$ transition matrix and multiplication buffers.
{% endraw %}

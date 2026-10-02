---
layout: post
title: 'Daily DSA: Stones of Destiny: Prime Nim Game (Medium)'
date: 2026-10-02 21:34:51 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Stones of Destiny:
  Prime Nim Game.'
cover_image: /assets/images/posts/daily-dsa-stones-of-destiny-prime-nim-game-2026-10-02-cover.png
cover_caption: ''
---

### Problem Statement

Two players, Alice and Bob, are playing a strategic game called **Prime Nim**. They are given $n$ piles of stones, where the $i$-th pile contains `stones[i]` stones. The players take turns, and Alice goes first.

In each turn, a player must:
1. Choose a non-empty pile.
2. Choose a prime number $p$ such that $p$ is less than or equal to the number of stones in that pile.
3. Remove exactly $p$ stones from the chosen pile.

The player who cannot make a move (i.e., no pile has enough stones to remove a prime number, which in this case means all piles have 0 or 1 stone) loses. Note that in this game, 1 is not a prime number.

Assuming both players play optimally, return `"Alice"` if Alice wins, and `"Bob"` if Bob wins.

### Examples

**Example 1:**
**Input:** `stones = [2, 3]`
**Output:** `"Bob"`
**Explanation:** 
- Alice can remove 2 stones from the first pile (leaving `[0, 3]`) or 2 stones from the second pile (leaving `[2, 1]`) or 3 stones from the second pile (leaving `[2, 0]`).
- If Alice moves to `[0, 3]`, Bob can remove 2 stones from the second pile (leaving `[0, 1]`). Alice cannot move (no prime exists $\le 1$). Bob wins.
- If Alice moves to `[2, 1]`, Bob removes 2 stones from the first pile (leaving `[0, 1]`). Bob wins.
- If Alice moves to `[2, 0]`, Bob removes 2 stones from the first pile (leaving `[0, 0]`). Bob wins.

**Example 2:**
**Input:** `stones = [4]`
**Output:** `"Alice"`
**Explanation:** 
- Alice can remove 2 stones (leaving 2) or 3 stones (leaving 1).
- If Alice removes 2 stones, the state becomes `[2]`. Bob must remove 2 stones (leaving 0). Bob wins.
- If Alice removes 3 stones, the state becomes `[1]`. Bob cannot move. Alice wins. Alice chooses the winning move.

### Constraints
- $1 \le n \le 10^5$
- $0 \le stones[i] \le 10^4$

---

### Approach

This is an impartial game that can be solved using the **Sprague-Grundy Theorem**. 

1. **Sprague-Grundy Theorem**: Any impartial game under the normal play convention is equivalent to a Nim pile of a certain size. This size is called the Grundy value or nim-value $G(s)$ of the state $s$.
2. **Calculating Grundy Values**: The Grundy value of a state is the smallest non-negative integer (MEX - Minimum Excluded value) that is not among the Grundy values of the states reachable in one move.
   - $G(n) = \text{mex}(\{G(n - p) \mid p \text{ is prime and } p \le n\})$
   - $G(0) = 0$
   - $G(1) = 0$ (since no primes $p \le 1$ exist)
3. **XOR Sum**: For a game with multiple independent piles, the Grundy value of the entire game is the XOR sum of the Grundy values of each pile.
   - $G_{total} = G(stones[0]) \oplus G(stones[1]) \oplus \dots \oplus G(stones[n-1])$
4. **Winning Condition**: If $G_{total} \neq 0$, the first player (Alice) wins. Otherwise, the second player (Bob) wins.

### Implementation Strategy
- Precompute primes up to $10^4$ using a sieve.
- Use dynamic programming to compute Grundy values for all $i \in [0, 10^4]$.
- Iterate through the input array, calculate the XOR sum, and return the result.

---

### C++ Solution

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <set>
#include <algorithm>

class Solution {
public:
    std::string primeNim(std::vector<int>& stones) {
        int max_val = 0;
        for (int s : stones) max_val = std::max(max_val, s);
        
        // 1. Sieve of Eratosthenes to find primes
        std::vector<int> primes;
        std::vector<bool> is_prime(max_val + 1, true);
        is_prime[0] = is_prime[1] = false;
        for (int p = 2; p <= max_val; p++) {
            if (is_prime[p]) {
                primes.push_back(p);
                for (int i = p * 2; i <= max_val; i += p)
                    is_prime[i] = false;
            }
        }

        // 2. Precompute Grundy values using MEX
        std::vector<int> g(max_val + 1, 0);
        for (int i = 2; i <= max_val; i++) {
            std::set<int> reachable_g;
            for (int p : primes) {
                if (p > i) break;
                reachable_g.insert(g[i - p]);
            }
            
            int mex = 0;
            while (reachable_g.count(mex)) {
                mex++;
            }
            g[i] = mex;
        }

        // 3. Calculate XOR sum of Grundy values for all piles
        int xor_sum = 0;
        for (int s : stones) {
            xor_sum ^= g[s];
        }

        return (xor_sum != 0) ? "Alice" : "Bob";
    }
};
```

### Complexity Analysis
- **Time Complexity**: $O(M \cdot \pi(M) + N)$, where $M$ is the maximum stone count ($10^4$) and $\pi(M)$ is the number of primes up to $M$. Precomputing Grundy values takes roughly $10^4 \times 1229$ operations in the worst case, which is well within the time limit. Processing the input takes $O(N)$.
- **Space Complexity**: $O(M)$ to store the Grundy values and the list of primes.

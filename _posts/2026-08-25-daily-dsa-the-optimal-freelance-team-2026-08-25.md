---
layout: post
title: 'Daily DSA: The Optimal Freelance Team (Hard)'
date: 2026-08-25 15:58:51 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: The Optimal Freelance
  Team.'
cover_image: /assets/images/posts/daily-dsa-the-optimal-freelance-team-2026-08-25-cover.png
cover_caption: ''
---

### Problem Description

You are a project manager looking to hire a team of freelancers for a new project. The project requires a specific set of skills, given as an array of strings `req_skills`.

You have a list of available `freelancers`, where each `freelancers[i]` is a list of strings representing the skills that the $i$-th freelancer possesses. You also have an array `costs`, where `costs[i]` is the daily rate of the $i$-th freelancer.

Your goal is to form a team that collectively possesses all the required skills while minimizing the total daily cost. If it is impossible to cover all the required skills, return -1.

### Examples

**Example 1:**

**Input:**  
`req_skills = ["java", "nodejs", "reactjs"]`  
`freelancers = [["java"], ["nodejs"], ["nodejs", "reactjs"]]`  
`costs = [10, 20, 15]`

**Output:** `25`  
**Explanation:**  
- Hiring freelancer 0 (cost 10) provides {"java"}.  
- Hiring freelancer 2 (cost 15) provides {"nodejs", "reactjs"}.  
- Total cost = 10 + 15 = 25. This is the minimum cost to cover all skills.

**Example 2:**

**Input:**  
`req_skills = ["algorithms", "frontend", "backend"]`  
`freelancers = [["algorithms", "frontend"], ["frontend", "backend"], ["algorithms"]]`  
`costs = [40, 50, 20]`

**Output:** `70`  
**Explanation:**  
- Hiring freelancer 1 (cost 50) and freelancer 2 (cost 20) covers all skills for a total cost of 70.

### Constraints

- `1 <= req_skills.length <= 16`
- `1 <= freelancers.length <= 100`
- `1 <= freelancers[i].length <= 16`
- `costs.length == freelancers.length`
- `1 <= costs[i] <= 10^5`
- All strings consist of lowercase English letters.
- `req_skills` contains unique strings.

### Approach

Since the number of required skills is small ($N \le 16$), we can use **Bitmask Dynamic Programming** to solve this variation of the Minimum Set Cover problem.

1.  **Map Skills to Bits**: Assign each skill in `req_skills` an index from $0$ to $N-1$ using a hash map.
2.  **Represent Freelancers as Masks**: For each freelancer, create a bitmask where the $j$-th bit is set if the freelancer possesses the $j$-th required skill.
3.  **DP State**: Define `dp[mask]` as the minimum cost to acquire the set of skills represented by the bitmask `mask`. There are $2^N$ possible states.
4.  **Transitions**: 
    - Initialize `dp[0] = 0` (zero cost to have no skills) and all other states to a very large value (infinity).
    - For each freelancer $i$ with bitmask `f_mask` and cost `costs[i]`:
        - Iterate through all current `mask` states from $2^N - 1$ down to $0$.
        - Update the state: `dp[mask | f_mask] = min(dp[mask | f_mask], dp[mask] + costs[i])`.
5.  **Result**: The final answer is `dp[(1 << N) - 1]`. If the value remains infinity, return -1.

### Complexity Analysis

- **Time Complexity**: $O(M \cdot 2^N)$, where $M$ is the number of freelancers and $N$ is the number of required skills. With $M=100$ and $N=16$, $100 \times 65536 = 6.5 \times 10^6$ operations, which is well within the typical 1-second time limit.
- **Space Complexity**: $O(2^N)$ to store the DP table.

### C++ Solution

```cpp
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>

using namespace std;

class Solution {
public:
    int minCost(vector<string>& req_skills, vector<vector<string>>& freelancers, vector<int>& costs) {
        int n = req_skills.size();
        unordered_map<string, int> skill_to_idx;
        for (int i = 0; i < n; ++i) {
            skill_to_idx[req_skills[i]] = i;
        }

        int m = freelancers.size();
        // Use a large value for infinity that won't overflow during addition
        long long INF = 1e15;
        vector<long long> dp(1 << n, INF);
        dp[0] = 0;

        for (int i = 0; i < m; ++i) {
            int f_mask = 0;
            for (const string& skill : freelancers[i]) {
                if (skill_to_idx.count(skill)) {
                    f_mask |= (1 << skill_to_idx[skill]);
                }
            }

            // Optimization: skip freelancers who provide no required skills
            if (f_mask == 0) continue;

            // Iterate backwards to ensure we build on results from previous freelancers
            for (int mask = (1 << n) - 1; mask >= 0; --mask) {
                if (dp[mask] != INF) {
                    int next_mask = mask | f_mask;
                    if (dp[next_mask] > dp[mask] + costs[i]) {
                        dp[next_mask] = dp[mask] + costs[i];
                    }
                }
            }
        }

        long long result = dp[(1 << n) - 1];
        return (result >= INF) ? -1 : (int)result;
    }
};
```

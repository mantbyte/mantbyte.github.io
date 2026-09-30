---
layout: post
title: 'Daily DSA: Stable Internship Matching (Medium)'
date: 2026-09-30 21:44:24 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Stable Internship
  Matching.'
cover_image: /assets/images/posts/daily-dsa-stable-internship-matching-2026-09-30-cover.png
cover_caption: ''
---

### Problem Statement

There are $N$ interns and $N$ companies. Each intern has a preference list ranking all $N$ companies from most preferred to least preferred. Similarly, each company has a preference list ranking all $N$ interns from most preferred to least preferred.

A matching is a set of $N$ pairs $(i, c)$ such that every intern $i$ is assigned to exactly one company $c$, and every company is assigned to exactly one intern.

A matching is considered **unstable** if there exists an intern $i$ and a company $c$ who are not matched with each other, but:
1. Intern $i$ prefers company $c$ over their currently assigned company.
2. Company $c$ prefers intern $i$ over their currently assigned intern.

Such a pair $(i, c)$ is called a **blocking pair**. A matching is **stable** if it contains no blocking pairs.

Your task is to find any stable matching and return the assignments as an array `ans` of size $N$, where `ans[i]` is the index of the company assigned to intern $i$.

### Examples

**Example 1:**
**Input:** 
$N = 2$
`internPrefs = [[0, 1], [0, 1]]` 
`companyPrefs = [[1, 0], [0, 1]]` 
**Output:** `[1, 0]` 
**Explanation:** 
- Intern 0 is matched with Company 1. 
- Intern 1 is matched with Company 0. 
Check for instability: 
- Intern 0 prefers Company 0 over Company 1. However, Company 0 prefers Intern 1 over Intern 0. So (0, 0) is not a blocking pair. 
- Intern 1 prefers Company 0 (their current match). No blocking pair. 
The matching is stable.

**Example 2:**
**Input:** 
$N = 3$
`internPrefs = [[0, 1, 2], [1, 0, 2], [0, 1, 2]]` 
`companyPrefs = [[2, 1, 0], [0, 1, 2], [2, 0, 1]]` 
**Output:** `[1, 2, 0]`
**Explanation:** 
- Intern 0 matches Company 1, Intern 1 matches Company 2, Intern 2 matches Company 0. This configuration is stable under the given preferences.

### Constraints

* $1 \le N \le 500$
* `internPrefs[i]` is a permutation of integers from $0$ to $N-1$.
* `companyPrefs[i]` is a permutation of integers from $0$ to $N-1$.

### Approach

The **Gale-Shapley Algorithm** is the standard approach to solve the Stable Marriage Problem. It guarantees a stable matching in $O(N^2)$ time.

1. **Initialization**: Start with all interns and companies being free. Create a queue of free interns.
2. **Proposal Phase**: While there is at least one free intern $i$:
    - Let $c$ be the highest-ranked company in $i$'s preference list to which $i$ has not yet proposed.
    - If company $c$ is free, match $(i, c)$.
    - If company $c$ is already matched with intern $i'$:
        - Check if $c$ prefers $i$ over $i'$. 
        - If $c$ prefers $i$, break the match $(i', c)$, match $(i, c)$, and add $i'$ back to the free interns queue.
        - If $c$ prefers $i'$, intern $i$ remains free and will propose to their next choice in the next iteration.
3. **Optimization**: To check if a company prefers one intern over another in $O(1)$, pre-process the `companyPrefs` into a 2D `rank` array where `rank[c][i]` is the position of intern $i$ in company $c$'s preference list (smaller value means higher preference).

### C++ Solution

```cpp
#include <vector>
#include <queue>
#include <algorithm>

using namespace std;

class Solution {
public:
    vector<int> findStableMatching(int n, vector<vector<int>>& internPrefs, vector<vector<int>>& companyPrefs) {
        // rank[c][i] stores the preference rank of intern i for company c
        vector<vector<int>> coRank(n, vector<int>(n));
        for (int c = 0; c < n; ++c) {
            for (int r = 0; r < n; ++r) {
                coRank[c][companyPrefs[c][r]] = r;
            }
        }

        vector<int> internMatch(n, -1); // internMatch[i] = company matched with i
        vector<int> coMatch(n, -1);     // coMatch[c] = intern matched with c
        vector<int> nextProposal(n, 0); // next company index for intern i to propose to
        queue<int> freeInterns;

        for (int i = 0; i < n; ++i) {
            freeInterns.push(i);
        }

        while (!freeInterns.empty()) {
            int i = freeInterns.front();
            freeInterns.pop();

            // Intern i proposes to their next most preferred company
            int c = internPrefs[i][nextProposal[i]++];

            if (coMatch[c] == -1) {
                // Company is free, they accept the proposal
                coMatch[c] = i;
                internMatch[i] = c;
            } else {
                int currentI = coMatch[c];
                // Company compares current intern with the new proposer
                if (coRank[c][i] < coRank[c][currentI]) {
                    // Company prefers new intern i
                    coMatch[c] = i;
                    internMatch[i] = c;
                    // Previous intern becomes free
                    internMatch[currentI] = -1;
                    freeInterns.push(currentI);
                } else {
                    // Company stays with current intern, i remains free
                    freeInterns.push(i);
                }
            }
        }

        return internMatch;
    }
};
```

### Complexity Analysis

* **Time Complexity**: $O(N^2)$. There are $N$ interns, and each intern proposes to each of the $N$ companies at most once. Each proposal and comparison is handled in $O(1)$ time.
* **Space Complexity**: $O(N^2)$ to store the `coRank` matrix for $O(1)$ preference lookups. The matching arrays and queue use $O(N)$ space.

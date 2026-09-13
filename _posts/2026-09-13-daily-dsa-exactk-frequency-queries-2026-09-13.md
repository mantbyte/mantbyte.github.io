---
layout: post
title: 'Daily DSA: Exact-K Frequency Queries (Hard)'
date: 2026-09-13 19:33:54 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Exact-K Frequency
  Queries.'
cover_image: /assets/images/posts/daily-dsa-exactk-frequency-queries-2026-09-13-cover.png
cover_caption: ''
---

### Problem Description

You are given an array `nums` of `n` integers and `q` queries. Each query is represented by a triplet `[L, R, K]`. For each query, your task is to find the number of distinct integers that appear **exactly** `K` times in the subarray `nums[L...R]` (inclusive, 0-indexed).

Since the queries are provided upfront, you should process them offline to achieve an efficient solution.

### Examples

**Example 1:**
**Input:** `nums = [1, 2, 2, 3, 3, 3]`, `queries = [[0, 5, 2], [1, 4, 1]]`  
**Output:** `[1, 0]`  
**Explanation:**
- Query 1: Subarray `nums[0...5]` is `[1, 2, 2, 3, 3, 3]`. 
  - `1` appears 1 time.
  - `2` appears 2 times.
  - `3` appears 3 times.
  Only the integer `2` appears exactly `K=2` times. The count is 1.
- Query 2: Subarray `nums[1...4]` is `[2, 2, 3, 3]`. 
  - `2` appears 2 times.
  - `3` appears 2 times.
  No integer appears exactly `K=1` time. The count is 0.

**Example 2:**
**Input:** `nums = [4, 4, 4, 4]`, `queries = [[0, 3, 4], [0, 2, 3]]`  
**Output:** `[1, 1]`  
**Explanation:**
- Query 1: Subarray `[4, 4, 4, 4]`, `4` appears 4 times. Since `K=4`, count is 1.
- Query 2: Subarray `[4, 4, 4]`, `4` appears 3 times. Since `K=3`, count is 1.

### Constraints

- $1 \le n, q \le 10^5$
- $1 \le nums[i] \le 10^9$
- $0 \le L \le R < n$
- $1 \le K \le n$

### Approach

1. **Offline Processing (Mo's Algorithm):** 
   Standard range query structures like Segment Trees or Fenwick Trees are difficult to use for "exactly K" frequency queries. Since there are no updates, we can use **Mo's Algorithm**. By sorting the queries in a specific block-based order, we can minimize the movement of range pointers ($L$ and $R$).

2. **Coordinate Compression:** 
   Since the values in `nums` can be up to $10^9$, we first map them to a smaller range $[0, N-1]$ using a hash map or by sorting and using `lower_bound` to maintain them as array indices.

3. **Frequency Management:**
   - Use an array `cnt[x]` to store the frequency of the compressed value `x` in the current window.
   - Use an array `freqFreq[f]` to store the number of distinct elements that currently have a frequency of exactly `f`.
   - When adding an element `x`: 
     - If `cnt[x] > 0`, decrement `freqFreq[cnt[x]]`.
     - Increment `cnt[x]`.
     - Increment `freqFreq[cnt[x]]`.
   - When removing an element `x`:
     - Decrement `freqFreq[cnt[x]]`.
     - Decrement `cnt[x]`.
     - If `cnt[x] > 0`, increment `freqFreq[cnt[x]]`.

4. **Result Extraction:**
   For each query `[L, R, K]`, after moving the pointers to the range, the answer is simply `freqFreq[K]`.

### C++ Solution

```cpp
#include <vector>
#include <algorithm>
#include <cmath>
#include <iostream>

using namespace std;

struct Query {
    int l, r, k, id;
};

class Solution {
public:
    vector<int> solveExactK(vector<int>& nums, vector<vector<int>>& queries_raw) {
        int n = nums.size();
        int q = queries_raw.size();

        // 1. Coordinate Compression
        vector<int> coords = nums;
        sort(coords.begin(), coords.end());
        coords.erase(unique(coords.begin(), coords.end()), coords.end());
        for (int &x : nums) {
            x = lower_bound(coords.begin(), coords.end(), x) - coords.begin();
        }

        // 2. Prepare Queries
        vector<Query> queries(q);
        for (int i = 0; i < q; ++i) {
            queries[i] = {queries_raw[i][0], queries_raw[i][1], queries_raw[i][2], i};
        }

        // 3. Mo's Sorting
        int blockSize = max(1, (int)(n / sqrt(q + 1)));
        sort(queries.begin(), queries.end(), [&](const Query& a, const Query& b) {
            int bA = a.l / blockSize;
            int bB = b.l / blockSize;
            if (bA != bB) return bA < bB;
            // Optimization: Alternate sort direction for right pointer
            return (bA % 2 == 0) ? (a.r < b.r) : (a.r > b.r);
        });

        // 4. Processing
        vector<int> cnt(coords.size(), 0);
        vector<int> freqFreq(n + 1, 0);
        vector<int> results(q);
        int curL = 0, curR = -1;

        auto add = [&](int val) {
            if (cnt[val] > 0) freqFreq[cnt[val]]--;
            cnt[val]++;
            freqFreq[cnt[val]]++;
        };

        auto remove = [&](int val) {
            freqFreq[cnt[val]]--;
            cnt[val]--;
            if (cnt[val] > 0) freqFreq[cnt[val]]++;
        };

        for (const auto& query : queries) {
            while (curR < query.r) add(nums[++curR]);
            while (curL > query.l) add(nums[--curL]);
            while (curR > query.r) remove(nums[curR--]);
            while (curL < query.l) remove(nums[curL++]);

            if (query.k >= 1 && query.k <= n) {
                results[query.id] = freqFreq[query.k];
            } else {
                results[query.id] = 0;
            }
        }

        return results;
    }
};
```

### Complexity Analysis

- **Time Complexity:** $O((n + q) \sqrt{n} + n \log n)$. The $n \log n$ part comes from coordinate compression and query sorting. The $(n + q) \sqrt{n}$ part is the standard complexity of Mo's algorithm where the left pointer moves $O(q \sqrt{n})$ and the right pointer moves $O(n \sqrt{n})$.
- **Space Complexity:** $O(n + q)$ to store the compressed array, the query structures, the frequency arrays, and the final results.

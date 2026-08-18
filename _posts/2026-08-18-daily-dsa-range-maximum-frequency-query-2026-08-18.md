---
layout: post
title: 'Daily DSA: Range Maximum Frequency Query (Hard)'
date: 2026-08-18 15:52:51 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Range Maximum
  Frequency Query.'
cover_image: /assets/images/posts/daily-dsa-range-maximum-frequency-query-2026-08-18-cover.png
cover_caption: ''
---

### Problem Description

You are given an integer array `nums` of size `n`. You need to process `q` operations of two types:

1.  **Update Operation**: `[1, index, val]`
    Update the value at `nums[index]` to `val`.

2.  **Query Operation**: `[2, left, right]`
    Find the maximum value in the subarray `nums[left...right]` (inclusive) and determine how many times this maximum value occurs within that specific range.

Return an array of pairs (or a 2D array), where each pair contains `[max_value, frequency]` for each query of type 2.

### Example 1

**Input:**
`nums = [3, 2, 3, 1, 3]`
`queries = [[2, 0, 4], [1, 2, 1], [2, 0, 4]]`

**Output:**
`[[3, 3], [3, 2]]`

**Explanation:**
1. The first query `[2, 0, 4]` asks for the max and frequency in the range `[0, 4]`. In `[3, 2, 3, 1, 3]`, the maximum is `3` and it appears `3` times.
2. The second operation `[1, 2, 1]` updates `nums[2]` to `1`. The array becomes `[3, 2, 1, 1, 3]`.
3. The third query `[2, 0, 4]` asks for the max and frequency in the range `[0, 4]`. In `[3, 2, 1, 1, 3]`, the maximum is still `3`, but it now appears only `2` times.

### Example 2

**Input:**
`nums = [10, 10, 10]`
`queries = [[2, 0, 1], [1, 0, 5], [2, 0, 2]]`

**Output:**
`[[10, 2], [10, 2]]`

### Constraints

- `1 <= nums.length <= 10^5`
- `1 <= q <= 10^5`
- `1 <= nums[i], val <= 10^9`
- `0 <= left <= right < nums.length`
- `0 <= index < nums.length`

### Approach

A standard array approach would take $O(N)$ per query, leading to $O(Q \times N)$, which is too slow ($10^{10}$ operations). To handle both point updates and range queries efficiently, a **Segment Tree** is the optimal choice.

Each node in the Segment Tree will store:
- `maxVal`: The maximum value in the range covered by the node.
- `count`: The frequency of that maximum value in the range.

**Merging two nodes (Left and Right):**
- If `Left.maxVal > Right.maxVal`, the parent node takes `Left.maxVal` and `Left.count`.
- If `Right.maxVal > Left.maxVal`, the parent node takes `Right.maxVal` and `Right.count`.
- If `Left.maxVal == Right.maxVal`, the parent node takes `Left.maxVal` and the sum of `Left.count + Right.count`.

**Complexity:**
- **Build:** $O(N)$
- **Update:** $O(\log N)$
- **Query:** $O(\log N)$
- **Space:** $O(N)$ to store the tree nodes.

### C++ Solution

```cpp
#include <vector>
#include <utility>
#include <algorithm>

using namespace std;

struct Node {
    int maxVal;
    int count;
};

class RangeMaxFreq {
private:
    int n;
    vector<Node> tree;

    Node merge(Node a, Node b) {
        if (a.maxVal > b.maxVal) return a;
        if (b.maxVal > a.maxVal) return b;
        if (a.maxVal == -1) return b;
        if (b.maxVal == -1) return a;
        return {a.maxVal, a.count + b.count};
    }

    void build(const vector<int>& nums, int node, int start, int end) {
        if (start == end) {
            tree[node] = {nums[start], 1};
            return;
        }
        int mid = start + (end - start) / 2;
        build(nums, 2 * node, start, mid);
        build(nums, 2 * node + 1, mid + 1, end);
        tree[node] = merge(tree[2 * node], tree[2 * node + 1]);
    }

    void update(int node, int start, int end, int idx, int val) {
        if (start == end) {
            tree[node] = {val, 1};
            return;
        }
        int mid = start + (end - start) / 2;
        if (idx <= mid) update(2 * node, start, mid, idx, val);
        else update(2 * node + 1, mid + 1, end, idx, val);
        tree[node] = merge(tree[2 * node], tree[2 * node + 1]);
    }

    Node query(int node, int start, int end, int l, int r) {
        if (r < start || end < l) return {-1, 0};
        if (l <= start && end <= r) return tree[node];
        int mid = start + (end - start) / 2;
        Node leftRes = query(2 * node, start, mid, l, r);
        Node rightRes = query(2 * node + 1, mid + 1, end, l, r);
        if (leftRes.maxVal == -1) return rightRes;
        if (rightRes.maxVal == -1) return leftRes;
        return merge(leftRes, rightRes);
    }

public:
    RangeMaxFreq(const vector<int>& nums) {
        n = nums.size();
        if (n > 0) {
            tree.assign(4 * n, {0, 0});
            build(nums, 1, 0, n - 1);
        }
    }

    pair<int, int> queryRange(int l, int r) {
        Node res = query(1, 0, n - 1, l, r);
        return {res.maxVal, res.count};
    }

    void updatePoint(int idx, int val) {
        update(1, 0, n - 1, idx, val);
    }
};
```

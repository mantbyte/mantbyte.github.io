---
layout: post
title: 'Daily DSA: Range Maximum Subarray Sum (Hard)'
date: 2026-10-26 21:55:51 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Range Maximum
  Subarray Sum.'
cover_image: /assets/images/posts/daily-dsa-range-maximum-subarray-sum-2026-10-26-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

Given an array `nums` of $N$ integers and $Q$ queries, you need to process two types of operations:

1.  **Update**: Change the value at a specific index `i` to a new value `v`.
2.  **Query**: Find the maximum possible sum of a non-empty contiguous subarray within the range $[L, R]$.

### Examples

**Example 1:**
**Input:** 
`nums = [1, -2, 3, 4]`, `queries = [["query", 0, 3], ["update", 1, 5], ["query", 0, 3]]`  
**Output:** `[7, 13]`  
**Explanation:**  
- First query: Range [0, 3] is `[1, -2, 3, 4]`. Max subarray is `[3, 4]` with sum 7.  
- Update: `nums` becomes `[1, 5, 3, 4]`.  
- Second query: Range [0, 3] is `[1, 5, 3, 4]`. Max subarray is the whole range with sum 13.

**Example 2:**
**Input:** 
`nums = [-5, -1, -2]`, `queries = [["query", 0, 2]]`  
**Output:** `[-1]`  
**Explanation:**  
- Max subarray is `[-1]` at index 1.

### Constraints

- $1 \le N, Q \le 5 \cdot 10^4$
- $-10^9 \le nums[i], v \le 10^9$
- $0 \le L \le R < N$

---

### Approach

To solve this problem efficiently, we use a **Segment Tree**. A standard Segment Tree allows us to find the sum of a range in $O(\log N)$, but finding the maximum subarray sum requires storing more metadata in each node.

Each node in the Segment Tree will represent a range $[l, r]$ and store four values:
1.  `sum`: The total sum of the range.
2.  `pref`: The maximum prefix sum in the range (must start from $l$).
3.  `suff`: The maximum suffix sum in the range (must end at $r$).
4.  `max_sub`: The maximum subarray sum within the range.

#### Merging Two Nodes ($L$ and $R$):
When merging a left child and a right child into a parent node:
-   `node.sum = L.sum + R.sum`
-   `node.pref = max(L.pref, L.sum + R.pref)`
-   `node.suff = max(R.suff, R.sum + L.suff)`
-   `node.max_sub = max({L.max_sub, R.max_sub, L.suff + R.pref})`

For leaf nodes (representing a single element $x$):
-   `sum = x`, `pref = x`, `suff = x`, `max_sub = x`.

### Complexity
- **Build**: $O(N)$
- **Update**: $O(\log N)$
- **Query**: $O(\log N)$
- **Space**: $O(N)$ to store the tree.

---

### C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

struct Node {
    long long sum;
    long long pref;
    long long suff;
    long long max_sub;

    static Node leaf(long long val) {
        return {val, val, val, val};
    }
};

Node merge(const Node& L, const Node& R) {
    Node res;
    res.sum = L.sum + R.sum;
    res.pref = max(L.pref, L.sum + R.pref);
    res.suff = max(R.suff, R.sum + L.suff);
    res.max_sub = max({L.max_sub, R.max_sub, L.suff + R.pref});
    return res;
}

class SegmentTree {
    int n;
    vector<Node> tree;

    void build(const vector<int>& nums, int node, int start, int end) {
        if (start == end) {
            tree[node] = Node::leaf(nums[start]);
            return;
        }
        int mid = (start + end) / 2;
        build(nums, 2 * node, start, mid);
        build(nums, 2 * node + 1, mid + 1, end);
        tree[node] = merge(tree[2 * node], tree[2 * node + 1]);
    }

    void update(int node, int start, int end, int idx, int val) {
        if (start == end) {
            tree[node] = Node::leaf(val);
            return;
        }
        int mid = (start + end) / 2;
        if (idx <= mid) update(2 * node, start, mid, idx, val);
        else update(2 * node + 1, mid + 1, end, idx, val);
        tree[node] = merge(tree[2 * node], tree[2 * node + 1]);
    }

    Node query(int node, int start, int end, int l, int r) {
        if (l == start && r == end) return tree[node];
        int mid = (start + end) / 2;
        if (r <= mid) return query(2 * node, start, mid, l, r);
        if (l > mid) return query(2 * node + 1, mid + 1, end, l, r);
        
        Node leftRes = query(2 * node, start, mid, l, mid);
        Node rightRes = query(2 * node + 1, mid + 1, end, mid + 1, r);
        return merge(leftRes, rightRes);
    }

public:
    SegmentTree(const vector<int>& nums) {
        n = nums.size();
        tree.resize(4 * n);
        build(nums, 1, 0, n - 1);
    }

    void update(int idx, int val) {
        update(1, 0, n - 1, idx, val);
    }

    long long query(int l, int r) {
        return query(1, 0, n - 1, l, r).max_sub;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n = 4;
    vector<int> nums = {1, -2, 3, 4};
    SegmentTree st(nums);

    cout << st.query(0, 3) << endl; // Output: 7
    st.update(1, 5);
    cout << st.query(0, 3) << endl; // Output: 13

    return 0;
}
```
{% endraw %}

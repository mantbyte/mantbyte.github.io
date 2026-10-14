---
layout: post
title: 'Daily DSA: Light Switch Board (Medium)'
date: 2026-10-14 20:20:38 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Light Switch
  Board.'
cover_image: /assets/images/posts/daily-dsa-light-switch-board-2026-10-14-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are managing a long hallway with `n` light bulbs, indexed `0` to `n - 1`. Initially, all bulbs are turned **off** (0).

You need to process `q` queries of two types:
1. **Toggle Range** (`1 left right`): For every bulb `i` where `left <= i <= right`, flip its state. If the bulb was off, it becomes on; if it was on, it becomes off.
2. **Count On** (`2 left right`): Return the number of bulbs that are currently **on** in the inclusive range `[left, right]`.

### Examples

**Example 1:**
**Input:** 
`n = 5` 
`queries = [[1, 0, 2], [2, 0, 4], [1, 2, 4], [2, 0, 4]]` 
**Output:** 
`[3, 4]`
**Explanation:**
- Initial state: `[OFF, OFF, OFF, OFF, OFF]`
- `1 0 2`: Toggle bulbs 0, 1, and 2. State: `[ON, ON, ON, OFF, OFF]`
- `2 0 4`: Count ON bulbs in `[0, 4]`. Indices 0, 1, 2 are ON. Result: `3`.
- `1 2 4`: Toggle bulbs 2, 3, and 4. Bulb 2 turns OFF, bulbs 3 and 4 turn ON. State: `[ON, ON, OFF, ON, ON]`
- `2 0 4`: Count ON bulbs in `[0, 4]`. Indices 0, 1, 3, 4 are ON. Result: `4`.

**Example 2:**
**Input:** 
`n = 10`, `queries = [[1, 0, 9], [2, 0, 9], [1, 5, 5], [2, 0, 9]]` 
**Output:** 
`[10, 9]`
**Explanation:**
- `1 0 9`: All 10 bulbs turn ON.
- `2 0 9`: Count is 10.
- `1 5 5`: Bulb 5 turns OFF.
- `2 0 9`: Count is 9.

### Constraints
- `1 <= n <= 10^5`
- `1 <= queries.length <= 10^5`
- `queries[i][0]` is either `1` (Toggle) or `2` (Count).
- `0 <= queries[i][1] <= queries[i][2] < n`

### Approach

A naive approach would take $O(N)$ for each toggle query, resulting in $O(N \cdot Q)$ total time, which is too slow for $10^5$. 

We use a **Segment Tree with Lazy Propagation** to optimize range updates and queries to $O(\log N)$:
1. **Segment Tree Node**: Each node in the tree stores `on_count`, the number of bulbs currently ON in that node's range.
2. **Lazy Propagation**: We maintain a boolean array `lazy`. If `lazy[v]` is true, it means the range covered by node `v` needs to be toggled, but the update hasn't been pushed to its children yet.
3. **Toggle Logic**: When we toggle a range $[L, R]$:
   - If the current node's range $[tl, tr]$ is entirely inside $[L, R]$, the new `on_count` becomes `(tr - tl + 1) - on_count`. We then flip the `lazy` flag for this node.
   - If there is a partial overlap, we push the current node's lazy flag to its children and recurse.
4. **Query Logic**: Similar to standard range sum queries, we aggregate the `on_count` from relevant nodes while pushing lazy flags down as needed.

### C++ Solution

```cpp
#include <vector>
#include <iostream>

using namespace std;

class LightSwitchBoard {
private:
    int n;
    vector<int> tree;
    vector<bool> lazy;

    void push(int v, int tl, int tr) {
        if (lazy[v]) {
            int tm = tl + (tr - tl) / 2;
            
            // Toggle left child
            tree[2 * v] = (tm - tl + 1) - tree[2 * v];
            lazy[2 * v] = !lazy[2 * v];
            
            // Toggle right child
            tree[2 * v + 1] = (tr - tm) - tree[2 * v + 1];
            lazy[2 * v + 1] = !lazy[2 * v + 1];
            
            lazy[v] = false;
        }
    }

    void update(int v, int tl, int tr, int l, int r) {
        if (l > r) return;
        if (l == tl && r == tr) {
            tree[v] = (tr - tl + 1) - tree[v];
            lazy[v] = !lazy[v];
        } else {
            push(v, tl, tr);
            int tm = tl + (tr - tl) / 2;
            update(2 * v, tl, tm, l, min(r, tm));
            update(2 * v + 1, tm + 1, tr, max(l, tm + 1), r);
            tree[v] = tree[2 * v] + tree[2 * v + 1];
        }
    }

    int query(int v, int tl, int tr, int l, int r) {
        if (l > r) return 0;
        if (l == tl && r == tr) return tree[v];
        push(v, tl, tr);
        int tm = tl + (tr - tl) / 2;
        return query(2 * v, tl, tm, l, min(r, tm)) + 
               query(2 * v + 1, tm + 1, tr, max(l, tm + 1), r);
    }

public:
    LightSwitchBoard(int n) : n(n) {
        tree.assign(4 * n, 0);
        lazy.assign(4 * n, false);
    }

    void toggle(int l, int r) {
        update(1, 0, n - 1, l, r);
    }

    int countOn(int l, int r) {
        return query(1, 0, n - 1, l, r);
    }
};

vector<int> processQueries(int n, vector<vector<int>>& queries) {
    LightSwitchBoard lsb(n);
    vector<int> results;
    for (auto& q : queries) {
        if (q[0] == 1) {
            lsb.toggle(q[1], q[2]);
        } else {
            results.push_back(lsb.countOn(q[1], q[2]));
        }
    }
    return results;
}
```

### Complexity Analysis
- **Time Complexity**: $O((N + Q) \log N)$. Building the tree (implicitly) takes $O(N)$, and each of the $Q$ queries takes $O(\log N)$ due to the segment tree structure.
- **Space Complexity**: $O(N)$ to store the segment tree and lazy propagation arrays (typically $4N$ nodes).
{% endraw %}

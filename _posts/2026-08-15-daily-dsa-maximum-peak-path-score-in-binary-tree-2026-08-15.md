---
layout: post
title: 'Daily DSA: Maximum Peak Path Score in Binary Tree (Medium)'
date: 2026-08-15 15:47:13 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Maximum Peak
  Path Score in Binary Tree.'
cover_image: /assets/images/posts/daily-dsa-maximum-peak-path-score-in-binary-tree-2026-08-15-cover.png
cover_caption: ''
---

### Problem Statement

Given the `root` of a binary tree where each node contains an integer `val`, a **Peak Path** is defined as a simple path starting at some node $u$, moving upwards to a highest ancestor node $A$, and then moving downwards to a node $v$ ($u$, $A$, and $v$ do not need to be distinct).

The **score** of a Peak Path is computed as:
$$\text{Score} = \sum_{x \in \text{path}(u \to A)} x.\text{val} - \sum_{y \in \text{path}(A \to v, y \neq A)} y.\text{val}$$

In other words, the values of all nodes on the upward path from $u$ to $A$ (inclusive) are **added**, while the values of all nodes on the downward path from $A$ to $v$ (excluding $A$) are **subtracted**.

Return the **maximum possible score** of any Peak Path in the binary tree.

---

### Examples

#### Example 1:
```
        5
       / \
      8   -3
     /     \
    4       2
```
**Input:** `root = [5, 8, -3, 4, null, null, 2]`  
**Output:** `20`  
**Explanation:**  
Choose the path starting at node `4`, moving up through `8` to peak `5`, and moving down to node `-3`:
- Upward segment: `4 -> 8 -> 5` (sum = $4 + 8 + 5 = 17$)
- Downward segment: `5 -> -3` (excluding peak `5`, value subtracted is $-3$)
- Score = $17 - (-3) = 20$.

#### Example 2:
```
       -10
       /  \
      9   20
          / \
         15  7
```
**Input:** `root = [-10, 9, 20, null, null, 15, 7]`  
**Output:** `42`  
**Explanation:**  
Choose peak node `20`. The upward leg comes from child `15` and no downward leg is taken (downward path stops at `20`).  
- Score = $15 + 20 = 35$.
However, taking peak at `20`, upward leg from `15` ($15 + 20$), downward leg to `7` gives $15 + 20 - (7) = 28$.
Taking the peak at `20` with upward leg from `15` and downward to none gives `35`.
Choosing the single node `20` gives `20`.
Notice if we pick peak `20` with downward path through a node with negative value, we get higher score. With the given values, the maximum score achieved is `35` (or `42` if peak is `20`, upward is `15`, downward is `-7`). Here with given positive values, the best is $15 + 20 = 35$.

#### Example 3:
```
       -5
```
**Input:** `root = [-5]`  
**Output:** `-5`  
**Explanation:** The tree has only one node, so the path consists of just `[-5]`. Score = `-5`.

---

### Constraints

- The number of nodes in the tree is in the range $[1, 10^5]$.
- $-10^4 \le \text{Node.val} \le 10^4$

---

### Approach

This problem can be framed as a variation of the classic **Tree Dynamic Programming** (similar to *Binary Tree Maximum Path Sum*).

For each subtree rooted at `node`, a path passing through `node` as the peak $A$ can be formed by combining:
1. An optimal upward path ending at `node` (we want to **maximize** this sum).
2. An optimal downward path starting just below `node` (we want to **minimize** this sum so that subtracting it adds the largest possible value).

For any subtree rooted at `curr`:
- Let `max_up(curr)` be the maximum sum of a path starting from any descendant of `curr` and moving strictly up to `curr`.
  $$\text{max\_up}(\text{curr}) = \text{curr.val} + \max(0, \max(\text{max\_up}(\text{left}), \text{max\_up}(\text{right})))$$
- Let `min_down(curr)` be the minimum sum of a path starting at `curr` and moving strictly down to any descendant.
  $$\text{min\_down}(\text{curr}) = \text{curr.val} + \min(0, \min(\text{min\_down}(\text{left}), \text{min\_down}(\text{right})))$$

When treating `curr` as the peak ancestor $A$:
- Upward from Left, Downward into Right: $\text{max\_up}(\text{left}) + \text{curr.val} - \text{min\_down}(\text{right})$ (if both subtrees exist)
- Upward from Right, Downward into Left: $\text{max\_up}(\text{right}) + \text{curr.val} - \text{min\_down}(\text{left})$ (if both subtrees exist)
- Peak using only one side (either only upward or only downward) or just `curr` itself: $\text{curr.val} + \max(0, \text{max\_up}) - \min(0, \text{min\_down})$.

By running a single post-order DFS traversal, we compute these quantities bottom-up in $O(N)$ time.

---

### C++ Solution

```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */

#include <algorithm>
#include <climits>

class Solution {
private:
    long long max_score = LLONG_MIN;

    struct SubtreeResult {
        long long max_up;   // Max path sum moving upward into this node
        long long min_down; // Min path sum moving downward from this node
    };

    SubtreeResult dfs(TreeNode* root) {
        if (!root) {
            return {LLONG_MIN / 2, LLONG_MAX / 2};
        }

        SubtreeResult left = dfs(root->left);
        SubtreeResult right = dfs(root->right);

        long long val = root->val;

        // 1. Calculate best up and down chains ending/starting at root
        long long best_child_up = std::max({0LL, left.max_up, right.max_up});
        long long best_child_down = std::min({0LL, left.min_down, right.min_down});

        long long curr_max_up = val + best_child_up;
        long long curr_min_down = val + best_child_down;

        // 2. Consider 'root' as the peak node A
        // Case A: Path only uses one branch (or no branches)
        max_score = std::max(max_score, curr_max_up);
        max_score = std::max(max_score, val - best_child_down);
        max_score = std::max(max_score, curr_max_up - best_child_down);

        // Case B: Peak combines left upward and right downward
        if (root->left && root->right) {
            if (left.max_up != LLONG_MIN / 2 && right.min_down != LLONG_MAX / 2) {
                max_score = std::max(max_score, left.max_up + val - right.min_down);
            }
            if (right.max_up != LLONG_MIN / 2 && left.min_down != LLONG_MAX / 2) {
                max_score = std::max(max_score, right.max_up + val - left.min_down);
            }
        }

        return {curr_max_up, curr_min_down};
    }

public:
    long long maxPeakPathScore(TreeNode* root) {
        max_score = LLONG_MIN;
        dfs(root);
        return max_score;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(N)$, where $N$ is the number of nodes in the binary tree. Each node is visited exactly once during the post-order traversal.
- **Space Complexity:** $\mathcal{O}(H)$, where $H$ is the height of the binary tree, corresponding to the maximum depth of the call stack ($\mathcal{O}(\log N)$ for balanced trees, $\mathcal{O}(N)$ in the worst case).

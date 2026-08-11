---
layout: post
title: 'Daily DSA: Count Pairs With XOR in Range (Hard)'
date: 2026-08-11 16:15:25 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Count Pairs With
  XOR in Range.'
cover_image: /assets/images/posts/daily-dsa-count-pairs-with-xor-in-range-2026-08-11-cover.png
cover_caption: ''
---

### Problem Description

Given an integer array `nums` and two integers `low` and `high`, return *the number of **nice pairs***.

A **nice pair** is a pair `(i, j)` such that:
- `0 <= i < j < nums.length`
- `low <= (nums[i] XOR nums[j]) <= high`

### Examples

**Example 1:**
```
Input: nums = [1, 4, 2, 7], low = 2, high = 6
Output: 6
Explanation: All possible pairs (i, j) with i < j and their XOR values:
- (0, 1): 1 XOR 4 = 5
- (0, 2): 1 XOR 2 = 3
- (0, 3): 1 XOR 7 = 6
- (1, 2): 4 XOR 2 = 6
- (1, 3): 4 XOR 7 = 3
- (2, 3): 2 XOR 7 = 5
All 6 pairs have XOR values in the range [2, 6].
```

**Example 2:**
```
Input: nums = [9, 8, 4, 2, 1], low = 5, high = 14
Output: 8
Explanation: The nice pairs are:
- (0, 2): 9 XOR 4 = 13
- (0, 3): 9 XOR 2 = 11
- (0, 4): 9 XOR 1 = 8
- (1, 2): 8 XOR 4 = 12
- (1, 3): 8 XOR 2 = 10
- (1, 4): 8 XOR 1 = 9
- (2, 3): 4 XOR 2 = 6
- (2, 4): 4 XOR 1 = 5
```

### Constraints

- `1 <= nums.length <= 2 * 10^4`
- `1 <= nums[i] <= 2 * 10^4`
- `1 <= low <= high <= 2 * 10^4`

---

### Approach

1. **Range Query Decomposition**:
   The condition `low <= (nums[i] XOR nums[j]) <= high` can be rewritten as:
   `count_pairs_less_than_or_equal(high) - count_pairs_less_than_or_equal(low - 1)`.
   This simplifies the problem to counting pairs whose XOR value is less than or equal to a target `limit`.

2. **Trie Structure for Bitwise Comparison**:
   We can insert binary representations of numbers into a **Trie** (Prefix Tree). Each node in the Trie represents a bit (`0` or `1`) and maintains a `count` field representing how many numbers pass through that node.

3. **Querying the Trie**:
   To find how many previously inserted numbers `y` satisfy `(x XOR y) <= limit`:
   - We traverse the Trie from the most significant bit (15th bit is enough since $2 \times 10^4 < 2^{15}$) down to the 0th bit.
   - At each bit position `b`:
     - Extract the bit of $x$ (`bit_x`) and the bit of $limit$ (`bit_limit`).
     - If `bit_limit == 1`:
       - Taking the branch `bit_x` makes the $b$-th bit of `(x XOR y)` equal to `0`, which is strictly smaller than `bit_limit` (`1`). Thus, **all** numbers in the subtree `node->children[bit_x]` will satisfy the condition. We add `node->children[bit_x]->count` to our result.
       - We then move to the branch `1 - bit_x` to evaluate the remaining bits where `(x XOR y)` equals `1` (matching `bit_limit`).
     - If `bit_limit == 0`:
       - We **must** follow the branch `bit_x` so that the $b$-th bit of `(x XOR y)` is `0`. Choosing `1 - bit_x` would make the $b$-th bit `1`, exceeding `limit` immediately.

4. **Overall Complexity**:
   - Inserting a number takes $O(B)$ time, where $B \approx 15$ is the maximum number of bits.
   - Querying for each number takes $O(B)$ time.
   - Total Time: $O(N \cdot B)$, which easily passes within the time limit.

---

### C++ Solution

```cpp
#include <vector>

using namespace std;

class TrieNode {
public:
    TrieNode* children[2];
    int count;
    
    TrieNode() {
        children[0] = nullptr;
        children[1] = nullptr;
        count = 0;
    }
};

class Trie {
private:
    TrieNode* root;
    static const int MAX_BIT = 15; // 2^15 = 32768 > 20000

public:
    Trie() {
        root = new TrieNode();
    }

    void insert(int num) {
        TrieNode* curr = root;
        for (int i = MAX_BIT; i >= 0; --i) {
            int bit = (num >> i) & 1;
            if (!curr->children[bit]) {
                curr->children[bit] = new TrieNode();
            }
            curr = curr->children[bit];
            curr->count++;
        }
    }

    // Returns the number of elements currently in Trie such that (num ^ element) <= limit
    int countLessThanOrEqual(int num, int limit) {
        TrieNode* curr = root;
        int count = 0;
        for (int i = MAX_BIT; i >= 0; --i) {
            if (!curr) break;
            int bit_num = (num >> i) & 1;
            int bit_limit = (limit >> i) & 1;

            if (bit_limit == 1) {
                // Branch with bit_num gives XOR result 0 < bit_limit (1)
                if (curr->children[bit_num]) {
                    count += curr->children[bit_num]->count;
                }
                // Move to branch with (1 - bit_num) which gives XOR result 1 == bit_limit
                curr = curr->children[1 - bit_num];
            } else {
                // Must take branch with bit_num so XOR result is 0 == bit_limit
                curr = curr->children[bit_num];
            }
        }
        return count;
    }
};

class Solution {
private:
    int countPairsWithXorLessThanOrEqual(const vector<int>& nums, int limit) {
        Trie trie;
        int totalPairs = 0;
        for (int num : nums) {
            totalPairs += trie.countLessThanOrEqual(num, limit);
            trie.insert(num);
        }
        return totalPairs;
    }

public:
    int countPairs(vector<int>& nums, int low, int high) {
        return countPairsWithXorLessThanOrEqual(nums, high) - 
               countPairsWithXorLessThanOrEqual(nums, low - 1);
    }
};
```

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(N \log(\max(\text{nums})))$. For each of the $N$ numbers, we insert and search in a Trie of depth $B \approx 16$ bits. Overall time is $O(16 \times N) = \mathcal{O}(N)$.
- **Space Complexity:** $\mathcal{O}(N \log(\max(\text{nums})))$. Each inserted number creates at most 16 nodes in the Trie. Space complexity is bounded by $\mathcal{O}(16 \times N) = \mathcal{O}(N)$.

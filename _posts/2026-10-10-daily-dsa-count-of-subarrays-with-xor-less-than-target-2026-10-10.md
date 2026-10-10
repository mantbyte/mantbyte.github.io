---
layout: post
title: 'Daily DSA: Count of Subarrays with XOR Less Than Target (Hard)'
date: 2026-10-10 21:10:17 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Count of Subarrays
  with XOR Less Than Target.'
cover_image: /assets/images/posts/daily-dsa-count-of-subarrays-with-xor-less-than-target-2026-10-10-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

Given an integer array `nums` and an integer `k`, return the number of non-empty continuous subarrays whose bitwise XOR sum is strictly less than `k`.

The bitwise XOR sum of an array `[a_1, a_2, ..., a_m]` is defined as `a_1 ^ a_2 ^ ... ^ a_m`.

---

### Examples

**Example 1:**
```text
Input: nums = [1, 4, 2, 7], k = 6
Output: 7
Explanation:
The XOR sums of all subarrays are:
- [1] -> 1 (< 6)
- [1, 4] -> 5 (< 6)
- [1, 4, 2] -> 7 (>= 6)
- [1, 4, 2, 7] -> 0 (< 6)
- [4] -> 4 (< 6)
- [4, 2] -> 6 (>= 6)
- [4, 2, 7] -> 1 (< 6)
- [2] -> 2 (< 6)
- [2, 7] -> 5 (< 6)
- [7] -> 7 (>= 6)

There are 7 subarrays with XOR sum strictly less than 6.
```

**Example 2:**
```text
Input: nums = [3, 5, 2], k = 4
Output: 2
Explanation:
The subarrays with XOR sum < 4 are:
- [3] -> 3 (< 4)
- [2] -> 2 (< 4)
Total = 2.
```

**Example 3:**
```text
Input: nums = [5, 5, 5, 5], k = 1
Output: 6
Explanation:
All subarrays with an even length have an XOR sum of 0, which is strictly less than 1. There are 6 such subarrays.
```

---

### Constraints

- `1 <= nums.length <= 10^5`
- `1 <= nums[i] <= 10^9`
- `1 <= k <= 10^9`

---

### Approach

1. **Prefix XOR Representation**:
   Let $P[i]$ be the prefix XOR up to index $i$, defined as $P[i] = nums[0] \oplus nums[1] \oplus \dots \oplus nums[i]$, with $P[-1] = 0$.
   The XOR sum of any subarray $nums[i..j]$ can be computed in $O(1)$ time as:
   $$\text{XOR}(nums[i..j]) = P[j] \oplus P[i - 1]$$
   Thus, the problem reduces to finding the number of pairs $(i, j)$ with $i \le j$ such that $P[j] \oplus P[i - 1] < k$.

2. **Bitwise Trie (Prefix Tree)**:
   As we iterate through each prefix XOR $P[j]$, we want to query how many previously seen prefix values $P[i - 1]$ satisfy $P[j] \oplus P[i - 1] < k$. After querying, we insert $P[j]$ into our data structure.

3. **Query Logic at Each Bit**:
   Since numbers can be up to $10^9 < 2^{30}$, we inspect bits from bit 29 down to 0.
   For a bit position $b$, let $v_b$ be the $b$-th bit of $P[j]$ and $k_b$ be the $b$-th bit of $k$:
   - **If $k_b == 1$**:
     - If we follow the child matching $v_b$ in the Trie, the resulting bit of the XOR is $0$. Since $0 < 1$ (the $b$-th bit of $k$), any numbers in this branch will yield an XOR value strictly smaller than $k$, regardless of the remaining lower bits. Thus, we can add all elements in this subtree (`node->child[v_b]->count`) directly to our answer.
     - To consider XOR values where the $b$-th bit is $1$ (matching $k_b$), we must step into the opposite child (`1 - v_b`).
   - **If $k_b == 0$**:
     - We cannot branch into $(1 - v_b)$ because the resulting XOR bit would be $1$, making the XOR strictly greater than $k$.
     - Thus, we can only continue our traversal into the matching child $v_b$.
   - If the required child does not exist, we stop the query early.

---

### C++ Source Code

```cpp
#include <vector>
#include <memory>

using namespace std;

class Solution {
private:
    static constexpr int MAX_BITS = 30;

    struct TrieNode {
        TrieNode* children[2] = {nullptr, nullptr};
        int count = 0;
    };

    void insert(TrieNode* root, int val) {
        TrieNode* curr = root;
        for (int b = MAX_BITS - 1; b >= 0; --b) {
            int bit = (val >> b) & 1;
            if (!curr->children[bit]) {
                curr->children[bit] = new TrieNode();
            }
            curr = curr->children[bit];
            curr->count++;
        }
    }

    long long countLessThanK(TrieNode* root, int val, int k) {
        TrieNode* curr = root;
        long long total = 0;

        for (int b = MAX_BITS - 1; b >= 0; --b) {
            if (!curr) break;

            int v_bit = (val >> b) & 1;
            int k_bit = (k >> b) & 1;

            if (k_bit == 1) {
                // Branch where the XOR bit is 0 is strictly less than k_bit (1)
                if (curr->children[v_bit]) {
                    total += curr->children[v_bit]->count;
                }
                // To continue matching k_bit, move to the branch where XOR bit is 1
                curr = curr->children[1 - v_bit];
            } else {
                // k_bit is 0, so XOR bit MUST be 0 to not exceed k
                curr = curr->children[v_bit];
            }
        }

        return total;
    }

    void freeTrie(TrieNode* node) {
        if (!node) return;
        freeTrie(node->children[0]);
        freeTrie(node->children[1]);
        delete node;
    }

public:
    long long countSubarraysXORLessThanK(vector<int>& nums, int k) {
        TrieNode* root = new TrieNode();
        
        // Insert 0 to represent the empty prefix P[-1]
        insert(root, 0);
        
        long long ans = 0;
        int current_xor = 0;

        for (int num : nums) {
            current_xor ^= num;
            ans += countLessThanK(root, current_xor, k);
            insert(root, current_xor);
        }

        freeTrie(root);
        return ans;
    }
};
```

---

### Complexity Analysis

- **Time Complexity**: $\mathcal{O}(N \times B)$, where $N$ is the number of elements in `nums` and $B = 30$ is the number of bits required to represent $10^9$. For each element, both insertion and query take $\mathcal{O}(B)$ operations, yielding an overall running time of $\approx 30 \times 10^5$ operations, which easily runs within 0.1 seconds.
- **Space Complexity**: $\mathcal{O}(N \times B)$ in the worst case to store the Trie nodes, requiring at most $30 \times 10^5$ nodes.
{% endraw %}

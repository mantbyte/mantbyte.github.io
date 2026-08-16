---
layout: post
title: 'Daily DSA: Split Linked List in Parts (Medium)'
date: 2026-08-16 15:48:05 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Split Linked
  List in Parts.'
cover_image: /assets/images/posts/daily-dsa-split-linked-list-in-parts-2026-08-16-cover.png
cover_caption: ''
---

### Problem Statement

Given the `head` of a singly linked list and an integer `k`, split the linked list into `k` consecutive linked list parts.

The length of each part should be as equal as possible: no two parts should have a size differing by more than one. This may lead to some parts being null.

The parts should be in the order of occurrence in the input list, and parts occurring earlier should always have a size greater than or equal to parts occurring later.

Return an array of the `k` parts.

### Examples

**Example 1:**
**Input:** head = [1,2,3], k = 5
**Output:** [[1],[2],[3],[],[]]
**Explanation:**
The first element output[0] has val = 1, next = null. The last two elements are null, but still represented as empty parts.

**Example 2:**
**Input:** head = [1,2,3,4,5,6,7,8,9,10], k = 3
**Output:** [[1,2,3,4],[5,6,7],[8,9,10]]
**Explanation:**
The input has been split into consecutive parts with size difference at most 1, and earlier parts are larger.

### Constraints

- The number of nodes in the list is in the range `[0, 1000]`.
- `0 <= Node.val <= 1000`
- `1 <= k <= 50`

### Approach

1. **Calculate Length:** First, traverse the entire linked list to find its total length `N`.
2. **Determine Part Sizes:** 
   - Each part will have at least `width = N / k` nodes.
   - The first `rem = N % k` parts will have an extra node (size `width + 1`) to distribute the remainder evenly.
3. **Split the List:** 
   - Iterate `k` times to create each part.
   - For each part, traverse the required number of nodes based on the calculated size.
   - Keep track of the `next` node to start the next part, then break the connection by setting the current tail's `next` to `nullptr`.
   - Store the head of each part in the result array.

### C++ Solution

```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */

class Solution {
public:
    vector<ListNode*> splitListToParts(ListNode* head, int k) {
        // Step 1: Count the total length of the list
        int n = 0;
        ListNode* curr = head;
        while (curr) {
            n++;
            curr = curr->next;
        }

        // Step 2: Determine the base width and the number of remainder nodes
        int width = n / k;
        int rem = n % k;

        vector<ListNode*> result(k, nullptr);
        curr = head;

        // Step 3: Split the list into k parts
        for (int i = 0; i < k; ++i) {
            if (!curr) break;

            result[i] = curr;
            int current_part_size = width + (i < rem ? 1 : 0);

            // Move to the end of the current part
            for (int j = 1; j < current_part_size; ++j) {
                curr = curr->next;
            }

            // Sever the connection and move to the next head
            ListNode* next_node = curr->next;
            curr->next = nullptr;
            curr = next_node;
        }

        return result;
    }
};
```

### Complexity Analysis

- **Time Complexity:** O(N + k), where N is the number of nodes in the linked list. We traverse the list once to find the length and once more to split it. We also iterate up to k times to fill the result array.
- **Space Complexity:** O(1) if we do not count the output array, as we only use a few pointer variables for the logic.

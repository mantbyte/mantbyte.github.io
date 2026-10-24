---
layout: post
title: 'Daily DSA: Multi-Pattern Keyword Search (Hard)'
date: 2026-10-24 19:20:30 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Multi-Pattern
  Keyword Search.'
cover_image: /assets/images/posts/daily-dsa-multipattern-keyword-search-2026-10-24-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are given a string `text` and an array of distinct strings `words`. 

Your task is to count how many times each string in `words` appears as a substring within `text`. Occurrences of words may overlap, and multiple words can match at the same position.

Return an array of integers `ans` of the same length as `words`, where `ans[i]` represents the total number of occurrences of `words[i]` in `text`.

---

### Examples

**Example 1:**
```text
Input: text = "ahishers", words = ["he", "she", "his", "hers"]
Output: [1, 1, 1, 1]
Explanation:
- "he" appears at index 4: text[4..5] = "he".
- "she" appears at index 3: text[3..5] = "she".
- "his" appears at index 1: text[1..3] = "his".
- "hers" appears at index 4: text[4..7] = "hers".
All words appear exactly once.
```

**Example 2:**
```text
Input: text = "aaaaa", words = ["a", "aa", "aaa"]
Output: [5, 4, 3]
Explanation:
- "a" appears at indices 0, 1, 2, 3, 4 (5 times).
- "aa" appears at indices 0, 1, 2, 3 (4 times).
- "aaa" appears at indices 0, 1, 2 (3 times).
```

**Example 3:**
```text
Input: text = "banana", words = ["an", "na", "pan", "ban"]
Output: [2, 2, 0, 1]
Explanation:
- "an" occurs at index 1 and 3 (2 times).
- "na" occurs at index 2 and 4 (2 times).
- "pan" does not occur in text (0 times).
- "ban" occurs at index 0 (1 time).
```

---

### Constraints

- $1 \le \text{text.length} \le 10^5$
- $1 \le \text{words.length} \le 10^5$
- $1 \le \sum \text{words}[i]\text{.length} \le 10^5$
- `text` and all strings in `words` consist only of lowercase English letters.
- All strings in `words` are pairwise distinct.

---

### Approach

Running standard single-pattern search algorithms like KMP independently for each pattern would take $O(|\text{words}| \cdot |\text{text}|)$ in the worst case, which easily exceeds time limits when both lengths are around $10^5$.

To match multiple patterns simultaneously in linear time, we can use the **Aho-Corasick Automaton**, which merges the concept of a **Trie** with the failure-function transitions of **KMP**:

1. **Trie Construction**:
   - Insert all strings from `words` into a standard Trie.
   - Store the trie node corresponding to the end of each pattern `words[i]` so that we can query its result later.

2. **Failure Links (Suffix Links) via BFS**:
   - The failure link $\text{fail}(u)$ of a state $u$ points to the state representing the longest proper suffix of the string ending at $u$ that exists in the Trie.
   - Using BFS (Breadth-First Search level by level):
     - For all direct children of the root (depth 1), set their failure link to root ($0$).
     - For a node $u$ with parent $p$ and character $c$:
       - Follow transitions: if the transition on $c$ exists, its fail link points to $\text{next}(\text{fail}(p), c)$.
       - To simplify text traversal into $O(1)$ per character, make the Trie into a complete automaton: if a node doesn't have an edge for character $c$, set $\text{trie}[u][c] = \text{trie}[\text{fail}(u)][c]$.

3. **Traversing the Text**:
   - Starting from the root, follow the transitions for each character of `text`.
   - Each time we arrive at state $u$, increment a visit counter: `count[u]++`.

4. **Propagating Counts along the Failure Tree**:
   - Every time a node $u$ is matched, all its proper suffixes (reachable by repeatedly following $\text{fail}(u)$) are implicitly matched as well.
   - Instead of traversing failure links at every step of `text` (which could degrade performance), we accumulate matches at the end.
   - By processing nodes in **reverse topological order** (i.e., reverse BFS order from leaves/deepest nodes to the root), we can propagate counts in a single pass:
     $$\text{count}[\text{fail}[u]] \mathrel{+}= \text{count}[u]$$

5. Finally, the answer for `words[i]` is simply the accumulated count at its terminal node.

---

### C++ Solution

```cpp
#include <vector>
#include <string>
#include <queue>

using namespace std;

class Solution {
    struct Node {
        int next[26];
        int fail = 0;
        int count = 0;
        Node() {
            fill(begin(next), end(next), 0);
        }
    };

public:
    vector<int> multiPatternSearch(string text, vector<string>& words) {
        // Allocate space for Trie nodes
        // Sum of pattern lengths is at most 10^5, so <= 10^5 + 5 nodes.
        vector<Node> trie;
        trie.emplace_back(); // Root is node 0

        int n = words.size();
        vector<int> word_node(n);

        // 1. Build Trie
        for (int i = 0; i < n; ++i) {
            int curr = 0;
            for (char ch : words[i]) {
                int c = ch - 'a';
                if (!trie[curr].next[c]) {
                    trie[curr].next[c] = trie.size();
                    trie.emplace_back();
                }
                curr = trie[curr].next[c];
            }
            word_node[i] = curr;
        }

        // 2. Build Failure Links using BFS
        queue<int> q;
        vector<int> bfs_order;
        bfs_order.reserve(trie.size());

        for (int c = 0; c < 26; ++c) {
            if (trie[0].next[c]) {
                q.push(trie[0].next[c]);
            }
        }

        while (!q.empty()) {
            int u = q.front();
            q.pop();
            bfs_order.push_back(u);

            for (int c = 0; c < 26; ++c) {
                if (trie[u].next[c]) {
                    trie[trie[u].next[c]].fail = trie[trie[u].fail].next[c];
                    q.push(trie[u].next[c]);
                } else {
                    // Automaton transition compression
                    trie[u].next[c] = trie[trie[u].fail].next[c];
                }
            }
        }

        // 3. Process Text
        int curr = 0;
        for (char ch : text) {
            curr = trie[curr].next[ch - 'a'];
            trie[curr].count++;
        }

        // 4. Push counts up the failure link tree (reverse BFS order)
        for (int i = (int)bfs_order.size() - 1; i >= 0; --i) {
            int u = bfs_order[i];
            int f = trie[u].fail;
            trie[f].count += trie[u].count;
        }

        // 5. Collect results
        vector<int> result(n);
        for (int i = 0; i < n; ++i) {
            result[i] = trie[word_node[i]].count;
        }

        return result;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:**
  - **Trie Construction**: $O(\sum |\text{words}[i]|)$ to insert all characters.
  - **Automaton & BFS**: $O(\sum |\text{words}[i]| \times \Sigma)$ where alphabet size $\Sigma = 26$.
  - **Text Traversal**: $O(|\text{text}|)$ since each transition takes $O(1)$ time.
  - **Count Propagation**: $O(\text{number of states}) = O(\sum |\text{words}[i]|)$.
  - **Total Time Complexity**: $\mathcal{O}(|\text{text}| + \Sigma \cdot \sum |\text{words}[i]|)$, strictly linear with respect to input size.

- **Space Complexity:**
  - $\mathcal{O}(\Sigma \cdot \sum |\text{words}[i]|)$ to store transition tables and auxiliary arrays for all automaton states.
{% endraw %}

---
layout: post
title: 'Daily DSA: Reconstructing the Ancestral DNA (Hard)'
date: 2026-09-06 18:52:13 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Reconstructing
  the Ancestral DNA.'
cover_image: /assets/images/posts/daily-dsa-reconstructing-the-ancestral-dna-2026-09-06-cover.png
cover_caption: ''
---

### Problem Statement

An ancient DNA sequence was sequenced using a method that only provides **bigrams** (pairs of consecutive nucleotides). Each bigram `[u, v]` indicates that the nucleotide `u` was immediately followed by the nucleotide `v` in the original sequence.

Given a collection of `n` bigrams, your task is to reconstruct the original DNA sequence. A valid sequence is guaranteed to exist and must use every bigram exactly once. If there are multiple valid sequences, return any of them.

### Examples

**Example 1:**
- **Input:** `fragments = [['A','B'], ['B','C'], ['C','A']]` 
- **Output:** `"ABCA"` 
- **Explanation:** The sequence "ABCA" contains bigrams "AB", "BC", and "CA".

**Example 2:**
- **Input:** `fragments = [['G','A'], ['A','T'], ['T','G'], ['G','G']]` 
- **Output:** `"GATGG"` 
- **Explanation:** The sequence "GATGG" uses bigrams "GA", "AT", "TG", and "GG" exactly once.

### Constraints

- `1 <= fragments.length <= 10^5` 
- `fragments[i].length == 2` 
- `fragments[i][j]` is an uppercase English letter ('A'-'Z'). 
- A valid sequence is guaranteed to exist using all provided bigrams.

### Approach

This problem can be modeled as finding an **Eulerian Path** in a directed graph:

1.  **Graph Construction:** Represent each unique nucleotide as a node and each bigram `[u, v]` as a directed edge from node `u` to node `v`.
2.  **Degree Counting:** Calculate the in-degree and out-degree of every node involved in the fragments.
3.  **Identify Start Node:** 
    - According to Eulerian Path properties for directed graphs, if a node has `outDegree - inDegree == 1`, it must be the starting point of the path.
    - If all nodes have `inDegree == outDegree`, the graph contains an Eulerian Circuit, and any node with at least one outgoing edge can serve as the starting point.
4.  **Hierholzer's Algorithm:** Use a stack-based DFS approach to traverse the edges. When a node has no more outgoing edges to visit, push it to the result list. The final path is the reverse of this result list.

### Complexity Analysis

- **Time Complexity:** O(N + Σ), where N is the number of fragments and Σ is the alphabet size (26). We process each edge exactly once during construction and once during the traversal.
- **Space Complexity:** O(N + Σ) to store the adjacency list, degree maps, and the traversal stack.

### C++ Solution

```cpp
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
#include <stack>

using namespace std; 

class Solution {
public:
    string reconstructDNA(vector<vector<char>>& fragments) {
        if (fragments.empty()) return "";

        unordered_map<char, vector<char>> adj;
        unordered_map<char, int> outDegree, inDegree;

        // Build the directed graph and track degrees
        for (const auto& f : fragments) {
            char u = f[0];
            char v = f[1];
            adj[u].push_back(v);
            outDegree[u]++;
            inDegree[v]++;
        }

        // Determine the starting node
        char startNode = fragments[0][0];
        for (auto const& [node, count] : outDegree) {
            // In an Eulerian path, start node has outDegree > inDegree
            if (count > inDegree[node]) {
                startNode = node;
                break;
            }
        }

        vector<char> res;
        stack<char> st;
        st.push(startNode);

        // Hierholzer's Algorithm (Iterative implementation)
        while (!st.empty()) {
            char u = st.top();
            if (adj.count(u) && !adj[u].empty()) {
                // Visit an unvisited edge
                char v = adj[u].back();
                adj[u].pop_back();
                st.push(v);
            } else {
                // No more outgoing edges, backtrack and record node
                res.push_back(u);
                st.pop();
            }
        }

        // The Eulerian path is found in reverse post-order
        reverse(res.begin(), res.end());
        
        // Convert vector of characters to final string
        return string(res.begin(), res.end());
    }
};
```

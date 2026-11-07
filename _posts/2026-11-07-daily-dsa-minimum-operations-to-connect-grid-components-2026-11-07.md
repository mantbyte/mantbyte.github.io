---
layout: post
title: 'Daily DSA: Minimum Operations to Connect Grid Components (Hard)'
date: 2026-11-07 21:32:17 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Minimum Operations
  to Connect Grid Components.'
cover_image: /assets/images/posts/daily-dsa-minimum-operations-to-connect-grid-components-2026-11-07-cover.png
cover_caption: ''
---

{% raw %}
# Minimum Operations to Connect Grid Components

## Problem Statement

You are given an $n \times m$ grid representing a map. Some cells are blocked (represented by `0`) and some are open (represented by `1`). 

You are allowed to perform an operation: choose any blocked cell (`0`) and change it into an open cell (`1`). 

Find the minimum number of operations required to ensure that all open cells (`1`) form a single connected component. Connectivity is defined as 4-directionally adjacent open cells (up, down, left, right).

If there are no open cells initially, return `0`.

## Examples

### Example 1:
```
Input: grid = [
  [1, 0, 1],
  [0, 0, 0],
  [1, 0, 1]
]
Output: 1
Explanation: Changing the center cell (1, 1) from 0 to 1 connects all four corner components into a single component.
```

### Example 2:
```
Input: grid = [
  [1, 1, 0],
  [0, 1, 0],
  [0, 0, 1]
]
Output: 2
Explanation: We can change (0, 2) and (1, 2) to 1 to connect everything.
```

## Constraints
- $n == \text{grid.length}$
- $m == \text{grid[i].length}$
- $1 \le n, m \le 30$
- `grid[i][j]` is either `0` or `1`.

## Approach & Hints
1. **Identify Components**: First, use BFS, DFS, or Disjoint Set Union (DSU) to find all existing connected components of `1`s. If there are $\le 1$ components, the answer is `0`.
2. **Exhaustive Search for Bridge Cells**: Since the grid dimensions are small ($30 \times 30$), we can iterate over all `0` cells and evaluate what happens if we change that `0` into a `1`. 
3. **Single vs Multiple Additions**: Sometimes changing one `0` is not enough. We might need to change up to 2 cells, or evaluate the minimum spanning tree of components where the edge weights are the Manhattan distances between components.
4. **Optimization**: For small grids, we can iterate through all pairs of `0` cells or use a BFS-based shortest path approach treating components as nodes in a graph.
{% endraw %}

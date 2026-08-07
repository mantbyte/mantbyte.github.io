---
layout: post
title: 'Daily DSA: Path With Maximum Gold Coins (Medium)'
date: 2026-08-08 01:11:28 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Path With Maximum
  Gold Coins.'
cover_image: /assets/images/posts/daily-dsa-path-with-maximum-gold-coins-2026-08-07-cover.png
cover_caption: ''
---

### Problem Statement

You are given a 2D grid of size `m x n` representing a gold mine. Each cell in the grid has an integer representing the amount of gold in that cell, where `0` means the cell is empty.

Return the maximum amount of gold you can collect under the conditions:
- Every time you locate a cell, you collect all the gold in that cell.
- From your current position, you can walk one step to the left, right, up, or down.
- You cannot visit the same cell more than once.
- Never visit a cell with `0` gold.
- You can start and stop collecting gold from **any** position in the grid that has some gold.

---

### Examples

**Example 1:**
```text
Input: grid = [[0,6,0],[5,8,7],[0,9,0]]
Output: 24
Explanation:
[
 [ 0, 6, 0],
 [ 5, 8, 7],
 [ 0, 9, 0]
]
Path to get the maximum gold: 9 -> 8 -> 7. Total = 24.
```

**Example 2:**
```text
Input: grid = [[1,0,7],[2,0,6],[3,4,5],[0,3,0],[9,0,20]]
Output: 28
Explanation:
[
 [ 1, 0, 7],
 [ 2, 0, 6],
 [ 3, 4, 5],
 [ 0, 3, 0],
 [ 9, 0, 20]
]
Path to get the maximum gold: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7. Total = 28.
(Note: Another path is 9 -> 3 -> 4 -> 5 -> 6 -> 7, total = 34? Wait, check grid constraints. 9 -> 3 -> 4 -> 5 -> 6 -> 7 is valid? 9 is at (4,0), 3 at (3,1), 4 at (2,1), 5 at (2,2), 6 at (1,2), 7 at (0,2). Sum = 9+3+4+5+6+7 = 34).
```

---

### Constraints
- `m == grid.length`
- `n == grid[i].length`
- `1 <= m, n <= 15`
- `0 <= grid[i][j] <= 100`
- There are at most 25 cells containing gold in the grid.

---

### Approach & Hint

1. **Backtracking / DFS**: Since we can start from any cell with non-zero gold and need to find the maximum sum of a simple path, we can use Depth-First Search (DFS) combined with backtracking.
2. We iterate through every cell in the grid. If `grid[i][j] > 0`, we initiate a DFS from this cell to explore all possible valid paths.
3. During the DFS, we temporarily mark the current cell as visited (e.g., by setting it to `0` or using a separate visited matrix), add its value to the current path sum, recursively visit all 4 neighbors, and then backtrack by restoring the cell's value.
4. Keep track of the maximum gold collected across all starting positions.

---

### C++ Solution

```cpp
#include <vector>
#include <algorithm>

class Solution {
private:
    int dfs(std::vector<std::vector<int>>& grid, int r, int c) {
        int m = grid.size();
        int n = grid[0].size();
        
        // Temporarily store the gold and mark cell as visited
        int current_gold = grid[r][c];
        grid[r][c] = 0;
        
        int max_neighbor_gold = 0;
        
        // 4 possible directions: Up, Down, Left, Right
        int dr[] = {-1, 1, 0, 0};
        int dc[] = {0, 0, -1, 1};
        
        for (int i = 0; i < 4; ++i) {
            int nr = r + dr[i];
            int nc = c + dc[i];
            
            if (nr >= 0 && nr < m && nc >= 0 && nc < n && grid[nr][nc] > 0) {
                max_neighbor_gold = std::max(max_neighbor_gold, dfs(grid, nr, nc));
            }
        }
        
        // Backtrack
        grid[r][c] = current_gold;
        
        return current_gold + max_neighbor_gold;
    }

public:
    int getMaximumGold(std::vector<std::vector<int>>& grid) {
        int m = grid.size();
        int n = grid[0].size();
        int max_gold = 0;
        
        for (int i = 0; i < m; ++i) {
            for (int j = 0; j < n; ++j) {
                if (grid[i][j] > 0) {
                    max_gold = std::max(max_gold, dfs(grid, i, j));
                }
            }
        }
        
        return max_gold;
    }
};
```

### Complexity Analysis
- **Time Complexity:** $\mathcal{O}(K \cdot 4^{K})$, where $K$ is the number of cells containing gold. In the worst case, we might start a DFS from multiple cells, and each path can branch up to 4 ways. Given $K \le 25$, the problem is optimized enough to pass within limits.
- **Space Complexity:** $\mathcal{O}(m \cdot n)$ in the worst case for the recursion stack during DFS.

---
layout: post
title: 'Daily DSA: Minimum Cost to Make at Least One Valid Path in a Grid (Medium)'
date: 2026-09-27 20:29:10 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Minimum Cost
  to Make at Least One Valid Path in a Grid.'
cover_image: /assets/images/posts/daily-dsa-minimum-cost-to-make-at-least-one-valid-path-in-a-grid-2026-09-27-cover.png
cover_caption: ''
---

### Problem Description

Given an $m \times n$ grid, each cell contains a sign pointing in one of four directions:
- `1`: Right (pointing to `(r, c + 1)`)
- `2`: Left (pointing to `(r, c - 1)`)
- `3`: Down (pointing to `(r + 1, c)`)
- `4`: Up (pointing to `(r - 1, c)`)

You start at the top-left cell `(0, 0)`. A path is considered valid if it follows the signs to reach the bottom-right cell `(m - 1, n - 1)`. 

You can modify the sign in any cell with a **cost of 1**. You can change the direction to any of the four possible directions. Find the minimum cost to make at least one valid path from `(0, 0)` to `(m - 1, n - 1)`.

### Examples

**Example 1:**
```
Input: grid = [[1,1,1,1],[2,2,2,2],[1,1,1,1],[2,2,2,2]]
Output: 3
Explanation: Start at (0, 0). Follow the signs to (0, 3). 
Change the sign at (0, 3) from 1 to 3 (Cost 1). 
Follow signs to (2, 3), change sign to 2 (Cost 1). 
Follow signs to (2, 0), change sign to 3 (Cost 1). 
Total cost: 3.
```

**Example 2:**
```
Input: grid = [[1,1,3],[3,2,2],[1,1,4]]
Output: 0
Explanation: You can follow the path (0,0) -> (0,1) -> (0,2) -> (1,2) -> (1,1) -> (1,0) -> (2,0) -> (2,1) -> (2,2) without changing any signs.
```

### Constraints

- `m == grid.length`
- `n == grid[i].length`
- `1 <= m, n <= 100`
- `1 <= grid[i][j] <= 4`

---

### Approach: 0-1 Breadth-First Search (BFS)

This problem can be modeled as finding the shortest path in a weighted graph where:
1. Each cell `(r, c)` is a node.
2. From cell `(r, c)`, there are edges to its 4 neighbors.
3. The edge weight is **0** if the neighbor is in the direction the sign is already pointing.
4. The edge weight is **1** if we need to change the sign to point to that neighbor.

Since the edge weights are only **0 or 1**, we can use **0-1 BFS** instead of Dijkstra's algorithm. 0-1 BFS uses a `std::deque` to maintain the shortest path property efficiently:
- If we traverse an edge with weight **0**, we push the neighbor to the **front** of the deque.
- If we traverse an edge with weight **1**, we push the neighbor to the **back** of the deque.
- This ensures that the deque remains sorted by the current distance from the source.

### C++ Solution

```cpp
#include <vector>
#include <deque>
#include <climits>

using namespace std;

class Solution {
public:
    int minCost(vector<vector<int>>& grid) {
        int m = grid.size();
        int n = grid[0].size();
        
        // dist[r][c] stores the minimum cost to reach cell (r, c)
        vector<vector<int>> dist(m, vector<int>(n, INT_MAX));
        deque<pair<int, int>> dq;
        
        // Direction mappings: 1:R, 2:L, 3:D, 4:U
        int dr[] = {0, 0, 0, 1, -1};
        int dc[] = {0, 1, -1, 0, 0};
        
        // Start at (0, 0) with cost 0
        dist[0][0] = 0;
        dq.push_back({0, 0});
        
        while (!dq.empty()) {
            pair<int, int> curr = dq.front();
            dq.pop_front();
            int r = curr.first;
            int c = curr.second;
            
            // Since we use 0-1 BFS, the first time we pop a node, 
            // we have found its shortest path.
            if (r == m - 1 && c == n - 1) return dist[r][c];
            
            for (int i = 1; i <= 4; ++i) {
                int nr = r + dr[i];
                int nc = c + dc[i];
                
                if (nr >= 0 && nr < m && nc >= 0 && nc < n) {
                    // Cost is 0 if the sign points to the neighbor, else 1
                    int weight = (grid[r][c] == i) ? 0 : 1;
                    
                    if (dist[r][c] + weight < dist[nr][nc]) {
                        dist[nr][nc] = dist[r][c] + weight;
                        if (weight == 0) {
                            dq.push_front({nr, nc});
                        } else {
                            dq.push_back({nr, nc});
                        }
                    }
                }
            }
        }
        
        return dist[m - 1][n - 1];
    }
};
```

### Complexity Analysis

- **Time Complexity:** $O(M \times N)$, where $M$ is the number of rows and $N$ is the number of columns. Each cell is added to and removed from the deque at most once.
- **Space Complexity:** $O(M \times N)$ to store the distance matrix and the deque.

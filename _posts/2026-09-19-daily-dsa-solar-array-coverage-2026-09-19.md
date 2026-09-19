---
layout: post
title: 'Daily DSA: Solar Array Coverage (Hard)'
date: 2026-09-19 19:09:24 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Solar Array Coverage.'
cover_image: /assets/images/posts/daily-dsa-solar-array-coverage-2026-09-19-cover.png
cover_caption: ''
---

### Problem Statement

You are an urban planner designing a sustainable energy grid for a city. You have been given a list of `n` rectangular solar panels to be installed on a flat 2D plane. Each solar panel is represented as `rectangles[i] = [x1, y1, x2, y2]`, where `(x1, y1)` is the bottom-left corner and `(x2, y2)` is the top-right corner of the $i^{th}$ rectangle.

Since some solar panels may overlap, the total energy generated depends on the **unique area** covered by the union of all rectangles. 

Return the total area covered by all rectangles in the plane. Since the answer may be very large, return it **modulo** $10^9 + 7$.

### Examples

**Example 1:**
**Input:** `rectangles = [[0,0,2,2],[1,0,2,3],[1,0,3,1]]`  
**Output:** `6`  
**Explanation:** 
- The first rectangle covers the area from (0,0) to (2,2). (Area = 4)
- The second rectangle covers (1,0) to (2,3). It adds the region (1,2) to (2,3). (Additional Area = 1)
- The third rectangle covers (1,0) to (3,1). It adds the region (2,0) to (3,1). (Additional Area = 1)
- Total unique area = 4 + 1 + 1 = 6.

**Example 2:**
**Input:** `rectangles = [[0,0,1000,1000],[500,500,1500,1500]]`  
**Output:** `1750000`  
**Explanation:** 
- Area of first: $1000 \times 1000 = 1,000,000$
- Area of second: $1000 \times 1000 = 1,000,000$
- Overlap area: $(1000-500) \times (1000-500) = 250,000$
- Total: $1,000,000 + 1,000,000 - 250,000 = 1,750,000$.

### Constraints

- `1 <= rectangles.length <= 1000`
- `rectangles[i].length == 4`
- `0 <= x1, y1, x2, y2 <= 10^9`
- `x1 < x2` and `y1 < y2`

---

### Approach

To solve this efficiently, we use a **Line Sweep Algorithm**. Instead of calculating the area of each rectangle and subtracting overlaps (which becomes complex with many rectangles), we imagine a vertical line sweeping from the leftmost x-coordinate to the rightmost x-coordinate.

1. **X-Coordinate Discretization**: Collect all unique $x_1$ and $x_2$ coordinates from the input. Sort them. These sorted coordinates divide the plane into several vertical strips.
2. **Iterate Through Strips**: For every interval between two consecutive sorted x-coordinates $[x_i, x_{i+1}]$:
   - The width of this strip is $\Delta x = x_{i+1} - x_i$.
   - If $\Delta x > 0$, we find all rectangles that cover this vertical strip (i.e., rectangles where $rect.x_1 \le x_i$ and $rect.x_2 \ge x_{i+1}$).
   - For these specific rectangles, we extract their y-intervals $[y_1, y_2]$.
3. **Merge Y-Intervals**: Within the current strip, we need to find the total height covered by the union of these y-intervals. 
   - Sort the y-intervals by their start points.
   - Merge them to find the total non-overlapping length $L$.
4. **Accumulate Area**: The area contributed by this strip is $\Delta x \times L$. Add this to the total area modulo $10^9 + 7$.

**Complexity Analysis:**
- **Time Complexity**: $O(N^2 \log N)$ where $N$ is the number of rectangles. There are at most $2N$ x-coordinates, and for each strip, we sort up to $N$ y-intervals.
- **Space Complexity**: $O(N)$ to store the coordinates and intervals.

### Implementation

```cpp
#include <vector>
#include <algorithm>
#include <set>

using namespace std;

class Solution {
public:
    int totalCoverageArea(vector<vector<int>>& rectangles) {
        long long MOD = 1e9 + 7;
        set<int> x_set;
        for (const auto& r : rectangles) {
            x_set.insert(r[0]);
            x_set.insert(r[2]);
        }

        vector<int> sorted_x(x_set.begin(), x_set.end());
        long long total_area = 0;

        for (int i = 0; i < (int)sorted_x.size() - 1; ++i) {
            long long width = (long long)sorted_x[i+1] - sorted_x[i];
            if (width == 0) continue;

            // Find all y-intervals covering this x-strip
            vector<pair<int, int>> y_intervals;
            for (const auto& r : rectangles) {
                if (r[0] <= sorted_x[i] && r[2] >= sorted_x[i+1]) {
                    y_intervals.push_back({r[1], r[3]});
                }
            }

            if (y_intervals.empty()) continue;

            // Merge y-intervals to find total height
            sort(y_intervals.begin(), y_intervals.end());
            
            long long total_y_len = 0;
            int current_y_end = -1;

            for (const auto& interval : y_intervals) {
                int start = max(current_y_end, interval.first);
                if (interval.second > start) {
                    total_y_len += (interval.second - start);
                    current_y_end = interval.second;
                }
            }

            total_area = (total_area + (width * total_y_len)) % MOD;
        }

        return (int)total_area;
    }
};
```

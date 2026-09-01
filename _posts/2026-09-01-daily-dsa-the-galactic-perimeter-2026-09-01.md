---
layout: post
title: 'Daily DSA: The Galactic Perimeter (Hard)'
date: 2026-09-01 19:59:56 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: The Galactic
  Perimeter.'
cover_image: /assets/images/posts/daily-dsa-the-galactic-perimeter-2026-09-01-cover.png
cover_caption: ''
---

### Problem Statement

You are a cosmic architect tasked with protecting a set of $N$ vital space stations in a 2D sector of the galaxy. Each space station is represented as a point $(x, y)$ on a coordinate plane. To protect these stations, you must build a single continuous energy fence that encloses all stations within its boundary (or on the boundary itself).

To minimize the energy consumption of the fence, you need to find the **minimum possible perimeter** of such a fence. If the stations are collinear, the fence should still enclose them by following the path from the first station to the last and returning to the start.

### Examples

**Example 1:**
**Input:** `points = [[0,0],[2,0],[0,2],[2,2],[1,1]]`
**Output:** `8.00000`
**Explanation:** The stations form a square with vertices at (0,0), (2,0), (2,2), and (0,2). The station at (1,1) is inside the square. The perimeter is $2 + 2 + 2 + 2 = 8$.

**Example 2:**
**Input:** `points = [[0,0],[1,1],[2,2]]`
**Output:** `5.65685`
**Explanation:** The stations are collinear. The minimum fence goes from (0,0) to (2,2) and back. The distance between (0,0) and (2,2) is $\sqrt{2^2 + 2^2} \approx 2.82843$. Total perimeter is $2 \times 2.82843 = 5.65685$.

**Example 3:**
**Input:** `points = [[1,1]]`
**Output:** `0.00000`
**Explanation:** A single station requires no perimeter.

### Constraints

- $1 \le points.length \le 10^5$
- $points[i].length == 2$
- $-10^6 \le x_i, y_i \le 10^6$
- All points are unique.

### Approach

The problem asks for the minimum perimeter that encloses all points, which is equivalent to finding the perimeter of the **Convex Hull** of the given set of points.

We use **Andrew's Monotone Chain Algorithm** to find the convex hull vertices in $O(N \log N)$ time:
1. **Sort:** Sort the points primarily by their x-coordinate and secondarily by their y-coordinate.
2. **Lower Hull:** Iterate through the sorted points and maintain a stack. For each new point, while the last two points in the stack and the current point make a "right turn" (determined using the cross product), pop the last point.
3. **Upper Hull:** Repeat the process in reverse order (from the last point to the first) to construct the upper half of the hull.
4. **Perimeter:** Once the hull vertices are identified, sum the Euclidean distances between adjacent vertices, including the edge that connects the last vertex back to the first.

**Cross Product Logic:**
For three points $A, B, C$, the cross product of vectors $\vec{AB}$ and $\vec{BC}$ is given by:
$(B.x - A.x) \times (C.y - A.y) - (B.y - A.y) \times (C.x - A.x)$
- If $> 0$: Left turn.
- If $= 0$: Collinear.
- If $< 0$: Right turn.

### C++ Solution

```cpp
#include <vector>
#include <algorithm>
#include <cmath>
#include <iomanip>

using namespace std;

class Solution {
    struct Point {
        long long x, y;
        bool operator<(const Point& other) const {
            if (x != other.x) return x < other.x;
            return y < other.y;
        }
        bool operator==(const Point& other) const {
            return x == other.x && y == other.y;
        }
    };

    long long cross_product(Point a, Point b, Point c) {
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    }

    double dist(Point a, Point b) {
        return sqrt((double)(a.x - b.x) * (a.x - b.x) + (double)(a.y - b.y) * (a.y - b.y));
    }

public:
    double calculatePerimeter(vector<vector<int>>& points) {
        int n = points.size();
        if (n <= 1) return 0.0;

        vector<Point> pts(n);
        for (int i = 0; i < n; ++i) {
            pts[i] = {(long long)points[i][0], (long long)points[i][1]};
        }

        sort(pts.begin(), pts.end());
        pts.erase(unique(pts.begin(), pts.end()), pts.end());
        n = pts.size();

        if (n <= 1) return 0.0;
        if (n == 2) return 2.0 * dist(pts[0], pts[1]);

        vector<Point> hull;

        for (int i = 0; i < n; ++i) {
            while (hull.size() >= 2 && cross_product(hull[hull.size() - 2], hull.back(), pts[i]) <= 0) {
                hull.pop_back();
            }
            hull.push_back(pts[i]);
        }

        int lower_size = hull.size();
        for (int i = n - 2; i >= 0; --i) {
            while (hull.size() > lower_size && cross_product(hull[hull.size() - 2], hull.back(), pts[i]) <= 0) {
                hull.pop_back();
            }
            hull.push_back(pts[i]);
        }

        hull.pop_back();

        double perimeter = 0;
        for (int i = 0; i < hull.size(); ++i) {
            perimeter += dist(hull[i], hull[(i + 1) % hull.size()]);
        }

        return perimeter;
    }
};
```

### Complexity Analysis

- **Time Complexity:** $O(N \log N)$, where $N$ is the number of points. This is dominated by the sorting step. The hull construction itself is $O(N)$ as each point is pushed and popped from the stack at most once.
- **Space Complexity:** $O(N)$ to store the points and the resulting convex hull vertices.

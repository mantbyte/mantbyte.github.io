---
layout: post
title: 'Daily DSA: The Galactic Barrier: Perimeter of the Convex Hull (Hard)'
date: 2026-11-03 23:00:14 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: The Galactic
  Barrier: Perimeter of the Convex Hull.'
cover_image: /assets/images/posts/daily-dsa-the-galactic-barrier-perimeter-of-the-convex-hull-2026-11-03-cover.png
cover_caption: ''
---

{% raw %}
### Problem Statement

You are an intergalactic engineer tasked with protecting a set of $N$ space stations located on a 2D orbital plane. To protect these stations from space debris, you must deploy a single continuous energy rope that encloses all the stations. 

Given an array `points` where `points[i] = [xi, yi]` represents the coordinates of the $i$-th space station, your goal is to find the **minimum length** of the energy rope required to surround all stations. This is equivalent to finding the perimeter of the Convex Hull of the given set of points.

### Examples

**Example 1:**
**Input:** `points = [[1,1],[2,2],[2,0],[2,4],[3,3],[4,2]]`  
**Output:** `12.24264`  
**Explanation:** The stations forming the boundary (convex hull) are `[2,0], [4,2], [2,4], [1,1]`. The perimeter is the sum of distances between these points.

**Example 2:**
**Input:** `points = [[0,0],[4,0],[4,4],[0,4],[2,2]]`  
**Output:** `16.00000`  
**Explanation:** The stations forming the boundary are the four corners of the square. The station at `[2,2]` is inside the boundary.

### Constraints

*   $1 \le points.length \le 10^5$
*   $-10^4 \le xi, yi \le 10^4$
*   All points are unique.

---

### Approach

To find the minimum perimeter, we must identify the subset of points that form the **Convex Hull**—the smallest convex polygon that contains all points. The most efficient way to do this for $10^5$ points is the **Monotone Chain Algorithm**, which runs in $O(N \log N)$ time.

#### Algorithm Steps:
1.  **Sort the points:** Sort all points lexicographically (primarily by x-coordinate, and by y-coordinate for ties).
2.  **Build the Lower Hull:** Iterate through the sorted points. For each point, while the last two points in the hull and the current point perform a clockwise turn (detected via the cross product), remove the last point from the hull.
3.  **Build the Upper Hull:** Iterate through the sorted points in reverse order. Perform the same cross-product check to ensure only counter-clockwise turns are made.
4.  **Calculate Perimeter:** Once the hull vertices are identified, calculate the Euclidean distance between every adjacent pair of vertices in the hull, including the distance from the last vertex back to the first.

#### Precision Note:
The cross product of vectors $OA$ and $OB$ is calculated as:  
$(A.x - O.x) * (B.y - O.y) - (A.y - O.y) * (B.x - O.x)$  
- If $> 0$, it's a counter-clockwise turn.  
- If $< 0$, it's a clockwise turn.  
- If $= 0$, the points are collinear.

### Complexity Analysis
- **Time Complexity:** $O(N \log N)$ due to the initial sorting of points. The hull construction itself is $O(N)$ as each point is pushed and popped from the hull at most once.
- **Space Complexity:** $O(N)$ to store the points and the resulting hull vertices.

---

### C++ Solution

```cpp
#include <vector>
#include <algorithm>
#include <cmath>
#include <iomanip>

using namespace std;

struct Point {
    long long x, y;
    bool operator<(const Point& other) const {
        if (x != other.x) return x < other.x;
        return y < other.y;
    }
};

class Solution {
public:
    long long cross_product(Point a, Point b, Point c) {
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    }

    double dist(Point a, Point b) {
        return sqrt((double)(a.x - b.x) * (a.x - b.x) + (double)(a.y - b.y) * (a.y - b.y));
    }

    double calculatePerimeter(vector<vector<int>>& points) {
        int n = points.size();
        if (n <= 1) return 0.0;

        vector<Point> pts(n);
        for (int i = 0; i < n; ++i) {
            pts[i] = { (long long)points[i][0], (long long)points[i][1] };
        }

        sort(pts.begin(), pts.end());

        vector<Point> hull;

        for (int i = 0; i < n; ++i) {
            while (hull.size() >= 2 && cross_product(hull[hull.size() - 2], hull.back(), pts[i]) <= 0) {
                hull.pop_back();
            }
            hull.push_back(pts[i]);
        }

        int lower_hull_size = hull.size();
        for (int i = n - 2; i >= 0; --i) {
            while (hull.size() > lower_hull_size && cross_product(hull[hull.size() - 2], hull.back(), pts[i]) <= 0) {
                hull.pop_back();
            }
            hull.push_back(pts[i]);
        }

        hull.pop_back();

        double perimeter = 0.0;
        int h = hull.size();
        for (int i = 0; i < h; ++i) {
            perimeter += dist(hull[i], hull[(i + 1) % h]);
        }

        return perimeter;
    }
};
```
{% endraw %}

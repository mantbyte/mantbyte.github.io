---
layout: post
title: 'Daily DSA: Closest Pair of Points (Hard)'
date: 2026-09-26 19:32:10 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Closest Pair
  of Points.'
cover_image: /assets/images/posts/daily-dsa-closest-pair-of-points-2026-09-26-cover.png
cover_caption: ''
---

### Problem Statement

Given a set of $n$ points in a 2D plane, find the minimum Euclidean distance between any two distinct points. 

The Euclidean distance between two points $P_1(x_1, y_1)$ and $P_2(x_2, y_2)$ is defined as:
$$\sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$$

### Examples

**Example 1:**
- **Input:** `points = [[2, 3], [12, 30], [40, 50], [5, 1], [12, 10], [3, 4]]`
- **Output:** `1.414214`
- **Explanation:** The closest points are `[2, 3]` and `[3, 4]`. The distance is $\sqrt{(2-3)^2 + (3-4)^2} = \sqrt{2} \approx 1.414214$.

**Example 2:**
- **Input:** `points = [[0, 0], [1, 1], [100, 100]]`
- **Output:** `1.414214`
- **Explanation:** The closest points are `[0, 0]` and `[1, 1]`.

### Constraints

- $2 \le n \le 10^5$
- $-10^9 \le x_i, y_i \le 10^9$
- All points are unique.

---

### Approach

A brute-force approach would take $O(n^2)$ time by comparing every pair of points. To achieve $O(n \log n)$, we use a **Divide and Conquer** strategy:

1.  **Preprocessing:** Sort the points based on their $x$-coordinates.
2.  **Divide:** Split the sorted points into two halves at the median $x$-coordinate.
3.  **Conquer:** Recursively find the minimum distance $d_L$ in the left half and $d_R$ in the right half.
4.  **Combine:** 
    - Let $d = \min(d_L, d_R)$.
    - The only way to find a distance smaller than $d$ is to check pairs where one point is in the left half and the other is in the right half.
    - Such points must lie within a vertical strip of width $2d$ centered at the median line ($x = x_{mid}$).
    - Collect all points in this strip and sort them by their $y$-coordinates.
    - For each point in the strip, check its distance to the next few points (mathematically, checking the next 7 points is sufficient to guarantee finding the minimum).

To optimize the sorting by $y$ in the combine step, we can perform a merge-sort-like step to maintain $y$-sorted order in $O(n)$ during the recursion, resulting in a total time complexity of $O(n \log n)$.

### C++ Solution

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <iomanip>

using namespace std;

struct Point {
    long long x, y;
};

// Comparator for sorting by X coordinate
bool compareX(const Point& a, const Point& b) {
    return a.x < b.x;
}

// Comparator for sorting by Y coordinate
bool compareY(const Point& a, const Point& b) {
    return a.y < b.y;
}

double dist(Point p1, Point p2) {
    return sqrt((double)(p1.x - p2.x) * (p1.x - p2.x) + (double)(p1.y - p2.y) * (p1.y - p2.y));
}

double solve(vector<Point>& pts, int l, int r) {
    // Base case: 3 or fewer points can be solved via brute force
    if (r - l <= 3) {
        double min_d = 1e18;
        for (int i = l; i <= r; ++i) {
            for (int j = i + 1; j <= r; ++j) {
                min_d = min(min_d, dist(pts[i], pts[j]));
            }
        }
        // Sort by Y for the merge step
        sort(pts.begin() + l, pts.begin() + r + 1, compareY);
        return min_d;
    }

    int mid = l + (r - l) / 2;
    long long midX = pts[mid].x;
    
    // Recursive calls
    double d = min(solve(pts, l, mid), solve(pts, mid + 1, r));

    // Merge the two Y-sorted halves
    inplace_merge(pts.begin() + l, pts.begin() + mid + 1, pts.begin() + r + 1, compareY);

    // Collect points within distance d of the vertical dividing line
    vector<Point> strip;
    for (int i = l; i <= r; i++) {
        if (abs(pts[i].x - midX) < d) {
            strip.push_back(pts[i]);
        }
    }

    // Check the strip (Y-sorted)
    for (int i = 0; i < strip.size(); i++) {
        for (int j = i + 1; j < strip.size() && (strip[j].y - strip[i].y) < d; j++) {
            d = min(d, dist(strip[i], strip[j]));
        }
    }

    return d;
}

double getClosestPair(vector<pair<long long, long long>>& coords) {
    int n = coords.size();
    vector<Point> pts(n);
    for (int i = 0; i < n; i++) {
        pts[i] = {coords[i].first, coords[i].second};
    }

    // Initial sort by X
    sort(pts.begin(), pts.end(), compareX);

    return solve(pts, 0, n - 1);
}

int main() {
    vector<pair<long long, long long>> input = {{2, 3}, {12, 30}, {40, 50}, {5, 1}, {12, 10}, {3, 4}};
    cout << fixed << setprecision(6) << getClosestPair(input) << endl;
    return 0;
}
```

### Complexity Analysis

- **Time Complexity:** $O(n \log n)$. The recurrence relation is $T(n) = 2T(n/2) + O(n)$. The $O(n)$ term comes from the `inplace_merge` and the strip processing (since each point in the strip is compared against a constant number of neighbors).
- **Space Complexity:** $O(n)$ to store the points and the temporary strip vector during recursion.

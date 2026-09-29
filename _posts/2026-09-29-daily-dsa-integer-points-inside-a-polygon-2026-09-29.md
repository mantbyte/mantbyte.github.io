---
layout: post
title: 'Daily DSA: Integer Points Inside a Polygon (Hard)'
date: 2026-09-29 21:48:51 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Hard DSA problem: Integer Points
  Inside a Polygon.'
cover_image: /assets/images/posts/daily-dsa-integer-points-inside-a-polygon-2026-09-29-cover.png
cover_caption: ''
---

### Problem Statement

You are given an array of $n$ points `coordinates` where `coordinates[i] = [xi, yi]` represents a vertex of a simple polygon. The vertices are given in order (either clockwise or counter-clockwise).

A **simple polygon** is a polygon that does not intersect itself and has no holes.

Your task is to find the number of points with **integer coordinates** that lie **strictly inside** the polygon.

### Examples

**Example 1:**
**Input:** `coordinates = [[0,0], [3,0], [0,4]]`
**Output:** `3`
**Explanation:** The vertices form a right triangle. The integer points on the boundary are (0,0), (1,0), (2,0), (3,0), (0,1), (0,2), (0,3), (0,4). The integer points strictly inside are (1,1), (1,2), and (2,1).

**Example 2:**
**Input:** `coordinates = [[0,0], [4,0], [4,4], [0,4]]`
**Output:** `9`
**Explanation:** The vertices form a 4x4 square. The total number of integer points inside are (1,1), (1,2), (1,3), (2,1), (2,2), (2,3), (3,1), (3,2), and (3,3).

### Constraints

- `3 <= n <= 10^5`
- `-10^6 <= xi, yi <= 10^6`
- The given points form a simple polygon.

---

### Approach

To solve this problem, we combine two fundamental geometric principles: **Shoelace Formula** and **Pick's Theorem**.

#### 1. Shoelace Formula (Area of a Polygon)
The area $A$ of a simple polygon with vertices $(x_1, y_1), (x_2, y_2), \dots, (x_n, y_n)$ can be calculated using:
$$2A = | \sum_{i=1}^{n} (x_i y_{i+1} - x_{i+1} y_i) |$$
where $(x_{n+1}, y_{n+1}) = (x_1, y_1)$. Note that $2A$ will always be an integer if all vertices have integer coordinates.

#### 2. Boundary Points
The number of integer points $B$ on a line segment connecting $(x_1, y_1)$ and $(x_2, y_2)$ is given by:
$$\text{Points on segment} = \gcd(|x_2 - x_1|, |y_2 - y_1|) + 1$$
To find the total boundary points $B$ of the polygon, we sum the $\gcd$ of the differences for every edge:
$$B = \sum_{i=1}^{n} \gcd(|x_{i+1} - x_i|, |y_{i+1} - y_i|)$$

#### 3. Pick's Theorem
Pick's Theorem relates the area $A$ of a polygon with integer vertices to the number of interior points $I$ and boundary points $B$:
$$A = I + \frac{B}{2} - 1$$
Rearranging for $I$ (the interior points):
$$2I = 2A - B + 2 \implies I = \frac{2A - B + 2}{2}$$

#### Complexity Analysis
- **Time Complexity:** $O(n \log(\max(coords)))$ due to the GCD calculation for each of the $n$ edges.
- **Space Complexity:** $O(1)$ extra space if we ignore the input storage.

---

### C++ Solution

```cpp
#include <vector>
#include <numeric>
#include <cmath>

using namespace std;

class Solution {
public:
    /**
     * Calculates the number of integer points strictly inside a simple polygon.
     * Uses Shoelace Formula for Area and Pick's Theorem for interior points.
     */
    long long countInteriorPoints(vector<vector<int>>& coordinates) {
        int n = coordinates.size();
        long long doubleArea = 0;
        long long boundaryPoints = 0;

        for (int i = 0; i < n; ++i) {
            long long x1 = coordinates[i][0];
            long long y1 = coordinates[i][1];
            long long x2 = coordinates[(i + 1) % n][0];
            long long y2 = coordinates[(i + 1) % n][1];

            // 1. Shoelace Formula part: sum(x_i * y_{i+1} - x_{i+1} * y_i)
            doubleArea += (x1 * y2 - x2 * y1);

            // 2. Count boundary points on edge i -> i+1
            // The number of integer points on a segment is gcd(dx, dy)
            boundaryPoints += std::gcd(abs(x2 - x1), abs(y2 - y1));
        }

        // The area is half the absolute value of the shoelace sum
        if (doubleArea < 0) doubleArea = -doubleArea;

        // 3. Pick's Theorem: Area = Interior + (Boundary / 2) - 1
        // Multiplying by 2: 2 * Area = 2 * Interior + Boundary - 2
        // Therefore: 2 * Interior = 2 * Area - Boundary + 2
        long long interiorPoints = (doubleArea - boundaryPoints + 2) / 2;

        return interiorPoints;
    }
};
```

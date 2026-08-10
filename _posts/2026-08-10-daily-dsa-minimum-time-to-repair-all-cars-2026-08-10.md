---
layout: post
title: 'Daily DSA: Minimum Time to Repair All Cars (Medium)'
date: 2026-08-10 16:33:02 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Minimum Time
  to Repair All Cars.'
cover_image: /assets/images/posts/daily-dsa-minimum-time-to-repair-all-cars-2026-08-10-cover.png
cover_caption: ''
---

### Problem Description

You are given an integer array `ranks` representing the ranks of some mechanics. `ranks[i]` is the rank of the $i^{th}$ mechanic. A mechanic with rank $r$ can repair $n$ cars in $r \times n^2$ minutes.

You are also given an integer `cars` representing the total number of cars to be repaired. All mechanics can work simultaneously. Return the **minimum** time needed to repair all the cars.

### Examples

**Example 1:**
**Input:** `ranks = [4, 2, 3, 1]`, `cars = 10`
**Output:** `16`
**Explanation:** 
- The 1st mechanic (rank 4) repairs 2 cars: $4 \times 2^2 = 16$ minutes.
- The 2nd mechanic (rank 2) repairs 2 cars: $2 \times 2^2 = 8$ minutes.
- The 3rd mechanic (rank 3) repairs 2 cars: $3 \times 2^2 = 12$ minutes.
- The 4th mechanic (rank 1) repairs 4 cars: $1 \times 4^2 = 16$ minutes.
In 16 minutes, all mechanics can repair $2+2+2+4 = 10$ cars.

**Example 2:**
**Input:** `ranks = [5, 1, 8]`, `cars = 6`
**Output:** `16`
**Explanation:** 
- The 1st mechanic (rank 5) repairs 1 car: $5 \times 1^2 = 5$ minutes.
- The 2nd mechanic (rank 1) repairs 4 cars: $1 \times 4^2 = 16$ minutes.
- The 3rd mechanic (rank 8) repairs 1 car: $8 \times 1^2 = 8$ minutes.
Total cars: $1+4+1 = 6$. Minimum time is 16 minutes.

### Constraints
- $1 \le ranks.length \le 10^5$
- $1 \le ranks[i] \le 100$
- $1 \le cars \le 10^6$

### Approach

1.  **Monotonicity:** As the time allowed increases, the number of cars repaired by each mechanic also increases. This monotonic property suggests that we can use **Binary Search on the Answer**.
2.  **Range Selection:** 
    - The minimum time `low` is 1.
    - The maximum time `high` can be estimated by the case where the mechanic with the best rank (minimum rank) repairs all the cars. If $r_{min}$ is the minimum rank, the time would be $r_{min} \times cars^2$.
3.  **Check Function:** For a given time $T$, how many cars can a mechanic with rank $r$ repair? 
    - $r \times n^2 \le T \implies n^2 \le T/r \implies n \le \lfloor \sqrt{T/r} \rfloor$.
    - Sum the cars repaired by all mechanics and check if the total is $\ge$ `cars`.

### C++ Solution

```cpp
#include <vector>
#include <algorithm>
#include <cmath>

using namespace std;

class Solution {
public:
    long long repairCars(vector<int>& ranks, int cars) {
        long long low = 1;
        // Upper bound: minimum rank mechanic repairs all cars
        long long minRank = *min_element(ranks.begin(), ranks.end());
        long long high = minRank * 1LL * cars * cars;
        long long result = high;

        while (low <= high) {
            long long mid = low + (high - low) / 2;
            if (canRepair(ranks, cars, mid)) {
                result = mid;
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        }
        return result;
    }

private:
    bool canRepair(const vector<int>& ranks, int totalCars, long long time) {
        long long count = 0;
        for (int r : ranks) {
            // n = sqrt(time / r)
            count += floor(sqrt((double)time / r));
            if (count >= totalCars) return true;
        }
        return count >= totalCars;
    }
};
```

### Complexity Analysis
- **Time Complexity:** $O(N \log(R_{min} \cdot C^2))$, where $N$ is the number of mechanics, $R_{min}$ is the minimum rank, and $C$ is the number of cars. Given the constraints, the log factor is roughly 60.
- **Space Complexity:** $O(1)$ excluding the input storage.

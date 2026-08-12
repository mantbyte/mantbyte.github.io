---
layout: post
title: 'Daily DSA: Single-Processor Task Scheduler with Priority (Medium)'
date: 2026-08-12 16:27:00 +0530
categories: DSA
excerpt: 'Sharpen your coding skills with today''s Medium DSA problem: Single-Processor
  Task Scheduler with Priority.'
cover_image: /assets/images/posts/daily-dsa-singleprocessor-task-scheduler-with-priority-2026-08-12-cover.png
cover_caption: ''
---

### Problem Statement

You are given $n$ tasks to be scheduled on a single-processor CPU. Each task is represented as a triplet `tasks[i] = [arrival_i, processing_i, priority_i]`:

* `arrival_i`: The time at which the $i$-th task becomes available for execution.
* `processing_i`: The amount of time required to finish processing the $i$-th task.
* `priority_i`: The priority level of the $i$-th task (higher integer values represent higher priority).

The CPU schedules tasks according to the following rules:
1. The CPU can only execute **one task at a time**.
2. Processing is **non-preemptive**: once a task starts running, it will run uninterrupted until completion.
3. If the CPU becomes idle, it waits until the next task arrives.
4. If multiple tasks are ready for processing at a given time, the CPU selects the available task with the **highest priority**.
5. If there is a tie in priority, the CPU chooses the task with the **earliest arrival time**. If a tie still persists, choose the task with the **smaller original index**.

Return an array `completion_times` of length $n$, where `completion_times[i]` is the exact time at which the $i$-th task finishes processing.

---

### Examples

**Example 1:**
```
Input: tasks = [[1, 4, 2], [2, 3, 5], [3, 2, 5]]
Output: [9, 5, 7]
Explanation:
- At time t = 0: No tasks available. CPU idle.
- At time t = 1: Task 0 arrives [1, 4, 2]. CPU starts processing Task 0.
- At time t = 2: Task 1 arrives [2, 3, 5]. Task 0 is still running.
- At time t = 3: Task 2 arrives [3, 2, 5]. Task 0 is still running.
- At time t = 5: Task 0 finishes (completion time = 5). Available ready tasks: Task 1 (priority 5, arrival 2) and Task 2 (priority 5, arrival 3).
  Both have priority 5, but Task 1 arrived earlier (t = 2). CPU executes Task 1.
- At time t = 8: Task 1 finishes (completion time = 8... wait, Task 0 finishes at t = 1+4=5).
  Correction:
  - Task 0 started at t = 1, takes 4 units -> finishes at t = 5. Ans[0] = 5? Wait, Task 0 was selected because at t=1 it was the ONLY task available.
  - At t = 5: Available: Task 1 (prio 5, arrival 2), Task 2 (prio 5, arrival 3). Task 1 starts at t = 5, takes 3 units -> finishes at t = 8.
  - At t = 8: Available: Task 2 (prio 5, arrival 3). Task 2 starts at t = 8, takes 2 units -> finishes at t = 10.
  Output: [5, 8, 10]
```

**Example 2:**
```
Input: tasks = [[0, 3, 1], [0, 2, 2], [5, 4, 3]]
Output: [5, 2, 9]
Explanation:
- At t = 0: Both Task 0 and Task 1 arrive. Task 1 has higher priority (2 > 1), so CPU executes Task 1.
- At t = 2: Task 1 finishes (completion time = 2). Available ready tasks: Task 0.
- At t = 2: Task 0 starts and takes 3 units -> finishes at t = 5.
- At t = 5: Task 0 finishes. Task 2 arrives at t = 5. CPU executes Task 2 immediately -> finishes at t = 5 + 4 = 9.
Output: [5, 2, 9]
```

---

### Constraints

* $1 \le n \le 10^5$
* `tasks[i].length == 3`
* $0 \le \text{arrival}_i \le 10^9$
* $1 \le \text{processing}_i \le 10^9$
* $1 \le \text{priority}_i \le 10^9$

---

### Approach / Hint

1. **Sorting by Arrival Time**: First, attach each task's original index to its data structure so that output results can be mapped back accurately. Sort all tasks primarily by their arrival time.
2. **Priority Queue for Available Tasks**: Maintain a **Max-Heap** (or custom comparator) containing tasks that have arrived by `currentTime` and are waiting to be executed.
   * The comparator should order by:
     1. Higher priority first
     2. Smaller arrival time second
     3. Smaller original index third
3. **Event Simulation Loop**:
   * Maintain `currentTime` starting at `0` (or arrival time of the first task).
   * If the priority queue is empty and the next task's arrival time is greater than `currentTime`, jump `currentTime` forward to that task's arrival time.
   * Push all tasks whose arrival time is $\le \text{currentTime}$ into the priority queue.
   * Pop the top task from the priority queue, process it by adding its `processing` duration to `currentTime`, and store the completion time at its original index.

---

### C++ Solution

```cpp
#include <vector>
#include <queue>
#include <algorithm>

using namespace std;

struct Task {
    long long arrival;
    long long processing;
    long long priority;
    int original_index;
};

// Custom comparator for Max-Heap
struct TaskComparator {
    bool operator()(const Task& a, const Task& b) const {
        if (a.priority != b.priority) {
            return a.priority < b.priority; // Higher priority comes first
        }
        if (a.arrival != b.arrival) {
            return a.arrival > b.arrival;  // Earlier arrival comes first
        }
        return a.original_index > b.original_index; // Smaller index comes first
    }
};

class Solution {
public:
    vector<long long> getTaskCompletionTimes(vector<vector<int>>& tasksInput) {
        int n = tasksInput.size();
        vector<Task> tasks(n);

        for (int i = 0; i < n; ++i) {
            tasks[i] = {
                (long long)tasksInput[i][0],
                (long long)tasksInput[i][1],
                (long long)tasksInput[i][2],
                i
            };
        }

        // Sort tasks primarily by arrival time
        sort(tasks.begin(), tasks.end(), [](const Task& a, const Task& b) {
            return a.arrival < b.arrival;
        });

        priority_queue<Task, vector<Task>, TaskComparator> readyQueue;
        vector<long long> completionTimes(n);

        long long currentTime = 0;
        int taskIdx = 0;

        while (taskIdx < n || !readyQueue.empty()) {
            // If no tasks are ready and processor is idle, jump time forward
            if (readyQueue.empty() && currentTime < tasks[taskIdx].arrival) {
                currentTime = tasks[taskIdx].arrival;
            }

            // Enqueue all tasks that have arrived by currentTime
            while (taskIdx < n && tasks[taskIdx].arrival <= currentTime) {
                readyQueue.push(tasks[taskIdx]);
                taskIdx++;
            }

            // Pick the next highest priority task
            Task currentTask = readyQueue.top();
            readyQueue.pop();

            currentTime += currentTask.processing;
            completionTimes[currentTask.original_index] = currentTime;
        }

        return completionTimes;
    }
};
```

---

### Complexity Analysis

- **Time Complexity:** $\mathcal{O}(n \log n)$
  Sorting the tasks takes $\mathcal{O}(n \log n)$ time. Each task is pushed into and popped from the priority queue exactly once, taking $\mathcal{O}(\log n)$ time per task. Thus, total time complexity is $\mathcal{O}(n \log n)$.
- **Space Complexity:** $\mathcal{O}(n)$
  The priority queue and task structures require $\mathcal{O}(n)$ additional memory space.

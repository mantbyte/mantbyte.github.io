---
layout: post
title: 'Beyond Kubernetes at Modal: Scaling 1 Million Concurrent Sandboxes'
date: 2026-09-23 22:24:14 +0530
categories: Tech
excerpt: Discover how Modal bypassed Kubernetes limitations to scale 1 million concurrent
  ephemeral sandboxes for modern AI workloads.
cover_image: /assets/images/posts/beyond-kubernetes-modal-scaling-sandboxes-cover.png
cover_caption: A conceptual visualization of high-density ephemeral sandboxes scaling
  beyond Kubernetes limits.
---

The explosion of generative AI and complex serverless workflows has fundamentally shifted what we demand from cloud infrastructure. We are no longer just deploying long-lived microservices that run for days, weeks, or months. Instead, modern workloads—ranging from multi-tenant code interpreters and dynamic AI agents to instantaneous function execution—require ultra-ephemeral, high-churn compute environments that spin up in milliseconds and vanish just as fast. 

To meet this demand, Modal engineers Colin Weld and Connor Adams rebuilt their sandbox infrastructure from the ground up to support millions of concurrent sandboxes. But this engineering feat required a radical departure from the industry standard. To achieve hyperscale, sub-second sandbox execution, Modal had to step outside the Kubernetes ecosystem entirely. 

This brings us to an uncomfortable truth for many platform engineers: Kubernetes is brilliantly engineered for long-lived microservices, but it is fundamentally strained by the hyper-ephemeral, high-density requirements of modern AI workloads. 

## Why Kubernetes Breaks at Hyperscale

To understand why Modal had to build a custom solution, we have to look at where traditional orchestrators hit their architectural limits. Kubernetes relies on a centralized control plane where every state change—whether it is scheduling a pod, updating a deployment, or tracking health checks—flows through a single strongly consistent data store: `etcd`. 

While `etcd` provides absolute safety and linearizability, it does so at a cost. In a high-churn environment where thousands of ephemeral sandboxes are created and destroyed every second, `etcd` becomes an immediate bottleneck. Every write is serialized, meaning that as concurrent container requests spike, the control plane experiences severe lock contention and tail latency degradation.

Beyond the state store, the core scheduler in Kubernetes faces severe scaling walls. The scheduler typically evaluates cluster state sequentially or via centralized queues, leading to performance degradation that scales poorly with the total number of active containers and nodes ($O(\text{containers})$ and $O(\text{nodes})$ complexity). When you introduce the demands of GenAI workloads—where thousands of users simultaneously spin up isolated execution environments—a centralized scheduler simply cannot push state changes fast enough to maintain sub-second guarantees.

This friction contextualizes a broader infrastructure trend we are seeing across the industry, echoing the architectural dilemmas discussed in [The Kubernetes Moment for Open-Weight AI: Standardizing the Infrastructure Stack](/tech/2026/07/26/kubernetes-moment-open-weight-ai-infrastructure.html). While Kubernetes remains unmatched for standard cluster orchestration, forcing it to handle massive, high-churn sandbox lifecycles is akin to using a freight train to navigate a Formula 1 circuit. It is built for a completely different operational profile.

## Deconstructing Modal’s New Architecture

To break past these centralized ceilings, the engineering team at Modal fundamentally rethought how container orchestration should work for ephemeral compute. They replaced the traditional monolithic control plane with a decentralized, highly parallel model.

| Architectural Dimension | Traditional Kubernetes | Modal’s Decoupled Architecture |
| :--- | :--- | :--- |
| **State Storage** | Centralized, strongly consistent (`etcd`) | Decentralized worker-as-source-of-truth |
| **Scheduler Design** | Centralized, serialized queueing | Horizontally scalable scheduling fleet |
| **Communication** | API server polling and watch loops | Direct Remote Procedure Calls (RPC) |
| **Workload Profile** | Long-lived microservices and pods | Ultra-ephemeral, high-churn sandboxes |

Instead of routing every sandbox lifecycle event through a single global database, Modal’s architecture shifts the paradigm: **it treats each worker as its own source of truth.** 

In this decentralized model, a horizontally scalable scheduling fleet handles incoming requests by communicating directly with workers via fast, low-overhead Remote Procedure Calls (RPC). Because individual workers maintain their own localized state, the system eliminates global locking contention. A spike in sandbox creation in one region or on one hardware rack does not block or slow down scheduling decisions happening elsewhere in the fleet. 

This decoupling of coordination from execution allows the control plane to scale horizontally alongside the compute infrastructure. As demand increases, you simply scale the scheduling fleet and add worker nodes without hitting a centralized `etcd` bottleneck.

## Achieving Sub-Second Cold Starts at Scale

Architecting a decentralized control plane is only half the battle; the real engineering challenge lies in shrinking the end-to-end latency of a sandbox's life cycle. For AI agents and interactive serverless applications, users expect sub-second cold starts. If a sandbox takes five seconds to initialize, the user experience breaks down entirely.

Modal’s engineering improvements target several critical phases of the sandbox lifecycle:

* **Eliminating Serialization Overhead:** By stripping away the heavy JSON-over-HTTP API translation layers common in traditional orchestrators, the scheduling fleet communicates state changes using optimized binary RPC protocols. This dramatically reduces CPU cycles spent marshaling and unmarshaling data during rapid task routing.
* **Optimizing Isolation Boundaries:** Rapid initialization requires striking a balance between security and speed. Modal optimized its process and network isolation layers to spin up lightweight execution environments without paying the full penalty of traditional virtualization boot times.
* **Absorbing Traffic Spikes:** When a viral AI application triggers a sudden wave of millions of concurrent requests, the system must handle massive container churn without cascading failures. Because there is no central scheduler queue to back up, workers independently accept and spin down tasks, naturally distributing the load across the entire hardware fleet.

Similar routing and scaling pressures surface in other high-throughput distributed systems, such as the LLM traffic management challenges explored in [Scaling AI Agents with AKS and Microsoft LLM Routing](/tech/2026/07/29/scaling-ai-agents-aks-microsoft-llm-routing.html), where maintaining low latency under erratic load profiles requires dropping one-size-fits-all abstractions in favor of specialized routing logic.

## Trade-offs, Comparisons, and Best Practices

Stepping outside the well-trodden Kubernetes ecosystem unlocks incredible performance, but it is not a free lunch. When you design a custom orchestration layer tailored for a hyper-specific workload, you trade away standard tooling and mature ecosystem guarantees.

### The Trade-offs

* **Pros:**
  * Massive, linear scalability without control-plane lockups.
  * Predictable, sub-second latencies for millions of concurrent ephemeral tasks.
  * Elimination of etcd and centralized scheduler bottlenecks.
* **Cons:**
  * Loss of out-of-the-box Kubernetes compatibility (Helm charts, standard Operators, and community tooling).
  * The engineering overhead of building and maintaining custom operational tooling, monitoring, and telemetry.
  * A steeper learning curve for engineers accustomed to standard cloud-native primitives.

### Best Practices for Custom Orchestration

If your engineering team is evaluating whether to build a custom scheduler or orchestration layer rather than forcing Kubernetes to fit your workload, keep these principles in mind:

1. **Define Your Churn Profile Early:** If your containers live for days, Kubernetes is likely the right tool. If your workloads churn in seconds and scale by orders of magnitude instantly, look at decentralized models.
2. **Embrace Eventual Consistency:** Strongly consistent global stores do not scale horizontally. Design your workers to be autonomous sources of truth that can reconcile state asynchronously.
3. **Prioritize Direct Communication Paths:** Eliminate intermediary brokers and API servers where possible. Direct RPC connections between schedulers and execution nodes dramatically reduce tail latency.

## Future Outlook: The Decoupling of Coordination and Execution

Modal’s architecture is part of a broader, quiet revolution happening across cloud infrastructure. For years, the industry operated under the assumption that Kubernetes was the universal answer to container orchestration. But as GenAI, serverless functions, and distributed AI agents redefine the compute landscape, we are seeing a clear architectural divergence.

The future belongs to systems that decouple the coordination plane from the execution plane. Rather than relying on monolithic orchestrators to manage everything from network policies to storage volumes and container lifecycles, modern infrastructure is moving toward lightweight, specialized execution engines designed for rapid isolation boundaries and massive concurrency. 

As developers continue to push the boundaries of what cloud workloads can do, Modal's approach proves that when your performance requirements demand it, abandoning convention in favor of first-principles engineering is the only way forward.

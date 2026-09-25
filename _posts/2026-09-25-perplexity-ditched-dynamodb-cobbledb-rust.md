---
layout: post
title: 'Why Perplexity Ditched DynamoDB for CobbleDB: Inside Their Custom Rust Database
  Migration'
date: 2026-09-25 22:29:07 +0530
categories: Tech
excerpt: Perplexity replaced Amazon DynamoDB with CobbleDB, a custom 40,000-line Rust
  database built in two months to slash latency and cloud bills.
cover_image: /assets/images/posts/default-cover.png
cover_caption: Architecture diagram illustrating Perplexity's migration from DynamoDB
  to the custom Rust-based CobbleDB.
---

When your application scales to handle hundreds of thousands of requests per second, the cracks in general-purpose cloud databases start to show. For Perplexity, the rapidly growing AI search engine, the breaking point arrived when standard cloud-managed NoSQL solutions could no longer keep up with the unique, high-throughput demands of generative AI query serving. Serving real-time answers requires retrieving massive amounts of context, document chunks, and embeddings concurrently—a workload that looks nothing like traditional web application traffic. 

Faced with escalating cloud bills and stubborn tail latencies, Perplexity’s infrastructure team made a bold engineering choice: they ditched Amazon DynamoDB. In its place, they built and deployed **CobbleDB**, a custom, 40,000-line distributed key-value store written entirely in Rust. 

Building a production-grade database from scratch usually takes years and a massive team of storage experts. But Perplexity pulled it off in just two months with a tiny crew, leaning heavily on autonomous AI coding agents to accelerate development. The resulting architecture not only slashed median batch-read latency by over 80% but also cut cloud storage expenses by at least 20%. Let's look inside the architecture, the load profile that broke DynamoDB, and how this custom Rust engine achieves its numbers.

## The Anatomy of an AI Query Load Profile

To understand why traditional key-value stores hit a wall, we have to look at what happens under the hood when a user submits a query to an AI search engine. Unlike a classic key-value lookup where an application fetches a single user session or profile (typically a few hundred bytes), an AI retrieval query triggers a complex fan-out pattern.

Each incoming Perplexity search query generates between **100 to 120 target page keys**. To serve these results within milliseconds, the query engine splits these targets into parallel batches of 10 to 20 keys, issuing concurrent read requests down to the storage tier. 

```
[Incoming AI Query]
       │
       ▼
[Query Router] ──(Generates 100–120 target page keys)
       │
       ├─► [Batch 1: 10–20 keys] (50KB avg payload each)
       ├─► [Batch 2: 10–20 keys] (50KB avg payload each)
       └─► [Batch N: 10–20 keys] (50KB avg payload each)
```

The compounding issue here isn't just request volume—it's payload size. While traditional NoSQL tables excel at handling millions of tiny rows, Perplexity’s records consist of rich document chunks, metadata, and embeddings with an average payload of roughly **50 kilobytes per record**. 

When you multiply 50KB by hundreds of parallel keys across production traffic scales exceeding **200,000 requests per second**, you quickly run into severe bandwidth saturation and throttling limits on managed cloud services. Standard cloud database batch-read APIs struggle to maintain predictable throughput when forced to shovel megabytes of data per second per node through generalized network interfaces and multi-tenant isolation layers. 

When general-purpose databases hit these hardware and software bottlenecks, teams often find themselves over-provisioning provisioned throughput or rewriting application logic, much like engineering teams optimizing inventory systems as seen in our breakdown of [how Shopify migrated Redis to MySQL for inventory](/tech/2026/08/09/shopify-migrated-redis-mysql-inventory.html). But at Perplexity's scale, minor configuration tweaks weren't enough. They needed a storage engine built from the metal up for their exact data shape.

## Architecting CobbleDB: A Custom Rust Storage Engine

CobbleDB is a distributed key-value store built specifically to handle batched, large-payload retrieval workloads. Comprising roughly 40,000 lines of Rust, the system leans heavily on modern systems programming primitives, including **RocksDB** for single-node storage engines and high-performance **NVMe SSDs** to maximize raw I/O throughput.

Rather than trying to build a monolithic database that handles everything from durable writes to analytical queries, Perplexity divided their storage architecture into a clean **three-tier specialized storage split**:

| Tier | Component | Underlying Technology | Primary Role |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Pillar** | YTsaurus over mechanical drives | Durable state management and source of truth |
| **Tier 2** | **Lorry** | Stateless queue consumer over Amazon S3 | Packing S3 batch exports and feeding downstream caches |
| **Tier 3** | **CobbleDB** | RocksDB, NVMe SSDs, Rust | Fast, low-latency routing and serving of hot retrieval data |

### The Three-Tier Storage Split

* **Pillar:** Acts as the heavy-duty durable state management layer. Built on top of YTsaurus and backed by cost-effective mechanical drives, Pillar holds the cold, permanent source of truth for the system.
* **Lorry:** Operates as a stateless queue consumer. Its job is to efficiently pack S3 batch exports, transforming bulk analytical storage into a consumable stream for the serving tiers.
* **CobbleDB:** The star of the show. CobbleDB sits at the edge, serving as a distributed key-value store optimized for high-throughput, low-latency lookups using local NVMe drives.

To route traffic efficiently, CobbleDB utilizes **zone-aware stateless query routers** paired with an **eventual consistency model**. Because AI search retrieval workloads care far more about speed and availability than strict linearizability for every single document chunk, loosening consistency guarantees allowed the team to strip away distributed locking overhead. The system uses techniques like speculative hedging—issuing parallel requests to redundant replicas if a primary node stutters—to keep tail latencies aggressively low.

## Speedrunning Systems Engineering with AI Agents

One of the most remarkable aspects of the CobbleDB project isn't just the architecture, but *how* it was built. Constructing a distributed, production-ready storage engine in Rust usually requires a large, specialized team working over several years. Perplexity accomplished this in **just two months**.

The engineering team behind CobbleDB consisted of:
* **Two veteran systems engineers** providing architectural oversight, system design, and critical path decisions.
* **An autonomous swarm of AI coding agents** handling boilerplate implementation, memory safety validation, and concurrent Rust structure generation.

| Traditional Database Development | Perplexity's CobbleDB Approach |
| :--- | :--- |
| **Team Size:** 10–20 engineers | **Team Size:** 2 engineers + AI agent swarm |
| **Timeline:** 12 to 24 months | **Timeline:** 2 months |
| **Focus:** General-purpose flexibility | **Focus:** Hyper-specific workload optimization |

This setup highlights an evolving paradigm in systems architecture. By using AI coding assistants to handle repetitive boilerplate, write extensive test suites, and catch subtle memory management bugs in concurrent Rust code, human engineers can focus entirely on high-level abstractions and performance characteristics. 

For complex debugging sessions and root-cause analysis during development, leaning on structured AI prompts proved invaluable, mirroring the methodologies explored when applying [context engineering for AI root-cause analysis](/tech/2026/07/25/context-engineering-ai-root-cause-analysis.html). The human engineers acted as architects and code reviewers, while the AI swarm acted as an indefatigable implementation engine.

## Performance and Economic Impact

Moving away from a managed cloud NoSQL database to a custom-built, NVMe-backed Rust storage engine yielded immediate, dramatic dividends. CobbleDB transformed Perplexity's read path, turning a chronic cloud bottleneck into a high-speed pipeline.

### Latency Benchmarks (Batch-Read Operations)

* **Median Latency (p50):** Dropped from **31.4 ms** down to **5.60 ms** (a nearly 5.6x speedup).
* **Tail Latency (p90):** Improved from **56.7 ms** down to **9.77 ms**.
* **Extreme Tail Latency (p99):** Plummeted from **123 ms** down to **24.2 ms**.

```
Latency Comparison (Lower is better)

p50:  DynamoDB [31.4 ms]
      CobbleDB [5.60 ms]

p90:  DynamoDB [56.7 ms]
      CobbleDB [9.77 ms]

p99:  DynamoDB [123 ms]
      CobbleDB [24.2 ms]
```

Beyond raw speed, the economic impact was profound. Managing hundreds of thousands of requests per second on DynamoDB incurred massive provisioned throughput and storage costs. By moving the hot retrieval path to self-hosted RocksDB instances running on high-density NVMe SSDs, Perplexity **cut their cloud storage and provisioning expenses by at least 20%**, even while scaling past 200,000 requests per second. 

## Broader Industry Lessons and Future Outlook

Perplexity's migration from DynamoDB to CobbleDB offers a clear signal for infrastructure teams operating at high scales. While managed cloud databases are fantastic for general-purpose web applications, MVPs, and unpredictable workloads, they often impose severe economic and performance ceilings when forced to handle hyper-specific, bandwidth-heavy AI pipelines. 

When your access patterns involve massive parallel batch reads of large document chunks and embeddings, general-purpose NoSQL solutions can trap you in a cycle of over-provisioning. Building a domain-specific storage engine—once considered an anti-pattern due to maintenance overhead—is becoming increasingly viable. 

This viability is turbocharged by modern tooling. As Perplexity demonstrated, combining deep systems engineering oversight with AI coding assistants allows small teams to build production-grade infrastructure at unprecedented speeds. 

Looking forward, Perplexity has announced plans to **open-source the CobbleDB codebase**, allowing the broader systems community to inspect, adopt, and contribute to the engine. As generative AI retrieval requirements continue to expand across the industry, we are likely to see a broader shift away from one-size-fits-all NoSQL solutions and toward vertically integrated, asynchronous, eventual-consistency stores optimized specifically for batched embeddings and document chunks.

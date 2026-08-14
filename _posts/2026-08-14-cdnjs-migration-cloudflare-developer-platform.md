---
layout: post
title: 'Scaling to 9 Billion Daily Requests: Inside the cdnjs Migration to Cloudflare''s
  Developer Platform'
date: 2026-08-14 21:28:39 +0530
categories: Tech
excerpt: cdnjs powers 12% of the web, handling over 9 billion daily requests. Discover
  how the team re-architected its infrastructure to an edge-native stack on Cloudflare.
cover_image: /assets/images/posts/cdnjs-migration-cloudflare-developer-platform-cover.png
cover_caption: A visualization of global network traffic flowing through Cloudflare's
  edge nodes.
---

When we talk about the infrastructure that holds the modern web together, we often focus on the giants: AWS, Google Cloud, or Azure. But there is a layer of the internet that is simultaneously more ubiquitous and more specialized. One of the most critical components of this layer is **cdnjs**.

If you have ever built a website using Bootstrap, jQuery, or Font Awesome, you have likely used cdnjs. It is a massive, community-driven library of front-end assets that currently powers approximately 12% of all websites on the internet. At its peak, it handles over 9 billion daily requests. To put that in perspective, that is more than 100,000 requests every single second, sustained 24/7.

For years, cdnjs operated on a hybrid infrastructure, balancing assets between Google Cloud Platform (GCP) for storage and Cloudflare for delivery. While this worked, it created a "split-brain" operational reality. Synchronizing data between a traditional cloud provider and a global edge network introduced latency, increased complexity, and limited the speed at which the library could ingest new packages.

Recently, the team behind cdnjs completed a total migration to the Cloudflare Developer Platform. This wasn't just a simple server move; it was a fundamental re-architecting of how a massive public utility functions. By moving to an edge-native stack—using Workers, R2, KV, and Workflows—cdnjs has become a blueprint for how to build high-scale, stateful applications without a single traditional server.

## Deconstructing the Legacy: Why Migrate?

The previous cdnjs architecture was a testament to "making it work" with the tools available at the time. The primary storage sat in GCP buckets. When a new version of a library was released on GitHub, an ingestion script would pull the files, process them, and push them to GCP. Cloudflare would then act as the caching proxy, pulling files from GCP (the origin) and distributing them to its global network.

This hybrid approach faced three primary technical hurdles:

1.  **Synchronization Latency:** There was a measurable delay between a package being updated on GitHub and it becoming available on the CDN. The "hop" from the ingestion server to GCP, and then the eventual cache-fill from GCP to Cloudflare's 330+ data centers, created a bottleneck.
2.  **Operational Overhead:** Maintaining two distinct environments meant twice the security surface area, twice the monitoring tools, and complex egress billing. Managing cross-cloud authentication and networking is a full-time job in itself.
3.  **The Metadata Bottleneck:** cdnjs isn't just a bucket of files; it’s an API. Developers and tools query cdnjs for version lists and SRI (Subresource Integrity) hashes. Generating and serving this metadata from a traditional origin meant that even small API calls had to travel back to a central server, increasing time-to-first-byte (TTFB).

The decision to migrate was driven by a need for "edge-native" performance. The goal was to move the entire lifecycle of a request—from ingestion to storage to delivery—into the same network. This migration also served as a massive "dogfooding" exercise for Cloudflare, using cdnjs as a stress test for its own serverless primitives.

## The New Backbone: Cloudflare R2 and Workers

The most significant change in the new architecture is the move from GCP storage to **Cloudflare R2**. R2 is an S3-compatible object store that notably charges zero egress fees. For a service like cdnjs, which serves petabytes of data, egress costs are usually the "hidden killer" of the budget.

### Migrating 1.1 TB of Data
The migration involved moving 1.1 TB of data, consisting of millions of small files (JavaScript, CSS, and font files). In the world of object storage, moving one 1TB file is easy; moving 10 million 100KB files is an engineering challenge. The team utilized R2’s multipart upload capabilities and internal migration tools to transfer the library without a single second of downtime.

### Workers as the Intelligent Routing Layer
In the new architecture, every one of those 9 billion daily requests is intercepted by a **Cloudflare Worker**. Unlike a traditional load balancer, a Worker is a programmable environment. It doesn't just "point" to a file; it executes logic to determine the best way to serve it.

```javascript
// A simplified example of how a Worker might route a cdnjs request
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const cache = caches.default;
    
    // Check if the asset is in the regional cache first
    let response = await cache.match(request);
    
    if (!response) {
      // If cache miss, fetch from R2 storage
      const objectKey = url.pathname.slice(1);
      const object = await env.CDNJS_BUCKET.get(objectKey);
      
      if (!object) {
        return new Response("Asset Not Found", { status: 404 });
      }

      // Construct response and add security headers (SRI, etc.)
      response = new Response(object.body, {
        headers: {
          "Content-Type": object.httpMetadata.contentType,
          "Cache-Control": "public, max-age=31536000, immutable",
          "x-cdnjs-origin": "R2-Edge"
        }
      });

      // Store in cache for future requests
      await cache.put(request, response.clone());
    }
    
    return response;
  }
};
```

### Achieving a 98.6% Cache Hit Rate
The efficiency of cdnjs depends entirely on its cache hit rate. If 9 billion requests hit the storage layer (R2) every day, the system would be prohibitively expensive and potentially slow. By leveraging Cloudflare’s Tiered Cache, the architecture ensures that if a file isn't in a local data center (say, in Mumbai), the request checks an "upper tier" data center (like Singapore) before going all the way back to the R2 bucket. This hierarchy resulted in a staggering **98.6% cache hit rate**.

| Feature | Legacy (GCP + Cloudflare) | New (Edge-Native) |
| :--- | :--- | :--- |
| **Storage** | GCP Cloud Storage | Cloudflare R2 |
| **Egress Fees** | High (Standard Cloud Rates) | Zero |
| **Routing** | DNS + Static Config | Programmable Workers |
| **Update Latency** | Minutes to Hours | Near-Instant |
| **Cache Hit Rate** | ~95% | 98.6% |

## Orchestrating the Ingestion Pipeline with Workflows

One of the most complex parts of cdnjs is the "autoupdate" feature. Every few minutes, the system must check thousands of GitHub repositories for new releases, download them, minify the code, generate SRI hashes, and update the metadata.

In the old system, this was a cron job running on a virtual machine. In the new system, this is handled by **Cloudflare Workflows**.

### Managing the Lifecycle of an Update
Workflows allow developers to write stateful, multi-step processes in code. When a new version of a library (e.g., `lodash v4.17.21`) is detected, a Workflow is triggered. This workflow manages several steps:
1.  **Download:** Pulling the source from GitHub.
2.  **Validation:** Ensuring the files are safe and match the expected structure.
3.  **Processing:** Generating minified versions if they aren't provided.
4.  **Persistence:** Writing the files to R2 and updating the metadata in KV.

### Handling High-Memory Tasks
A challenge with serverless environments like Workers is the memory limit. Minifying a massive JavaScript library can be memory-intensive. Currently, cdnjs uses a hybrid approach for this specific step: while the orchestration lives in Workflows, the actual "heavy lifting" of minification is sometimes offloaded to internal containerized services. 

However, as the platform evolves, the goal is to move these tasks into "Large Memory" Workers. This is part of the broader shift toward the [Cloudflare Computer vision](/tech/2026/08/08/cloudflare-computer-stateful-ai-agents.html), where the distinction between a "script" and a "server" disappears entirely.

## Stateful Serverless: Durable Objects and KV

How do you keep track of 4,000+ libraries and their tens of thousands of versions without a traditional SQL database? The answer lies in the combination of **Workers KV** and **Durable Objects**.

### Workers KV for Metadata
Workers KV is a low-latency, eventually consistent key-value store. It is perfect for the cdnjs API. When a developer asks for "all versions of React," the Worker queries KV. Since this data doesn't change every second, the eventual consistency model is ideal—it allows the metadata to be cached at the edge, providing sub-10ms response times for API queries.

### Durable Objects for Coordination
While KV is great for reading, it isn't designed for high-write coordination. If two separate ingestion processes tried to update the same library simultaneously, you could end up with a race condition. 

This is where **Durable Objects (DO)** come in. A Durable Object is a stateful class that is guaranteed to be unique across the entire global network. By using a DO for each library, cdnjs can ensure that only one process is modifying a library’s state at any given time. This provides the "strong consistency" needed for reliable package management. 

This architecture mirrors the advancements seen in global consensus protocols like [Meerkat and Quepaxa](/tech/2026/08/02/cloudflare-meerkat-quepaxa-global-consensus.html), which allow for stateful operations at the edge without the bottleneck of a single primary database in a US-East region.

## Optimization at the Edge: Compression and Security

Serving 9 billion requests is as much about saving bytes as it is about speed. The migration allowed cdnjs to implement more aggressive and dynamic compression strategies.

### Dynamic Brotli and Gzip
Different browsers support different compression algorithms. By using Workers, cdnjs can inspect the `Accept-Encoding` header and serve the most optimal version of a file. **Brotli**, which often provides 20-30% better compression than Gzip for text-based assets, is used for the majority of modern traffic. This reduces the payload size, leading to faster page loads for the end user and lower storage throughput for the CDN.

### Subresource Integrity (SRI) at Scale
Security is paramount when you are serving the code that powers 12% of the web. If cdnjs were compromised, an attacker could inject malicious code into millions of sites. 

To prevent this, cdnjs relies heavily on **Subresource Integrity (SRI)**. SRI allows browsers to verify that the file they fetched has not been tampered with by checking a cryptographic hash. The new architecture automates the generation of these hashes at the moment of ingestion and stores them in KV. Because the entire pipeline is now within the Cloudflare ecosystem, the "attack surface" is significantly reduced—there is no longer a need to move files over the public internet between different cloud providers.

> "By moving storage and compute into the same security perimeter, we've effectively eliminated several classes of man-in-the-middle and cross-cloud authentication vulnerabilities."

## The Dogfooding Dividend: Improving the Platform

One of the most interesting aspects of this migration is that it wasn't just good for cdnjs; it was good for every developer using Cloudflare. When you run a service at the scale of cdnjs, you find the "edges" of the platform.

### Pushing the Limits
During the migration, the cdnjs team encountered several limitations that Cloudflare eventually turned into platform improvements:
*   **Worker Script Sizes:** The complex logic required for cdnjs pushed the limits of how large a Worker script could be. This led to optimizations in how Worker code is bundled and deployed.
*   **R2 Throughput:** Serving billions of requests meant R2 had to handle unprecedented levels of concurrent reads. The engineering work done to stabilize R2 for cdnjs directly improved the performance of R2 for all other users.
*   **Multipart Uploads:** Handling millions of small files helped refine the R2 API, making it more robust for high-concurrency migrations.

This process is a classic example of "dogfooding." By building a mission-critical utility on their own stack, the engineers were forced to fix the friction points that a smaller user might never encounter.

## Future Outlook: The Path to 100% Edge-Native

The migration of cdnjs is a milestone, but it is not the end of the road. The architecture is designed to evolve. 

The next phase of the project involves moving the remaining "heavy" tasks—specifically high-resource minification and image optimization—directly into Workers. As Cloudflare continues to expand the CPU and memory limits for serverless tasks, the need for any container-based infrastructure will vanish.

Furthermore, we are looking toward a future of **autonomous edge agents**. Imagine a system where the library maintenance isn't just a scripted workflow, but a set of stateful AI agents that can monitor GitHub for security vulnerabilities, automatically patch library versions, and verify the integrity of the entire 1.1 TB repository in real-time. This aligns with the ongoing shift toward [Post-Quantum security standards](/tech/2026/07/25/post-quantum-enterprise-api-migration-roadmap.html), ensuring that the web's most used libraries remain secure even against future compute threats.

The cdnjs migration proves that serverless is no longer just for "glue code" or simple APIs. It is a robust, scalable environment capable of powering the very infrastructure of the internet. For developers, the message is clear: the edge is no longer just a place to cache your files; it is the place where your entire application should live.

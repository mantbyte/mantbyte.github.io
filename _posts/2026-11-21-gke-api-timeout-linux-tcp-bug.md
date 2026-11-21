---
layout: post
title: 'When the Kernel Forgets to Say Goodbye: Tracing a GKE API Timeout to a Linux
  TCP Bug'
date: 2026-11-21 16:18:26 +0530
categories: Tech
excerpt: Intermittent GKE API timeouts can lead you deep down a rabbit hole into the
  Linux kernel's TCP state machine, where sockets get stranded in limbo.
cover_image: /assets/images/posts/gke-api-timeout-linux-tcp-bug-cover.png
cover_caption: Network packet captures and Linux kernel architecture diagram illustrating
  TCP connection state machines.
---

{% raw %}
Intermittent API connectivity failures are among the most frustrating issues an SRE can encounter. You check your dashboards, and everything looks healthy. Pods are running, nodes are reporting green, and memory utilization is nominal. Yet, out of nowhere, kubectl commands hang, automated CI/CD pipelines drop connections, and the Google Kubernetes Engine (GKE) control plane feels sluggish or entirely unreachable. When these transient bugs strike complex cloud-native architectures, they often mask a fascinating interaction between layers of the stack that we usually take for granted. 

What starts as a vague timeout error in a deployment script can quickly pull you down a rabbit hole spanning cloud-managed load balancers, sidecar proxy layers, and deep inside the Linux kernel's TCP state machine. Recently, Google engineers unraveled a particularly elusive class of GKE API failures. By tracing the symptoms down to the wire and into the kernel source code, they uncovered a subtle bug where the operating system literally forgot how to say goodbye to a network connection.

Let's break down how this multi-layer mystery unfolded, why sockets ended up stranded in limbo, and what it teaches us about the hidden fragility of modern infrastructure.

## Anatomy of the Failure: Sockets Stuck in Limbo

To understand the bug, we have to look at what happens when a TCP connection finishes its lifecycle. Under normal conditions, tearing down a connection involves a four-way handshake (or a combined FIN/ACK sequence). One party sends a `FIN` packet to signal it has finished sending data, and the other responds with an `ACK`. 

Problems begin when a socket enters the `FIN_WAIT_2` state. In this state, one side has sent its `FIN` and received an acknowledgment, but it is still waiting for the *remote* side to send its own `FIN` packet to officially close the connection from that direction. 

```
Client (Envoy)                   Server (GKE API)
      |                                 |
      | ----------- FIN --------------> |
      | <---------- ACK --------------- |  (Enters FIN_WAIT_2)
      |                                 |
      |     (Packet reordered/lost)     |
      | <---------- FIN --------------- |  <-- Lost or reordered!
      |                                 |
```

Normally, a kernel implements a timeout (controlled by `net.ipv4.tcp_fin_timeout`) for `FIN_WAIT_2` so that a stranded socket doesn't hang around forever if the peer vanishes. However, under specific circumstances involving half-closed connections, things can go awry. 

During the investigation of the GKE API timeouts, packet captures revealed a baffling pattern: the control plane was responding to brand-new TCP connection requests with stale `ACK` packets. These weren't acknowledgments for the new handshake; they were ghost packets belonging to previously closed connections whose identifiers (ports and sequence numbers) had been recycled too quickly or mismanaged by the local stack. 

When a socket remains indefinitely stuck in `FIN_WAIT_2` instead of timing out or cleaning up, the local system's available ephemeral port and socket connection tables slowly exhaust. New connection requests from clients trying to talk to the Kubernetes API server are met with confusing, out-of-order acknowledgments or rejected outright. The API server appears intermittently dead, not because it is crashing or overloaded, but because its network stack is choking on zombie sockets that refuse to die.

## The Trifecta of Triggers: PSC, Envoy, and the Kernel

Transient production bugs of this magnitude are rarely caused by a single line of faulty code. Instead, they require a precise alignment of behaviors across completely different architectural boundaries. In this GKE scenario, the failure was triggered by the convergence of three distinct components:

| Component | Role in the Failure |
| :--- | :--- |
| **Private Service Connect (PSC)** | Introduced micro-delays and packet reordering characteristics across virtual network interfaces. |
| **Envoy Proxy** | Utilized advanced half-close connection handling, keeping sockets open longer in specific states. |
| **Linux Kernel** | Contained a logic flaw that caused it to discard specific reordered `FIN` packets, trapping the socket. |

### 1. Private Service Connect (PSC)
Google Cloud's Private Service Connect allows consumers to access producer services securely using internal IP addresses. In the GKE control-plane architecture, clusters connect to the Kubernetes API server via PSC, traversing virtualized network interfaces. Virtualized networking layers routinely optimize, route, and occasionally reorder packets to maximize throughput across massive multi-tenant fabrics. While generally transparent, these subtle routing paths can introduce minute packet reordering characteristics that standard TCP stacks are designed to handle—most of the time.

### 2. Envoy Proxy
Envoy is the ubiquitous edge and service mesh proxy used across modern cloud-native infrastructures. Envoy makes heavy use of TCP's "half-close" feature, allowing one side of a connection to stop sending data while continuing to listen for incoming data from the backend. This pattern is entirely compliant with the RFCs and helps optimize proxy resource utilization. However, it means Envoy frequently leaves connections lingering in states where it expects explicit termination signals from both ends.

### 3. The Linux Kernel TCP Bug
Here is where the three forces collided. When PSC slightly reordered packets during a connection teardown, an incoming `FIN` packet arrived at the destination host *before* an expected preceding packet. Because of a specific logic bug in the Linux kernel's TCP implementation, the networking stack mishandled this reordered `FIN`. Instead of queuing it or processing it correctly once the sequence gap was filled, the kernel effectively dropped or ignored the packet's intent to close. 

Envoy was waiting for a clean close, PSC had shuffled the delivery order, and the Linux kernel silently dropped the signal. The result? The kernel forgot how to say goodbye, leaving the socket stranded indefinitely in `FIN_WAIT_2`.

## Deep Dive: From Packet Captures to Kernel Patching

Debugging an issue that only surfaces intermittently under high-throughput production load requires moving past standard application logs. Engineers had to capture telemetry at the wire level and trace how individual packet sequences traversed the operating system.

By deploying advanced network tracing and capturing traffic at both the client proxy boundary and the Kubernetes control-plane ingress, the diagnostic team isolated the exact sequence of events. They noticed that connections hitting the API endpoint would occasionally experience a micro-burst of packet reordering. Following that reordering, the kernel state machine would fail to transition the socket out of `FIN_WAIT_2`, even after the system's internal cleanup timers should have stepped in.

The root cause was tracked down to a flaw in how the Linux kernel's TCP layer processed out-of-order `FIN` flags. When a `FIN` arrived out of sequence, the state update logic failed to properly account for the flags attached to the segment under specific queuing conditions. 

The fix required a precise surgical strike on the kernel's TCP state machine logic. The patch was authored by kernel networking maintainer Eric Dumazet. 

```c
/* Conceptual representation of the TCP state fix area */
if (tp->nonagle & TCP_NAGLE_OFF) {
    // Correcting how out-of-order FIN flags are processed 
    // to prevent sockets from hanging in FIN_WAIT_2
    tcp_fin(sk);
}
```

*Note: This is a conceptual illustration of the logic area; actual kernel patches involve intricate adjustments to sequence validation and queue management in `net/ipv4/tcp_input.c`.*

Once merged upstream into Linux version `6.9.7`, the fix was quickly recognized as critical for enterprise cloud infrastructure. Maintaining stability across managed Kubernetes services means these upstream fixes cannot stay trapped in bleeding-edge kernel releases. The patch was subsequently backported to the `6.6` and `6.1` Long-Term Support (LTS) kernel branches, ensuring that cloud providers and enterprise distributions could adopt the fix without upgrading their entire kernel ecosystem.

## Broader Implications for Cloud-Native Infrastructure

Incidents like this highlight a sobering reality of modern cloud-native engineering: **the hidden fragility of stacked, multi-tenant architectures.** 

When we deploy applications to Kubernetes, we abstract away an immense amount of complexity. We rely on virtual private clouds, managed load balancers, sidecar proxies, container runtimes, and the underlying host kernel. Each of these layers is engineered by different teams, written in different languages, and optimized for different goals. 

Crucially, every component in this GKE failure chain was behaving *correctly* according to its own specification:
- PSC was routing packets efficiently across a massive virtualized network.
- Envoy was utilizing standard half-close behaviors to manage proxy connections.
- The Linux kernel was executing its TCP state machine (albeit with a subtle logic bug under pressure).

It was only at the intersection of these fully compliant, isolated software behaviors that a cascading failure materialized. For platform engineers and Site Reliability Engineers, this underscores why deep systems literacy remains vital. When your control plane starts timing out, you cannot simply look at your Kubernetes deployment manifests. You have to understand how container networks interact with host sysctls, how load balancers handle idle timeouts, and how kernel versions manage TCP connection teardowns. 

Similar architectural interdependencies often pop up when scaling distributed networking layers, such as when maintaining zero-downtime traffic flows during service mesh federation or when integrating advanced proxy routing logic across multi-cluster environments (as explored in discussions on [GKE and Linkerd federation architecture](/tech/2026/07/27/gke-linkerd-federation-zero-downtime.html)).

## Future Outlook: Kernel Maintenance and Advanced Telemetry

As cloud providers push the boundaries of scale, performance, and multi-tenancy, our reliance on the foundational layers of the Linux operating system only deepens. This incident offers a clear glimpse into where platform engineering is heading.

First, it highlights our critical dependency on rigorous upstream Linux kernel maintenance and rapid backporting pipelines. Managed Kubernetes services like GKE abstract the infrastructure, but they cannot abstract away physics or kernel bugs. The speed at which maintainers like Eric Dumazet can diagnose, patch, and backport fixes to LTS kernels is the invisible safety net holding up the modern cloud.

Second, it points to a rising necessity for deterministic, unified telemetry across proxy and kernel boundaries. Traditional monitoring tells you *that* the API is timing out. Advanced observability platforms must soon bridge the gap between application-level metrics (like Envoy connection pools) and systems-level telemetry (like kernel socket states and TCP queue drops). 

For platform engineering teams, the takeaway is clear: the stack is getting deeper, and our debugging tools must evolve with it. Cultivating internal expertise in Linux systems, packet analysis, and kernel behavior is no longer just a nice-to-have skill for systems programmers—it is a core requirement for keeping distributed, cloud-native infrastructure resilient.
{% endraw %}

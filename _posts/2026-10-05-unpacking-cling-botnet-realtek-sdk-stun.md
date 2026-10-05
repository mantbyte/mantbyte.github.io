---
layout: post
title: 'Unpacking the Cling Botnet: How Realtek Jungle SDK Exploits Abuse STUN for
  Stealthy C2'
date: 2026-10-05 19:48:13 +0530
categories: Tech
excerpt: Discover how the Cling botnet leverages Realtek SDK vulnerabilities and abuses
  STUN protocols to establish stealthy C2 channels.
cover_image: /assets/images/posts/unpacking-cling-botnet-realtek-sdk-stun-cover.png
cover_caption: A conceptual digital illustration of a stealthy IoT botnet exploiting
  a router network architecture.
---

{% raw %}
The IoT threat landscape has entered an era of quiet efficiency. Where older botnets relied on deafening volume—scanning subnets with brute-force dictionary attacks and communicating over easily flagged, hardcoded IP addresses—modern campaigns prioritize blending in. A striking example of this philosophy is the Cling botnet. Rather than inventing novel communication channels or deploying noisy, custom protocols, Cling co-opts the very infrastructure of the internet, weaponizing standard network utilities to establish command-and-control (C2) channels that look virtually indistinguishable from routine application traffic.

At the core of this campaign is a clever abuse of the Session Traversal Utilities for NAT (STUN) protocol. By masquerading its C2 infrastructure behind the identity of legitimate Google STUN servers, Cling manages to hide in plain sight. Understanding how this botnet moves from an initial remote code execution flaw in embedded software to a deeply entrenched, protocol-abusing node offers a valuable masterclass in modern IoT attack mechanics.

## Anatomy of the Entry Point: Exploiting Realtek Jungle SDK (CVE-2021-35394)

Every botnet needs a vector to breach the perimeter, and Cling relies on a familiar, highly effective flaw: CVE-2021-35394. Carrying a maximum CVSS score of 9.8, this critical remote code execution (RCE) vulnerability resides within the Realtek Jungle SDK, a software development kit used widely across routers, gateways, and various edge networking hardware from multiple vendors. 

The vulnerability stems from improper input handling in several components of the SDK, commonly manifesting in services that process external data without sufficient sanitization. When exposed to the WAN interface—often due to misconfigurations or unpatched upstream firmware—attackers can send crafted HTTP requests or manipulate protocol parsers to execute arbitrary shell commands with root privileges. 

| Vulnerability Metric | Detail |
| :--- | :--- |
| **CVE Identifier** | CVE-2021-35394 |
| **Component** | Realtek Jungle SDK |
| **Severity** | Critical (CVSS 9.8) |
| **Attack Vector** | Network (Remote Code Execution) |
| **Privileges Required** | None |

Because the Realtek Jungle SDK underpins a massive footprint of consumer and small-office/home-office (SOHO) routers, the potential attack surface is vast. Once threat actors successfully trigger CVE-2021-35394, they have unrestricted execution rights on the underlying embedded operating system, usually a stripped-down Linux distribution running BusyBox utilities. From here, the malware wastes no time securing its foothold.

## Payload Execution and Persistence: Inside the Cling Lifecycle

Gaining execution is only the first step; maintaining stability and persistence on resource-constrained embedded systems requires deliberate engineering. Once the initial dropper executes via the SDK exploit, the Cling malware initializes its local environment through a structured routine designed to avoid resource contention and evade casual administrative checks.

### Single-Instance Enforcement

Embedded devices often run hot, and multiple instances of a heavy binary can quickly crash a router or attract the attention of a watchdog timer. Cling enforces single-instance execution by binding a local socket to a specific port—**33957**—using the `SO_REUSEADDR` socket option:

```c
// Conceptual representation of Cling's single-instance check
int sock = socket(AF_INET, SOCK_STREAM, 0);
int optval = 1;
setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval));

struct sockaddr_in addr;
addr.sin_family = AF_INET;
addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
addr.sin_port = htons(33957);

if (bind(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
    // Another instance is already running; exit gracefully
    exit(0);
}
```

By attempting to bind to port 33957, the malware ensures that if it is reinfected by a competing campaign or a duplicate execution script, subsequent instances terminate immediately, keeping a low operational profile.

### Filesystem Footprint and Persistence

After establishing its exclusive lock, Cling copies its binary payload into discrete locations across the filesystem to survive basic reboots and obscure its origin:
- `/root/.cling`
- `/usr/local/bin/.cling`

To ensure survival across device reboots, the malware hooks into the system's initialization sequence. It modifies standard SysV init scripts, embedding hooks that execute the `.cling` binary during system startup. 

In some deployment variants, attackers employ an even cleverer persistence vector: replacing the system's legitimate `wget` binary with a malicious wrapper or link. Whenever a legitimate administrative script or cron job invokes `wget` to pull updates or check connectivity, it inadvertently triggers the Cling execution lifecycle instead.

## Stealthy Command and Control: Weaponizing STUN for C2

The most sophisticated aspect of the Cling botnet is its choice of C2 communication channel. Traditional botnets connect to hardcoded IP addresses over custom TCP or UDP ports, making them sitting ducks for network intrusion detection systems (IDS) and firewall blocklists. Cling avoids this entirely by leveraging "Living-Off-The-Protocol" techniques, specifically targeting STUN.

### Understanding STUN in Normal Operations

Session Traversal Utilities for NAT (STUN), defined in RFC 5389, is a lightweight protocol used by VoIP applications, gaming consoles, and WebRTC clients to discover their public-facing IP address and port mapping behind a Network Address Translator (NAT). 

In a normal transaction, a client sends a STUN Binding Request to a public STUN server (such as Google’s widely used public infrastructure):

```
[Client Device] -- (STUN Binding Request) --> [STUN Server: stun.l.google.com]
[Client Device] <-- (STUN Binding Response) -- [STUN Server: stun.l.google.com]
```

Because NAT traversal traffic is ubiquitous, enterprise firewalls and home routers permit outbound STUN traffic (typically over UDP port 3478) without a second thought. 

### Mimicking Google Infrastructure

Cling weaponizes this exact behavior. Instead of communicating with an obvious malicious domain, the malware formats its C2 traffic to look like standard STUN binding requests and responses. More alarmingly, analysis of network telemetry reveals that C2 command packets in Cling campaigns have appeared to originate from **`74.125.250.129`**—an IP address legitimately belonging to Google's public STUN infrastructure (`stun.l.google.com`).

By crafting packets that mimic legitimate responses from Google's servers, or by manipulating STUN transaction IDs to encode command payloads, the malware achieves several defensive evasion goals:
- **Firewall Bypass:** Traffic matches standard NAT traversal signatures, bypassing deep packet inspection (DPI) rules that look for unknown or proprietary C2 protocols.
- **Log Noise:** Network administrators reviewing firewall logs see routine communication with a trusted global tech giant, masking malicious data transfer.
- **Payload Smuggling:** Commands and operational directives are embedded directly within the attribute fields of the STUN packets, blending seamlessly with normal network metadata.

## Operational Impact: Proxying, Tunneling, and DDoS Capabilities

Once a device is successfully compromised, locked to port 33957, and checking in via weaponized STUN channels, it is fully enrolled in the botnet. Threat actors leverage these embedded nodes for a variety of malicious operational objectives.

### Worm-like Propagation

Armed with root access via CVE-2021-35394, infected routers do not just sit idle. They often act as staging grounds for recursive exploitation. The botnet scans local network segments and wide-area address spaces for other vulnerable Realtek SDK endpoints, automatically launching exploit payloads to expand the botnet's footprint without requiring constant manual intervention from the operator.

### TCP Tunneling and Proxying

Residential and small-business IP addresses are valuable commodities for cybercriminals. Cling equips infected routers with TCP tunneling and proxying utilities. This turns the compromised SOHO device into an anonymous proxy relay, allowing threat actors to route malicious traffic—such as credential stuffing, web scraping, and secondary attacks—through the unsuspecting victim's residential IP address, effectively laundering their origin.

### Distributed Denial-of-Service (DDoS)

While quieter than legacy IoT botnets that launch volumetric floods indiscriminately, Cling-infected devices retain the capability to participate in coordinated Distributed Denial-of-Service (DoS) campaigns. Because routers sit at the edge of high-bandwidth connections relative to their local subnets, marshalling thousands of compromised gateways provides an effective lever for application-layer or volumetric attacks when commanded via the covert STUN C2 channel.

## Defensive Strategies and Future Outlook

Defending against threats like Cling requires a fundamental shift in how security teams approach IoT monitoring. Traditional perimeter security—relying on static IP blacklists and signature-based antivirus rules—is fundamentally unequipped to catch malware that abuses legitimate protocols and trusted infrastructure IPs.

### Actionable Mitigation and Detection

To protect networks and detect sophisticated protocol abuse, defenders should implement the following hardening measures:

- **Firmware Patching and Asset Management:** Immediately apply vendor patches for CVE-2021-35394. If patches are unavailable from the hardware vendor, restrict administrative access to local interfaces and disable remote WAN management entirely.
- **Inspect STUN Traffic Anomalies:** Security operations centers (SOCs) and network administrators should audit outbound STUN traffic. While blocking STUN entirely can break VoIP and conferencing apps, monitoring for unusual payload sizes, high frequency, or anomalous transaction ID structures within STUN packets can reveal C2 activity.
- **File Integrity Monitoring (FIM):** On devices where root access is available, monitor critical directories (`/root/`, `/usr/local/bin/`) and system binaries like `wget` for unauthorized modifications or hidden files (`.cling`).
- **Network Segmentation:** Isolate IoT and SOHO networking gear from sensitive internal corporate resources. A compromised router should not have a clear path to internal file servers or administrative VLANs.

```
+-------------------------------------------------------+
|                Recommended Defense Stack              |
+-------------------------------------------------------+
|  1. Patch CVE-2021-35394 (Realtek Jungle SDK)         |
|  2. Restrict WAN management interfaces                |
|  3. Monitor STUN transaction IDs & payload anomalies   |
|  4. Enforce strict IoT network segmentation           |
+-------------------------------------------------------+
```

### The Future of Living-Off-The-Protocol Threats

The emergence of the Cling botnet signals an industry-wide maturation of IoT threat actor tactics. As perimeter defenses and automated endpoint detection tools grow more sophisticated, malware authors are abandoning noisy, custom protocols in favor of "living-off-the-protocol" techniques. 

We can expect future IoT malware variants to increasingly weaponize standard network utilities—such as STUN, TURN, ICE, and even standard DNS or HTTPS tunneling—making differentiation between benign application behavior and malicious C2 an escalating challenge. For security vendors and enterprise defenders, the path forward demands advanced behavioral analysis engines capable of inspecting protocol semantics rather than just inspecting port numbers and destination IPs.
{% endraw %}

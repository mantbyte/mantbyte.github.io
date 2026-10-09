---
layout: post
title: 'FBI vs. Raptor Train: Deconstructing the Disruption of Flax Typhoon’s Global
  Botnet'
date: 2026-10-09 15:55:28 +0530
categories: Geopolitics
excerpt: The FBI's active defense operation against the Raptor Train botnet marks
  a turning point in state-sponsored cyber warfare. Explore the technical architecture
  of this 200,000-device network.
cover_image: /assets/images/posts/fbi-raptor-train-flax-typhoon-botnet-cover.png
cover_caption: A visualization of a global network of compromised SOHO routers and
  IoT devices.
---

{% raw %}
For years, the perimeter of enterprise security was thought to be the corporate firewall. However, as remote work became the norm and the Internet of Things (IoT) exploded, the actual "edge" of the network shifted to the living rooms of employees and the utility closets of small businesses. This shift created a massive, poorly defended attack surface. In late 2024, the technical community witnessed the culmination of this vulnerability: the "Raptor Train" botnet.

Operated by the PRC-linked threat actor known as Flax Typhoon (or RedJuliett), Raptor Train was not a typical script-kiddie DDoS botnet. It was a sophisticated, multi-tier infrastructure consisting of over 200,000 compromised Small Office/Home Office (SOHO) routers, IP cameras, and Network Attached Storage (NAS) devices. Its purpose was not just disruption, but long-term persistence and stealthy relaying of traffic to target critical infrastructure in Taiwan and the United States. The FBI’s subsequent court-authorized "active defense" operation to dismantle this network marks a pivotal moment in how law enforcement handles large-scale state-sponsored cyber threats.

## Anatomy of the Raptor Train: Multi-Tier C2 Architecture

To understand why Raptor Train was so difficult to detect, we must look at its hierarchical Command and Control (C2) structure. Unlike simpler botnets that connect directly to a single master server, Flax Typhoon utilized a three-tier system designed for maximum operational security (OPSEC) and obfuscation.

### Tier 1: The Compromised Edge
The first tier consisted of the "bots"—the 200,000+ infected SOHO devices. These were primarily consumer-grade routers (Zyxel, Buffalo, ASUS), IP cameras, and NVRs (Network Video Recorders). These devices served as the initial entry point and the final hop for malicious traffic. By routing attacks through a residential IP address, Flax Typhoon could bypass geo-fencing and IP reputation filters that would normally block traffic coming from known Chinese data centers.

### Tier 2: The Proxy Layer
Traffic from Tier 1 did not go straight to the attackers. Instead, it was routed through a second tier of proxy nodes. These nodes were often more robust compromised servers or specifically leased infrastructure. Their job was to aggregate traffic from thousands of Tier 1 devices and pass it up the chain. This layer acted as a buffer; if a Tier 1 device was discovered and analyzed, it would only point to a Tier 2 proxy, not the actual heart of the operation.

### Tier 3: Management and Control
At the top of the pyramid sat the primary C2 servers. This is where the operators of Flax Typhoon issued commands, managed the botnet's growth, and exfiltrated data. To maintain persistent connections between these tiers, the group heavily relied on **SoftEther VPN**.

SoftEther is a powerful, open-source multi-protocol VPN software. Its flexibility—supporting SSL-VPN, L2TP/IPsec, and OpenVPN protocols—made it an ideal tool for the attackers. It allowed them to create stable, encrypted tunnels that could traverse NAT (Network Address Translation) and firewalls, ensuring that even if a device’s IP address changed, the "train" stayed on the tracks.

| Tier | Component | Primary Function |
| :--- | :--- | :--- |
| **Tier 1** | SOHO/IoT Devices | Traffic relay, obfuscation of origin, initial foothold. |
| **Tier 2** | Proxy Nodes | Aggregation of bot traffic, OPSEC buffer. |
| **Tier 3** | C2 Masters | Centralized command, payload delivery, data exfiltration. |

## The Vulnerability Chain: Exploiting the Edge

The rapid expansion of Raptor Train to 200,000 nodes was not an accident; it was the result of a systematic exploitation of known vulnerabilities in edge devices. Flax Typhoon targeted "low-hanging fruit"—devices that are frequently connected to the internet with default configurations or unpatched firmware.

### CVE-2023-28771: The Zyxel Catalyst
One of the most significant entry points was **CVE-2023-28771**, a critical vulnerability in the IKEv2 implementation of several Zyxel firewalls and routers. This flaw allowed for remote code execution (RCE) by sending a specially crafted packet to the device. Because the exploit occurred at the network layer before authentication, it was highly effective for mass exploitation.

### CVE-2023-49103 and CVE-2021-20090
The group also targeted **OwnCloud** (CVE-2023-49103), a popular file-sharing solution often hosted on NAS devices. By exploiting an information disclosure vulnerability, attackers could gain environment variables including administrative credentials. Similarly, **Buffalo routers** were targeted using **CVE-2021-20090**, a path traversal vulnerability that allowed attackers to bypass authentication and gain control of the device.

The "soft underbelly" of critical infrastructure isn't always the high-end industrial control system; often, it is the $80 router used by a contractor to access the network remotely. These devices lack the robust logging and endpoint detection and response (EDR) capabilities found in enterprise hardware, making them perfect "ghost" nodes for state-sponsored actors.

## Living-off-the-Land: The Flax Typhoon Toolkit

Once Flax Typhoon gained access to a device or a connected network, they moved away from custom malware and toward a philosophy known as **Living-off-the-Land (LotL)**. This technique involves using legitimate, pre-installed system tools to carry out malicious activities, making detection by traditional antivirus software nearly impossible.

### Persistence via China Chopper
For initial persistence on web-facing servers, the group frequently deployed the **China Chopper Web Shell**. This is a tiny, 4KB script that provides a powerful remote terminal. Because of its size and the fact that it can be embedded in existing legitimate files, it is incredibly difficult to find during a manual audit.

### Lateral Movement and Credential Harvesting
Once inside a target network, Flax Typhoon utilized several well-known tools:

*   **Mimikatz:** Used for harvesting passwords, hashes, and PINs from memory. This allowed the actors to escalate privileges quickly.
*   **PowerShell & WinRM:** By using Windows' own management frameworks, the attackers could execute commands across the network without ever dropping a malicious binary to the disk.
*   **Task Scheduler:** Used to ensure that their scripts and proxies would restart automatically upon system reboot.

By minimizing their digital footprint and using tools that system administrators use every day, Flax Typhoon could remain inside a network for months or even years without triggering an alert. This "hiding in plain sight" strategy is a hallmark of PRC-linked APT (Advanced Persistent Threat) groups.

```powershell
# Example of a typical LotL command to gather system info silently
Get-WmiObject Win32_OperatingSystem | Select-Object Caption, OSArchitecture, Version | Out-File C:\Users\Public\sysinfo.txt
# This command uses legitimate WMI calls that rarely trigger security alerts.
```

## The FBI Operation: Legal and Technical Precedents

In a departure from traditional "observe and report" tactics, the FBI obtained court authorization to take an active role in disrupting the Raptor Train. This operation was not just about seizing servers; it involved interacting directly with the infected Tier 1 devices to "clean" them.

### Technical Execution of the Takedown
The FBI's operation involved sending commands to the compromised devices through the hijacked C2 infrastructure. These commands were designed to:
1.  **Uninstall the malware:** Specifically, the custom binaries used to maintain the botnet connection.
2.  **Close backdoors:** Disabling the unauthorized SoftEther VPN instances and web shells.
3.  **Prevent Re-infection:** In some cases, the operation involved temporary measures to block the specific ports used by the C2 servers.

This process is technically delicate. Law enforcement must ensure that the "cleaning" command does not brick the device or disrupt the legitimate internet traffic of the innocent home user or small business. It is a form of "surgical" intervention in the digital space.

### Legal Framework
The operation relied on **Rule 41 of the Federal Rules of Criminal Procedure**, which was amended in 2016 to allow judges to issue warrants for remote electronic searches and seizures when the location of the devices is unknown or spread across multiple districts. This legal evolution was essential for tackling a botnet of 200,000 nodes scattered globally.

This action mirrors the 2022 disruption of the **Cyclops Blink** botnet (linked to Russia's Sandworm), but the scale of Raptor Train was significantly larger. It signals a shift toward an "active defense" posture, where the goal is to impose costs on the adversary by forcing them to rebuild their entire infrastructure from scratch.

## Strategic Implications for Critical Infrastructure

The existence of Raptor Train was not a theoretical exercise; it was a loaded weapon aimed at critical infrastructure. By controlling a massive fleet of SOHO devices, Flax Typhoon could launch coordinated attacks on sectors defined by the **Purdue Model** of industrial control systems.

The Purdue Model segments an enterprise into layers, from the physical process (Layer 0) up to the corporate network (Layer 4/5). A compromised router in a SOHO environment often sits at the intersection of these layers, especially in utility companies where remote monitoring is common. As we have seen in recent reports on [US water infrastructure vulnerabilities](/geopolitics/2026/08/15/us-water-cyberwarfare-purdue-model-breach.html), the breach of a single edge device can lead to unauthorized access to Programmable Logic Controllers (PLCs) that manage water pressure or chemical levels.

Furthermore, the targeting of Taiwanese infrastructure highlights the geopolitical weight of these botnets. By maintaining a persistent presence in the networks of transport, energy, and communication providers, Flax Typhoon ensures that the PRC has "pre-positioned" capabilities to cause chaos during a potential conflict. The risk is not just data theft; it is the potential for kinetic impact through cyber means.

In high-stakes environments, the lesson is clear: reliance on software-defined security is insufficient. The need for [physical isolation and zero-trust architectures](/geopolitics/2026/08/20/t-mobile-salt-typhoon-physical-isolation.html) has never been more urgent. As we evaluate the [maritime and energy risks in Europe](/geopolitics/2026/08/12/gerbera-threat-maritime-risks-european-energy.html), the pattern of targeting edge infrastructure to gain a foothold in critical sectors remains a consistent theme among state actors.

## Future Outlook: The Evolution of State-Sponsored Botnets

The disruption of Raptor Train is a major victory, but it is a temporary one. Threat actors like Flax Typhoon are resilient and well-funded. We can expect their tactics to evolve in several key ways:

1.  **Encrypted and Decentralized C2:** Future botnets will likely move away from centralized Tier 3 servers in favor of peer-to-peer (P2P) architectures or highly encrypted C2 channels that use legitimate cloud services (like AWS or Azure) as fronting mechanisms.
2.  **Mandatory Firmware Standards:** There is a growing push for governments to mandate security standards for SOHO routers. This includes "secure by design" principles, such as disabling UPnP by default, enforcing strong passwords, and providing automated, signed firmware updates.
3.  **AI-Driven Anomaly Detection:** For defenders, the next frontier is using machine learning to identify the subtle traffic patterns associated with botnet relays. Even if the traffic is encrypted, the timing and volume of packets can reveal the presence of a proxy node.

The "Raptor Train" saga serves as a wake-up call for the cybersecurity industry. It demonstrates that the security of a global corporation or a national power grid is only as strong as the most neglected router on its periphery. As law enforcement adopts more aggressive disruption tactics, the battle for the "edge" will only intensify, requiring a coordinated effort between hardware manufacturers, software developers, and policy makers to secure the foundations of our connected world.
{% endraw %}

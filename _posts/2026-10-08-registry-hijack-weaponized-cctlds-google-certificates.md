---
layout: post
title: 'Anatomy of a Registry Hijack: How Attackers Weaponized .gh, .sl, and .as for
  Google Certificates'
date: 2026-10-08 06:23:12 +0530
categories: Tech
excerpt: Attackers bypassed traditional perimeter security by compromising ccTLD registries
  to trick automated certificate authorities into issuing valid Google certificates.
cover_image: /assets/images/posts/registry-hijack-weaponized-cctlds-google-certificates-cover.png
cover_caption: Visual diagram of the DNS registry hijack vector targeting automated
  certificate authorities.
---

{% raw %}
Security incidents usually conjure images of phishing campaigns, zero-day memory corruption bugs, or compromised corporate credentials. When attackers target tech giants like Google, we naturally assume sophisticated enterprise endpoint infiltration or internal network lateral movement. But in late September 2026, a series of attacks bypassed traditional perimeter defense entirely. Instead of hacking Google, the attackers went straight to the infrastructure roots: country-code top-level domain (ccTLD) registries.

By compromising the registries for Ghana (`.gh`), Sierra Leone (`.sl`), and American Samoa (`.as`), malicious actors manipulated authoritative DNS records at the highest levels. This gave them the power to trick automated certificate authorities into issuing valid, trusted HTTPS certificates for major Google and YouTube properties. No enterprise firewalls were breached. No administrator credentials were stolen at Google. The trust chain itself was weaponized from the outside in.

## The Attack Vector: Compromising ccTLD Infrastructure

To understand how this attack worked, we need to look at how the Domain Name System is structured. At the apex of the DNS hierarchy sit root zones and top-level domain (TLD) registries. Below TLDs are second-level domains (like `.com.gh` or `.com.as`), followed by subdomains. 

Normally, securing a domain involves logging into a domain registrar (like Namecheap, GoDaddy, or Route 53) and updating your DNS records. However, compromising a ccTLD registry completely bypasses standard registrar security. 

> "A registry-level compromise doesn't target a single house on the street; it captures the master blueprint office of the entire neighborhood."

When attackers seized control of the `.gh`, `.sl`, and `.as` registries, they gained the ability to modify authoritative DNS pointers and glue records for any domain registered under those extensions. If an organization owned a regional Google property sitting on one of these ccTLDs, the registry operators had the ultimate authority to dictate where validation queries would land.

To the rest of the internet, whatever nameserver the hijacked registry pointed to *was* the source of truth.

## Automated CAs and the ACME Validation Vulnerability

With full control over the authoritative DNS records for the targeted domains, the attackers set their sights on obtaining valid HTTPS certificates. Between September 22 and 27, 2026, they targeted automated Certificate Authorities (CAs), specifically Let's Encrypt and ZeroSSL.

Modern CAs rely heavily on the Automated Certificate Management Environment (ACME) protocol to issue Domain-Validated (DV) certificates at scale. The mechanics of a standard DNS-01 or HTTP-01 ACME challenge are straightforward:

```
+-------------------+      1. Request Cert      +-------------------+
|                   | ------------------------> |                   |
|  Attacker/Client  |                           |     Let's Encrypt |
|                   | <------------------------ |       / ZeroSSL   |
+-------------------+      2. ACME Challenge    +-------------------+
                                     |
                                     | 3. Query DNS
                                     v
                           +-------------------+
                           | Hijacked ccTLD    |
                           | Registry / NS     |
                           +-------------------+
```

1. **The Request:** The client requests a certificate for a specific domain name.
2. **The Challenge:** The CA issues a challenge (e.g., placing a specific token in a DNS TXT record).
3. **The Validation:** The CA queries the global DNS system to verify the challenge token.

Because the attackers had already compromised the `.gh`, `.sl`, and `.as` registries, they altered the DNS records to point the validation queries directly to servers under their control. When Let's Encrypt and ZeroSSL checked the domain ownership via the ACME protocol, the hijacked nameservers dutifully responded with the correct validation tokens. 

The CAs, acting precisely as designed, trusted the current authoritative DNS state. They had no way of knowing that the authoritative servers had been subverted at the registry level. Consequently, Let's Encrypt issued 11 unauthorized certificates, and ZeroSSL issued 1, giving the attackers cryptographically valid TLS credentials for major Google and YouTube properties operating under those ccTLDs.

| Certificate Authority | Unauthorized Certificates Issued | Validation Protocol |
| :--- | :--- | :--- |
| **Let's Encrypt** | 11 | ACME (DNS-01 / HTTP-01) |
| **ZeroSSL** | 1 | ACME (DNS-01 / HTTP-01) |
| **Traditional CAs** | 0 | Manual/Automated Enterprise Checks |

## Detection, Mitigation, and the Chrome CRLSet Response

The saving grace of the modern public key infrastructure (PKI) is transparency. Every certificate issued by a trusted public CA must be logged in publicly accessible Certificate Transparency (CT) logs. These append-only cryptographic ledgers allow security researchers, domain owners, and automated monitors to audit every single certificate issued globally in real-time.

As soon as the unauthorized certificates for Google and YouTube properties hit the CT logs, monitoring systems flagged the anomalous issuances. Google security teams mobilized immediately, coordinating with Let's Encrypt and ZeroSSL to revoke the fraudulent certs.

Concurrently, browser vendors deployed emergency mitigations. Google rolled out updates via Chrome CRLSets—a mechanism that pushes rapid, out-of-band certificate revocation lists directly to browser instances without requiring a full browser software update. 

| Defense Layer | Response Action | Speed / Mechanism |
| :--- | :--- | :--- |
| **Certificate Transparency** | Detected anomalous issuances in public logs | Real-time monitoring |
| **CA Coordination** | Revoked the 12 unauthorized certificates | Immediate manual/automated revocation |
| **Chrome CRLSets** | Blocked rogue certificates client-side | Out-of-band browser push |

Thanks to CT logs and rapid browser-level enforcement, the window for potential Man-in-the-Middle (MitM) attacks was severely constrained, neutralizing the operational utility of the stolen certificates before widespread exploitation could occur.

## Defensive Architecture: Securing DNS and Certificate Issuance

While the 2026 incident targeted registry operators—entities outside the direct control of enterprise IT departments—engineers and system administrators can implement several architectural layers to harden their domains against DNS-based certificate hijack attempts.

### 1. Enforce Strict CAA Records
Certification Authority Authorization (CAA) DNS records allow domain owners to declare which CAs are explicitly authorized to issue certificates for their domains. If a domain has a strict CAA record pointing *only* to a trusted corporate CA, automated public CAs like Let's Encrypt or ZeroSSL are programmatically required to reject certificate requests from unauthorized third parties—even if those parties control the DNS records.

```text
example.com. IN CAA 0 issue "pki.enterprise.internal"
example.com. IN CAA 0 issuewild ";"
```

*Note: While a total registry compromise can theoretically allow attackers to modify CAA records as well, combining CAA with DNSSEC creates formidable friction.*

### 2. Implement DNSSEC
Domain Name System Security Extensions (DNSSEC) cryptographically signs DNS records using public-key cryptography. When implemented correctly from the root down to the authoritative name server, DNSSEC ensures that responses received by resolvers have not been tampered with in transit. While a full registry compromise allows attackers to manipulate the signed zone if they capture the private signing keys of the registry, robust monitoring of DS (Delegation Signer) records at the parent zone can expose unauthorized changes instantly.

### 3. Registry-Level Operational Security
For organizations managing or closely partnering with ccTLD registries, the incident underscores the urgent need for enterprise-grade hygiene at the registry level:
* **Multi-Factor Authentication (MFA):** Mandating hardware-token MFA for all registry operator administrative interfaces.
* **Registry Locks:** Implementing registry-lock protocols that require out-of-band verification (such as phone calls or physical paperwork) for any changes to nameservers or glue records.
* **Comprehensive Audit Logging:** Immutable, real-time logging of all administrative actions taken on registry infrastructure.

## Future Outlook: Shrinking Validation Reuse Windows

The fundamental vulnerability exploited in the `.gh`, `.sl`, and `.as` incident was the long lifespan of domain validations. Historically, once a CA validated that a client controlled a domain, that validation could be reused for up to 398 days. If an attacker could temporarily hijack DNS for a brief window, they could cache that validation state and request certificates at their leisure.

The industry is aggressively closing this window. Under evolving CA/Browser Forum guidelines, domain validation reuse windows are shrinking rapidly:

* **March 2027:** The maximum reuse window drops to **100 days**.
* **March 2029:** The reuse window drops further to just **10 days**.

At the same time, automated CAs are pushing boundaries independently. Let's Encrypt and other leading PKI operators are exploring aggressive reduction targets—such as shortening validation validity windows to as little as **7 hours by 2028**.

```
[Historical: 398 Days] ---> [March 2027: 100 Days] ---> [March 2029: 10 Days] ---> [2028 Target: 7 Hours]
```

### What This Means for Security Practitioners
Shorter validation reuse windows fundamentally alter the economics of DNS and registry hijacking. A temporary, fleeting compromise of a ccTLD registry or authoritative nameserver will no longer provide a multi-month window for attackers to harvest certificates. If validation expires within hours, an attacker must maintain continuous, undetected control over the DNS infrastructure throughout the entire lifecycle of the certificate request—making stealthy, short-term attacks exceedingly difficult to pull off.

As infrastructure providers and browser vendors continue to tighten trust loops, attacks relying on transient infrastructure manipulation will face diminishing returns. The lesson from the September 2026 incident is clear: securing the endpoints is no longer enough; the entire cryptographic and DNS supply chain must be locked down from root to leaf.
{% endraw %}

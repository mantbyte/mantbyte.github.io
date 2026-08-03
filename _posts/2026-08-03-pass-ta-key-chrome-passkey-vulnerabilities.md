---
layout: post
title: 'Pass-ta-key: Unmasking the Three Post-Compromise Attacks Bypassing Google
  Chrome Passkeys'
date: 2026-08-03 22:45:18 +0530
categories: Tech
excerpt: Passkeys were meant to make credential theft obsolete, but Unit 42's Pass-ta-key
  research reveals critical vulnerabilities in Google Chrome's Windows implementation.
  Here is how malware bypasses WebAuthn protections without touching the TPM.
cover_image: /assets/images/posts/pass-ta-key-chrome-passkey-vulnerabilities-cover.png
cover_caption: A digital graphic illustrating a broken cryptographic passkey shield
  over a browser interface
---

The industry-wide transition toward passwordless authentication, spearheaded by the FIDO Alliance and the WebAuthn standard, was supposed to signal the end of the credential-theft era. By replacing phishable strings of characters with hardware-bound cryptographic keys (passkeys), we promised a future where local malware could no longer simply "scrape" secrets from a browser's memory or configuration files. The assumption was simple: even if a machine is compromised, the private keys reside within the Trusted Platform Module (TPM) or a secure enclave, remaining unreachable to unauthorized software.

However, recent research by Palo Alto Networks' Unit 42 has challenged this "unhackable" narrative. Their discovery of three distinct attack paths—collectively dubbed **Pass-ta-key**—reveals that while the underlying cryptography of WebAuthn remains robust, the implementation code surrounding it is vulnerable. These attacks don't break the encryption; instead, they manipulate the logic Chrome uses to manage, sync, and verify these credentials on Windows.

By targeting the "plumbing" of the Google Password Manager rather than the vault itself, local malware can bypass biometric prompts, hijack enrollment flows, and even extract the master secrets used for end-to-end encryption. For security architects and engineers, this serves as a critical reminder that a secure protocol is only as strong as the code that executes it.

## The Foundation: Chrome's Passkey Architecture on Windows

To understand how these attacks work, we must first look at how Google Chrome handles passkeys on a Windows environment. Unlike a simple password, a passkey is a public-private key pair. On Windows, Chrome integrates deeply with the operating system's security features to protect these pairs.

### The Sync LevelDB Database
Chrome stores the metadata for your passkeys—such as the Relying Party ID (the website), the user ID, and the encrypted credential IDs—in a LevelDB database. This database, typically found in the user’s profile directory, acts as the primary ledger for the Google Password Manager. While the actual private keys are hardware-bound, the metadata is essential for Chrome to know which key to use for which website.

### Windows CNG and the TPM
For the actual cryptographic operations, Chrome utilizes the **Windows Cryptography API: Next Generation (CNG)**. When a passkey is created, Chrome asks the Windows CNG to generate a key pair. If the device has a TPM, the private key is "wrapped" by the TPM, ensuring it cannot be exported in plaintext. To use the key, a process must call the CNG API, which then interacts with the hardware.

### The Security Domain Secret (SDS)
One of the most convenient features of Google’s passkey implementation is cross-device synchronization. To enable this without giving Google access to your private keys, Chrome uses a mechanism called the **Security Domain Secret (SDS)**. 

The SDS is a 32-byte master key that facilitates end-to-end encryption for the passkey vault. When you sign into Chrome on a new device, the SDS is used to "unlock" the synchronized passkeys. As we will see later, this secret is the "Crown Jewel" for an attacker.

## Attack Path 1: Pass-ta-key and the User Verification Bypass

The first attack path, the namesake **Pass-ta-key**, targets the assertion process. When you log into a site using a passkey, the site sends a "challenge" to the browser. The browser signs this challenge using the private key and sends back an "assertion."

Normally, this process requires **User Verification (UV)**—a PIN or a biometric scan (Windows Hello). This is enforced by a specific bit in the WebAuthn assertion known as the "UV bit." If the UV bit is set to 1, the server knows the user was physically present and verified.

### The Mechanism
An attacker with local, unprivileged access can perform the following steps:
1.  **Reconnaissance:** Read the metadata from the Sync LevelDB to identify the target's passkeys and their associated `credential_id`.
2.  **API Manipulation:** Instead of going through the standard Chrome UI, the malware calls the Windows CNG API directly to sign the challenge provided by the target website.
3.  **The UV Bit Flaw:** Because the malware is running in the user's session, it can sometimes trick the system into generating a valid signature. Crucially, the researchers found that they could construct a valid WebAuthn assertion where the UV bit is manually set, even if no biometric prompt was ever shown to the user.

### Limitations
While powerful, this attack is "noisy" in terms of network traffic, as the malware must interact with the target website to get a challenge. However, it successfully achieves the primary goal: using a hardware-bound key without the user's knowledge or physical interaction.

## Attack Path 2: Silver Pass-ta-key and Deferred Enrollment

The second attack path, **Silver Pass-ta-key**, is more subtle. It exploits the "Deferred User-Verification Key Creation" logic within Chrome.

### The Enrollment Gap
When a user enables passkey sync on a new device, there is often a window of time between when the passkey metadata is downloaded and when the local hardware-bound "user-verification key" is fully bound to the TPM. Chrome allows for a "deferred" state to ensure a smooth user experience, especially if the user hasn't set up Windows Hello yet.

### The Exploitation
In a Silver Pass-ta-key attack, the malware identifies a passkey in this "deferred" state. The attacker then:
1.  Intercepts the enrollment flow.
2.  Generates their own key pair (which they control).
3.  Registers their attacker-controlled key as the "verified" key for that specific passkey entry in the Google Password Manager.

By doing this, the attacker effectively "backdoors" the passkey. The next time the user (or the attacker) attempts to use that passkey, the system accepts the attacker's key as the legitimate source of truth for user verification. This bypasses the need for the original hardware-bound secrets entirely because the attacker has inserted their own secret into the trust chain.

## Attack Path 3: Golden Pass-ta-key and the Master Secret Extraction

The final and most devastating attack is the **Golden Pass-ta-key**. If the first attack is a lockpick and the second is a backdoored key, the Golden attack is stealing the master blueprint for every lock in the house.

### Targeting the SDS
As mentioned earlier, the Security Domain Secret (SDS) is the 32-byte key used for end-to-end encryption of the passkey vault. For Chrome to function, this SDS must occasionally reside in the memory of the Chrome client process.

### Memory Scraping
The Golden Pass-ta-key attack involves:
1.  **Memory Injection/Scraping:** Malware targets the Chrome process memory. Even without administrative privileges, malware running as the user can often inspect the memory of other processes owned by the same user.
2.  **Pattern Matching:** The SDS follows specific patterns or is stored in predictable structures within Chrome's memory.
3.  **Extraction:** Once the 32-byte SDS is extracted, the attacker can decrypt the *entire* passkey vault stored in the Sync LevelDB.

> This is analogous to a "Golden Ticket" attack in Active Directory. Once you have the master secret, you no longer need to bypass individual prompts; you own the entire identity infrastructure for that user.

With the SDS, an attacker can move the encrypted LevelDB blobs to an offline machine, decrypt them, and have full access to every passkey the user has saved, across all their synchronized devices.

## Technical Deep Dive: CNG, LevelDB, and Memory Forensics

To understand the sophistication of these attacks, we need to look at the specific technical interfaces involved.

### Interfacing with Windows CNG
The malware doesn't need to implement complex crypto. It simply uses the system's own libraries. A typical flow for the malware to interact with the TPM-backed keys involves the `ncrypt.dll` library:

```cpp
// High-level pseudocode for accessing a hardware-bound key
NCRYPT_PROV_HANDLE hProv;
NCRYPT_KEY_HANDLE hKey;

// Open the storage provider (usually the Microsoft Software Key Storage Provider 
// or the Platform Crypto Provider for TPM)
NCryptOpenStorageProvider(&hProv, MS_PLATFORM_CRYPTO_PROVIDER, 0);

// Open the specific persisted key found in the LevelDB metadata
NCryptOpenPersistedKey(hProv, &hKey, L"Chrome_Passkey_Internal_Name", 0, 0);

// Sign the challenge
NCryptSignHash(hKey, NULL, pbHash, cbHash, pbSignature, cbSignature, &cbResult, 0);
```

By calling these functions, the malware leverages the OS's own permissions. If the OS doesn't strictly enforce a UI prompt at the `NCryptSignHash` level, the malware gets a valid signature for free.

### Parsing LevelDB
Chrome's LevelDB isn't a single file but a collection of `.ldb` and `.log` files. Malware can use standard LevelDB libraries to parse these files. The "blobs" of interest are usually Protobuf-encoded structures that contain the `credential_id` and the encrypted private key material. This is very similar to how modern info-stealers target session cookies, a topic explored in our analysis of [Sourtrade malware and Bun runtime assembly](/tech/2026/07/26/sourtrade-malware-bun-runtime-assembly.html).

### Identifying the SDS in Memory
The SDS isn't just floating randomly. It is often part of an `os_crypt` structure or a specific class related to "WebAuthn Credential Sync." Researchers use memory forensics to find these 32-byte sequences by looking for high-entropy strings located near known Chrome memory constants.

| Attack Component | Target | Tooling/API |
| :--- | :--- | :--- |
| **Metadata** | Sync LevelDB | `leveldb` / `Protobuf` |
| **Signatures** | TPM / Hardware Key | `ncrypt.dll` (CNG) |
| **Vault Decryption** | Security Domain Secret | Memory Scraping / `ReadProcessMemory` |
| **Persistence** | Enrollment Flow | Chrome Internal Sync Logic |

## Impact Assessment and the 'Post-Compromise' Fallacy

A common rebuttal to research like this is: *"If an attacker already has malware running on the machine, it's game over anyway."* This is known as the post-compromise fallacy, and it ignores the nuance of security engineering.

The goal of technologies like TPMs, Passkeys, and Biometrics is **Defense in Depth**. They are designed specifically to ensure that even if the primary boundary (the OS session) is breached, the most sensitive assets (the user's identity) remain protected.

### Why These Bypasses Matter
1.  **Escalation of Privilege:** Local malware is often limited in what it can do. By bypassing the TPM prompt, the malware escalates from "observing the user" to "acting as the user" on high-value targets like banking or corporate portals.
2.  **Silent Persistence:** Unlike session cookie theft, where a cookie might expire in 24 hours, a hijacked passkey or an extracted SDS provides long-term, silent access to an account.
3.  **Bypassing Multi-Factor Authentication (MFA):** Passkeys are often the *only* factor required for login. By stealing the passkey, the attacker bypasses the entire MFA stack in one go.

## Future Outlook: Hardening the Passkey Ecosystem

The discovery of Pass-ta-key is not an indictment of passkeys themselves, but a roadmap for improvement. The FIDO Alliance and browser vendors are already looking at ways to mitigate these implementation-specific flaws.

### Mandatory Hardware Attestation
One path forward is requiring **Hardware Attestation** during the re-enrollment or sync process. This would allow a relying party (the website) to verify that the key being registered was generated inside a genuine, secure TPM, and not by a piece of malware mimicking the enrollment flow.

### Improved Memory Protection
To combat the Golden Pass-ta-key attack, browser vendors are exploring **Virtualization-Based Security (VBS)** and **Enclaves**. By moving the storage and handling of the Security Domain Secret (SDS) into a separate, isolated memory space that even the main Chrome process cannot easily read, the risk of memory scraping is significantly reduced.

### The Cat-and-Mouse Game
As we move toward a passwordless world, the battlefield is shifting. Attackers are no longer looking for passwords in databases; they are looking for logic flaws in the way our browsers talk to our hardware. The Pass-ta-key research is a vital contribution to this evolution, forcing developers to look beyond the cryptographic primitives and secure the actual code that brings those primitives to life.

In the coming years, expect to see tighter integration between the browser and OS-level security features, making the "plumbing" of our digital identities as robust as the vaults they are meant to protect.

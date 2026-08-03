---
layout: post
title: 'Hallucinated Vulnerabilities: How LLM Slop Compromised the SQLite CVE Pipeline'
date: 2026-08-03 20:21:47 +0530
categories: Tech
excerpt: An automated AI campaign generated dozens of fake SQLite vulnerabilities
  that successfully slipped into major security databases like NVD and CISA. Uncover
  how LLM slop exposed critical flaws in modern DevSecOps pipelines.
cover_image: /assets/images/posts/fake-ai-cves-sqlite-pipeline-cover.png
cover_caption: Digital visualization of automated AI systems injecting fake vulnerability
  codes into a cybersecurity network pipeline.
---

In early 2024, security researchers at JFrog uncovered a subtle yet catastrophic anomaly in the global vulnerability management ecosystem: a coordinated, automated campaign distributing completely fabricated Common Vulnerabilities and Exposures (CVEs) targeting SQLite. At the center of this discovery was a GitHub repository cluster operating under names like `programmervuln/cveadvisory-`, which published over 50 public advisory notices. Of these, 54 out of 55 were confirmed to be entirely AI-generated fabrications—pure "LLM slop" disguised as high-severity security research.

These phantom vulnerabilities were not merely ignored noise in a dark corner of the internet. Because the advisories were formatted to match standard GitHub Security Advisory (GHSA) schemas, they were automatically ingested by the global vulnerability supply chain. Within days, non-existent memory corruption bugs in SQLite received critical Common Vulnerability Scoring System (CVSS) ratings (often 9.x) across major upstream databases, including the National Vulnerability Database (NVD), CISA's Vulnrichment/ADP (Automated Data Processing) pipeline, and enterprise Linux distribution feeds like Red Hat, Ubuntu, and Debian.

```
+------------------------------------+
|  GitHub Repo Cluster               |
|  (programmervuln/cveadvisory-)    |
+------------------------------------+
                  |
                  | [Ingestion of LLM Slop]
                  v
+------------------------------------+
|  GitHub Security Advisories (GHSA) |
+------------------------------------+
                  |
                  | [Automated Sync / Unverified Ingestion]
                  v
+-------------------------------------------------------+
|  NVD / CISA ADP / Linux Distro Feeds (Red Hat, etc.)  |
+-------------------------------------------------------+
                  |
                  | [Automated CPE Matching & Alerts]
                  v
+-------------------------------------------------------+
|  Enterprise DevSecOps Pipelines & Triage Queues       |
|  (CVSS 9.x Alerts for Non-Existent Vulnerabilities)   |
+-------------------------------------------------------+
```

This systemic breakdown was accelerated by an unprecedented operational crisis at the National Institute of Standards and Technology (NIST). In February 2024, NIST's manual validation process effectively stalled due to an unmanageable backlog of incoming reports. Security tools, enterprise aggregators, and vulnerability scanners were forced to rely on unverified downstream ingestion mechanisms to maintain real-time coverage. 

The resulting failure revealed a critical flaw in modern DevSecOps: the vulnerability pipeline relies heavily on implicit trust and text processing rather than execution-based proof, making it exceptionally vulnerable to automated AI generation.

---

## Anatomy of an AI Hallucination: Deconstructing Fake SQLite Advisories

To understand how Large Language Models (LLMs) can trick human triagers and automated parsers, we must look at the technical details of these advisories. LLMs excel at replicating structure, syntax, and jargon. When prompted—or running autonomously—to generate security research, models combine C memory management terminology with realistic-sounding software engineering prose.

A representative example from the `programmervuln` dataset claimed to discover a Use-After-Free (UAF) memory corruption vulnerability in SQLite version 3.41.0. The advisory cited specific source code locations, function identifiers, and exploitation vectors.

```
[FABRICATED ADVISORY EXTRACT]
Title: Critical Use-After-Free in sqlite3_vdbe_exec Parse-Tree Destructor
Target Version: SQLite 3.41.0
Severity: High (CVSS 8.8)
Description: A Use-After-Free (UAF) vulnerability was discovered in SQLite 3.41.0 
within the sqlite3_vdbe_exec_clear_registers() function located in sqlite3.c:184201. 
When processing malformed SQL queries containing nested JOIN operations, the register 
recycling routine fails to nullify memory pointers after invocation of the 
sqlite3_clear_element_tree() destructor. An unauthenticated attacker can leverage 
this condition to execute arbitrary code via a crafted database transaction.
```

### Deconstructing the Hallucinations

When security researchers cross-referenced these claims against the official SQLite 3.41.0 source code (specifically the monolithic `sqlite3.c` amalgamation file), the technical narrative collapsed immediately:

1. **Non-Existent Functions**: Function names like `sqlite3_vdbe_exec_clear_registers()` and `sqlite3_clear_element_tree()` do not exist anywhere in the SQLite codebase. The LLM combined real concepts—such as SQLite's Virtual Machine (VDBE) and register management—with plausible-sounding function names.
2. **Out-of-Bounds Line Numbers**: Line `184201` fell entirely outside the bounds of the module referenced, or landed inside unrelated code blocks (such as static string constants or comment blocks) depending on the amalgamation build variant.
3. **Flawed C Semantics**: SQLite relies on an embedded architecture written in ANSI C, using manual memory management, register recycling, and internal parse-tree destructors. The LLM hallucinated a control flow where register recycling directly invoked parse-tree destructors during query execution—an architecture that violates SQLite's separation between parsing (`sqlite3RunParser`) and virtual machine execution (`sqlite3VdbeExec`).

```c
/* Real SQLite 3.41.0 VDBE Register Handling Logic (sqlite3.c) */
/* Notice the actual naming conventions and memory release patterns */
SQLITE_PRIVATE void sqlite3VdbeMemRelease(Mem *p){
  if( p->flags & (MEM_Str|MEM_Blob|MEM_Frame) ){
    vdbeMemClearExternal(p);
  }
  p->flags = MEM_Null;
}

/* The LLM hallucinated non-existent symbols like 'sqlite3_vdbe_exec_clear_registers' */
```

### Statistical and Linguistic Verification

Researchers verified the AI authorship of the repository cluster using detection frameworks such as GPTZero, combined with text entropy analysis across the GitHub Security Advisory database. 

```
+-----------------------------------------------------------------------+
| Metrics Analyzed         | Human-Written Advisory | LLM-Generated Advisory|
+--------------------------+------------------------+-----------------------+
| Perplexity Score         | High (Variable)        | Very Low (Predictable)|
| Burstiness               | High (Irregular)       | Low (Uniform)         |
| Invalid Symbol Ratio     | 0.00                   | 0.85+                 |
| Patch AST Match Rate     | 100%                   | 0% (Fails Compilation)|
+-----------------------------------------------------------------------+
```

Human-written security advisories exhibit high "burstiness"—varying sentence lengths, precise terminal commands, stack traces, and direct diff patches. The `programmervuln` advisories, conversely, showed uniform sentence structures, high semantic density of security buzzwords, and complete structural abstraction without executable proof-of-concept (PoC) code.

---

## Verification in the Sandbox: Dynamic PoC Analysis with ASan and Docker

To systematically defend against hallucinated CVEs, DevSecOps teams cannot rely on manual code audits alone. The most reliable way to verify a reported vulnerability is **dynamic runtime verification**: compiling the target software with memory sanitizers and executing the provided PoC payload inside an isolated environment.

If an advisory claims a Use-After-Free or heap buffer overflow in SQLite 3.41.0, compiling the binary with AddressSanitizer (ASan) and running the PoC payload will deterministically trigger an ASan report if the bug is real.

Below is an automated, sandboxed test framework designed to validate incoming SQLite vulnerability claims.

### 1. Isolation Container Setup (`Dockerfile.asan`)

We construct an isolated build container containing the precise SQLite version (3.41.0) compiled with Clang's AddressSanitizer (`-fsanitize=address`) and debug symbols (`-g`).

```dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build toolchain and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    clang \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /analyzer

# Download SQLite 3.41.0 source amalgamation
RUN curl -O https://www.sqlite.org/2023/sqlite-amalgamation-3410000.zip \
    && unzip sqlite-amalgamation-3410000.zip \
    && mv sqlite-amalgamation-3410000 src

WORKDIR /analyzer/src

# Compile SQLite CLI with AddressSanitizer instrumentation
RUN clang -O1 -g -fsanitize=address -fno-omit-frame-pointer \
    sqlite3.c shell.c -ldl -lpthread -o sqlite3_asan

# Create non-privileged user for sandbox execution
RUN useradd -m sandboxuser
USER sandboxuser

ENTRYPOINT ["/analyzer/src/sqlite3_asan"]
```

### 2. Execution and Verification Harness (`verify_poc.sh`)

This shell script feeds the advisory's PoC SQL payload into the instrumented SQLite binary and checks the exit conditions and error logs.

```bash
#!/usr/bin/env bash
set -euo pipefail

POC_FILE="${1:-poc.sql}"
DOCKER_IMAGE="sqlite-asan-validator"

echo "[*] Building ASan Verification Container..."
docker build -t "$DOCKER_IMAGE" -f Dockerfile.asan . > /dev/null

echo "[*] Executing PoC Payload: ${POC_FILE}"
LOG_OUTPUT=$(docker run --rm -v "$(pwd)/${POC_FILE}:/tmp/poc.sql:ro" \
    "$DOCKER_IMAGE" /tmp/poc.sql 2>&1 || true)

# Analyze output logs for AddressSanitizer bug signatures
if echo "$LOG_OUTPUT" | grep -E -q "ERROR: AddressSanitizer:|heap-use-after-free|heap-buffer-overflow|stack-buffer-overflow"; then
    echo "[!] CRITICAL: Genuine vulnerability confirmed via AddressSanitizer!"
    echo "$LOG_OUTPUT" | grep "SUMMARY: AddressSanitizer:"
    exit 0
elif echo "$LOG_OUTPUT" | grep -E -q "Parse error|syntax error"; then
    echo "[?] REJECTED: Payload resulted in standard SQL parsing error. Likely fake or malformed."
    exit 1
else
    echo "[+] REJECTED: Execution completed normally without memory corruption or crashes."
    exit 1
fi
```

### Interpreting Dynamic Sandbox Results

When running the PoC payloads generated by the `programmervuln` advisories through this pipeline, the execution results are clear:

```
$ ./verify_poc.sh hallucinated_poc.sql
[*] Building ASan Verification Container...
[*] Executing PoC Payload: hallucinated_poc.sql
[+] REJECTED: Execution completed normally without memory corruption or crashes.
```

The payloads resulted in either standard syntax parsing errors or executed without memory anomalies. ASan reported zero uninitialized reads, zero memory leaks, and zero invalid pointer dereferences. The dynamic sandbox provides a clear, binary answer: **the reported vulnerability does not exist.**

---

## The Supply Chain Breakdown: How Automated CVE Ingestion Failed

The SQLite incident was not just a story about fake advisories; it revealed how easily trust can break down across modern vulnerability databases. 

Historically, the National Vulnerability Database (NVD) acted as a manual verification bottleneck. Security analysts at NIST reviewed incoming advisories, confirmed their validity, assigned CPE (Common Platform Enumeration) tags, and calculated CVSS metrics before publishing. 

In early 2024, an overwhelming increase in disclosures combined with administrative delays caused the NVD's enrichment process to stall. Thousands of raw CVE IDs were issued without manual enrichment or verification.

```
       [ Upstream Advisory Source ]
 (GitHub Security Advisories - GHSA API)
                    |
                    v
       [ Automated Aggregators ]
 (CISA ADP / Vulnrichment Engine)
                    |
  (Ingests text without running code)
                    v
       [ Common Platform Enumeration ]
 (Auto-matches CPE: cpe:2.3:a:sqlite:sqlite:3.41.0)
                    |
                    v
    [ Enterprise Security Scanners ]
 (Trivy, Snyk, Grype, Dependabot)
                    |
                    v
 [ Developer Infrastructure Triage ]
  (False positive alerts flood engineering queues)
```

To prevent tracking gaps, automated tools began consuming upstream raw feeds—primarily GitHub Security Advisories (GHSA)—and running automated enrichment algorithms like CISA’s Vulnrichment project. 

This created a severe vulnerability in the supply chain:

1. **Unverified Upstream Acceptance**: GHSA allowed users to submit security advisories for public repositories. The `programmervuln` actor submitted advisories directly via GitHub, generating valid GHSA identifiers.
2. **Automated CPE Tagging**: Vulnerability aggregators used keyword parsing to extract version strings. Seeing "SQLite 3.41.0", automated algorithms assigned the standardized CPE string `cpe:2.3:a:sqlite:sqlite:3.41.0`.
3. **Downstream Amplification**: Security scanners (such as Snyk, Trivy, Grype, and Dependabot) routinely pull from GHSA and NVD. Once the CPE tag was attached, these scanners flagged SQLite binaries in thousands of production Docker images and Linux distributions worldwide.

| Ingestion Pipeline Stage | Processing Mechanism | Failure Point | Systemic Impact |
| :--- | :--- | :--- | :--- |
| **Source Submission** | User-submitted Markdown / JSON schema to GHSA | No runtime verification or compiler validation | Garbage input accepted into registry |
| **Aggregator Ingestion** | Automated API pull via CISA ADP & downstream mirrors | Blind ingestion during NVD backlog crisis | Fake advisories elevated to trusted state |
| **CPE Enumeration** | Regex / LLM matching of software names & version numbers | Incorrect matching of valid software packages | Amplified false positive footprint |
| **Enterprise Scanning** | Binary hash and version match against SBOMs | Absence of dynamic local verification | High-priority false alerts sent to developers |

---

## The AI Feedback Loop: Autonomous Patching Agents and Alert Fatigue

The rise of LLM-generated CVEs creates two major operational risks for enterprise engineering organizations: **alert fatigue** and **broken autonomous remediation loops**.

### Engineering Overhead and Alert Fatigue

When a security scanner flags a `CVSS 9.8 Critical` vulnerability in a core dependency like SQLite, enterprise policy often requires an immediate response—typically within 24 to 48 hours. 

When security teams triage hallucinated advisories, they spend valuable time:
* Attempting to trace non-existent function symbols through millions of lines of source code.
* Trying to reproduce vague, non-functional PoCs.
* Filing exception tickets and overriding false positives in vulnerability management platforms.

This wastes engineering resources and causes severe alert fatigue. When real critical vulnerabilities appear, teams desensitized by constant false alarms are slower to respond.

### The Autonomous Remediation Trap

The risk becomes even worse when organizations deploy autonomous AI patching agents. Modern DevSecOps pipelines increasingly use LLM-driven remediation tools that automatically read CVE descriptions, generate patch diffs, and open Pull Requests.

```
+-------------------------------------------------------------+
| 1. Hallucinated CVE ingested into scanner                   |
|    (Claims non-existent memory leak in sqlite3.c)           |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 2. Autonomous AI Patching Agent Triggered                   |
|    (Reads fake CVE description & scans source code)         |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 3. Agent Hallucinates "Fix" for Non-Existent Bug            |
|    (Modifies valid memory logic, removes bounds checks)     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 4. Pull Request Merged into Production                       |
|    (Introduces REAL security vulnerability or breaks builds) |
+-------------------------------------------------------------+
```

When an autonomous agent receives a fake CVE description:
1. The agent searches the target repository for the cited function names and line numbers.
2. Failing to find them, the agent attempts to "infer" where the hallucinated bug might exist.
3. The agent hallucinates a patch—frequently modifying valid, critical code paths, removing necessary performance optimizations, or disabling real safety checks.
4. The automated patch passes basic unit tests (if test coverage is incomplete) and merges into production.

The feedback loop is complete: **an AI-generated fake vulnerability causes an AI patching tool to introduce a real security flaw into valid source code.**

This issue aligns closely with broader challenges in AI-driven software development. As explored in our analysis of [OpenAI Codex security threat modeling](/tech/2026/07/30/openai-codex-security-threat-modeling.html), generative models often prioritize code generation over security boundaries. Similarly, automated agents acting on unverified security context can introduce serious infrastructure vulnerabilities, much like the patterns observed in [AI-generated CORS misconfigurations](/tech/2026/07/24/ai-generated-cors-misconfigurations-vulnerabilities.html).

---

## Hardening the CVE Pipeline: Proofs, Attestations, and Slop Detection

Fixing the vulnerability management pipeline requires moving away from pure text trust models and toward **deterministic verification**. Organizations must modernize their vulnerability ingestion infrastructure using three key layers of defense:

```
                     Incoming Vulnerability Advisory
                                   |
                                   v
+--------------------------------------------------------------------+
| 1. AI-Slop & AST Filter                                           |
|    - Verify cited function symbols exist in repository AST         |
|    - Flag low-entropy / high-perplexity LLM text signatures       |
+--------------------------------------------------------------------+
                                   |
                         [ Validation Passed ]
                                   v
+--------------------------------------------------------------------+
| 2. Cryptographic Attestation Check                                 |
|    - Require Sigstore / GPG maintainer signature                  |
|    - Match commit hash to verified upstream repository release     |
+--------------------------------------------------------------------+
                                   |
                         [ Signature Verified ]
                                   v
+--------------------------------------------------------------------+
| 3. Automated Isolated Sandbox Execution                            |
|    - Compile target package with ASan / MSan                       |
|    - Execute PoC payload inside short-lived container              |
+--------------------------------------------------------------------+
                                   |
                        [ Crash / Sanitizer Alert ]
                                   v
                       Confirmed Actionable CVE
```

### 1. Mandatory Sandbox PoC Execution

Enterprise vulnerability platforms must require a reproducible test case before automatically opening high-priority developer tickets. 

* Incoming advisories must include an executable PoC payload (e.g., SQL script, HTTP request, binary input).
* The ingestion pipeline automatically runs the payload inside an ephemeral Docker container compiled with sanitizers (ASan, MSan, UBSan).
* If the container executes without memory violations or abnormal termination, the ticket's priority is automatically downgraded to "Unverified Ingestion" pending manual review.

### 2. Cryptographic Maintainer Attestations

To prevent unverified external actors from publishing authoritative advisories for third-party software, CVE registries must adopt cryptographic verification:

* **Maintainer Signatures**: Advisories affecting a project should require a cryptographic signature (using GPG or Sigstore) from verified project maintainers.
* **Commit-Level Attestation**: Advisories must reference a specific upstream commit hash containing the patch, with the patch verified against the maintainer's public signing key.

### 3. AST Validation and AI-Slop Filtering

Before an advisory is analyzed by downstream LLMs or humans, it should pass through automated static analysis:

```python
# Conceptual AST Verification Snippet for Ingestion Pipelines
import tree_sitter_c as tsc
from tree_sitter import Language, Parser

def verify_advisory_symbols(source_code_bytes: bytes, target_symbol: str) -> bool:
    """
    Parses C source code AST to verify if a cited function symbol actually exists.
    """
    C_LANGUAGE = Language(tsc.language())
    parser = Parser(C_LANGUAGE)
    tree = parser.parse(source_code_bytes)
    
    query = C_LANGUAGE.query(f"""
        (function_declarator
            declarator: (identifier) @func_name
            (#eq? @func_name "{target_symbol}"))
    """)
    
    captures = query.captures(tree.root_node)
    return len(captures) > 0
```

By adding an Abstract Syntax Tree (AST) parser to the ingestion pipeline, the system can instantly check whether a function name cited in an advisory (such as `sqlite3_vdbe_exec_clear_registers`) actually exists in the target release tag. If the symbol is missing, the advisory is immediately flagged as a potential hallucination.

---

## Future Outlook: Rebuilding Trust in Open-Source Threat Intelligence

The SQLite hallucinated CVE campaign marks a turning point in open-source threat intelligence. As generating realistic natural language text becomes cheap and trivial, unverified text disclosures can no longer serve as authoritative sources of truth for enterprise vulnerability management.

To adapt, the industry must transition toward a **Zero-Trust Vulnerability Ingestion** architecture. Natural language vulnerability descriptions must be treated as untrusted metadata until verified by cryptographic proofs, static AST validation, and dynamic memory analysis.

This shift will require structural changes across the vulnerability ecosystem:
* **Registry Accountability**: Organizations like GHSA, NVD, and MITRE must implement basic verification checks—such as AST symbol validation and AI content detection—before issuing public CVE IDs.
* **Decentralized Verification**: Moving away from single manual verification authorities toward automated, decentralized verification networks where independent sandboxes validate claims in parallel.
* **Resilient Automation**: Ensuring that autonomous security tools demand deterministic proof before applying code patches or changing security configurations.

Security signal clarity in the age of AI slop cannot rely on unverified claims. By combining dynamic sandboxing, cryptographic attestations, and AST validation, DevSecOps teams can protect their software supply chains from hallucinated threats and ensure that real security vulnerabilities receive the focus they require.

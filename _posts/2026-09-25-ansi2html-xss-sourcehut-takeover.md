---
layout: post
title: 'From Terminal to Takeover: How an XSS in ansi2html Compromised SourceHut'
date: 2026-09-25 09:48:23 +0530
categories: Tech
excerpt: An unauthenticated attacker exploited a stored XSS vulnerability in the ansi2html
  library, using malicious build logs to achieve full account takeover on SourceHut.
cover_image: /assets/images/posts/default-cover.png
cover_caption: Conceptual visualization of terminal build logs transforming into a
  web-based XSS attack vector.
---

Modern software development relies heavily on the humble build log. Whether you are troubleshooting a failed deployment locally or inspecting a remote CI/CD pipeline, watching a stream of colored text scroll down your screen offers an immediate, visceral connection to what your machine—or someone else's infrastructure—is doing. But what happens when that terminal output jumps the air gap from a controlled command-line environment directly into a web browser? 

For SourceHut, an alternative ecosystem of modular developer services, an unauthenticated attacker discovered that trusting colorful build logs could lead straight to disaster. By exploiting a stored cross-site scripting (XSS) vulnerability in `ansi2html`—a popular library used by `builds.sr.ht` to convert terminal escape codes into web-friendly HTML—an attacker could achieve full account takeover simply by tricking a user into viewing a build log. 

This incident serves as a stark reminder of how boundary crossings between backend data formats and frontend rendering engines create subtle, devastating attack vectors. If you are interested in other ways modern runtime and supply chain environments get upended, take a look at our analysis on the [Sourtrade malware and Bun runtime assembly](/tech/2026/07/26/sourtrade-malware-bun-runtime-assembly.html). But first, let's look at how a string of harmless-looking terminal codes became a weapon.

## Deconstructing the Threat: ANSI Escape Codes and OSC 8

To understand how a build log can compromise a web application, we have to look at how terminal formatting works under the hood. ANSI escape sequences date back to physical teletype terminals and VT100s. Instead of just printing raw characters, these sequences use special byte combinations—starting with the Escape character (`\x1b` or `\033`) followed by a bracket `[`—to instruct the terminal to change text color, move the cursor, or clear the screen.

Over the decades, terminal emulators evolved far beyond simple text display. One of the more powerful and modern additions to the ANSI specification is **OSC 8 (Operating System Command 8)**. OSC 8 was introduced to allow command-line applications to embed clickable hyperlinks directly into the terminal stream, formatted like this:

```bash
printf "\e]8;;https://example.com\e\\Click Here\e]8;;\e\\\n"
```

When a modern terminal emulator encounters this sequence, it renders "Click Here" as a clickable anchor tag pointing to `https://example.com`. 

The architectural catch occurs when CI/CD platforms decide to display these terminal logs inside a web dashboard. Because web browsers natively understand HTML rather than ANSI escape codes, developers rely on translation libraries to bridge the gap. These libraries parse the input stream, strip out the raw escape bytes, and output styled HTML elements like `<span>` for colors and `<a>` for OSC 8 hyperlinks. 

The security failure happens when a parser translates a terminal feature into a web primitive without accounting for the semantic differences between a terminal and a browser DOM.

## The Vulnerability: Stored XSS in ansi2html

The core flaw lived inside `ansi2html`, a Python library widely used to convert ANSI console sequences into HTML. Specifically, versions `>=1.7.0` and `<1.9.4` suffered from a failure to adequately sanitize generated attributes when parsing crafted OSC 8 hyperlinks.

When handling OSC 8 sequences, the library was designed to output HTML anchor tags. However, it failed to properly validate or escape the URL parameters and custom attributes passed within the escape sequence. An attacker could craft a malicious sequence that broke out of the expected `href` attribute context or injected arbitrary HTML attributes, such as `onclick`, `onload`, or raw JavaScript URIs (`javascript:...`).

> "When translating terminal streams into web pages, any missing validation on escape sequences transforms log data from passive text into active executable code."

Consider what happens when a logging library converts an unsanitized OSC 8 payload into an HTML string:

```python
# Conceptual representation of vulnerable translation
# Input: Malicious OSC 8 payload containing JavaScript URI
# Output: <a href="javascript:alert(document.cookie)">Malicious Link</a>
```

Because `builds.sr.ht` used this vulnerable version of `ansi2html` to render continuous integration build logs without an additional sanitization layer, any malicious output generated during a build was faithfully translated into executable markup and stored in the database.

## Exploitation Mechanics on builds.sr.ht

SourceHut is built around a unique architecture of decoupled microservices, including `meta.sr.ht` (authentication and user management), `git.sr.ht` (hosting), and `builds.sr.ht` (the CI/CD engine). Unlike centralized platforms that isolate issue trackers and CI environments behind heavy layers of corporate access control, SourceHut integrates tightly with public mailing lists.

This integration created an ideal attack vector. An unauthenticated attacker could interact with public mailing lists that had automated CI integration (`builds.sr.ht`) enabled. By submitting a patch or a project configuration containing malicious build instructions, the attacker could force the CI runner to execute code that printed the crafted ANSI/OSC 8 payload into the standard output stream of the build.

Once the build finished, the resulting log—now containing the stored XSS payload—was saved to the `builds.sr.ht` backend. The trap was set. When an unsuspecting user, particularly a project maintainer or a platform administrator, visited the web dashboard to inspect the build results, their browser would fetch the stored log, parse the malicious HTML injected by `ansi2html`, and execute the embedded JavaScript in the context of their authenticated session.

## Impact: From Log Injection to Full Account Takeover

Cross-Site Scripting in an authenticated web application is rarely just a cosmetic issue, and on SourceHut, the consequences were severe. Because the malicious JavaScript executed inside the browser session of a logged-in user, it inherited all of that user's permissions.

If the victim viewing the log happened to be an administrator or a project maintainer with elevated privileges, the attack script could execute actions on their behalf. The potential impact included:

* **Session Hijacking:** Stealing session cookies or local storage tokens to impersonate the user.
* **CSRF Token Harvesting:** Reading anti-CSRF tokens from the DOM to perform unauthorized state-changing requests.
* **Malicious Manifest Resubmission:** Automatically triggering new, malicious build runs that could further compromise infrastructure.
* **Credential Exfiltration:** Accessing sensitive deployment keys, environment variables, and private repository secrets stored or accessible within the user's dashboard context.

| Attack Phase | Mechanism | Target / Result |
| :--- | :--- | :--- |
| **Injection** | Public mailing list patch with malicious CI instructions | `builds.sr.ht` log storage |
| **Trigger** | Admin/Maintainer views the build log in the web UI | Browser execution of injected JavaScript |
| **Compromise** | Session token theft & automated API calls | Full account takeover and secret exfiltration |

Much like dealing with automated policy flaws or dependency risks—such as managing vulnerabilities via tools discussed in our guide on [Dependabot's default cooldown policy](/tech/2026/07/29/dependabot-default-cooldown-policy.html)—protecting your software supply chain requires catching these gaps before they reach production.

## Remediation and Defensive Engineering

Upon discovery of the vulnerability, SourceHut founder Drew DeVault moved quickly to mitigate the risk. The immediate fix on `builds.sr.ht` involved updating the platform to automatically sanitize the output generated by `ansi2html` before rendering it to users in the web interface. Concurrently, upstream maintainers released version `1.9.4` of `ansi2html`, patching the root cause by properly escaping attributes within OSC 8 hyperlink sequences.

However, relying solely on an upstream library patch is a fragile security strategy. Robust defensive engineering requires a defense-in-depth approach when rendering untrusted data in a browser context:

### 1. Implement Strict Output Sanitization
Never trust that a formatting library (whether for markdown, syntax highlighting, or ANSI conversion) will produce safe HTML. Pass all rendered HTML through a rigorous sanitizer like DOMPurify (for frontend rendering) or Python's Bleach library (for backend processing) to strip out dangerous tags and attributes.

```python
import bleach

# Allowed tags and attributes for rendering build logs safely
ALLOWED_TAGS = ['span', 'a', 'br', 'pre', 'code']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'rel'],
    'span': ['class', 'style']
}

def safe_render_log(raw_html):
    return bleach.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
```

### 2. Enforce a Hardened Content Security Policy (CSP)
A strong CSP acts as a vital safety net against XSS. By restricting script execution sources, disallowing inline scripts, and controlling where connections can be made via `connect-src`, you can neutralize an XSS payload even if it manages to make its way into the DOM. For instance, ensuring your CSP blocks unauthorized script execution prevents attackers from successfully exfiltrating session tokens via JavaScript.

Similar defense-in-depth strategies are crucial across all enterprise software components, such as securing artifact repositories against bypass techniques like those detailed in our report on [CVE-2026-82329 in JFrog Artifactory](/tech/2026/09/01/cve-2026-82329-jfrog-artifactory-bypass.html).

## Future Outlook: Untrusted Logs Need Untrusted Handling

The SourceHut incident with `ansi2html` highlights a broader, ongoing challenge in modern web application design: bridging the gap between text-based terminal systems and rich web interfaces. As long as CI/CD platforms, log aggregation tools, and cloud monitoring dashboards continue to translate terminal escape codes into HTML, the risk of parser differentials remains high.

The core takeaway for developers and security engineers is simple: **treat all log inputs as inherently untrusted data.** Whether logs come from an automated test runner, a third-party dependency, or a public patch submission, they must be parsed, sanitized, and isolated with the same rigor applied to user-uploaded files or form inputs. By treating terminal output as a potential attack surface, we can ensure that our build pipelines remain a tool for shipping code, rather than a vector for a takeover.

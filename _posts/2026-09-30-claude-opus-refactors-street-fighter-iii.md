---
layout: post
title: 'Agentic Codebase Transformation: How $4,000 and Claude 3 Opus Refactored Street
  Fighter III'
date: 2026-09-30 15:05:34 +0530
categories: News
excerpt: CodeScene recently demonstrated the power of agentic AI by refactoring the
  legendary Street Fighter III codebase in just 21 days for only $4,000.
cover_image: /assets/images/posts/claude-opus-refactors-street-fighter-iii-cover.png
cover_caption: An artistic representation of AI agents analyzing and restructuring
  classic arcade game code.
---

In the world of software engineering, legacy codebases are often treated like ancient archaeological sites: we know there is value buried within, but one wrong move could cause the entire structure to collapse. This is particularly true for legendary titles like *Street Fighter III*. With over 300,000 lines of intricate, manual C code, the game’s engine is a masterpiece of late-90s optimization and a nightmare of modern technical debt. Traditionally, refactoring a codebase of this scale and complexity would require a dedicated team of senior engineers, a multi-year timeline, and a massive budget.

However, a recent case study by CodeScene has challenged this paradigm. Using an agentic workflow powered by Claude 3 Opus and a specialized verification framework, they managed to refactor the *Street Fighter III* codebase in just 21 days. The cost? Approximately $4,000 in LLM tokens. The result? A jump in "Code Health" from a mediocre 5.6 to a perfect 10.0. This wasn't just a simple find-and-replace operation; it was a fundamental restructuring of 252,055 lines of code across 726 files.

## The Hadouken of Technical Debt: Why Street Fighter III?

To understand why this achievement is significant, we must first look at the nature of the code itself. *Street Fighter III* (specifically the versions running on the CPS-3 arcade hardware) represents the pinnacle of 2D fighting game engineering. The code is written in C, but it is C born of necessity—packed with "clever" hacks, global state variables, and massive "Brain Methods" designed to squeeze every ounce of performance out of limited hardware.

Refactoring such code is a high-stakes gamble. In an embedded game engine, logic is often tightly coupled with timing. A seemingly harmless change to a collision detection function could introduce a one-frame delay, breaking the "feel" of the game or desyncing the animation state. This is why most companies choose to wrap legacy code in "black box" containers rather than cleaning it up. The risk-to-reward ratio of manual refactoring simply doesn't add up for most business stakeholders.

The CodeScene experiment sought to prove that AI agents, when properly constrained and verified, could handle the "heavy lifting" of technical debt removal. By targeting a codebase as notoriously difficult as a classic fighting game, they set a high bar for what agentic software evolution can achieve.

## The Agentic Stack: Claude 3 Opus and the Model Context Protocol

The success of this refactor wasn't due to a single prompt, but rather a sophisticated "Agentic Stack." While early AI coding assistants functioned primarily as autocomplete tools, the agents used here were autonomous entities capable of reasoning about the codebase.

### Why Claude 3 Opus?
While models like GitHub Copilot (based on OpenAI’s Codex) or specialized models like Sol are popular, CodeScene opted for **Claude 3 Opus**. The decision was driven by two primary factors:
1.  **Reasoning Capabilities:** Opus demonstrates a superior ability to follow complex, multi-step instructions without "hallucinating" architectural patterns that don't exist in the source.
2.  **Context Window:** Refactoring requires an understanding of how a change in `collision.c` might affect `physics.h`. Opus’s large context window allowed the agents to ingest relevant headers and related implementation files simultaneously.

### The Role of the Model Context Protocol (MCP)
To prevent the agent from working in a vacuum, CodeScene utilized the **Model Context Protocol (MCP)**. MCP acts as a standardized bridge between the LLM and external tools. Instead of the LLM just "guessing" if a change was good, the MCP server provided the agent with real-time quality signals.

If an agent proposed a refactor that increased cyclomatic complexity or introduced a "God Object" pattern, the MCP-connected quality tools would immediately flag the issue. This creates a feedback loop where the agent self-corrects based on objective metrics before the code ever reaches a human reviewer. This is a crucial component of [context engineering in AI root cause analysis](/tech/2026/07/25/context-engineering-ai-root-cause-analysis.html), where providing the right environmental data is more important than the raw power of the model itself.

## The Verification Oracle: Deterministic Replay-Trace Harnesses

The most significant barrier to autonomous refactoring is the "Verification Problem." How do you know the AI didn't subtly change the game's logic? In a fighting game, "close enough" is a failure.

The solution was the implementation of a **Deterministic Replay-Trace Harness**. This served as the "Oracle" for the agents.

### How the Oracle Works
A deterministic replay-trace works by recording every input and every resulting state change in the original, un-refactored game. Because the game engine is deterministic, the same sequence of inputs (e.g., Forward, Down, Down-Forward + Punch) should always result in the same state hash at the end of every frame.

| Component | Function |
| :--- | :--- |
| **Input Logger** | Records frame-by-frame joystick and button inputs. |
| **State Hasher** | Generates a unique hash of the entire game RAM/state after every frame. |
| **Comparison Engine** | Compares the hash from the "Golden" (original) code against the "Refactored" code. |

The agent's workflow followed a strict loop:
1.  **Identify** a "Brain Method" (a complex, multi-responsibility function).
2.  **Refactor** the method into smaller, clean components.
3.  **Compile** the new code.
4.  **Run** the replay-trace harness.
5.  **Verify:** If the state hashes matched the original for 10,000+ frames of gameplay, the refactor was considered "behaviorally neutral."

If a single bit in the game's memory differed—even if the game *looked* fine on screen—the Oracle rejected the change. This allowed the agents to move beyond simple chat-based coding and into the realm of autonomous engineering.

## 2,903 Commits in 21 Days: The Execution Phase

The sheer scale of the work performed by the agents is difficult for a human team to wrap their heads around. Over a three-week period, the agents executed a relentless cycle of refactoring and verification.

### By the Numbers
*   **Total Commits:** 2,903
*   **Files Modified:** 726
*   **Lines of Code Touched:** 252,055
*   **Total Cost:** ~$4,000 (LLM tokens)
*   **Timeframe:** 21 days

To put this in perspective, a senior developer might produce 5 to 10 meaningful, refactored commits in a productive day. The agents were averaging over 130 commits per day, 24/7. 

### Managing the Velocity Crisis
This level of output creates a new problem: the "Velocity Crisis." Traditional human code review processes are not designed to handle 100+ commits a day from a single "contributor." If a human had to manually review every line of the 252,055 modified, the project would have stalled immediately.

Instead, the team shifted their focus. The humans didn't review the *code*; they reviewed the *harness*. By ensuring the Verification Oracle was airtight, the team could trust the agent's output. This shift is a core theme in managing the [velocity crisis in agentic coding](/tech/2026/07/27/velocity-crisis-code-review-agentic-coding.html), where the human role transitions from "line-by-line reviewer" to "system architect and auditor."

## Quantifying Quality: From 5.6 to 10.0 Code Health

The primary goal wasn't just to change code, but to improve its "health." CodeScene uses a proprietary "Code Health" score, which aggregates various metrics like nesting depth, function length, and the presence of "code smells."

### Eliminating Brain Methods and God Objects
The *Street Fighter III* codebase was riddled with "Brain Methods"—functions that try to do everything at once. One such function might handle input, physics, and frame-data updates for a character's special move, spanning hundreds of lines with deeply nested `if/else` statements.

The agents systematically broke these down. Using Claude 3 Opus's understanding of C, the agents extracted logic into discrete, named functions. They replaced magic numbers with named constants and centralized global state into structured objects.

> "The agents didn't just clean the code; they modernized the architecture. They took 1990s C and turned it into something that looks like modern, maintainable systems code." — CodeScene Case Study

### Results Comparison

| Metric | Pre-Refactor | Post-Refactor |
| :--- | :--- | :--- |
| **Code Health Score** | 5.6 / 10 | 10.0 / 10 |
| **Average Function Length** | 84 lines | 12 lines |
| **Cyclomatic Complexity (Avg)** | 24 | 4 |
| **Brain Methods** | 142 | 0 |
| **God Objects** | 12 | 0 |

A Code Health score of 10.0 is almost unheard of in large-scale C projects. It represents a codebase where every function is small, focused, and easy to test.

## The Shift: From Manual Coding to Agentic Verification

This experiment marks a fundamental shift in the software development lifecycle. We are moving away from an era where developers spend 80% of their time writing and debugging lines of code, and into an era of **Agentic Verification**.

### The New Developer Workflow
In this new model, the developer's primary responsibility is the design of the "Test Harness" or "Oracle." If you can define exactly what the code *should* do and provide a deterministic way to verify it, the AI can handle the implementation.

This is similar to the shifts we are seeing in other areas of infrastructure, such as [agentic cloud operations and testing](/tech/2026/08/22/aws-bench-agentic-cloud-ops-testing.html), where the focus is on defining the desired state rather than the steps to achieve it.

### Where Humans Still Trump the LLM
Despite the success, agents are not a total replacement for human intuition. During the *Street Fighter III* project, humans were still required for:
*   **High-Level Architectural Decisions:** Deciding *which* patterns to use (e.g., choosing between a State pattern or a Strategy pattern).
*   **Edge Case Definition:** Identifying scenarios that the replay-trace might have missed (e.g., what happens when the memory overflows or a controller is unplugged?).
*   **Harness Debugging:** When the Oracle and the Agent disagree, a human must step in to determine which one is "wrong."

## Future Outlook: Does High-Health Code Reduce Future AI Costs?

The implications of this project extend far beyond retro gaming. For enterprise organizations running on legacy Java, COBOL, or C++ systems, the $4,000 refactor provides a blueprint for modernization.

However, the most intriguing question is what happens *after* the refactor. CodeScene and Lund University are currently conducting a follow-up study to test a compelling hypothesis: **Does high-health code reduce future AI inference costs?**

The theory is that clean, modular code requires fewer tokens for an LLM to understand and modify. If a function is 10 lines long and perfectly named, an agent can fix a bug in it using a fraction of the context (and cost) required for a 500-line "Brain Method." In this sense, refactoring isn't just about making code better for humans; it's about optimizing the codebase for the "AI coworkers" of the future.

As we look forward, the ability to autonomously transform legacy "spaghetti code" into high-health, AI-optimized systems will be a significant competitive advantage. The *Street Fighter III* refactor isn't just a win for game preservation; it's a "K.O." for the traditional, slow-moving approach to technical debt.

---
layout: post
title: 'Beyond Stateless Auth: Securing AI Agents with AWS Dogwood and Temporal Policy'
date: 2026-08-16 18:19:21 +0530
categories: Tech
excerpt: As AI agents evolve from chatbots to autonomous actors, traditional stateless
  security models are failing. Discover how AWS Dogwood introduces temporal awareness.
cover_image: /assets/images/posts/securing-ai-agents-aws-dogwood-temporal-cover.png
cover_caption: A conceptual visualization of a secure, time-aware governance layer
  for autonomous AI agents.
---

The industry is currently undergoing a fundamental shift in how we interact with Large Language Models (LLMs). We are moving away from the era of "chatbots"—where a human provides a prompt and the model provides a static completion—and into the era of "agents." These autonomous entities don't just talk; they act. They use tools, call APIs, query databases, and execute code to achieve complex, multi-step goals.

However, as we empower these agents with tool-calling capabilities, we encounter a significant "memory gap" in our security infrastructure. Traditional Identity and Access Management (IAM) systems, built on Role-Based Access Control (RBAC) or Attribute-Based Access Control (ABAC), are fundamentally stateless. They evaluate a single request in a vacuum: *Does Agent A have permission to call Tool B right now?* This "context-less" approach is increasingly insufficient for securing agentic workflows. An agent might have permission to read a database and permission to send an email, but it should arguably never be allowed to read a sensitive database and *then* send an email in the same session. To secure the next generation of AI, we need a governance layer that understands time and sequence.

## The Agentic Shift and the Memory Gap in Security

In the current landscape, as the [tech industry moves towards efficient AI](/news/2026/07/23/tech-industry-moves-towards-efficient-ai.html), the complexity of agentic tool calls is skyrocketing. When an agent is tasked with "optimizing a cloud budget," it might perform dozens of individual actions: listing EC2 instances, checking pricing APIs, and terminating underutilized resources. 

From a security perspective, each individual action might look perfectly benign. However, the *aggregate* of these actions could be catastrophic. Traditional security models fail here because they lack "temporal awareness." They cannot see the sequence of events leading up to a request. This is the memory gap: our security policies are amnesiacs, treating every step of a long-running autonomous process as if it were the very first interaction.

If an agent is compromised or suffers from "hallucination-driven logic," it can perform a "slow-drip" attack. It might bypass rate limits by making small, frequent requests that stay just under the threshold of traditional stateless monitors. Without a way to enforce policies across a timeline, we are essentially giving agents a blank check, hoping their internal logic remains aligned with our business goals. We need a deterministic control layer that sits outside the LLM's non-deterministic reasoning—a guardrail with a memory.

## Introducing AWS Dogwood: Cedar with a Memory

To bridge this gap, researchers at AWS have introduced **Dogwood**, a research-backed extension to the Cedar policy language. For those unfamiliar, Cedar is an open-source language for access control that is designed to be readable, fast, and—crucially—amenable to formal verification. While standard Cedar is excellent for defining who can do what, it shares the same stateless limitations as other modern IAM frameworks.

Dogwood evolves Cedar by introducing stateful governance. It allows developers to write policies that don't just look at the current request's attributes, but also look back at the history of what that agent has done. The core innovation in Dogwood is the introduction of the `when temporal` clause. 

In a standard Cedar policy, you might see a structure like this:
```cedar
permit(
    principal,
    action == Action::"CallTool",
    resource == Resource::"Database"
)
when { context.is_authenticated == true };
```

Dogwood extends this logic by allowing the policy to query an event history log. It transforms authorization from a binary "Yes/No" based on the present into a sophisticated evaluation based on the past. By decoupling the governance logic from the agent's application code, Dogwood ensures that security rules remain immutable and enforceable, even if the agent's underlying model changes or behaves unexpectedly.

## The Mechanics of Temporal Logic (MFOTL)

The technical engine driving Dogwood is **Metric First-Order Temporal Logic (MFOTL)**. While the name sounds intimidating, the concept is quite intuitive for anyone who has managed a timeline or a sequence of logs.

In layman's terms, standard logic deals with "What is true right now?" Temporal logic deals with "What was true, and when did it happen?" MFOTL allows Dogwood to evaluate constraints over a continuous timeline. It tracks events as they occur and allows the policy engine to reason about the intervals between them.

Dogwood uses MFOTL to support two primary types of temporal constraints:

1.  **Past-looking constraints:** These are the "guardrails." They ask, "Has this agent performed Action X within the last Y minutes?" or "Did the agent access Resource Z before attempting this current action?" This is critical for preventing data exfiltration or aggregate resource abuse.
2.  **Future-looking liveness (Experimental):** While primarily focused on the past, the theoretical framework of MFOTL also allows for "liveness" properties—ensuring that if Action A happens, Action B *must* eventually follow within a certain timeframe.

Unlike simple counters or traditional rate-limiters, MFOTL provides a formal mathematical framework for these evaluations. This ensures that the policy engine remains deterministic. In environments where [compute constraints and engineering strategy](/geopolitics/2026/07/26/deepseek-strategy-engineering-ai-compute-constraints.html) dictate the architecture, having a lightweight yet mathematically rigorous way to handle history is a major advantage. Dogwood doesn't require a massive database query for every authorization; it uses the event history to build a state representation that the Cedar interpreter can digest quickly.

## Architecture: From Event Logs to Authorization Decisions

Implementing Dogwood requires a shift in how we think about the authorization flow. In a typical stateless system, the application sends a request to the authorizer, and the authorizer returns a decision. In the Dogwood architecture, there is an intermediary: the **Event History Log**.

### The Data Flow
1.  **The Request:** An AI agent attempts to call a tool (e.g., `send_slack_message`).
2.  **History Retrieval:** The system retrieves the relevant history of events for that specific agent session or principal from the Event History Log.
3.  **Context Translation:** Dogwood translates these historical events into a format that the Cedar engine can understand. This is often injected into the `context` field of the Cedar request.
4.  **Policy Evaluation:** The Dogwood-enhanced Cedar engine evaluates the policy, including the `when temporal` clauses, against the current request and the provided history.
5.  **The Decision:** The engine returns a `Permit` or `Forbidden` decision.
6.  **Log Update:** If the action is permitted and executed, it is recorded back into the Event History Log to inform future decisions.

### Integration with MCP
A key component in this architecture is the **Model Context Protocol (MCP)**. MCP provides a standardized way for agents to interact with tools. By using MCP, developers can ensure that every tool call is transparent and logged in a uniform format. Dogwood leverages this transparency, using the standardized outputs of MCP to populate the event log. This creates a "deterministic control layer" where the policy engine acts as the final arbiter, regardless of how complex the agent's internal reasoning becomes.

| Feature | Traditional Cedar (Stateless) | AWS Dogwood (Temporal) |
| :--- | :--- | :--- |
| **Primary Logic** | Boolean/Attribute-based | Metric First-Order Temporal Logic |
| **Context** | Current request only | Request + Historical Event Log |
| **Use Case** | Permissions (Who can do what) | Governance (What sequence is allowed) |
| **State Management** | None (Externalized) | Managed via Event History |
| **Complexity** | Low to Medium | Medium to High |

## Use Case 1: Preventing Aggregate Resource Exhaustion

One of the most immediate practical applications of Dogwood is managing resource consumption. AI agents are notoriously bad at self-regulation. An agent might be programmed to "find the best price for a flight," and in its zeal, it might call a paid Search API 500 times in ten minutes. 

A traditional rate-limiter might allow 10 calls per minute. The agent could stay just under that limit but still run up a $1,000 bill over the course of an hour. With Dogwood, we can write a policy that aggregates "spend" events over a wider, sliding window.

### Example Dogwood Policy:
```cedar
// Deny the action if the total spend in the last 24 hours exceeds $100
forbid(
    principal,
    action == Action::"PaidToolCall",
    resource
)
when temporal {
    sum(event.price) where { 
        event.action == Action::"PaidToolCall" && 
        event.timestamp > now - duration("24h") 
    } > 100
};
```

In this scenario, the policy engine isn't just looking at the current $0.50 API call. It is summing up every `PaidToolCall` event linked to that principal in the last 24 hours. This provides a "budgetary guardrail" that is decoupled from the agent's logic. Even if the agent's code has a bug that causes an infinite loop of API calls, the Dogwood policy will shut it down once the threshold is met.

## Use Case 2: Data Exfiltration and the 'Sensitive Access' Guardrail

A more critical security concern is the "Confused Deputy" problem. This occurs when an agent is tricked (perhaps via prompt injection) into using its legitimate permissions to perform an illegitimate action. For example, an agent might be authorized to read internal company documents to help a user write a report. However, if that same agent also has permission to post to a public Slack channel or send an email, it could be coerced into leaking sensitive data.

Stateless IAM cannot prevent this because "Read Document" and "Send Email" are both permitted actions for the agent. Dogwood solves this by enforcing **sequence-based constraints**.

### The Policy Logic:
"If the agent has accessed a resource tagged as `Sensitive` within the current session, deny any action that involves external egress (Internet, Email, Public API)."

```cedar
forbid(
    principal,
    action in [Action::"SendEmail", Action::"PublicPost"],
    resource
)
when temporal {
    exists event where {
        event.action == Action::"ReadDocument" &&
        event.resource.tags.contains("Sensitive") &&
        event.session_id == context.session_id
    }
};
```

This policy creates a stateful isolation barrier. It effectively "taints" the agent's session the moment it touches sensitive data. This is a powerful defense against data exfiltration that doesn't require complex, hardcoded logic within the application layer. It moves the security boundary from the code to the policy.

## Current Limitations and the Formal Analysis Gap

While Dogwood represents a massive leap forward, it is currently in a research-heavy phase, and there are trade-offs to consider. 

The most significant limitation is the **Formal Analysis Gap**. Standard Cedar is famous for its ability to undergo automated reasoning. You can use the Cedar SDK to prove that a policy will *never* allow a certain action under any circumstances. Because Dogwood introduces the dimension of time and a dynamic event log, the state space becomes much larger and more complex. Currently, the automated reasoning tools available for standard Cedar do not yet support the temporal clauses in Dogwood. This means developers must rely more heavily on traditional testing and auditing.

Furthermore, there is the **Performance Overhead**. Processing a long history of events for every authorization decision can introduce latency. While Dogwood is designed to be efficient by using optimized state representations, an agent that makes thousands of calls per minute could theoretically bottleneck the authorizer. Architects must carefully consider the size of the "lookback window" and the granularity of the events being logged.

Finally, there is the challenge of **non-deterministic agent behavior**. If an agent's history is used to restrict its future, and the agent's behavior is non-deterministic, it can be difficult to debug why an action was denied. It requires a high level of observability into the event history to understand the "why" behind a Dogwood decision.

## The Future of Agent Governance: Liveness and Multi-Agent Handoffs

Looking ahead, the roadmap for Dogwood and temporal policy governance is ambitious. AWS researchers are exploring the implementation of **absolute-time windows**, which would allow for policies tied to specific calendar events or business hours (e.g., "Agents cannot modify production databases during the holiday freeze").

Another exciting frontier is **Liveness Properties**. In distributed systems, liveness ensures that "something good eventually happens." For AI agents, this could mean enforcing that if an agent starts a transaction or locks a resource, it *must* complete the transaction or release the lock within a specific timeframe. If it fails to do so, the governance layer could trigger a compensatory action or an alert to a human supervisor.

We are also moving toward a world of **Multi-Agent Orchestration**. In these systems, specialized agents hand off tasks to one another. Securing these handoffs is incredibly difficult with stateless logic. Dogwood could be used to manage "locks" and "tokens" between agents, ensuring that only one agent has access to a specific tool at a time and that the handoff occurs only after certain historical conditions (like a successful security scan) are met.

The convergence of Policy-as-Code and AI safety is inevitable. As agents become more autonomous, the "human in the loop" will increasingly be replaced by "policy in the loop."

## Conclusion: Building a Deterministic Future for Non-Deterministic Agents

The rise of AI agents brings a level of unpredictability that traditional security frameworks are simply not equipped to handle. By treating authorization as a stateless, point-in-time event, we leave ourselves vulnerable to aggregate resource abuse and complex data exfiltration attacks. 

AWS Dogwood, with its foundation in temporal logic, provides the missing piece of the puzzle: **memory**. By allowing us to write policies that reason about the past, Dogwood enables "guardrails with context." It allows organizations to enforce complex business logic and security constraints without cluttering the agent's application code. 

As we continue to push the boundaries of what autonomous agents can do, the importance of decoupling governance from agent logic cannot be overstated. We are building a future where the agents are non-deterministic, but the rules they play by are absolute, verifiable, and state-aware. For developers and architects, now is the time to experiment with stateful authorization. The "memory gap" is closing, and the era of truly secure, autonomous agentic workflows is beginning.

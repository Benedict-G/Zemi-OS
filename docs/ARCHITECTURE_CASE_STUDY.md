# Zemi OS  
## Architecture Case Study  
Independent Architecture Project – Secure, Deterministic AI Execution Framework

---

## 1. Executive Summary

Zemi OS is an independent architecture project exploring how AI-driven systems can be executed securely, deterministically, and without uncontrolled automation.

The project was designed to answer a core question:

How can local AI systems perform useful automation while maintaining strict execution control, auditability, and safety constraints?

Zemi enforces deterministic routing before LLM reasoning, mandatory approval for destructive operations, and permission-declared skill execution. The system operates entirely in a local-first environment and requires no cloud infrastructure.

This case study outlines the architectural decisions, security model, execution controls, and tradeoffs involved in building the system.

---

## 2. Problem Statement

Modern AI assistants often rely on probabilistic reasoning without strict execution constraints. When extended with tool usage or file system access, this creates risk:

- Uncontrolled file modification
- Unverified skill execution
- Hidden automation chains
- Lack of audit visibility
- Over-reliance on LLM autonomy

The goal of Zemi was not to build a chatbot.

The goal was to design an execution framework where:

- No destructive action occurs without recorded approval
- All execution flows through a single controlled routing layer
- Skills cannot operate outside declared permissions
- All actions are logged and auditable
- Local infrastructure remains sovereign and isolated

---

## 3. Design Goals

Zemi was built around the following principles:

1. Determinism before intelligence  
2. Explicit approval for destructive operations  
3. Zero-trust skill architecture  
4. Local-first infrastructure  
5. Clear separation of execution layers  
6. Observable and auditable system behavior

Non-Goals:

- Fully autonomous AI agent behavior  
- Cloud-dependent architecture  
- Self-modifying system logic  
- Automatic privilege escalation  

The project prioritizes execution control over convenience.

---

## 4. System Architecture Overview

Zemi is structured as a layered execution system. Each layer has clearly defined responsibilities and cannot bypass the deterministic routing core.

### Layer 1 — Core OS Layer
Responsible for execution control and enforcement.

Components:
- DeterministicRouter
- ApprovalEngine (FIFO queue with expiration)
- TrustTierEnforcer
- FileOperationManager (vault-bound)
- RateLimiter
- SafeModeController
- KillSwitchController
- ModelFallbackManager

All actions must pass through the DeterministicRouter before execution.

---

### Layer 2 — Intelligence Layer
Responsible for structured interpretation and model interaction.

Components:
- IntentAnalyzer
- Model routing (primary + fallback via Ollama)
- ChunkedFileProcessor
- Structured task system (YAML + Markdown driven)

Importantly, intelligence does not execute actions directly.
It produces structured instructions that must be validated and routed.

---

### Layer 3 — Interaction Layer
Handles external interfaces.

- Slack integration (Socket Mode)
- Local voice interface (Whisper STT / Piper TTS)

All inputs from this layer are routed through the DeterministicRouter before any system-level action occurs.

---

### Layer 4 — Skills Subsystem
Implements modular capability expansion.

Each skill:
- Declares permissions in a manifest
- Runs within defined boundaries
- Cannot directly access the filesystem
- Is hash-verified on load
- Can be auto-disabled if integrity checks fail

Skills cannot chain execution outside router control.

---

### Layer 5 — Admin Dashboard
A separate FastAPI process providing:

- Approval queue visibility
- Skill lifecycle management
- Model configuration
- Safe Mode & Kill Switch controls
- Structured system logs

The dashboard does not bypass routing logic.

---

## 5. Core Architectural Decisions

### Deterministic Routing Before LLM Reasoning

LLMs generate structured intent.  
They do not execute.

This prevents probabilistic reasoning from directly triggering system changes.

---

### Mandatory Approval for Destructive Actions

Any action involving:
- File deletion
- File overwrite
- Skill installation
- System modification

Requires explicit approval before execution.

Approvals expire automatically if not confirmed.

---

### Zero-Trust Skill Model

Skills must declare required permissions.
Permissions are enforced by the router.
No skill can elevate privileges dynamically.

---

### Local-Only Inference

All AI inference runs locally via Ollama.
No required cloud API dependencies exist.

This reduces:
- External data exposure
- Token leakage risk
- Network-based attack surface

---

## 6. Security Model

Security in Zemi is enforced through layered constraints rather than trust in model behavior.

### Credential Protection
- AES-256 encryption via Fernet
- Encrypted vault storage
- No plaintext credential persistence
- No secrets committed to version control

### Trust Tier Enforcement
Operations are categorized into tiers:

Tier 0 — Read-only operations  
Tier 1 — Non-destructive modifications  
Tier 2 — Sensitive operations (require approval)  
Tier 3 — Critical/destructive operations (strict approval required)

The TrustTierEnforcer prevents unauthorized escalation.

---

### Execution Controls
- Router-controlled chaining only
- No direct skill-to-skill execution
- No self-modifying system logic
- Kill Switch immediately halts execution
- Safe Mode disables all destructive operations

All routed actions are logged for auditability.

---

## 7. Tradeoffs & Constraints

Designing for deterministic control introduces tradeoffs.

### Reduced Autonomy
The system intentionally limits LLM-driven automation in favor of safety.

### Increased Complexity
Layer separation and approval gating increase architectural overhead.

### Slower Execution Flow
Approval queues and validation steps add latency compared to autonomous agents.

These tradeoffs were accepted to prioritize security and predictability over speed.

---

## 8. Lessons Learned

### Determinism Simplifies Debugging
Routing all actions through a single execution path significantly improves traceability.

### Explicit Permission Models Prevent Drift
Manifest-declared permissions reduce scope creep and accidental privilege escalation.

### Safety Constraints Improve Architecture Discipline
Designing around “must not” constraints resulted in clearer separation of concerns.

### Observability Is Critical
Structured logging is essential for understanding AI-driven systems in production-like environments.

---

## 9. Future Evolution

Potential areas of expansion include:

- Role-based access controls (RBAC)
- Multi-user isolation
- External API abstraction layer (optional)
- Advanced telemetry dashboards
- Production-ready container orchestration

Future iterations would maintain the core philosophy of deterministic routing and explicit approval gating.

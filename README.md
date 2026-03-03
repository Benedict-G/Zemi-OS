# Zemi OS

Zemi is a local-first AI Operating System built around deterministic routing, permission-bound skill execution, and strict security enforcement.

It is designed as a secure execution framework where no destructive action occurs without explicit approval, and all logic flows through a single controlled routing layer.

---

## Architectural Philosophy

Zemi enforces:

- Deterministic routing before LLM reasoning
- Router-controlled chaining only
- No destructive action without recorded approval
- Permission-declared, sandboxed skills
- Fully auditable execution logging
- Zero required cloud infrastructure

All execution flows through a central DeterministicRouter.

---

## System Layers

Zemi is structured across five controlled layers:

1. **Core OS Layer**
   - DeterministicRouter
   - ApprovalEngine (FIFO, 5-minute expiration)
   - TrustTierEnforcer
   - FileOperationManager (vault-enforced)
   - RateLimiter
   - SafeModeController
   - KillSwitchController
   - ModelFallbackManager

2. **Intelligence Layer**
   - IntentAnalyzer
   - Primary + fallback LLM routing (Ollama)
   - ChunkedFileProcessor
   - Structured task system (YAML + Markdown)

3. **Interaction Layer**
   - Slack interface
   - Local voice interface (Whisper STT + Piper TTS)
   - All interaction routed through DeterministicRouter

4. **Skills Subsystem**
   - Manifest-declared permissions
   - Sandboxed execution
   - Hash verification with auto-disable
   - Router-controlled execution chain

5. **Admin Dashboard**
   - FastAPI (separate process)
   - Approval queue visibility
   - Model management
   - Skill lifecycle management
   - Safe Mode + Kill Switch

---

## Security Model

Zemi implements:

- AES-256 (Fernet) encrypted credential vault
- Tiered trust enforcement (Tier 0–3)
- Mandatory approval for destructive actions
- Structured logging of all routed actions
- No direct filesystem access for skills
- No auto-approval mechanisms
- Local-only AI inference via Ollama

---

## Internal API Contract

Example endpoints:

POST /route  
GET /status  
GET /logs  
POST /safe-mode  
POST /kill-switch  
POST /snapshot  
POST /skills/install  
POST /skills/enable  

All endpoints authenticated and logged.

---

## Tech Stack

- Python
- FastAPI
- Ollama (Llama 3.1 / Mistral fallback)
- Docker / Colima
- Slack API (Socket Mode)
- Tailscale VPN
- Fernet (AES-256 encryption)

---

## Status

Active development project focused on secure AI execution control systems and local-first infrastructure design.

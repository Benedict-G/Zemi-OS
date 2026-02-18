# Zemi V1 - Learning Notes

## Project Overview
Building a local AI assistant (Zemi V1) on Mac Mini M4
- Security-first architecture
- No external AI APIs
- Complete control and privacy

---

## Technologies Learned

### Python
- Virtual environments (venv)
- Async/await patterns
- Package management (pip)
- Libraries: ollama, matrix-nio, cryptography, TinyDB

### Docker
- Container management
- Docker Compose
- Volume mounting
- Network isolation

### Linux/macOS
- Terminal/bash commands
- File permissions (chmod)
- SSH remote access
- Process management

### AI/LLM
- Ollama (local LLM hosting)
- Llama 3.2 model
- Prompt engineering
- Intent classification

### Networking
- Tailscale VPN
- Matrix protocol
- HTTPS/SSL certificates
- Port management

---

## Key Commands Reference

### Docker
```bash
docker ps                    # List running containers
docker logs [container]      # View logs
docker exec -it [name] bash  # Enter container
docker-compose up -d         # Start services
```

### Zemi Operations
```bash
cd ~/ZemiV1/core
source ../venv/bin/activate  # Activate Python env
python zemi_main.py          # Start Zemi
```

### Tailscale
```bash
tailscale status    # Check connection
tailscale ip -4     # Get IP address
```

---

## Phase Completion Log

### ✅ Phase 1-11: Infrastructure
- Ollama, Docker, Matrix, Tailscale all operational
- Voice stack ready
- Vault encrypted

### ✅ Phase 12: Orchestrator (In Progress)
**What I learned:**
- Async Python patterns
- Matrix message handling
- Encryption challenges (E2EE rooms)
- Event loop debugging

**Challenges solved:**
- Docker launch issues on macOS
- Matrix authentication 
- Rate limiting
- Encrypted vs unencrypted rooms

**Current issue:**
- Capabilities response not triggering properly

---

## Troubleshooting Solutions

### Issue: Docker won't start
**Solution:** Use Docker Desktop app directly, not brew services

### Issue: Matrix login failed
**Solution:** Create fresh user with known password

### Issue: Messages not syncing
**Solution:** Manual polling loop + check for encrypted rooms

---

## Next Steps
- [ ] Fix orchestrator capabilities
- [ ] Complete Phase 13-15
- [ ] Add skills system
- [ ] Encrypted room support

---

## Resources
- Matrix Spec: https://spec.matrix.org
- Ollama Docs: https://ollama.ai
- Docker Docs: https://docs.docker.com

---

*Last updated: February 15, 2026*

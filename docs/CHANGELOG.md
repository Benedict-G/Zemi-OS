# Zemi Changelog

All notable changes to Zemi will be documented in this file.

## [1.0.0] - 2026-02-15

### Added
- Initial stable release
- Ollama integration with Llama 3.2:3b model
- Matrix Synapse self-hosted server
- Element X mobile client support
- Encrypted credential vault (AES-256)
- Permission-based execution system (4 levels)
- Comprehensive audit logging
- Automated encrypted backups (weekly cron)
- Voice stack (Whisper STT + Coqui TTS)
- HTTPS web dashboard
- Tailscale VPN integration
- Remote SSH access
- Skills system framework
- Auto-start via shell profile
- Minimal firewall with stateful tracking

### Security
- Air-gapped AI processing (no external APIs)
- End-to-end encryption for Matrix
- Encrypted vault with Fernet
- No public ports exposed
- Human approval for Level 2+ actions
- Complete audit trail with timestamps

### Infrastructure
- Docker containerization via Colima
- Isolated browser container (Playwright)
- Proton Bridge configured (not integrated)
- Matrix server with federation disabled
- Backup system with 7-day rotation

### Known Issues
- LaunchAgent not working on macOS 26.3 beta
- Firewall minimal due to Colima compatibility
- E2EE Matrix rooms unsupported (python-olm compilation fails)
- Auto-start requires manual login (not true boot startup)

---

## [1.1.0] - 2026-02-16 (Planned)

### Added
- Web browsing integration via Brave Search
- Email automation via Proton Bridge
- Enhanced skills: web_search.md, email_compose.md
- Skill-based AI context injection

### Changed
- Orchestrator now loads skills on startup
- AI prompts include relevant skill instructions
- Better intent analysis with skill context

### Fixed
- Skills system fully operational
- Rate limit handling improved

---

## [1.2.0] - 2026-02-17 (Planned)

### Added
- Proton Calendar integration (CalDAV)
- Notion API integration
- Task management integration
- Note-taking via filesystem
- Slack integration
- Telegram integration
- RSS feed reader
- Read-it-later service integration

### Changed
- Expanded skills library
- More productivity-focused automation

---

## [2.0.0] - TBD (Future)

### Added (Potential)
- Multi-user support
- Multiple AI model backends
- E2EE Matrix room support
- Cloud hybrid architecture
- Web-based configuration UI
- Native mobile app

### Breaking Changes
- Database schema updates
- API changes
- Configuration format changes

---

*Format: [MAJOR.MINOR.PATCH]*
*MAJOR: Breaking changes*
*MINOR: New features, backwards compatible*
*PATCH: Bug fixes, no new features*


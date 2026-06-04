# Changelog

All notable changes to the **LPU AI Academic Advisor** project will be documented in this file.

## [1.1.0] - 2026-06-04
### Added
- **Quantum Bridge Architecture:** Implemented a strictly zero-interaction server-side AI synthesis bridge using Puter API.
- **Automated Seeding:** Professional data seeding for Aiven PostgreSQL from local CSV sources.
- **Enhanced E2E Suite:** Comprehensive end-to-end testing suite with 100% pass rate.
- **Security Templates:** Professional GitHub issue and pull request templates.

### Changed
- **Unified Configuration:** Standardized environment variable naming to `PUTER_TOKEN`.
- **Robust Env Loading:** Switched to `load_dotenv(override=True)` for consistent configuration management.
- **Documentation Overhaul:** Updated README, Architecture, and Setup guides to reflect the "Quantum Edition" status.

### Fixed
- **Database Connection:** Resolved line-break issues in `.env` and optimized SSL/TLS connectivity for Aiven.
- **Bypass Logic:** Eliminated all user-facing Puter login prompts through backend orchestration.

## [1.0.0] - 2026-06-02
### Added
- Initial release of the LPU Academic Advisor Chatbot.
- Integration with Streamlit for UI and Aiven for PostgreSQL.
- Basic intent detection and knowledge base retrieval.

# WondrChat Version History

| Version | Date | Summary |
|---------|------|---------|
| [v2.1](v2.1/RELEASE.md) | April 2026 | HIPAA de-identification, hybrid RAG, mental health dashboard, symptom tracking, survivorship schedules, PREMM5, nutrition |
| [v2.0](v2.0/RELEASE.md) | March 2026 | Full platform with 13 clinical feedback items, 20-doc KB, 4 screening instruments, clinical trials integration |

## Deferred: React + Vite Migration

Planned but on hold. The frontend is a 7,800+ line monolithic HTML file. Migration to React + Vite with shadcn/ui is recommended when:
- An accessibility audit is required for a partnership
- Feature velocity is slowed by the monolithic file
- A second developer joins the project

Approach: Strangler fig pattern over 16 weeks. See [v2.1 improvement roadmap](../WondrChat_Research_Brief.md) Area 4 for full plan.

# {{project_name}} — /beginners-mind profile

> **About this file.** This profile is the project's pact with the `/beginners-mind` skill. The two H2 sections below are read with _different access rules_: the **Visible to fresh observer** section is shared with the Phase 3 fresh-observer subagent; the **Orchestrator only** section is _never_ passed to that subagent. The skill enforces this split.

## Visible to fresh observer

- **Scope:** {{scope_paths_comma_separated}}
- **Out of scope:** {{exclude_paths_comma_separated}}
- **Behavioral signal sources:** {{signal_sources_comma_separated}}
- **Corpus location:** {{corpus_path}}
- **State location:** {{state_path}}
- **Cadence:** {{cadence_days}}
- **Token budget:** {{token_budget}}
- **What to watch for:** {{owner_standing_concerns}}
- **What to skip:** {{owner_anti_recs}}

## Orchestrator only — do not include in fresh-observer subagent context

- **Design history pointers:** {{design_doc_pointers}}
- **Known-weird-but-intentional choices:** {{intentional_quirks}}
- **Decisions log:** {{decisions_log}}

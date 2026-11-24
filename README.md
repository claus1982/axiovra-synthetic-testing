# AXIOVRA Synthetic Testing

Independent open-source experiment for goal-driven Android UI testing. The public project tests its own generic harness against an Android emulator's built-in Settings app. No proprietary applications, binaries, credentials, or product evidence belong here.

## Run
In Actions, choose **Android demo** and Run workflow. `smoke` (default) validates emulator + independent UI oracle without any AI calls. `agent` uses Mobilerun with Gemini; before enabling it, provision a dedicated free-tier-only API project with billing disabled, set repository secret GOOGLE_API_KEY and variable GEMINI_FREE_TIER_CONFIRMED=true, and set GEMINI_MODEL to a currently free-tier eligible model. No paid provider or fallback is configured. API quotas and provider terms apply; a step limit is not a monetary guarantee.

The experimental `local` mode runs Qwen3.5 2B via Ollama on the ephemeral cloud runner, with cloud inference disabled and no API key. This is a bounded CPU feasibility probe, not a performance claim. The model must pass the same independent oracle; no fallback to a paid API.

The agent receives a goal rather than click instructions. An independent UI assertion checks the actual result. The public artifact contains only a demo screenshot and a small JSON report. A failed assertion fails the run.

## Boundaries
Public workflows are for developing and testing this public project, not a proxy for private CI. Proprietary targets require separately authorized compute, private evidence and appropriate AI data-handling terms. No private app integration is enabled here. Never add private APKs, maps credentials or real user data.

## Local checks
`python -m unittest discover -s tests`

Mobilerun: https://github.com/droidrun/mobilerun (upstream dependency).

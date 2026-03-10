# Reddit Research — Tasks

## Friday PM (1 hour — OpenClaw use case review)

- [ ] **Crow MCP platform** — persistent memory + P2P sharing as MCP servers. Compare to Clawtex architecture. What did they solve differently?
  - https://reddit.com/r/LLMDevs/comments/1rnte6v/i_built_an_opensource_mcp_platform_that_adds/
- [ ] **Mic + Chief of Staff pipeline** — passive audio → OpenClaw → actionable outputs. Almost identical to our setup. Compare approaches, note the privacy-for-local argument (Clawtex positioning).
  - https://reddit.com/r/LocalLLaMA/comments/1rmqxa7/i_wear_a_mic_all_day_and_feed_transcripts_to_an/
- [ ] **218 OpenClaw tools directory** — quick scan for anything Clawdia/Clawtex should have. Don't rabbit-hole.
  - https://reddit.com/r/openclaw/comments/1rmgt2m/i_went_through_218_openclaw_tools_so_you_dont/

## Parked (review if time)

- AMI maturity audit rubric — run against Clawdia as baseline
- OpenClaw enforcement layer (Substack article) — hardening patterns
- 13-agent Claude team — multi-agent coordination patterns

## Backlog

- [ ] Set up cron/launchd for twice-weekly scheduled scans (Mon + Thu 08:00)
- [ ] Wire up email sending (Gmail MCP) for digest delivery
- [ ] Tighten scoring — recency weighting too aggressive for initial lookback runs

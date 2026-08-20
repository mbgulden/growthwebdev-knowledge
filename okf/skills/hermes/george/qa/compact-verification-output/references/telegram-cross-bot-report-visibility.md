# Telegram cross-bot report visibility

## Lesson

When Hermes helper agents are running as Telegram bots in the same group, a proof packet posted by one bot may be visible to the human operator but not delivered into another bot's Hermes session. A reviewer bot should not assume it can react to bot-authored messages just because they appear in the group UI.

This matters for Prismatic Fred/Ned/AGY/Kai workflows where George is expected to review compact proof packets from other bot profiles.

## Durable contract

Every cross-agent proof/report prompt should require both:

```text
POST_COMPACT_PROOF_IN_CHAT=required
WRITE_SAME_PACKET_TO_ARTIFACT=required
ARTIFACT_PATH=<shared/repo path keyed by marker>
```

Recommended path shape for Prismatic lanes:

```text
~/.hermes/prismatic/<agent>-reports/<MARKER>.md
```

A repo artifact, CI artifact, or JSON status file is also acceptable if the reviewer can independently read it.

## Review procedure

1. If the operator says another bot posted a result but the reviewer bot cannot see it, do not challenge the operator's observation.
2. Explain the ingestion boundary briefly: the reviewing bot did not receive the bot-authored message.
3. Ask for one of:
   - human paste/forward/reply-copy of the packet, or
   - artifact path / repo artifact / status JSON.
4. Independently inspect the artifact before accepting the proof.
5. Report with explicit boundary:

```text
AD_HOC_OR_CANONICAL=<ad-hoc targeted|live supervisor artifact|canonical suite>
NOT_CLAIMING=<canonical full-suite green, production proof, browser proof, etc.>
```

## Prompt snippet

```text
Return your compact proof packet in this Telegram group AND write the exact same packet to:
<ARTIFACT_PATH>

George may not receive bot-authored Telegram messages directly, so the artifact is required for independent review.
```

## Pitfall

Do not treat “posted in Telegram” as durable evidence for bot-to-bot review. Human-visible chat is not the same as reviewer-session-visible input.

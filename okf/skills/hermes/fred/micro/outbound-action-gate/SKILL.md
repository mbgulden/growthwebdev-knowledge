---
name: outbound-action-gate
description: The hard rule that only Michael sends/publishes/records. Agents may draft and package, but may not send, publish, record, or mark anything as sent without explicit confirmation. This is a gate, not a preference.
---

# outbound-action-gate

## The rule

Outbound actions — anything that leaves the agent's local context and reaches the outside world — require Michael's explicit confirmation:

- **Send**: email, message, Slack post, Telegram message (when going to a third party), SMS, etc.
- **Publish**: blog post, social media post, public doc, public comment.
- **Record**: video, audio, screenshot capture, screen recording.
- **Mark sent/published/recorded**: any state change that says "this was sent/published/recorded" without Michael's explicit "yes, send it" or "yes, publish it" or "yes, record it" confirmation.

## What agents MAY do without confirmation

- **Draft**: write the artifact (email body, post text, recording script) locally.
- **Package**: prepare the artifact (attachments, formatting, scheduling).
- **Preview**: render the artifact for review.
- **Suggest**: present the artifact and ask "shall I send this?"

## What agents MAY NOT do without confirmation

- Send the email.
- Post the message.
- Publish the blog post.
- Record the video.
- Update any state field to say "sent", "published", "recorded", "delivered", or "completed" for an outbound action.

## Why this is a hard rule

Once something is sent/published/recorded, it's out. You can't un-send. Michael needs the gate because:
- The agent's sense of "ready to send" may not match Michael's.
- The agent may not see context Michael has (timing, audience, sensitivity).
- The cost of confirmation is one message; the cost of a mis-send is reputational.

## Anti-patterns

- "It looked ready so I sent it."
- "I marked it sent and Michael can correct if needed." (Marking sent is itself the action.)
- "It was an urgent-looking draft so I figured Michael would want it out." (Ask, don't assume.)

## Verification

Every outbound action has a corresponding confirmation message from Michael in the conversation. State fields that imply "sent" are only updated after confirmation.

# HDE guest runtime: strict name capture, richer chart insight, Telegram Markdown fallback (2026-07)

## Trigger

Use this reference when HDE/George/the guide gets stuck in chart/profile intake, creates fake people from ordinary phrases, returns shallow chart facts, or Telegram live delivery fails with Markdown entity parse errors.

## Durable lessons

### 1. Name capture must be conservative

The bug class was loose regex capture after words like `for`, `under`, or `named`. A sentence such as:

```text
Build a chart for the stinking little chart born 06/14/1990 at 9:30 AM in Boise, Idaho
```

must **not** create a person/profile named `the_stinking_little_chart`.

Preferred runtime pattern:

- New chart labels require a real-looking first + last name, usually 2–4 capitalized tokens.
- One-token names are allowed only when they already match a stored profile.
- Reject ordinary phrases containing chart/bodygraph/report/profile/birth/phrase/sentence/words/stinking/random/etc.
- If a loose phrase appears where a name should be, ask for a first + last name or tell the user to say `my chart`.

User-facing repair line that tested well:

```text
I won’t create or update a profile from a loose phrase. Give me the person’s first and last name, or say “my chart” if this is for you.
```

### 2. Slot clipboard beats rigid wizards

The runtime should parse any slots the user already gave — name, date, time, location — and ask only for the missing piece. Do not force first date, then time, then location when the user already supplied all or most of it.

Natural profile edits should work when the target profile is clear:

```text
Canary Guest birth time is 7:45 AM
```

That should update the profile, rebuild the chart, and return PDF metadata without asking `what do you want to edit?`.

### 3. Chart output needs an insight layer

The stock anchors are necessary but not sufficient:

- Type
- Strategy
- Authority
- Profile

Append a short interpretive first-read layer that includes:

- where Strategy/Authority becomes practical pressure,
- signature vs not-self as an everyday dashboard,
- profile as a learning style, not a personality box,
- reliable defined centers,
- likely conditioning pressure from undefined/open centers,
- one concrete channel/cross clue when available,
- one best next practical step.

Canary marker:

```text
A more useful first read:
```

### 4. Guard against canary profile pollution

One regression polluted `michael_gulden` with canary birth data. Verification must check that Michael’s canonical profile remains:

```text
1989-12-10 17:07 Simi Valley, CA
Projector / Splenic / 3/5
```

When a canary isolates the people index, make sure all modified profile/index state is restored, not only fake canary folders removed.

### 5. Telegram Markdown parse fallback

Live Telegram watcher found sends failing with:

```text
Bad Request: can't parse entities: Can't find end of the entity...
```

Router text delivery should try Markdown first for rich rendering, then retry the same text as plain text if Telegram rejects entity parsing. Do not let a useful guide answer disappear because Telegram disliked underscores or punctuation.

Implementation shape:

```python
resp = await client.post(sendMessage, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
if resp.status_code != 200 and "parse" in resp.text.lower():
    await client.post(sendMessage, json={"chat_id": chat_id, "text": text})
```

## Verification pattern

Use both canonical and focused proof:

```bash
python3 -m py_compile /home/ubuntu/guest_hermes_bot/guest_agent_server.py \
  /home/ubuntu/work/hd-platform-staging/scripts/hde_guest_canary.py \
  /home/ubuntu/work/hd-platform-staging/scripts/hde_tenant_router.py

cd /home/ubuntu/work/hd-platform-staging
npm run build
python3 scripts/hde_guest_canary.py --guest-id 23 --pretty
```

Focused `/tmp/hermes-verify-*` script should assert:

- live guest runtime matches template,
- invalid phrase-as-name direct API request is rejected,
- no chart is generated for that invalid phrase,
- canary covers `exercise_name_capture_guard`, richer chart insight, and natural profile edit,
- router has Markdown parse fallback,
- `guest-hermes-23` is healthy,
- `hde_router.service` is active,
- Michael profile stayed restored after canary.

This remains server-side/ad-hoc proof. Live Telegram proof still requires a real user/tester message.
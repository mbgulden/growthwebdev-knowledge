# HDE payment server systemd import/path pitfall — 2026-07

Session lesson from production deployment of shared HDE email theme into `payment/server.py`.

## Failure mode

`payment/server.py` compiled successfully from the repo root, but `hde-payment.service` crashed under systemd:

```text
ModuleNotFoundError: No module named 'shared'
```

Cause: the service executes `/usr/bin/python3 /home/ubuntu/work/hd-platform/payment/server.py`. In that shape, Python places `payment/` on `sys.path`, not the repository root, so sibling imports like `from shared.hde_email_theme import ...` fail unless the repo root is added explicitly or the unit sets `PYTHONPATH`.

## Fix pattern

At the top of standalone scripts under subdirectories that import sibling packages, add the repo root before sibling imports:

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.hde_email_theme import attach_themed_alternative, build_report_email
```

Alternative: set `Environment=PYTHONPATH=/home/ubuntu/work/hd-platform` in the systemd unit. Prefer the script-local guard when the script is already a standalone entrypoint.

## Verification

After deploying changes to `payment/server.py`:

1. Run `python -m py_compile payment/server.py` from the intended runtime env.
2. Restart `hde-payment.service`.
3. Check `systemctl is-active hde-payment.service`.
4. Check recent journal for `ModuleNotFoundError` or Stripe exceptions.
5. Smoke same-origin checkout with a valid payload; expect a live Stripe Checkout URL (`cs_live_...`) but do not complete payment.

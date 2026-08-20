# HDE demo production promotion — lane-safe systemd templates

Session learning from HDE demo-flow production promotion.

## Durable pattern

Ned's HD Platform push guard rejects tracked files under `deploy/systemd/*` as out-of-lane. For Ned-owned operational templates, keep the repository source under a Ned-owned lane such as:

```text
scripts/systemd/<unit>.service
scripts/systemd/<unit>.timer
```

Then document the install step separately:

```bash
sudo cp scripts/systemd/hde_demo_trial_lifecycle.service /etc/systemd/system/
sudo cp scripts/systemd/hde_demo_trial_lifecycle.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now hde_demo_trial_lifecycle.timer
```

## Gate-script requirement

Gate/check scripts should not hardcode `deploy/systemd`. Add an environment-configurable template directory, e.g.:

```text
HDE_DEMO_SYSTEMD_TEMPLATE_DIR=${HDE_DEMO_SYSTEMD_TEMPLATE_DIR:-$REPO_ROOT/scripts/systemd}
```

Use env overrides for staging vs production timer names and template prefixes so the same gate can validate staging evidence while defaulting to production names before install.

## Verification pattern

After moving templates into lane:

1. `git diff --check`
2. `systemd-analyze verify scripts/systemd/*.service scripts/systemd/*.timer`
3. Compile changed Python gate/reminder scripts.
4. Run the production gate twice when relevant:
   - with staging overrides: expected `PASS` if staging evidence is installed;
   - with defaults: expected `BLOCKED` before production timers/evidence are installed.
5. Push normally; do not bypass the lane guard.

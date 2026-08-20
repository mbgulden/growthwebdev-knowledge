# 2026-07 HDE Google OAuth: GA4/GTM/GSC/Site Verification

## Why this matters

During an HDE audit follow-up, Michael pointed out that Kai had Google auth info available. The durable lesson is that “Google auth” had multiple layers:

- Kai/AGY could authenticate to Google as Michael.
- Kai profile had gcloud config files, but no usable ADC `application_default_credentials.json` for this task.
- A global ADC existed and refreshed, but only had the Search Console/Webmasters scope.
- The HDE reusable marketing-stack token did not exist yet.
- A Google OAuth client secrets file existed outside git and could generate the required consent URL.

A raw AGY/Kai auth check was therefore insufficient for GA4/GTM/GSC/Site Verification work.

## Required full-stack scopes used

```text
https://www.googleapis.com/auth/analytics.edit
https://www.googleapis.com/auth/analytics.readonly
https://www.googleapis.com/auth/tagmanager.edit.containers
https://www.googleapis.com/auth/tagmanager.manage.accounts
https://www.googleapis.com/auth/tagmanager.readonly
https://www.googleapis.com/auth/webmasters
https://www.googleapis.com/auth/siteverification
```

## Reusable script pattern

A project script generated, exchanged, and verified OAuth without printing tokens:

```bash
cd /home/ubuntu/work/hd-platform-GRO-3988
python3 scripts/google-oauth-scope-flow.py url
python3 scripts/google-oauth-scope-flow.py exchange --code '<returned-code-or-localhost-redirect-url>'
python3 scripts/google-oauth-scope-flow.py verify
```

The script saved the authorized-user token outside git:

```text
/home/ubuntu/.config/hde-google-oauth/analytics-tagmanager-searchconsole.json
```

Safe report fields:

- token path
- file permissions
- authenticated email when available
- present/missing scopes
- API probe status

Never report raw `access_token`, `refresh_token`, `client_secret`, or full credential JSON.

## Localhost redirect gotcha

The user may paste a redirect like:

```text
localhost/?iss=https://accounts.google.com&code=...&scope=...
```

If the exchange helper reports `invalid_grant` / malformed auth code from the full redirect, extract only the `code` parameter and retry the exchange before declaring the code bad.

## Verification result pattern

Successful scope verification looked like:

```text
saved_token_path=/home/ubuntu/.config/hde-google-oauth/analytics-tagmanager-searchconsole.json
missing_required_scopes=[]
permissions=-rw-------
```

That proves OAuth consent/scopes, not API usability.

## Next blocker discovered

Live probes then returned HTTP 403 API-disabled errors for the OAuth client project. This is a different layer from OAuth and should be reported that way.

APIs to probe/enable for full stack:

```text
analyticsadmin.googleapis.com
 tagmanager.googleapis.com
searchconsole.googleapis.com
siteverification.googleapis.com
```

Console URL shape:

```text
https://console.developers.google.com/apis/api/<API_NAME>/overview?project=<PROJECT_ID_OR_NUMBER>
```

Example project from this session was `772364335560`; do not hardcode that for other customers/sites without re-reading current client credentials or API error output.

## Report wording to preserve

Good:

```text
OAuth exchange worked and the token has all required scopes. New blocker: the Google APIs are disabled on the OAuth client project. Auth is good; project services are not.
```

Bad:

```text
Google auth is fixed, so the HDE Google stack is ready.
```

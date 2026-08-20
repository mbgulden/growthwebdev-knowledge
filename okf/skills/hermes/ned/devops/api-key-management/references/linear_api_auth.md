## Linear API Authentication Quirks

When interacting with the Linear API, pay close attention to the `Authorization` header format.

*   **API Keys:** If using a Linear API key, do NOT prepend `Bearer ` to the key in the `Authorization` header. The API expects the raw API key directly.
    *   Correct: `Authorization: lin_api_***`
    *   Incorrect: `Authorization: Bearer lin_api_***`

*   **OAuth Tokens:** If using an OAuth token, the `Bearer ` prefix is typically required.

Always ensure the `Content-Type: application/json` and `X-Apollo-Operation-Name` (e.g., `IssueDetails`) headers are also set to avoid CSRF and `BAD_REQUEST` errors.
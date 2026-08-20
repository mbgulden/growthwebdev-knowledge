---
name: agy-google-api-operations
description: Interact with Google Sheets, Docs, and Drive using MCP tools or Google APIs.
version: 1.0.0
---

# AGY Google API Operations

Query, search, read, and write document data inside Google Drive and Google Sheets.

## Trigger Conditions

Use when importing/exporting spreadsheet data, searching documents, or generating reports.

## Numbered Steps with Exact Commands

1. **Search for documents in Google Drive**:
   Use lazy-loaded `drive_search` MCP tool:
   ```json
   {
     "ServerName": "gdrive",
     "ToolName": "drive_search",
     "Arguments": {
       "query": "name contains 'Leads'"
     },
     "toolSummary": "Search Drive for Leads sheet",
     "toolAction": "Searching Google Drive"
   }
   ```

2. **Read Spreadsheet cells**:
   Use lazy-loaded `sheets_read` MCP tool:
   ```json
   {
     "ServerName": "gdrive",
     "ToolName": "sheets_read",
     "Arguments": {
       "spreadsheetId": "TARGET_SPREADSHEET_ID",
       "range": "Sheet1!A1:D10"
     },
     "toolSummary": "Read Google Sheet content",
     "toolAction": "Reading Google Sheet"
   }
   ```

3. **Verify document metadata**:
   Read document details to check modifications:
   ```json
   {
     "ServerName": "gdrive",
     "ToolName": "drive_about",
     "Arguments": {},
     "toolSummary": "Check Drive credentials",
     "toolAction": "Querying Drive metadata"
   }
   ```

## Pitfalls

- **Incorrect ranges**: Ensure sheet names match exactly (including spacing and capitalization).
- **Authentication errors**: If MCP tools return auth errors, verify tokens are active or refresh Google OAuth settings.

## Verification Steps

- Confirm tool execution results return structured rows/cells or document content lists.

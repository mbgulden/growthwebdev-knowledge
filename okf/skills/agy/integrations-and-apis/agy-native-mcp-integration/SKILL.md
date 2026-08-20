---
name: agy-native-mcp-integration
description: Query and interact with Model Context Protocol (MCP) servers.
version: 1.0.0
---

# AGY Model Context Protocol Integration

Call external integrations and microservice tools using the MCP specifications.

## Trigger Conditions

Use this skill when accessing data sources or systems that have native MCP server interfaces (such as Google Drive, Sheets, or Custom scripts).

## Numbered Steps with Exact Commands

1. **Inspect available MCP tools**:
   Call list resource or check configuration schema files under the CLI config.

2. **Invoke a target tool**:
   Formulate the tool call with parameters:
   ```json
   {
     "ServerName": "gdrive",
     "ToolName": "drive_about",
     "Arguments": {},
     "toolSummary": "Verify Drive credentials",
     "toolAction": "Calling drive about tool"
   }
   ```

3. **Handle server responses**:
   Check returned schemas and parse content output.

## Pitfalls

- **Server Not Found**: If calling a tool on an inactive server, ensure the server name matches spelling exactly.
- **Incorrect Arguments**: MCP parameters are strictly validated by JSON schemas. Check schema docs on error.

## Verification Steps

- Call the list resources tool on a target server:
  ```json
  {
    "ServerName": "gdrive",
    "toolSummary": "List Drive resources",
    "toolAction": "Listing server resources"
  }
  ```
  Verify it returns the resource list successfully.

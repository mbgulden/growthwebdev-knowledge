---
type: Reference
title: "Agy Local Agent Architecture"
description: "Mirrored from Google Drive on 2026-06-25. Source: Drive file 1bek7q4ReXJbt6LFpDJLs3LQKRQxQbVYR1qmBNZ06vwI (modified 2026-06-08). Originally part of the Prismatic source plugin plans and AGY architecture reports."
resource: https://docs.google.com/document/d/1bek7q4ReXJbt6LFpDJLs3LQKRQxQbVYR1qmBNZ06vwI/edit?usp=drivesdk
tags: [drive-mirror, prismatic, gemini-evaluation, agy-report, source-plugin-plans]
timestamp: 2026-06-25T04:04:37.756Z
git_repo: mbgulden/growthwebdev-knowledge
linear_issue: TBD
last_verified: 2026-06-25
verified_by: fred
status: current
drive_file_id: "1bek7q4ReXJbt6LFpDJLs3LQKRQxQbVYR1qmBNZ06vwI"
drive_modified: "2026-06-08T10:10:43.466Z"
---

\# Prismatic Engine Spec — Local Agent Architecture  
\*\*Linear Issue:\*\* \[GRO-822\](https://linear.app/growthwebdev/issue/GRO-822)    
\*\*Author:\*\* Antigravity Senior Systems Architect    
\*\*Date:\*\* June 8, 2026    
\*\*Status:\*\* Under Review

\---

\#\# 1\. Local Agent Integration Model

To integrate local models as first-class, "forever" workers alongside cloud API agents (like Claude/GPT), the Prismatic Engine uses the \*\*Local Agent Interface\*\*. 

Instead of treating local models as special cases, the engine abstracts the LLM host (Ollama, vLLM, LM Studio) behind a standard provider wrapper. The local agent receives a signal payload, executes its reasoning loop locally, interacts with tools, and posts completion signals.

\!\[Local Agent Pipeline\](file:///home/ubuntu/work/prismatic-engine/reports/images/local\_agent\_architecture.svg)

\#\#\# 1.1 Configuration Scheme (\`config/local\_agents.yaml\`)  
Local agents are defined in the engine config registry:

\`\`\`yaml  
version: 2  
local\_agents:  
  \- name: "local-proofreader"  
    provider: "ollama"  
    model: "qwen2.5:7b-instruct-q5\_K\_M"  
    endpoint: "http://localhost:11434"  
    context\_window: 8192  
    temperature: 0.1  
    max\_steps: 5  
    capabilities: \["proofreading", "markdown-audit"\]  
    system\_prompt: |  
      You are a senior proofreader. Analyze the provided file path, identify spelling/grammar issues,  
      and correct them using the file\_write tool. Always maintain the original document style.  
    tools:  
      \- "file\_read"  
      \- "file\_write"

  \- name: "local-coder"  
    provider: "vllm"  
    model: "Qwen/Qwen2.5-Coder-32B-Instruct"  
    endpoint: "http://localhost:8000/v1"  
    context\_window: 32768  
    temperature: 0.2  
    max\_steps: 15  
    capabilities: \["code-writer", "bug-fixer"\]  
    system\_prompt: |  
      You are an elite software engineering agent. Read the task specification, search the codebase,  
      modify files to implement the request, run tests, and output a detailed diff.  
    tools:  
      \- "file\_read"  
      \- "file\_write"  
      \- "grep\_search"  
      \- "run\_command"  
\`\`\`

\---

\#\# 2\. Abstract Python Interface (\`prismatic/agents/local.py\`)

Every local agent is managed by the \`LocalAgent\` class, which implements the standard execution lifecycle:

\`\`\`python  
import json  
import requests  
from typing import Dict, List, Any  
from prismatic.agents.base import BaseAgent  
from prismatic.tools.registry import execute\_tool

class LocalAgent(BaseAgent):  
    def \_\_init\_\_(self, config: Dict\[str, Any\]):  
        self.name \= config\["name"\]  
        self.provider \= config\["provider"\]  \# "ollama" or "vllm" (OpenAI-compatible)  
        self.model \= config\["model"\]  
        self.endpoint \= config\["endpoint"\]  
        self.context\_window \= config.get("context\_window", 8192\)  
        self.temperature \= config.get("temperature", 0.2)  
        self.max\_steps \= config.get("max\_steps", 10\)  
        self.system\_prompt \= config\["system\_prompt"\]  
        self.tools \= config.get("tools", \[\])

    def execute\_task(self, task\_payload: Dict\[str, Any\]) \-\> Dict\[str, Any\]:  
        """Main agent execution loop."""  
        messages \= \[  
            {"role": "system", "content": self.system\_prompt},  
            {"role": "user", "content": json.dumps(task\_payload)}  
        \]  
          
        step \= 0  
        while step \< self.max\_steps:  
            step \+= 1  
            \# 1\. Fetch next token generation / tool choice from model  
            response \= self.\_query\_llm(messages)  
            messages.append(response)  
              
            \# 2\. Check if the model requested a tool call  
            if "tool\_calls" in response and response\["tool\_calls"\]:  
                for tool\_call in response\["tool\_calls"\]:  
                    tool\_name \= tool\_call\["name"\]  
                    tool\_args \= tool\_call\["arguments"\]  
                      
                    \# Security check: Ensure tool is in the agent's allowed list  
                    if tool\_name not in self.tools:  
                        tool\_result \= f"Error: Tool '{tool\_name}' is not authorized for this agent."  
                    else:  
                        \# Execute the tool locally on the workspace  
                        tool\_result \= execute\_tool(tool\_name, tool\_args)  
                      
                    \# Append tool response to context  
                    messages.append({  
                        "role": "tool",  
                        "name": tool\_name,  
                        "content": str(tool\_result),  
                        "tool\_call\_id": tool\_call.get("id")  
                    })  
            else:  
                \# Loop terminates when the model returns a final text answer without tool calls  
                return {"status": "SUCCESS", "result": response\["content"\]}  
                  
        return {"status": "FAILED", "error": "Exceeded max execution steps budget."}

    def \_query\_llm(self, messages: List\[Dict\[str, str\]\]) \-\> Dict\[str, Any\]:  
        """Bridges differences between Ollama and OpenAI-compatible vLLM formats."""  
        if self.provider \== "ollama":  
            url \= f"{self.endpoint}/api/chat"  
            payload \= {  
                "model": self.model,  
                "messages": messages,  
                "options": {"temperature": self.temperature},  
                "stream": False  
            }  
            \# Parse tool definitions into Ollama format...  
            res \= requests.post(url, json=payload).json()  
            return res\["message"\]  
        else:  
            \# Standard OpenAI chat completion format for vLLM / LM Studio  
            url \= f"{self.endpoint}/chat/completions"  
            payload \= {  
                "model": self.model,  
                "messages": messages,  
                "temperature": self.temperature,  
            }  
            res \= requests.post(url, json=payload).json()  
            return res\["choices"\]\[0\]\["message"\]  
\`\`\`

\---

\#\# 3\. Practical Workflows

\#\#\# 3.1 Today's Practical Workflows (June 2026\)

The table below outlines the 5 workflows that run reliably on local hardware today:

| Workflow | Min VRAM | Recommended Model | Replacement Goal | Setup Complexity |  
|---|---|---|---|---|  
| \*\*Content Proofreader\*\* | 8 GB | Qwen 2.5 7B Q5\_K\_M | Replaces human proofreading & Claude-3-Haiku API calls for simple docs | Low |  
| \*\*Structured Log Extractor\*\*| 12 GB | Qwen 2.5 14B Q4\_K\_M | Converts raw text logs into structured JSON datasets | Low-Medium |  
| \*\*Local RAG Doc Assistant\*\* | 16 GB | Llama 3.1 8B FP16 | Fast, offline vector query over local specs & code bases | Medium |  
| \*\*Code Auditor & Reviewer\*\* | 24 GB | Qwen 2.5 Coder 32B Q5\_K\_M | Automates initial code reviews, checking syntax and imports | Medium |  
| \*\*Bulk Issue Classifier\*\* | 8 GB | Llama 3.1 8B Q4\_K\_M | Labels incoming tasks based on description keywords | Low |

\* \*\*Content Proofreader Workflow:\*\* Triggered when a markdown file is changed. The \`local-proofreader\` reviews spelling, grammar, and style, then writes corrected files back to disk.  
\* \*\*Code Auditor Workflow:\*\* Spawns when a git commit is made. The agent runs tests, parses the file diffs, and inserts a review comment outlining potential bugs or performance bottlenecks.  
\* \*\*Local RAG Doc Assistant:\*\* Reads all system specifications, indexes them into a local SQLite-based vector store (using chroma or faiss), and answers developer queries offline.

\#\#\# 3.2 Future Workflows (Late 2026 / 2027\)

As models achieve better logical reasoning and speed, the engine will run:

1\. \*\*Self-Healing Code Loops:\*\* The local coder is hooked up to a compiler/test runner. If a test fails, the model reads the stack trace, modifies the code, and reruns the test in a loop until it passes.  
2\. \*\*Air-Gapped Compliance Pipeline:\*\* Scans codebases and documents for secrets, proprietary keys, and GDPR/CCPA violations without sending data outside the local network.  
3\. \*\*Cost-Free R\&D Agents:\*\* Runs multi-agent simulations (e.g. Monte Carlo search for optimal algorithms) overnight, generating thousands of candidate solutions at zero API cost.  
4\. \*\*Dynamic Hybrid Routing:\*\* A fast classifier agent evaluates the difficulty of incoming issues. If the task is simple (formatting, tests), it routes it to a local worker. If it is high-complexity, it routes to a cloud API (Claude 3.5 Sonnet).

\---

\#\# 4\. Michael's Hardware Optimization (192GB VRAM Setup)

Michael’s setup consists of \*\*two servers, each containing 96GB VRAM\*\*. This offers a massive 192GB total pool of fast memory, allowing us to run frontier-class models locally. We propose three configuration designs:

\!\[Michael's Setup Configuration\](file:///home/ubuntu/work/prismatic-engine/reports/images/michael\_setup.svg)

\#\#\# 4.1 Configuration Option Comparison

| Metric | Option A: Single Sharded 405B | Option B: Specialist Swarm Cluster | Option C: Hybrid MoE Server Node |  
|---|---|---|---|  
| \*\*Software Stack\*\* | vLLM (Tensor Parallel \= 2\) | Ollama/vLLM (Independent instances) | vLLM (Pipeline Parallel \= 2\) |  
| \*\*Model Load\*\* | Llama 3.1 405B (Q3\_K\_M) | 1× DeepSeek-R1 (70B Q8) \+ 4× Qwen Coder 32B | DeepSeek-R1 (671B MoE FP8) |  
| \*\*Concurrent Capacity\*\* | 1 User / Task at a time | 5 Concurrent Specialized Tasks | 1 User / Task (very fast active load) |  
| \*\*Throughput (Tokens/s)\*\*| Low-Medium (\~10-15 t/s) | High (Combined 120+ t/s) | High (\~30-40 t/s) |  
| \*\*Logical Capability\*\* | Excellent general knowledge | Outstanding coding \+ specialized reasoning | State-of-the-Art Reasoning |  
| \*\*Ideal For\*\* | Deep zero-shot planning | Parallel workspace execution | Advanced code-synthesis loops |

\#\#\# 4.2 Recommendation: The Specialist Swarm Cluster (Option B)  
While running Llama 405B or DeepSeek-R1 dense sharding is excellent for single-question logical depth, the latency of network interconnects between two physically separate server nodes can degrade generation rates. 

For \*\*developer productivity and agentic workflows\*\*, we recommend \*\*Option B: Specialist Swarm Cluster\*\*. This setup dedicates:  
\* \*\*Server 1\*\* to run a highly precise \*\*DeepSeek-R1 (70B Distilled or sharded FP8)\*\* as the "Lead Architect" model, providing high-quality task planning, code reviews, and mathematical logic.  
\* \*\*Server 2\*\* to run \*\*four concurrent instances of Qwen 2.5 Coder 32B (FP16)\*\*. These act as the "Coder Workers", executing the actual file editing and code writing in parallel.

This configuration maximizes physical resource utilization and prevents queue blockages, allowing up to 4 autonomous coding agents to run simultaneously without interfering with each other's VRAM constraints.  

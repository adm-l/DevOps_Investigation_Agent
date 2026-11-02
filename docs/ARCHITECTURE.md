# Architecture

```text
User -> FastAPI (API key, request ID, rate limit)
     -> DevOpsAgent <-> Ollama /api/chat
     -> MCPClientManager (namespaced registry)
          |-> Logs MCP server
          |-> Database MCP server
          |-> Kubernetes MCP server
          |-> GitHub MCP server
     <- tool results -> Ollama reasoning -> incident report
```

## Multiple MCP sessions

FastAPI lifespan creates one MCPClientManager. The manager starts each server as a separate stdio subprocess and creates one ClientSession per server. It initializes each session, calls `list_tools()`, and stores tool owner, original name, description, and JSON schema. Public names use `<server>__<tool>` to avoid collisions.

When the model calls a tool, the manager looks up its owning server and dispatches through that server's session. AsyncExitStack closes all sessions and subprocess transports on shutdown.

## Agent loop

1. Send system/user messages and discovered tool schemas to Ollama.
2. Parse model tool calls.
3. Dispatch each registered tool to its owner session.
4. Append tool results and ask the model to continue.
5. Stop when a final answer arrives or the configured step limit is reached.

Tool calls are bounded by a semaphore and timeout. MCP startup failure fails application startup. Individual tool errors are returned to the model as error results. Ollama failures become API 502 responses.

## Security boundaries

Tools are read-only mocks. There are no shell, SQL execution, pod restart, deployment mutation, or GitHub write tools. API key auth is not a substitute for tool-level authorization. Before connecting real systems, add per-user/per-tool RBAC, approval for high-impact actions, secrets management, redaction, and durable audit logging.

## Production extensions

Use Redis/gateway rate limiting, OpenTelemetry, durable audit records, per-server health/reconnect policy, least-privilege credentials, network isolation, dependency/image scanning, and resource limits.

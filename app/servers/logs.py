import json
from mcp.server.fastmcp import FastMCP
mcp=FastMCP("mock-logs-server")
MOCK_LOGS=[
 {"timestamp":"2026-11-02T10:14:02Z","service":"payment-service","level":"ERROR","message":"database connection pool exhausted","trace_id":"tr-1001"},
 {"timestamp":"2026-11-02T10:14:04Z","service":"payment-service","level":"ERROR","message":"request failed: context deadline exceeded while acquiring database connection","trace_id":"tr-1002"},
 {"timestamp":"2026-11-02T10:15:10Z","service":"payment-service","level":"WARN","message":"upstream authorization latency elevated","trace_id":"tr-1003"},
 {"timestamp":"2026-11-02T10:15:12Z","service":"catalog-service","level":"INFO","message":"cache refresh completed","trace_id":"tr-1004"}]

@mcp.tool()
def search_logs(service:str,query:str="",level:str="",limit:int=20)->str:
    """Search mock application logs by service and optional text or severity."""
    if not 1<=limit<=100: raise ValueError("limit must be between 1 and 100")
    rows=[x for x in MOCK_LOGS if x["service"]==service]
    if query: rows=[x for x in rows if query.lower() in x["message"].lower()]
    if level: rows=[x for x in rows if x["level"]==level.upper()]
    return json.dumps({"count":len(rows[:limit]),"logs":rows[:limit]})

@mcp.tool()
def get_error_details(trace_id:str)->str:
    """Return mock trace details for a known trace identifier."""
    row=next((x for x in MOCK_LOGS if x["trace_id"]==trace_id),None)
    return json.dumps({"found":bool(row),"trace":row,"detail":"Database pool acquisition exceeded 2 seconds." if row else None})

if __name__=="__main__": mcp.run(transport="stdio")

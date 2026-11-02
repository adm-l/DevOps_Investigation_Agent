import json
from mcp.server.fastmcp import FastMCP
mcp=FastMCP("mock-database-server")

@mcp.tool()
def get_db_metrics(service:str)->str:
    """Return mock database connection pool and latency metrics for a service."""
    if service!="payment-service":
        return json.dumps({"service":service,"connections_in_use":4,"pool_max":30,"p95_ms":18})
    return json.dumps({"service":service,"database":"payments-db","connections_in_use":50,"pool_max":50,"pool_waiters":37,"connection_utilization_percent":100,"p95_query_latency_ms":1850,"status":"degraded","sample_window":"5m"})

@mcp.tool()
def get_slow_queries(service:str,limit:int=10)->str:
    """Return mock slow SQL query fingerprints; no SQL is executed."""
    if not 1<=limit<=25: raise ValueError("limit must be between 1 and 25")
    rows=[{"fingerprint":"select-payment-by-id","mean_ms":920,"calls":840,"wait_event":"ClientRead"},{"fingerprint":"insert-payment-event","mean_ms":340,"calls":1200,"wait_event":"Lock"}] if service=="payment-service" else []
    return json.dumps({"service":service,"queries":rows[:limit]})

if __name__=="__main__": mcp.run(transport="stdio")

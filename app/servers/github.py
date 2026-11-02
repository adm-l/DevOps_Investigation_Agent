import json
from mcp.server.fastmcp import FastMCP
mcp=FastMCP("mock-github-server")

@mcp.tool()
def get_recent_commits(repository:str,limit:int=5)->str:
    """Return mock recent commit metadata; does not access GitHub."""
    if not 1<=limit<=20: raise ValueError("limit must be between 1 and 20")
    rows=[{"sha":"a1b2c3d","author":"dev-example","message":"Increase payment DB pool timeout","age":"22 minutes"},{"sha":"e4f5a6b","author":"platform-example","message":"Adjust payment worker concurrency","age":"2 hours"}]
    return json.dumps({"repository":repository,"commits":rows[:limit]})

@mcp.tool()
def get_open_incidents(service:str)->str:
    """Return mock issue/incident references associated with a service."""
    rows=[{"id":"INC-2041","title":"Payment API intermittent timeout","state":"open","priority":"P1"},{"id":"INC-2038","title":"Database pool saturation alert","state":"investigating","priority":"P2"}] if service=="payment-service" else []
    return json.dumps({"service":service,"incidents":rows})

if __name__=="__main__": mcp.run(transport="stdio")

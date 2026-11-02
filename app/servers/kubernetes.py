import json
from mcp.server.fastmcp import FastMCP
mcp=FastMCP("mock-kubernetes-server")

@mcp.tool()
def get_pod_status(service:str,namespace:str="default")->str:
    """Inspect mock pod health, restarts, and readiness for a service."""
    pods=[{"name":"payment-api-7c9d8f-2kx1p","ready":"1/1","restarts":5,"phase":"Running","cpu":"820m","memory":"780Mi"},{"name":"payment-api-7c9d8f-8qz4m","ready":"0/1","restarts":9,"phase":"Running","cpu":"910m","memory":"890Mi"}] if service=="payment-service" else [{"name":f"{service}-6f7d9c-x1abc","ready":"1/1","restarts":0,"phase":"Running","cpu":"90m","memory":"120Mi"}]
    return json.dumps({"namespace":namespace,"service":service,"pods":pods})

@mcp.tool()
def get_deployment_status(service:str,namespace:str="default")->str:
    """Inspect mock deployment desired, available, and unavailable replica counts."""
    degraded=service=="payment-service"
    return json.dumps({"namespace":namespace,"deployment":service,"desired_replicas":3,"ready_replicas":2 if degraded else 3,"available_replicas":2 if degraded else 3,"unavailable_replicas":1 if degraded else 0,"rollout_status":"Progressing" if degraded else "Healthy"})

if __name__=="__main__": mcp.run(transport="stdio")

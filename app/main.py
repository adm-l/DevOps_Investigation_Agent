import logging, uuid
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.agent import AgentError, DevOpsAgent
from app.config import get_settings
from app.mcp_manager import MCPClientManager
from app.schemas import InvestigationRequest, InvestigationResponse
from app.security import InMemoryRateLimiter, require_api_key

cfg=get_settings()
logging.basicConfig(level=getattr(logging,cfg.log_level.upper(),logging.INFO),format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger=logging.getLogger(__name__)
limiter=InMemoryRateLimiter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    manager=MCPClientManager()
    await manager.connect_all()
    agent=DevOpsAgent(manager)
    app.state.manager,app.state.agent=manager,agent
    try:
        yield
    finally:
        await agent.close()
        await manager.close()

app=FastAPI(title=cfg.app_name,version="1.0.0",lifespan=lifespan)

@app.middleware("http")
async def request_context(request:Request,call_next):
    request_id=request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id=request_id
    try:
        response=await call_next(request)
    except Exception:
        logger.exception("request_failed request_id=%s",request_id)
        response=JSONResponse(status_code=500,content={"detail":"Internal server error"})
    response.headers["X-Request-ID"]=request_id
    return response

@app.get("/health/live")
async def liveness():
    return {"status":"alive"}

@app.get("/health/ready")
async def readiness(request:Request):
    manager=getattr(request.app.state,"manager",None)
    if manager is None or not manager.sessions:
        raise HTTPException(status_code=503,detail="MCP servers are not ready")
    return {"status":"ready","mcp_servers":sorted(manager.sessions),"tool_count":len(manager.tools)}

@app.post("/api/v1/investigations",response_model=InvestigationResponse,dependencies=[Depends(require_api_key)])
async def investigate(payload:InvestigationRequest,request:Request):
    limiter.check(request)
    agent=getattr(request.app.state,"agent",None)
    if agent is None:
        raise HTTPException(status_code=503,detail="Agent is not ready")
    rid=request.state.request_id
    try:
        result=await agent.investigate(payload.service,payload.incident,rid)
        return InvestigationResponse(request_id=rid,service=payload.service,answer=result["answer"],steps=result["steps"],tools_called=result["tools_called"])
    except AgentError as exc:
        logger.warning("investigation_failed request_id=%s error=%s",rid,exc)
        raise HTTPException(status_code=502,detail=str(exc)) from exc

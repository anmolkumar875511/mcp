import hashlib
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()

EMAIL = "24f2002298@ds.study.iitm.ac.in".strip().lower()

TOOL = {
    "name": "solve_challenge",
    "description": "Returns the exam challenge answer based on request headers.",
    "inputSchema": {"type": "object", "properties": {}},
}


def reply(rid, result):
    return JSONResponse({"jsonrpc": "2.0", "id": rid, "result": result})


def error(rid, code, message):
    return JSONResponse({"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}})


@app.post("/")
@app.post("/mcp")
async def mcp(request: Request):
    body = await request.json()
    method = body.get("method")
    rid = body.get("id")

    # Notifications (like notifications/initialized) have no id -> reply 202 with no body
    if rid is None:
        return Response(status_code=202)

    if method == "initialize":
        client_version = body.get("params", {}).get("protocolVersion", "2025-03-26")
        return reply(rid, {
            "protocolVersion": client_version,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "exam-mcp", "version": "1.0.0"},
        })

    if method == "ping":
        return reply(rid, {})

    if method == "tools/list":
        return reply(rid, {"tools": [TOOL]})

    if method == "tools/call":
        # The challenge comes from the HTTP header, NOT the JSON body
        challenge = request.headers.get("x-exam-challenge", "")
        answer = hashlib.sha256(f"{challenge}:{EMAIL}".encode()).hexdigest()[:16]
        return reply(rid, {"content": [{"type": "text", "text": answer}]})

    return error(rid, -32601, f"Method not found: {method}")


@app.get("/")
async def home():
    return {"status": "ok"}
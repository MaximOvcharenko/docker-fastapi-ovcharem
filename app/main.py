from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def read_root():
    return { "msg": "Hello!", "Docker": "0.1" }


@app.get("/api/ip")
async def get_ip(request: Request):
    return {"ip": request.client.host}

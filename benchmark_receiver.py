from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Number of requests received by this receiver.
request_count = 0

# Controls whether the receiver is currently failing.
failure_mode = False


@app.get("/")
def health():
    return {
        "message": "benchmark receiver working",
        "failure_mode": failure_mode,
        "request_count": request_count,
    }


@app.post("/success")
async def success(request: Request):
    global request_count

    await request.body()
    request_count += 1

    print(
        f"CUSTOMER BACKEND | request #{request_count} | 200"
    )

    return {
        "message": "customer backend received webhook",
        "status": "success",
    }


@app.post("/fail")
async def fail(request: Request):
    global request_count

    await request.body()
    request_count += 1

    print(
        f"CUSTOMER BACKEND | request #{request_count} | 500"
    )

    return JSONResponse(
        status_code=500,
        content={
            "message": "customer backend simulated failure",
        },
    )


@app.post("/recover")
async def recover(request: Request):
    global request_count

    await request.body()
    request_count += 1

    # First two requests fail.
    # Third and subsequent requests succeed.
    if request_count <= 2:
        print(
            f"CUSTOMER BACKEND | request #{request_count} | 500"
        )

        return JSONResponse(
            status_code=500,
            content={
                "message": "customer backend temporarily unavailable",
                "request_count": request_count,
            },
        )

    print(
        f"CUSTOMER BACKEND | request #{request_count} | 200"
    )

    return {
        "message": "customer backend recovered",
        "request_count": request_count,
    }


@app.post("/reset")
async def reset():
    global request_count

    request_count = 0

    print("CUSTOMER BACKEND | counter reset")

    return {
        "message": "receiver reset",
        "request_count": request_count,
    }
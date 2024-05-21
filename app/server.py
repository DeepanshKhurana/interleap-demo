from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

from packages.coding_problem_generator.coding_problem_generator import chain as coding_problem_generator
from packages.exception_example.exception_example import chain as exception_example

app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add
add_routes(app, coding_problem_generator, path="/coding_problem_generator")
add_routes(app, exception_example, path="/exception_example")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

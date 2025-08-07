from fastapi import FastAPI


app = FastAPI(
    title="HackRx API",
    description="API for HackRx, a platform for processing and answering questions based on documents.",
)

from .routes import router  # noqa: E402

app.include_router(router)

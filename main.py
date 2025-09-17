from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import users, questions, answers, companies

app = FastAPI(title="면기연 API", description="면접 기업 연구 플랫폼 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(companies.router)

@app.get("/")
async def root():
    return {"message": "면기연 API Server is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

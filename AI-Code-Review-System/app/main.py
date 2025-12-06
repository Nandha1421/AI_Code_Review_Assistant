from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.schema import ReviewRequest, ReviewResponse
from app.review import review_code

app = FastAPI(title="AI Code Review Assistant")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/health")
def health():
	return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root():
		html = """
		<html>
			<head><title>AI Code Review Assistant</title></head>
			<body>
				<h2>AI Code Review Assistant (prototype)</h2>
				<p>Available endpoints:</p>
				<ul>
					<li><a href="/docs">OpenAPI docs (interactive)</a></li>
					<li><a href="/redoc">ReDoc docs</a></li>
					<li><a href="/health">/health</a> - simple health check</li>
				</ul>
				<p>To run a review, POST JSON to <code>/review</code> with keys <code>code</code> and <code>language</code>.</p>
			</body>
		</html>
		"""
		return HTMLResponse(content=html, status_code=200)


@app.post("/review", response_model=ReviewResponse)
def review_endpoint(request: ReviewRequest):
	"""Accept code and return a structured review."""
	return review_code(request)


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

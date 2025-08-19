from fastapi import FastAPI
from routes import generatedata, home_page, languagechange, upload_data

# API
app = FastAPI()

app.include_router(home_page.router)
app.include_router(upload_data.router, prefix = "/api")
app.include_router(generatedata.router, prefix = "/api")
app.include_router(languagechange.router, prefix = "/api")
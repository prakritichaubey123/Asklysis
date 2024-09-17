import os
import pandas as pd
from fastapi import FastAPI, File, UploadFile, Form
from pandasai import Agent
from io import BytesIO
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

api_key = os.getenv("PANDASAI_API_KEY")
if api_key:
    os.environ["PANDASAI_API_KEY"] = api_key
else:
    raise ValueError("PANDASAI_API_KEY is not set in the environment variables")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def main():
    with open("index.html", "r") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    if file.filename.endswith('.csv'):
        df = pd.read_csv(BytesIO(await file.read()))
    elif file.filename.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(BytesIO(await file.read()))
    else:
        return JSONResponse({"error": "File format not supported."}, status_code=400)

    # Save the DataFrame to a temporary location
    df.to_csv("uploaded_file.csv", index=False)
    return JSONResponse({"message": "File successfully uploaded. Ready for data analysis.", "columns": df.columns.tolist()})

@app.post("/analyze/")
async def analyze_data(query: str = Form(...)):

    df = pd.read_csv("uploaded_file.csv")
    
    agent = Agent(df)
    response = agent.chat(query)
    return JSONResponse({"response": response})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

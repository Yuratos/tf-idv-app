
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import psycopg2
from psycopg2.extras import DictCursor
import json
import os
import traceback
import uvicorn
import re
from collections import defaultdict


app = FastAPI()
templates = Jinja2Templates(directory="templates")

#file indexation
import re
from collections import defaultdict

def count_word_occurrences(file_path):
    word_counts = defaultdict(int)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            words = re.findall(r'\b(?![ivxlcdm]+\b)[A-Za-zА-Яа-я]{2,}+\b', line.lower())
            for word in words:
                word_counts[word] += 1
                
    return dict(word_counts), len(word_counts) 

# PostgreSQL connection
def get_db_connection():
    try:
        host = os.environ.get('POSTGRES_HOST', 'biometric_db')
        port = int(os.environ.get('POSTGRES_PORT', 5432))
        dbname = os.environ.get('POSTGRES_DB', 'biometrics')
        user = os.environ.get('POSTGRES_USER', 'biometrics_user')
        
        try:
            with open('/run/secrets/db_password', 'r') as f:
                password = f.read().strip()
                if not password:
                    raise ValueError("Empty password file")
        except Exception as file_error:
            print(f"[-] Error reading password file: {file_error}")
            raise
        
        print(f"[DEBUG] Connecting to PostgreSQL: host={host}, port={port}, dbname={dbname}, user={user}")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        print("[+] Successfully connected to PostgreSQL database")
        return conn
    except Exception as e:
        print(f"[-] PostgreSQL connection error: {e}")
        traceback.print_exc()
        return None
@app.get("/", response_class=HTMLResponse)
async def index(request:Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    finally:
        pass

@app.post("/", response_class=HTMLResponse, )
async def index(file:UploadFile= File(...)):
    try:
        bytes = await file.read()
        content = bytes.decode('utf-8')
        word_counts = defaultdict(int)

        for line in content:
            words = re.findall(r'\b(?![ivxlcdm]+\b)[A-Za-zА-Яа-я]{2,}+\b', line.lower())
            for word in words:
                word_counts[word] += 1
        
        
        return {file.filename, file.read}
    except Exception as e:
        print(f"[-] Error processing file: {e}")
        traceback.print_exc()
        return {"error": "File processing error"}
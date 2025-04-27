
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
import datetime


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
        #host = os.environ.get('POSTGRES_HOST', 'biometric_db')
        #port = int(os.environ.get('POSTGRES_PORT', 8432))
        #dbname = os.environ.get('POSTGRES_DB', 'biometrics')
        #user = os.environ.get('POSTGRES_USER', 'biometrics_user')
        
        host = "0.0.0.0"
        port = 8432
        dbname = 'text_db'
        user = 'postgres'
        #try:
        #    with open('/run/secrets/db_password', 'r') as f:
        #        password = f.read().strip()
        #        if not password:
        #            raise ValueError("Empty password file")
        #except Exception as file_error:
        #    print(f"[-] Error reading password file: {file_error}")
        #    raise
        password = "postgres"

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
    
def store_textfile_data(filename, content, words):
    """Save textfile to PostgreSQL"""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO textfile (filename, timestamp, content, words) VALUES (%s, %s, %s, %s)",
                    (filename, datetime.datetime.now(), content, words)
                )
                conn.commit()
                print(f"[+] Stored file data {filename}")

        except Exception as e:
            print(f"[-] Error storing file data: {e}")
        finally:
            conn.close()
            

            
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
        sum_words = 0


        for line in content.split('\n'):
            words = re.findall(r'\b(?![ivxlcdm]+\b)[A-Za-zА-Яа-я]{2,}+\b', line.lower())
            for word in words:
                word_counts[word] += 1
                sum_words += 1

        store_textfile_data(file.filename, bytes, sum_words)
        print(file.filename)

            
        
        return HTMLResponse(content=f"File {file.filename} processed successfully.")
    except Exception as e:
        print(f"[-] Error processing file: {e}")
        traceback.print_exc()
        return {"error": "File processing error"}
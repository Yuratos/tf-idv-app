from fastapi import FastAPI, Request, UploadFile, File, Form, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from collections import OrderedDict
import psycopg2
from psycopg2.extras import execute_values
import traceback
import re
from collections import defaultdict
import datetime
import math
import re


app = FastAPI()
templates = Jinja2Templates(directory="templates")


# PostgreSQL connection
def get_db_connection():
    try:

        
        host = "0.0.0.0"
        port = 8432
        dbname = 'text_db'
        user = 'postgres'
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

def store_statistic_data(data, text_id, words_count):

    """Save defaultdict(int) data to PostgreSQL"""
    conn = get_db_connection() # Коннект к бд
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Преобразуем defaultdict в список кортежей (key, value)
            records = [(key, value, text_id) for key, value in data.items()]
            
            execute_values( 
                cur,
                "INSERT INTO word_data (word, doc_count, total_count) VALUES %s",
                records,
                page_size=1000
            )
            conn.commit()
            print(f"[+] Stored {len(records)} items from statistic for text id: {text_id}")
            
    except Exception as e:
        print(f"[-] Error storing statistic data: {e}")
        conn.rollback()
    finally:
        conn.close()

def count_files_per_words(input_words):
    # Если входная строка - разбиваем по запятым
    if isinstance(input_words, str):
        words = [word.strip() for word in input_words.split(',')]
    else:
        words = input_words  # если уже список

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        wd.word, 
                        COUNT(DISTINCT a.text_id) AS file_count 
                    FROM 
                        unnest(%s::text[]) AS target_words(word)
                    LEFT JOIN 
                        word_data wd ON target_words.word = wd.word
                    LEFT JOIN 
                        association a USING(word_id)
                    GROUP BY 
                        wd.word;
                """, (words,))
                
                result = {row['word']: row['file_count'] for row in cur.fetchall()}
                
                # Добавляем отсутствующие слова с 0
                return {word: result.get(word, 0) for word in words}
                
        except Exception as e:
            print(f"[-] Error: {e}")
            return {word: 0 for word in words}  # fallback
        finally:
            conn.close()

def count_files_in_db():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM textfile")
                conn.commit()
        
                return cur.fetchall()[0][0]
        except Exception as e:
            print(f"[-] Error filecheck: {e}")
        finally:
            conn.close()

def store_textfile_data(filename, content, words):
    """Save textfile to PostgreSQL"""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO textfile (filename, timestamp, content, words) VALUES (%s, %s, %s, %s) RETURNING text_id",
                    (filename, datetime.datetime.now(), content, words)
                )
                conn.commit()
                print(f"[+] Stored file data {filename}")

                # Получаем ID вставленной записи
                retrieved_id = cur.fetchall()
                print(f"[+] Retrieved ID for {filename}: {retrieved_id}")
                return retrieved_id[0][0]
        except Exception as e:
            print(f"[-] Error storing file data: {e}")
        finally:
            conn.close()



# Временное хранилище данных (можно заменить на БД или кэш)
storage = {
    "data": None,
}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, page: int = 1):
    items_per_page = 50
    data = storage["data"]
    
    if data:
        total_items = len(data)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        page = max(1, min(page, total_pages))
        
        start = (page - 1) * items_per_page
        end = start + items_per_page
        paged_data = list(data.items())[start:end]
    else:
        paged_data = []
        total_pages = 1

    return templates.TemplateResponse("index.html", {
        "request": request,
        "data": paged_data,
        "current_page": page,
        "total_pages": total_pages
    })

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):


    try:
        bytes = await file.read()
        content = bytes.decode('utf-8')
        word_counts = defaultdict(int)
        sum_words = 0
        
        for line in content.split('\n'):
            words = re.findall(r'\b(?![ivxlcdm]+\b)[A-Za-zА-Яа-я]{2,}+\b', line.lower())
            for word in words:
                word_counts[word] += 1 # количество вхождений слова
                
                sum_words += 1 # количество слов в файле

        if_counts = {word: round(count / sum_words, 3) for word, count in word_counts.items()}
        

        
        print(list(word_counts.keys()))

        # sql request to check file count in DB
        files_count = count_files_in_db()
        if files_count == 0:
            files_count = 1

        
        word_in_doc_base = count_files_per_words(list(word_counts.keys()))
        print("количество файлов с словами:", word_in_doc_base)

        for key in word_in_doc_base:
            if word_in_doc_base[key] == 0:
               word_in_doc_base[key] += 1   

        idf_counts = {word: round(math.log(count/files_count, 3)) for word, count in word_in_doc_base.items()}
        print("idf: \n",idf_counts)

        # SQL requests to store files in DB
        texfile_id =store_textfile_data(file.filename, bytes, sum_words) # сохраняем файл в БД, получаем id

        combined = {word: (count, idf_counts[word]) for word, count in if_counts.items()}
        print(combined)


        #store_statistic_data(word_counts, , sum_words) # сохраняем статистику в БД
        print(f"[+] File {file.filename} processed successfully. Words count: {sum_words}")

        
   
        storage["data"] = combined
        return RedirectResponse(url="/?page=1", status_code=303)
    except Exception as e:
        print(f"[-] Error processing file: {e}")
        traceback.print_exc()
        return {"error": "File processing error"}


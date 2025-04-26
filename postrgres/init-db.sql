CREATE EXTENSION IF NOT EXISTS plpython3u;

-- Create table for words data
CREATE TABLE IF NOT EXISTS "words_data" (
  "id" integer PRIMARY KEY,
  "word" varchar,
  "tf" float,
  "idf" float,
  "from_text" integer NOT NULL
);

CREATE TABLE IF NOT EXISTS "texfile" (
  "id" integer PRIMARY KEY,
  "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP,
  "filename" varchar,
  "content" bytea,
  "words" integer
);

ALTER TABLE "words_data" ADD FOREIGN KEY ("from_text") REFERENCES "texfile" ("id");
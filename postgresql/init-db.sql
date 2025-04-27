CREATE EXTENSION IF NOT EXISTS plpython3u;

CREATE TABLE /*IF NOT EXISTS*/ "words_data" (
  id SERIAL PRIMARY KEY,
  word varchar,
  tf float,
  idf float,
  from_text integer
);
  
CREATE TABLE /*IF NOT EXISTS*/ "textfile" (
  id SERIAL PRIMARY KEY,
  "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP,
  "filename" varchar,
  content bytea,  
  words integer
);

ALTER TABLE "words_data" ADD FOREIGN KEY ("from_text") REFERENCES "textfile" ("id");
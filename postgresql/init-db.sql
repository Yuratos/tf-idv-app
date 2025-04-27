-- Исправленный вариант
CREATE TABLE textfile (
  text_id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP,
  filename VARCHAR(255),
  content BYTEA,         -- Заменили binary на TEXT (для PostgreSQL используйте BYTEA если нужны бинарные данные)
  words INTEGER
);  

CREATE TABLE word_data (
  word_id SERIAL PRIMARY KEY,
  word VARCHAR(255) NOT NULL UNIQUE,  -- Добавлена уникальность и длина
  doc_count INTEGER,
  total_count INTEGER    -- Переименовано для ясности (было "count")
);

CREATE TABLE association (
  word_id INTEGER REFERENCES word_data(word_id),  -- Исправлен тип
  text_id INTEGER REFERENCES textfile(text_id),   -- Исправлен тип
  word_count_in INTEGER NOT NULL,
  
  PRIMARY KEY (word_id, text_id)  -- Составной первичный ключ вместо отдельного ass_id
);

-- Таблицы association_textfile и association_word_data УДАЛЕНЫ как избыточные
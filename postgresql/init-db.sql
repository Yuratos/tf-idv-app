
CREATE TABLE textfile (
  text_id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP,
  filename VARCHAR(255),
  content BYTEA,         
  words INTEGER
);  

CREATE TABLE word_data (
  word_id SERIAL PRIMARY KEY,
  word VARCHAR(255) NOT NULL UNIQUE,  
  doc_count INTEGER,
  total_count INTEGER    
);

CREATE TABLE association (
  word_id INTEGER REFERENCES word_data(word_id),  
  text_id INTEGER REFERENCES textfile(text_id),   
  word_count_in INTEGER NOT NULL,
  
  PRIMARY KEY (word_id, text_id)  
);


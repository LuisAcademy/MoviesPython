-- Definição da tabela SOT para créditos, com tipos corretos e Foreign Key.

CREATE TABLE IF NOT EXISTS sot_credits (
    movie_id INTEGER PRIMARY KEY NOT NULL,
    title TEXT,
    "cast" JSON,
    crew JSON,
    FOREIGN KEY (movie_id) REFERENCES sot_movies(id)
);
-- Definição da tabela SOT para filmes, com tipos de dados corretos e constraints.

CREATE TABLE IF NOT EXISTS sot_movies (
    id INTEGER PRIMARY KEY NOT NULL,
    title TEXT NOT NULL,
    original_title TEXT,
    budget BIGINT,
    revenue BIGINT,
    genres JSON,
    keywords JSON,
    overview TEXT,
    popularity REAL, -- Usando REAL para maior compatibilidade com números de ponto flutuante
    release_date DATE,
    runtime INTEGER,
    status TEXT,
    tagline TEXT,
    vote_average REAL,
    vote_count INTEGER,
    homepage TEXT,
    original_language TEXT,
    production_companies JSON,
    production_countries JSON,
    spoken_languages JSON
);
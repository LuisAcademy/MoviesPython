-- Definição da tabela SOR para tmdb_5000_credits
-- Todas as colunas são do tipo TEXT.

CREATE TABLE IF NOT EXISTS sor_tmdb_credits (
    movie_id TEXT,
    title TEXT,
    "cast" TEXT, -- "cast" é uma palavra reservada em SQL, por isso as aspas
    crew TEXT
);
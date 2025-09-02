-- Definição da tabela SOR para tmdb_5000_movies
-- Todas as colunas são do tipo TEXT para garantir a ingestão dos dados brutos.

CREATE TABLE IF NOT EXISTS sor_tmdb_movies (
    budget TEXT,
    genres TEXT,
    homepage TEXT,
    id TEXT,
    keywords TEXT,
    original_language TEXT,
    original_title TEXT,
    overview TEXT,
    popularity TEXT,
    production_companies TEXT,
    production_countries TEXT,
    release_date TEXT,
    revenue TEXT,
    runtime TEXT,
    spoken_languages TEXT,
    status TEXT,
    tagline TEXT,
    title TEXT,
    vote_average TEXT,
    vote_count TEXT
);
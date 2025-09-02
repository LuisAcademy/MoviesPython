-- Script de transformação (SPEC) para popular a sot_movies a partir da sor_tmdb_movies.
-- Realiza a limpeza e a conversão de tipos (casting).

INSERT INTO sot_movies (
    id,
    title,
    original_title,
    budget,
    revenue,
    genres,
    keywords,
    overview,
    popularity,
    release_date,
    runtime,
    status,
    tagline,
    vote_average,
    vote_count,
    homepage,
    original_language,
    production_companies,
    production_countries,
    spoken_languages
)
SELECT
    CAST(id AS INTEGER),
    title,
    original_title,
    CAST(budget AS BIGINT),
    CAST(revenue AS BIGINT),
    CAST(genres AS JSON),
    CAST(keywords AS JSON),
    overview,
    CAST(popularity AS REAL),
    -- Trata datas vazias para evitar erros
    CASE WHEN release_date = '' THEN NULL ELSE CAST(release_date AS DATE) END,
    -- Trata runtime vazio ou nulo
    CASE WHEN runtime = '' OR runtime IS NULL THEN NULL ELSE CAST(runtime AS INTEGER) END,
    status,
    tagline,
    CAST(vote_average AS REAL),
    CAST(vote_count AS INTEGER),
    homepage,
    original_language,
    CAST(production_companies AS JSON),
    CAST(production_countries AS JSON),
    CAST(spoken_languages AS JSON)
FROM
    sor_tmdb_movies;
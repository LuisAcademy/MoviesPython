-- Script de transformação (SPEC) para popular a sot_credits a partir da sor_tmdb_credits.

INSERT INTO sot_credits (
    movie_id,
    title,
    "cast",
    crew
)
SELECT
    CAST(movie_id AS INTEGER),
    title,
    CAST("cast" AS JSON),
    CAST(crew AS JSON)
FROM
    sor_tmdb_credits;
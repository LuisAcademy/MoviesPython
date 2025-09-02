# Modelagem de Dados - Projeto TMDB

Este documento descreve a modelagem de dados para o projeto de análise de filmes do TMDB, definindo os Sistemas de Registro (SOR), Sistemas da Verdade (SOT) e suas Especificações (SPEC).

---

## Modelo 1: Filmes (`tmdb_5000_movies.csv`)

### SOR (System of Record): `sor_tmdb_movies`

- **Origem:** Upload do arquivo `tmdb_5000_movies.csv`.



- **Descrição:** Representa os dados brutos e inalterados dos filmes. Nesta fase, todos os campos são tratados como texto para preservar a integridade original.

### SOT (System of Truth): `sot_movies`

- **Descrição:** Tabela principal e confiável para consulta de informações de filmes. Os dados são limpos, padronizados e tipados corretamente.
- **Chave Primária:** `id`

### SPEC (Specification): `spec_sot_movies`

| Nome da Coluna          | Tipo de Dado | Descrição                                             | Restrições (Constraints)  |
| :---------------------- | :----------- | :---------------------------------------------------- | :------------------------ |
| `id`                    | `INTEGER`    | Identificador único do filme (TMDB ID).               | `PRIMARY KEY`, `NOT NULL` |
| `title`                 | `TEXT`       | Título principal do filme.                            | `NOT NULL`                |
| `original_title`        | `TEXT`       | Título original do filme (no idioma de origem).       | `NOT NULL`                |
| `budget`                | `BIGINT`     | Orçamento do filme em dólares.                        |                           |
| `revenue`               | `BIGINT`     | Receita do filme em dólares.                          |                           |
| `genres`                | `JSON`       | Lista de gêneros associados ao filme.                 |                           |
| `keywords`              | `JSON`       | Lista de palavras-chave associadas ao filme.          |                           |
| `overview`              | `TEXT`       | Sinopse/resumo do filme.                              |                           |
| `popularity`            | `FLOAT`      | Métrica de popularidade do filme no TMDB.             |                           |
| `release_date`          | `DATE`       | Data de lançamento do filme.                          |                           |
| `runtime`               | `INTEGER`    | Duração do filme em minutos.                          |                           |
| `status`                | `TEXT`       | Status do filme (Ex: "Released", "Post Production").  |                           |
| `tagline`               | `TEXT`       | Slogan ou frase de efeito do filme.                   |                           |
| `vote_average`          | `FLOAT`      | Nota média de avaliação do filme.                     |                           |
| `vote_count`            | `INTEGER`    | Número total de votos recebidos.                      |                           |
| `homepage`              | `TEXT`       | URL do site oficial do filme.                         |                           |
| `original_language`     | `TEXT`       | Código do idioma original (Ex: "en", "fr").           |                           |
| `production_companies`  | `JSON`       | Lista de companhias de produção.                      |                           |
| `production_countries`  | `JSON`       | Lista de países onde o filme foi produzido.           |                           |
| `spoken_languages`      | `JSON`       | Lista de idiomas falados no filme.                    |                           |

---

## Modelo 2: Créditos (`tmdb_5000_credits.csv`)

### SOR (System of Record): `sor_tmdb_credits`

- **Origem:** Upload do arquivo `tmdb_5000_credits.csv`.
- **Descrição:** Contém os dados brutos sobre o elenco (`cast`) e a equipe técnica (`crew`) de cada filme.

### SOT (System of Truth): `sot_credits`

- **Descrição:** Tabela confiável com os dados de elenco e equipe técnica, já higienizados e com tipos definidos.
- **Chave Primária:** `movie_id`
- **Chave Estrangeira:** `movie_id` referenciando `sot_movies(id)`

### SPEC (Specification): `spec_sot_credits`

| Nome da Coluna | Tipo de Dado | Descrição                                                                      | Restrições (Constraints)                         |
| :------------- | :----------- | :----------------------------------------------------------------------------- | :----------------------------------------------- |
| `movie_id`     | `INTEGER`    | Identificador único do filme.                                                  | `PRIMARY KEY`, `NOT NULL`, `FOREIGN KEY (sot_movies.id)` |
| `title`        | `TEXT`       | Título do filme (informativo, pode ser removido após a junção com `sot_movies`). |                                                  |
| `cast`         | `JSON`       | Lista de atores e seus personagens.                                            |                                                  |
| `crew`         | `JSON`       | Lista da equipe técnica (diretor, roteirista, etc.).                           |                                                  |
install:
    uv sync


up:
    docker-compose up -d

down:
    docker-compose down -v

run:
    uv run streamlit run app.py

test:
    uv run pytest -sv tests

dbt-test MODEL_NAME:
    just dbt test --models {{MODEL_NAME}}

dbt *COMMAND:
    uv run dbt {{COMMAND}} --project-dir dbt_superstore --target dev
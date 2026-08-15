from typing import Sequence

import numpy as np
import psycopg
from pgvector.psycopg import register_vector


class PgVectorStore:
    def __init__(
        self,
        db_url: str = "postgresql://copilot:copilot@127.0.0.1:5433/incident_copilot",
    ):
        self.db_url = db_url

    def connect(self):
        conn = psycopg.connect(self.db_url)
        register_vector(conn)
        return conn

    def clear(self) -> None:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM chunks")

    def insert_chunk(
        self,
        source: str,
        chunk_id: int,
        content: str,
        embedding: np.ndarray,
    ) -> None:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO chunks (source, chunk_id, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        source,
                        chunk_id,
                        content,
                        embedding,
                    ),
                )

    def insert_many(
        self,
        rows: Sequence[tuple[str, int, str, np.ndarray]],
    ) -> None:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO chunks (source, chunk_id, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    rows,
                )

    def search_by_source(
            self,
            query_embedding: np.ndarray,
            source: str,
            top_k: int = 3,
    ) -> list[tuple]:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        source,
                        chunk_id,
                        content,
                        1 - (embedding <=> %s) AS similarity
                    FROM chunks
                    WHERE source = %s
                    ORDER BY embedding <=> %s
                    LIMIT %s
                    """,
                    (
                        query_embedding,
                        source,
                        query_embedding,
                        top_k,
                    ),
                )

                return cur.fetchall()

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 3,
    ) -> list[tuple]:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        source,
                        chunk_id,
                        content,
                        1 - (embedding <=> %s) AS similarity
                    FROM chunks
                    ORDER BY embedding <=> %s
                    LIMIT %s
                    """,
                    (
                        query_embedding,
                        query_embedding,
                        top_k,
                    ),
                )

                return cur.fetchall()
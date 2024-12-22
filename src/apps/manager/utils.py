from typing import Any

from django.db.models.query import QuerySet


async def get_async_query_result(query: QuerySet) -> list[Any]:
    """Make async query and return result."""
    result = []
    async for obj in query:
        result.append(obj)
    return result

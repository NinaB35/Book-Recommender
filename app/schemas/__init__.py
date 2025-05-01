from typing import Annotated

from fastapi import Path, Query

PrimaryKey = Annotated[int, Path(ge=1)]
Skip = Annotated[int, Query(ge=0)]
Limit = Annotated[int, Query(ge=1, le=1000)]

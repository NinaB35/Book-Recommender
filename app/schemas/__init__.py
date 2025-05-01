from typing import Annotated

from fastapi import Path

PrimaryKey = Annotated[int, Path(ge=1)]

from typing import Any, Generic, TypeVar
from collections.abc import Sequence
from math import ceil
from pydantic import BaseModel

from pydantic.generics import GenericModel
from fastapi_pagination import Params, Page
from fastapi_pagination.bases import AbstractPage, AbstractParams


DataType = TypeVar("DataType")
T = TypeVar("T")


class PageBase(Page[T], Generic[T]):
    pages: int
    # next_page: int | None
    # previous_page: int | None


class IResponseBase(GenericModel, Generic[T]):
    data: T | None
    message: str = ""
    meta: dict = {}


class IResponsePage(AbstractPage[T], Generic[T]):
    message: str | None = ""
    meta: dict = {}
    data: PageBase[T]

    __params_type__ = Params  # Set params related to Page

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        params: AbstractParams,
    ) -> PageBase[T] | None:
        if params.size is not None and total is not None and params.size != 0:
            pages = ceil(total / params.size)
        else:
            pages = 0

        return cls(
            data=PageBase(
                ##### TODO: 아래 data들의 key들 어떤 것들만 사용할 것인지 추후 수정
                items=items,
                page=params.page,
                size=params.size,
                total=total,
                pages=pages,
                # next_page=params.page + 1 if params.page < pages else None,
                # previous_page=params.page - 1 if params.page > 1 else None,
            )
        )


class IGetResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str | None = "success"


class IGetResponsePaginated(IResponsePage[DataType], Generic[DataType]):
    message: str | None = "Data got correctly"


class IPostResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str | None = "success"


class IPutResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str | None = "Data updated correctly"


class IDeleteResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str | None = "Data deleted correctly"
    
def create_response(
    data: DataType | None,
    message: str | None = None,
    meta: dict | Any | None = {},
) -> dict[str, DataType] | DataType:
    if message is None:
        return {"data": data, "meta": meta}
    return {"data": data, "message": message, "meta": meta}


def create_list_response(
    data: IResponsePage | None,
    message: str | None = None,
    meta: dict | Any | None = {},
) -> dict[str, DataType] | DataType:
    data.message = "Data paginated correctly" if message is None else message
    data.meta = meta
    return data

def create_common_exception_response(code: str, message: str) -> dict[str, str]:
    return {
            "content": {
                "application/json": {
                   "example": { "detail": {"code": code, "message": message} }
                }
            }
        }
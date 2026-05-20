from fastapi import APIRouter, Depends

from app.api.dependencies import get_list_theaters_use_case
from app.application.use_cases.list_theaters import ListTheaters
from app.domain.entities.theater import Theater

router = APIRouter()


@router.get("/theaters", response_model=list[Theater])
def get_theaters(
    use_case: ListTheaters = Depends(get_list_theaters_use_case),
) -> list[Theater]:
    return use_case()

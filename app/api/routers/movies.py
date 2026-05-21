from fastapi import APIRouter, Depends

from app.api.dependencies import get_list_movies_use_case
from app.application.use_cases.list_movies import ListMovies
from app.domain.entities.movie import Movie

router = APIRouter()


@router.get("/movies", response_model=list[Movie])
def get_movies(
    use_case: ListMovies = Depends(get_list_movies_use_case),
) -> list[Movie]:
    return use_case()

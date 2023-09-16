from fastapi import APIRouter, status, Depends
from auth import check_authorization_header


router = APIRouter(
    prefix="/accounts", dependencies=[Depends(check_authorization_header)]
)


@router.get(path="", status_code=status.HTTP_200_OK)
def get_accounts() -> dict[str, list[str]]:
    accounts: list[str] = ["BE01234567890123"]
    return {"accounts": accounts}

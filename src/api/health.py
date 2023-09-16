from fastapi import APIRouter, status, HTTPException


router = APIRouter(prefix="/health")


@router.get(path="", status_code=status.HTTP_200_OK)
async def get_health() -> dict[str, str]:
    return {"status": "OK"}


@router.get(path="/{service}", status_code=status.HTTP_200_OK)
async def get_health_service(service: str) -> dict[str, str]:
    if service == "database":
        return {"service": "database", "status": "OK"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not such service '{service}'!",
        )

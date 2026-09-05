from fastapi import APIRouter, HTTPException, Query, status
from app.database import get_all_analyses, get_analysis_by_id, delete_analysis_by_id

router = APIRouter()


@router.get("/history")
async def list_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Retrieves stored analysis history records.
    """
    return get_all_analyses(limit=limit, offset=offset)


@router.get("/history/{analysis_id}")
async def get_history_detail(analysis_id: str):
    """
    Retrieves complete stored report payload for a specific analysis ID.
    """
    result = get_analysis_by_id(analysis_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return result


@router.delete("/history/{analysis_id}")
async def delete_history_item(analysis_id: str):
    """
    Deletes an analysis report entry from history.
    """
    success = delete_analysis_by_id(analysis_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return {"status": "deleted", "analysis_id": analysis_id}

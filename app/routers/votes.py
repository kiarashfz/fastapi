from fastapi import HTTPException, status, Depends, Response, APIRouter
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_user_id

router = APIRouter(
    prefix="/votes",
    tags=["Votes"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.VoteResponse)
async def voting(vote: schemas.VoteCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    post = db.query(models.Post).get(vote.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {vote.post_id} not found.")
    else:
        exists_vote = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                                   models.Vote.user_id == user_id).first()
        if exists_vote:
            if vote.dir == 1:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have voted this post before.")
            elif vote.dir == 0:
                db.delete(exists_vote)
                db.commit()
                return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            if vote.dir == 1:
                new_vote = models.Vote(post_id=vote.post_id, user_id=user_id)
                db.add(new_vote)
                db.commit()
                db.refresh(new_vote)
                return new_vote
            elif vote.dir == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You didn't vote on this post yet.")

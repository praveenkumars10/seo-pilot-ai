import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.database import get_db
from backend.app.models.website import Website
from backend.app.schemas.website import WebsiteCreate, WebsiteUpdate, WebsiteResponse

router = APIRouter(prefix="/websites", tags=["Websites"])
logger = logging.getLogger(__name__)

@router.get("", response_model=List[WebsiteResponse])
async def list_websites(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Website).order_by(Website.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
async def create_website(payload: WebsiteCreate, db: AsyncSession = Depends(get_db)):
    # Check if canonical_url already registered
    existing = await db.execute(select(Website).where(Website.canonical_url == payload.canonical_url))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Website with this canonical URL is already registered.")

    website = Website(**payload.model_dump())
    db.add(website)
    await db.commit()
    await db.refresh(website)
    return website

@router.get("/{website_id}", response_model=WebsiteResponse)
async def get_website(website_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Website).where(Website.id == website_id))
    website = result.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")
    return website

@router.put("/{website_id}", response_model=WebsiteResponse)
async def update_website(website_id: str, payload: WebsiteUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Website).where(Website.id == website_id))
    website = result.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(website, field, val)

    await db.commit()
    await db.refresh(website)
    return website

@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website(website_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Website).where(Website.id == website_id))
    website = result.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")
    await db.delete(website)
    await db.commit()
    return None


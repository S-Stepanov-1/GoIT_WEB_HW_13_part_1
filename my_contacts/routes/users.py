import os

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

from my_contacts.database.db_connect import get_db
from my_contacts.database.models import User
from my_contacts.schemas import UserResponse
from my_contacts.repository import users as repository_users
from my_contacts.services.auth import auth_service

load_dotenv()

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(),
                             current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    uploaded_file_info = cloudinary.uploader.upload(file.file,
                                                    public_id=f"My Contacts App/{current_user.username}",
                                                    overwrite=True)

    avatar_url = cloudinary.CloudinaryImage(f"My Contacts App/{current_user.username}") \
        .build_url(width=300, height=300, crop="fill", version=uploaded_file_info.get('version'))

    await repository_users.update_avatar(current_user.user_email, avatar_url, db)

    response_message = "Avatar successfully updated"
    user_response = UserResponse(username=current_user.username,
                                 user_email=current_user.user_email,
                                 detail=response_message)
    return user_response

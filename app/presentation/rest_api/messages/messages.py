from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, status, Depends, File, UploadFile as FastAPIUploadFile, Form
from pydantic import WithJsonSchema
from starlette.responses import JSONResponse
from business_logic.active_session.active_session_manager import active_session_manager
from business_logic.active_session.message_sender.private_message import PrivateMessageRoute
from app.business_logic.cache.session_key_storage import session_key_storage
from business_logic.encryption.symmetric import SymmetricEncode
from business_logic.file_manager.file_manager import FileManager
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.message.download_file_use_case import DownloadFileUseCase
from business_logic.use_cases.message.send_private_msg_and_save_use_case import SendPrivateMsgAndSave
from database import db
from dtos import (
    PrivateMessageDtoPostRequest,
    JWTAccessToken,
)
from models.user import RoleEnum
from presentation.dependencies.auth import RoleChecker


route = APIRouter()

UploadFile = Annotated[
    FastAPIUploadFile, WithJsonSchema({"type": "string", "format": "binary"})
]


@route.post(
    path='/message/send',
    tags=['Message'],
    summary='Отправка сообщения пользователю',
    description='Отправка сообщения пользователю',
    operation_id='send_private_message_operation'
)
async def send_private_message(
        message_id: UUID = Form(...),
        recipient_id: str = Form(...),
        message_for_recipient: str | None = Form(None),
        recipient_key_version: str = Form(...),
        sender_id: str = Form(...),
        message_for_sender: str | None = Form(None),
        sender_key_version: str = Form(...),
        files: list[UploadFile] | None = File(None),
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    if not message_for_recipient and not message_for_sender and not files:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='Попытка отправить пустое сообщение'
        )
    if not message_for_recipient or not message_for_sender:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='Отсутствует, либо зашифрованное сообщения для отправителя, либо для получателя'
        )
    dto_request = PrivateMessageDtoPostRequest(
        id=message_id,
        recipient_id=recipient_id,
        message_for_recipient=message_for_recipient,
        recipient_key_version=recipient_key_version,
        sender_id=sender_id,
        message_for_sender=message_for_sender,
        sender_key_version=sender_key_version,
    )
    if access_token.user_id != dto_request.sender_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='id отправителя не совпадает с id пользователя в токене'
        )
    private_msg_response = await SendPrivateMsgAndSave(
        session_id=access_token.session_id,
        uow=UnitOfWork(db),
        file_manager=FileManager,
        private_msg_route=PrivateMessageRoute(
            active_session=active_session_manager,
            symmetric_encode=SymmetricEncode,
            session_key_storage=session_key_storage
        )
    ).execute(
        dto_private_msg=dto_request,
        upload_file=files
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=private_msg_response.model_dump(mode='json')
    )


@route.get(
    path='/files/{file_id}/download',
    tags=['Message'],
    summary='Загрузка файлов с сервера',
    description='Streaming отправка media файлов клиенту',
    operation_id='download_file_operation'
)
async def download_file(
        file_id: UUID,
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    result = await DownloadFileUseCase(
        uow=UnitOfWork(db),
        file_manager=FileManager
    ).execute(
        user_upload_id=access_token.user_id,
        file_id=file_id
    )
    return result
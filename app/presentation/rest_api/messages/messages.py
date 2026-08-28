import json
from typing import Annotated
from uuid import UUID, uuid4
from fastapi import APIRouter, status, Depends, File, UploadFile as FastAPIUploadFile, Form
from pydantic import WithJsonSchema
from starlette.responses import JSONResponse
from bootstrap import get_bootstrap
from app.business_logic.active_session.message_sender.group_message import GroupMessageRoute
from app.business_logic.active_session.message_sender.private_message import PrivateMessageRoute
from app.business_logic.encryption.symmetric import SymmetricEncode
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.message.delete_msg_use_case import DeleteMsgUseCase
from app.business_logic.use_cases.message.download_file_use_case import DownloadFileUseCase
from app.business_logic.use_cases.message.get_messages_use_case import GetPrivateMsgAndSave
from app.business_logic.use_cases.message.send_group_msg_and_save_use_case import SendGroupMsgAndSave
from app.business_logic.use_cases.message.send_private_msg_and_save_use_case import SendPrivateMsgAndSave
from app.shared.dtos import (
    PrivateMessageDtoPostRequest,
    JWTAccessToken,
    GroupMessageDtoPostRequest, MessageType,
)
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.auth import RoleChecker


route = APIRouter()
bootstrap = get_bootstrap()

UploadFile = Annotated[
    FastAPIUploadFile, WithJsonSchema({"type": "string", "format": "binary"})
]


@route.post(
    path='/users/{recipient_id}/message/send',
    #path='/message/send',
    tags=['Message'],
    summary='Отправка сообщения пользователю',
    description='Отправка сообщения пользователю',
    operation_id='send_private_message_operation'
)
async def send_private_message(
        recipient_id: str,
        message_id: UUID = Form(...),
        message_for_recipient: str | None = Form(None),
        recipient_key_version: str = Form(None),
        sender_id: str = Form(...),
        message_for_sender: str | None = Form(None),
        sender_key_version: str = Form(None),
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
        uow=UnitOfWork(bootstrap.database),
        file_manager=FileManager,
        private_msg_route=PrivateMessageRoute(
            active_session=bootstrap.active_session_manager,
            symmetric_encode=SymmetricEncode,
            session_key_storage=bootstrap.session_key_storage
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
        uow=UnitOfWork(bootstrap.database),
        file_manager=FileManager
    ).execute(
        user_upload_id=access_token.user_id,
        file_id=file_id
    )
    return result


@route.get(
    path='/users/me/message/history/{user_id}',
    #path='/message/me/history/{user_id}',
    tags=['Message'],
    summary='Получение истории сообщений с пользователем',
    operation_id='get_history_message'
)
def get_message(
        user_id: str,
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    results = GetPrivateMsgAndSave(
        uow=UnitOfWork(bootstrap.database)
    ).execute(
        user_id_who=access_token.user_id,
        user_id_whom=user_id
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[result.model_dump(mode='json') for result in results]
    )


@route.post(
    path='/rooms/{room_id}/message/send',
    #path='/message/group/send',
    tags=['Room', 'Message'],
    summary='Отправка сообщения в группу',
    operation_id='send_group_message_operation'
)
async def send_group_message(
        room_id: UUID,
        sender_id: str = Form(...),
        payload: str = Form(None),
        files: list[UploadFile] | None = File(None),
        access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    dto_request = GroupMessageDtoPostRequest(
        id=uuid4(),
        room_id=room_id,
        sender_id=sender_id,
        payload=json.loads(payload)
    )
    if not dto_request.payload['message'] and not files:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='Попытка отправить пустое сообщение'
        )
    if dto_request.sender_id != access_token.user_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='id отправителя не совпадает с id пользователя в токене'
        )
    result = await SendGroupMsgAndSave(
        session_id=access_token.session_id,
        file_manager=FileManager,
        uow=UnitOfWork(bootstrap.database),
        group_msg_route=GroupMessageRoute(bootstrap.active_session_manager),
    ).execute(
        dto_group_msg=dto_request,
        upload_file=files
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump(mode='json')
    )


@route.delete(
    path='/messages/{message_id}/delete',
    tags=['Message'],
    summary='Удаление сообщения',
    operation_id='delete_msg_operaion'
)
async def delete_message(
    message_id: UUID,
    type_message: MessageType,
    access_token: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN]))
):
    await DeleteMsgUseCase(
        uow=UnitOfWork(bootstrap.database),
        file_manager=FileManager,
        active_session_manager=bootstrap.active_session_manager,
        type_message=type_message
    ).execute(
        sender_id=access_token.user_id,
        message_id=message_id,
        type_msg=type_message
    )
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=f'Сообщение с id {message_id} удалено'
    )
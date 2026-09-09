from typing import Annotated
from uuid import UUID, uuid4
from fastapi import APIRouter, status, Depends, File, UploadFile as FastAPIUploadFile, Form
from pydantic import WithJsonSchema
from starlette.responses import JSONResponse, Response
from bootstrap import get_bootstrap
from app.business_logic.use_cases import (
    DeleteMsgUseCase,
    DownloadFileUseCase,
    GetPrivateMsgAndSave,
    SendGroupMsgAndSave,
    SendPrivateMsgAndSave
)
from app.business_logic.active_session.message_sender.group_message import GroupMessageRoute
from app.business_logic.active_session.message_sender.private_message import PrivateMessageRoute
from app.business_logic.encryption.symmetric import SymmetricEncode
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.shared.dtos import (
    PrivateMessageDtoPostRequest,
    JWTAccessToken,
    GroupMessageDtoPostRequest,
    MessageType,
    ActionType,
    RequestClientDtoHandle
)
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.base import RequestClientDepends
import json


route = APIRouter()
bootstrap = get_bootstrap()

UploadFile = Annotated[
    FastAPIUploadFile, WithJsonSchema({"type": "string", "format": "binary"})
]


@route.post(
    path='/users/{recipient_id}/message/send',
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
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.SEND_PRIVATE_MESSAGE
            )
        )
):
    try:
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
        if request_client_dep.token_info.user_id != dto_request.sender_id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content='id отправителя не совпадает с id пользователя в токене'
            )
        private_msg_response = await SendPrivateMsgAndSave(
            session_id=request_client_dep.token_info.session_id,
            uow=UnitOfWork(bootstrap.database),
            file_manager=FileManager,
            private_msg_route=PrivateMessageRoute(
                active_session=bootstrap.active_session_manager,
                symmetric_encode=SymmetricEncode,
                session_key_storage=bootstrap.redis_cache.session_key_storage
            ),
            dto_audit=request_client_dep.dto_audit
        ).execute(
            dto_private_msg=dto_request,
            upload_file=files,
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=private_msg_response.model_dump(mode='json')
        )
    except Exception:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content='Ошибка отправки сообщения'
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
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.DOWNLOAD_FILE
            )
        )
):
    result = await DownloadFileUseCase(
        uow=UnitOfWork(bootstrap.database),
        file_manager=FileManager,
        dto_audit=request_client_dep.dto_audit
    ).execute(
        user_upload_id=request_client_dep.token_info.user_id,
        file_id=file_id,
    )
    return result


@route.get(
    path='/users/me/message/history/{user_id}',
    tags=['Message'],
    summary='Получение истории сообщений с пользователем',
    operation_id='get_history_message'
)
def get_message(
        user_id: str,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.GET_HISTORY_MSG
            )
        )
):
    results = GetPrivateMsgAndSave(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(
        user_id_who=request_client_dep.token_info.user_id,
        user_id_whom=user_id,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[result.model_dump(mode='json') for result in results]
    )


@route.post(
    path='/rooms/{room_id}/message/send',
    tags=['Room', 'Message'],
    summary='Отправка сообщения в группу',
    operation_id='send_group_message_operation'
)
async def send_group_message(
        room_id: UUID,
        sender_id: str = Form(...),
        payload: str = Form(None),
        files: list[UploadFile] | None = File(None),
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.SEND_GROUP_MESSAGE
            )
        ),
):
    try:
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
        if dto_request.sender_id != request_client_dep.token_info.user_id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content='id отправителя не совпадает с id пользователя в токене'
            )
        result = await SendGroupMsgAndSave(
            session_id=request_client_dep.token_info.session_id,
            file_manager=FileManager,
            uow=UnitOfWork(bootstrap.database),
            group_msg_route=GroupMessageRoute(bootstrap.active_session_manager),
            dto_audit=request_client_dep.dto_audit
        ).execute(
            dto_group_msg=dto_request,
            upload_file=files,
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=result.model_dump(mode='json')
        )
    except Exception:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content='Ошибка отправки сообщения'
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
    request_client_dep: RequestClientDtoHandle = Depends(
        RequestClientDepends[JWTAccessToken](
            allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
            action_type=ActionType.DELETE_MSG
        )
    )
):
    await DeleteMsgUseCase(
        uow=UnitOfWork(bootstrap.database),
        file_manager=FileManager,
        active_session_manager=bootstrap.active_session_manager,
        type_message=type_message,
        dto_audit=request_client_dep.dto_audit
    ).execute(
        sender_id=request_client_dep.token_info.user_id,
        message_id=message_id,
        type_msg=type_message,
    )
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=f'Сообщение с id {message_id} удалено'
    )
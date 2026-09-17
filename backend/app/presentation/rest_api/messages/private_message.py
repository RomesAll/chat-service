from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, status, Depends, File, UploadFile as FastAPIUploadFile, Form, HTTPException
from pydantic import WithJsonSchema
from starlette.responses import JSONResponse
from app.business_logic.use_cases.message.msg_update_use_case import MsgUpdateUseCase
from app.data_access.database.repositories import PrivateMessageRepository
from app.shared.dtos.jwt import TokenType
from bootstrap import get_bootstrap
from app.business_logic.use_cases import (
    GetPrivateMsgAndSave,
    SendPrivateMsgAndSave
)
from app.business_logic.active_session.message_sender.private_message import PrivateMessageRoute
from app.business_logic.encryption.symmetric import SymmetricEncode
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.shared.dtos import (
    PrivateMessageDtoPostRequest,
    JWTAccessToken,
    ActionType,
    RequestClientDtoHandle, PrivateMessageDtoUpdateRequest
)
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.base import RequestClientDepends


route = APIRouter()
bootstrap = get_bootstrap()

UploadFile = Annotated[
    FastAPIUploadFile, WithJsonSchema({"type": "string", "format": "binary"})
]


@route.post(
    path='/users/{recipient_id}/message/send',
    tags=['PrivateMessage'],
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
        reply_to_message_id: UUID | None = Form(None),
        forwarded_from_message_id: UUID | None = Form(None),
        forwarded_from_user_id: str | None = Form(None),
        files: list[UploadFile] | None = File(None),
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.SEND_PRIVATE_MESSAGE
            )
        )
):
    if not message_for_recipient and not message_for_sender and not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Попытка отправить пустое сообщение'
        )
    if not message_for_recipient or not message_for_sender:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Отсутствует, либо зашифрованное сообщения для отправителя, либо для получателя'
        )
    dto_request = PrivateMessageDtoPostRequest(
        id=message_id,
        recipient_id=recipient_id,
        message_for_recipient=message_for_recipient,
        recipient_key_version=recipient_key_version,
        sender_id=sender_id,
        message_for_sender=message_for_sender,
        sender_key_version=sender_key_version,
        reply_to_message_id=reply_to_message_id,
        forwarded_from_message_id=forwarded_from_message_id,
        forwarded_from_user_id=forwarded_from_user_id
    )
    if request_client_dep.token_info.user_id != dto_request.sender_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='id отправителя не совпадает с id пользователя в токене'
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
        content={
            'message': 'Сообщение успешно сохранено',
            'detail': private_msg_response.model_dump(mode='json')
        }
    )


@route.get(
    path='/users/me/message/history/{user_id}',
    tags=['PrivateMessage'],
    summary='Получение истории сообщений с пользователем',
    operation_id='get_history_message'
)
def get_private_message(
        user_id: str,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
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
        content={
            'message': 'Сообщения успешно получены',
            'detail': [result.model_dump(mode='json') for result in results]
        }
    )


@route.put(
    path='/message/{message_id}',
    tags=['PrivateMessage'],
    summary='Обновление сообщений',
    operation_id='update_msg_operaion'
)
async def update_private_message(
    message_id: UUID,
    message_request: PrivateMessageDtoUpdateRequest,
    delete_file_ids: list[UUID] | None = None,
    request_client_dep: RequestClientDtoHandle = Depends(
        RequestClientDepends[JWTAccessToken](
            token_type=TokenType.ACCESS_TOKEN,
            allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
            action_type=ActionType.UPDATE_MESSAGE
        )
    )
):
    result = await MsgUpdateUseCase(
        session_id=request_client_dep.token_info.session_id,
        uow=UnitOfWork(bootstrap.database),
        file_manager=FileManager,
        msg_route=PrivateMessageRoute(
            active_session=bootstrap.active_session_manager,
            symmetric_encode=SymmetricEncode,
            session_key_storage=bootstrap.redis_cache.session_key_storage
        ),
        dto_audit=request_client_dep.dto_audit,
        repo=PrivateMessageRepository,
    ).execute(
        message_id=message_id,
        dto_request=message_request,
        file_ids=delete_file_ids,
        sender_id=request_client_dep.token_info.user_id
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': 'Сообщение успешно обновленно',
            'detail': result.model_dump(mode='json')
        }
    )

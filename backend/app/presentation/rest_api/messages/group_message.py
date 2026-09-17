from typing import Annotated
from uuid import UUID, uuid4
from fastapi import APIRouter, status, Depends, File, UploadFile as FastAPIUploadFile, Form
from fastapi.exceptions import HTTPException
from pydantic import WithJsonSchema
from starlette.responses import JSONResponse
from app.business_logic.use_cases.message.get_group_messages_use_case import GetGroupMsg
from app.business_logic.use_cases.message.msg_update_use_case import MsgUpdateUseCase
from app.data_access.database.repositories import GroupMessageRepository
from app.shared.dtos.jwt import TokenType
from bootstrap import get_bootstrap
from app.business_logic.use_cases import (
    SendGroupMsgAndSave,
)
from app.business_logic.active_session.message_sender.group_message import GroupMessageRoute
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.shared.dtos import (
    JWTAccessToken,
    GroupMessageDtoPostRequest,
    ActionType,
    RequestClientDtoHandle, GroupMessageDtoUpdateRequest
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
    path='/rooms/{room_id}/message/send',
    tags=['Room', 'GroupMessage'],
    summary='Отправка сообщения в группу',
    operation_id='send_group_message_operation'
)
async def send_group_message(
        room_id: UUID,
        sender_id: str = Form(...),
        payload: str = Form(None),
        reply_to_message_id: UUID | None = Form(None),
        forwarded_from_message_id: UUID | None = Form(None),
        forwarded_from_user_id: str | None = Form(None),
        files: list[UploadFile] | None = File(None),
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.SEND_GROUP_MESSAGE
            )
        ),
):
    dto_request = GroupMessageDtoPostRequest(
        id=uuid4(),
        room_id=room_id,
        sender_id=sender_id,
        payload=json.loads(payload),
        reply_to_message_id = reply_to_message_id,
        forwarded_from_message_id = forwarded_from_message_id,
        forwarded_from_user_id = forwarded_from_user_id
    )
    if not dto_request.payload['message'] and not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Попытка отправить пустое сообщение'
        )
    if dto_request.sender_id != request_client_dep.token_info.user_id:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='id отправителя не совпадает с id пользователя в токене'
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
        content={
            'message': 'Сообщение успешно сохранено',
            'detail': result.model_dump(mode='json')
        }
    )


@route.get(
    path='/rooms/{room_id}/messages/history',
    tags=['Room', 'GroupMessage'],
    summary='Получение истории сообщений в групповой комнате',
    operation_id='get_history_group_message'
)
def get_group_message(
        room_id: UUID,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
                allowed_roles=[RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN],
                action_type=ActionType.GET_HISTORY_MSG
            )
        )
):
    results = GetGroupMsg(
        uow=UnitOfWork(bootstrap.database),
        dto_audit=request_client_dep.dto_audit
    ).execute(
        room_id=room_id,
        user_id=request_client_dep.token_info.user_id
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'Сообщения успешно получены',
            'detail': [result.model_dump(mode='json') for result in results]
        }
    )


@route.put(
    path='/rooms/{room_id}/messages/{message_id}',
    tags=['Room', 'GroupMessage'],
    summary='Обновление сообщений',
    operation_id='update_group_msg_operaion'
)
async def update_group_message(
    message_id: UUID,
    message_request: GroupMessageDtoUpdateRequest,
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
        msg_route=GroupMessageRoute(
            active_session=bootstrap.active_session_manager,
        ),
        dto_audit=request_client_dep.dto_audit,
        repo=GroupMessageRepository,
    ).execute(
        message_id=message_id,
        dto_request=message_request,
        file_ids=delete_file_ids,
        sender_id=request_client_dep.token_info.user_id
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': 'Сообщение успешно обновлено',
            'detail': result.model_dump(mode='json')
        }
    )
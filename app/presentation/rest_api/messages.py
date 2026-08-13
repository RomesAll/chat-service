from fastapi import APIRouter, Response, status, Depends
from business_logic.active_session.active_session_manager import active_session_manager
from business_logic.active_session.route_message import RouteMessage
from business_logic.unit_of_work import UnitOfWork
from business_logic.use_cases.message.send_group_msg_and_save import SendGroupMsgAndSave
from business_logic.use_cases.message.send_private_msg_and_save import SendPrivateMsgAndSave
from database import db
from dtos import (
    PrivateMessageDtoPostRequest,
    GroupMessageDtoPostRequest, JWTAccessToken
)
from models.user import RoleEnum
from presentation.dependencies.auth import AuthChecker, RoleChecker

route = APIRouter()


@route.post(
    path='/{user_id}/send',
    tags=['Message'],
    summary='Отправка сообщения пользователю',
    description='Отправка сообщения пользователю',
    operation_id='send_private_message_operation'
)
async def send_private_message(
        dto_request: PrivateMessageDtoPostRequest,
        user_info: JWTAccessToken = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN])),
):
    await SendPrivateMsgAndSave(
        uow=UnitOfWork(db),
        route_message=RouteMessage(active_session=active_session_manager)
    ).execute(dto_request)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        content=f'Сообщение отправлено пользователю {user_info['user_id']}'
    )


@route.post(
    path='/chats/{chat_id}/messages',
    tags=['Message'],
    summary='Отправка сообщения в группу (комнату)',
    description='Отправка сообщения в группу (комнату)',
    operation_id='send_group_message_operation'
)
async def send_group_message(
        dto_request: GroupMessageDtoPostRequest,
        user_info: dict = Depends(RoleChecker([RoleEnum.DEFAULT_USER, RoleEnum.SUPER_ADMIN])),
):
    await SendGroupMsgAndSave(
        uow=UnitOfWork(db),
        route_message=RouteMessage(active_session=active_session_manager)
    ).execute(dto_request)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        content=f'Сообщение пользователя {user_info['user_id']} отправлено в комнату {dto_request.chat_id}'
    )
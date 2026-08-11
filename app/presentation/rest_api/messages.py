from fastapi import APIRouter
from business_logic.use_cases.registry.use_case_registry import UseCaseRegistry
from dtos import (
    PrivateMessageDtoGetResponse,
    PrivateMessageDtoPostRequest,
    ActionType,
    GroupMessageDtoGetResponse,
    GroupMessageDtoPostRequest
)

route = APIRouter()


@route.post(
    path='/{user_id}/send',
    tags=['Message'],
    summary='Отправка сообщения пользователю',
    description='Отправка сообщения пользователю',
    response_model=PrivateMessageDtoGetResponse,
    operation_id='send_private_message_operation'
)
async def send_private_message(dto_request: PrivateMessageDtoPostRequest):
    use_case = UseCaseRegistry.get(dto_request, ActionType.SEND_PRIVATE_MSG_AND_SAVE)
    dto_response = await use_case.execute()
    return dto_response


@route.post(
    path='/chats/{chat_id}/messages',
    tags=['Message'],
    summary='Отправка сообщения в группу (комнату)',
    description='Отправка сообщения в группу (комнату)',
    response_model=GroupMessageDtoGetResponse,
    operation_id='send_group_message_operation'
)
async def send_group_message(dto_request: GroupMessageDtoPostRequest):
    use_case = UseCaseRegistry.get(dto_request, ActionType.SEND_GROUP_MSG_AND_SAVE)
    dto_response = await use_case.execute()
    return dto_response
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, status, Depends, UploadFile as FastAPIUploadFile
from pydantic import WithJsonSchema
from starlette.responses import JSONResponse
from app.shared.dtos.jwt import TokenType
from bootstrap import get_bootstrap
from app.business_logic.use_cases import (
    DeleteMsgUseCase,
    DownloadFileUseCase,
)
from app.business_logic.file_manager.file_manager import FileManager
from app.business_logic.unit_of_work import UnitOfWork
from app.shared.dtos import (
    JWTAccessToken,
    MessageType,
    ActionType,
    RequestClientDtoHandle
)
from app.data_access.database.models.user import RoleEnum
from app.presentation.dependencies.base import RequestClientDepends


route = APIRouter()
bootstrap = get_bootstrap()

UploadFile = Annotated[
    FastAPIUploadFile, WithJsonSchema({"type": "string", "format": "binary"})
]


@route.get(
    path='/files/{file_id}/download',
    tags=['GroupMessage', 'PrivateMessage'],
    summary='Загрузка файлов с сервера',
    description='Streaming отправка media файлов клиенту',
    operation_id='download_file_operation'
)
async def download_file(
        file_id: UUID,
        request_client_dep: RequestClientDtoHandle = Depends(
            RequestClientDepends[JWTAccessToken](
                token_type=TokenType.ACCESS_TOKEN,
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


@route.delete(
    path='/messages/{message_id}',
    tags=['GroupMessage', 'PrivateMessage'],
    summary='Удаление сообщения',
    operation_id='delete_msg_operaion'
)
async def delete_message(
    message_id: UUID,
    type_message: MessageType,
    request_client_dep: RequestClientDtoHandle = Depends(
        RequestClientDepends[JWTAccessToken](
            token_type=TokenType.ACCESS_TOKEN,
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
        status_code=status.HTTP_200_OK,
        content=f'Сообщение с id {message_id} удалено'
    )
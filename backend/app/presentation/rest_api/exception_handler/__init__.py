from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.business_logic.exceptions import CheckPswError, CheckMasterPswError, RefreshTokenInActive, \
    RefreshTokenIdNotFound, VerifyCodeInCorrect, VerifyCodeStorageError, PermissionFileDownError, UserNotFoundInRoom, \
    GenerateInviteTokenOnlyOwner
from app.data_access.exceptions import (
    DataBaseError,
    ConnectionDBError,
    DBTimeoutError,
    RecordNotFound,
    InCorrectStmtError,
    BreachIntegrity,
    UniqueViolationError,
    ForeignKeyViolationError,
    NotNullViolationError
)
from app.presentation.rest_api.exception_handler.auth_exc_handler import (
    psw_error,
    psw_error_master_key,
    refresh_token_in_active,
    refresh_token_not_found,
    verify_code_incorrect,
    verify_code_storage_error
)
from app.presentation.rest_api.exception_handler.base import validation_exception_handler
from app.presentation.rest_api.exception_handler.database_exc_handler import (
    breach_integrity_error,
    connection_db_error,
    db_base_error,
    foreignkey_violation_error,
    incorrect_stmt_error,
    not_null_violation_error,
    record_not_found_db_error,
    time_out_db_error,
    unique_violation_error,
)
from app.presentation.rest_api.exception_handler.message_exc_handler import permission_file_down_error, \
    file_not_found_error, user_not_found_in_room
from app.presentation.rest_api.exception_handler.room_exc_handler import generate_invite_url_only_owner


def register_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(BreachIntegrity, breach_integrity_error)
    app.add_exception_handler(ConnectionDBError, connection_db_error)
    app.add_exception_handler(DataBaseError, db_base_error)
    app.add_exception_handler(ForeignKeyViolationError, foreignkey_violation_error)
    app.add_exception_handler(InCorrectStmtError, incorrect_stmt_error)
    app.add_exception_handler(NotNullViolationError, not_null_violation_error)
    app.add_exception_handler(RecordNotFound, record_not_found_db_error)
    app.add_exception_handler(DBTimeoutError, time_out_db_error)
    app.add_exception_handler(UniqueViolationError, unique_violation_error)

    app.add_exception_handler(CheckPswError, psw_error)
    app.add_exception_handler(CheckMasterPswError, psw_error_master_key)
    app.add_exception_handler(RefreshTokenInActive, refresh_token_in_active)
    app.add_exception_handler(RefreshTokenIdNotFound, refresh_token_not_found)
    app.add_exception_handler(VerifyCodeInCorrect, verify_code_incorrect)
    app.add_exception_handler(VerifyCodeStorageError, verify_code_storage_error)

    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    app.add_exception_handler(PermissionFileDownError, permission_file_down_error)
    app.add_exception_handler(FileNotFoundError, file_not_found_error)
    app.add_exception_handler(UserNotFoundInRoom, user_not_found_in_room)

    app.add_exception_handler(GenerateInviteTokenOnlyOwner, generate_invite_url_only_owner)




__version__ = 'v1.4.1'
__author__ = 'RomesAll'
__all__ = [
    'register_exception_handler'
]
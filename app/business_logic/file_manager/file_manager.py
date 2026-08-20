from fastapi import UploadFile
import aiofiles


class FileManager:
    """Менеджер для потокового чтенеия-записи файла"""
    @classmethod
    async def read_file(cls, file_path, chunk_size: int = 65536):
        """Генератор для потокового чтения из файла"""
        async with aiofiles.open(file_path, mode="rb") as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    @classmethod
    async def read_upload_file_in_chunks(cls, upload_file: UploadFile, chunk_size: int = 65536):
        """Генератор для потокового чтения из UploadFile Fastapi"""
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break
            yield chunk

    @classmethod
    async def write_file(cls, path_to_save: str, file: UploadFile, chunk_size: int = 65536):
        """Функция для потокового сохранения"""
        async with aiofiles.open(path_to_save, mode="wb") as f:
            async for chunk in cls.read_upload_file_in_chunks(file, chunk_size):
                await f.write(chunk)
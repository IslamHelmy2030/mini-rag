from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController
from models import ResponseSignal
import aiofiles
import logging

logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id:str}")
async def upload_data(
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
):
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    result = {
        "is_valid": is_valid,
        "result_signal": result_signal
    }
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)

    file_path = data_controller.generate_unique_filename(file.filename, project_id)
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            chunk_size = getattr(app_settings, "FILE_DEFAULT_CHUNK_SIZE", 1048576)
            while chunk := await file.read(chunk_size):
                await out_file.write(chunk)
    except Exception as e:
        logger.exception("Error uploading file: %s", e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": False,
                "result_signal": ResponseSignal.FILE_UPLOADED_FAILED.value,
            },
        )

    return JSONResponse(
        content={
            "is_valid": is_valid,
            "result_signal": ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value
        }
    )

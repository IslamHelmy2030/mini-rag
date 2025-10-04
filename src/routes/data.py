from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProcessController
from models import ResponseSignal
import aiofiles
import logging
from .schemes.data import ProcessRequest




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

    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
        "is_valid": is_valid,
        "result_signal": result_signal
    })

    file_path, file_id = data_controller.generate_unique_filepath(file.filename, project_id)
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
            "result_signal": ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value,
            "file_id": file_id,
        }
    )


@data_router.post("/process/{project_id:str}")
async def process_data(project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    process_controller = ProcessController(project_id)

    file_content = process_controller.get_file_content(file_id)
    file_chunks = process_controller.process_file_content(file_content, file_id, chunk_size, overlap_size)

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result_signal": ResponseSignal.PROCESSING_FAILED.value,
            },
        )
    return file_chunks


from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProcessController
from models import ResponseSignal
import aiofiles
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from models.enums.AssetTypeEnum import AssetTypeEnum
import os


#logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
):
    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb)

    project = await project_model.get_project_or_create_one(project_id)


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
        #logger.exception("Error uploading file: %s", e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": False,
                "result_signal": ResponseSignal.FILE_UPLOADED_FAILED.value,
            },
        )

    #Store the assets in the database
    asset_model = await AssetModel.create_instance(db_client=request.app.mongodb)
    asset_resource = Asset(
        asset_project_id = project.id,
        asset_type = AssetTypeEnum.FILE.value,
        asset_name = file_id,
        asset_size = os.path.getsize(file_path)

    )

    asset_record = await asset_model.create_asset(asset_resource)

    return JSONResponse(
        content={
            "is_valid": is_valid,
            "result_signal": ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value,
            "asset_record":str(asset_record.id)
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(request:Request, project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb)
    project = await project_model.get_project_or_create_one(project_id)

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

    file_chunks_records = [
        DataChunk(
            chunk_text = chunk.page_content,
            chunk_metadata = chunk.metadata,
            chunk_order = i+1,
            chunk_project_id = project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    chunk_model = await ChunkModel.create_instance(db_client=request.app.mongodb)

    if process_request.do_reset == 1:
        await chunk_model.delete_chunks_by_project_id(project.id)

    no_records = await chunk_model.insert_many_chunks(file_chunks_records)

    return JSONResponse(
        content={
            "result_signal": ResponseSignal.PROCESSING_SUCCESSFULLY.value,
            "inserted_chunks": no_records,
        }
    )


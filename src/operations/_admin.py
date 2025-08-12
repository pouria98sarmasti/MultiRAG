


from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from pydantic import validate_call

import uuid


from src.operations._db_setup import get_sqlalchemy_db
from src.models._admin import AdminUploadedDatasetInfo, AdminUploadedDatasetContent
from src.schema._admin import AdminUploadedDatasetType
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AdminUploadedDatasetContentOperations:
    def __init__(self) -> None:
        self.session = get_sqlalchemy_db
    

    async def create(self, dataset_id: uuid.UUID, content: bytes):
        dataset = AdminUploadedDatasetContent(
            dataset_id=dataset_id,
            content=content,
        )
        
        async with self.session() as session:
            session.add(dataset)
            await session.commit()
        

    
    async def get_content(self, dataset_id: uuid.UUID):
        query = sa.select(AdminUploadedDatasetContent).where(AdminUploadedDatasetContent.dataset_id==dataset_id)
        
        async with self.session() as session:
            dataset = await session.scalar(query)

        if dataset:
            return dataset.content
        else:
            return dataset


class AdminUploadedDatasetInfoOperations:
    def __init__(self) -> None:
        self.session = get_sqlalchemy_db
    
    
    @validate_call
    async def create(self, name: str, dataset_type: AdminUploadedDatasetType, expertise: str, file_size_mb: float, admin_id: uuid.UUID):
        dataset = AdminUploadedDatasetInfo(
            dataset_name=name,
            expertise=expertise,
            dataset_type=dataset_type,
            # dataset_content=dataset_content,
            file_size_mb=file_size_mb,
            admin_id=admin_id,
        )
        
        async with self.session() as session:
            session.add(dataset)
            await session.commit()
        
        return dataset
    
    async def delete(self, dataset_id: uuid.UUID):
        query = sa.delete(AdminUploadedDatasetInfo).where(AdminUploadedDatasetInfo.id==dataset_id)
        
        async with self.session() as session:
            _ = await session.execute(query)
            await session.commit()
    
    async def get_by_dataset_id(self, dataset_id: uuid.UUID):
        query = sa.select(AdminUploadedDatasetInfo).where(AdminUploadedDatasetInfo.id==dataset_id)
        
        async with self.session() as session:
            dataset = await session.scalar(query)
        
        return dataset
    
    async def list_by_admin_id(self, admin_id: uuid.UUID):
        query = sa.select(AdminUploadedDatasetInfo).where(AdminUploadedDatasetInfo.admin_id==admin_id)
        
        async with self.session() as session:
            datasets = await session.scalars(query)
        
        return datasets.all()
    
    
    
    async def list_by_vectorize_status(self, is_vectorized: bool | None = None):
        if is_vectorized is None:
            query = sa.select(AdminUploadedDatasetInfo)
        else:
            query = sa.select(AdminUploadedDatasetInfo).where(AdminUploadedDatasetInfo.is_vectorized==is_vectorized)
        
        async with self.session() as session:
            datasets = await session.scalars(query)
        
        return datasets.all()
    
    async def change_vectorize_status(self, dataset_id:uuid.UUID, is_vectorized: bool):
        select_query = sa.select(AdminUploadedDatasetInfo).where(AdminUploadedDatasetInfo.id==dataset_id)
        update_query = sa.update(AdminUploadedDatasetInfo).where(AdminUploadedDatasetInfo.id==dataset_id).values(is_vectorized=is_vectorized)
        
        async with self.session() as session:
            dataset = await session.scalar(select_query)
            if dataset:
                _ = await session.execute(update_query)
                await session.commit()
                dataset.is_vectorized = is_vectorized
                return dataset
            else:
                raise ValueError(f"Upload with ID {dataset_id} not found")


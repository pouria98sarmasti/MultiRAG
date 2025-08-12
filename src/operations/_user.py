


from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

import uuid


from src.operations._db_setup import get_sqlalchemy_db
from src.models._user import UserUploadedDatasetType, UserUploadedDataset, User
from src.schema._user import ListAllUsersOutput, UserCreateOutput
from src.utils.logger import setup_logger

logger = setup_logger(__name__)




class UserOperations:
    def __init__(self) -> None:
        self.session = get_sqlalchemy_db
    
    async def create(self, username: str, user_id: uuid.UUID):
        new_user = User(
            username=username,
            id=user_id,
        )
        
        async with self.session() as session:
            session.add(new_user)
            await session.commit()
        
        # return new_user
        return UserCreateOutput(**new_user.__dict__)

    async def delete(self, user_id: uuid.UUID):
        query = sa.delete(User).where(User.id==user_id)
        
        async with self.session() as session:
            _ = await session.execute(query)
            await session.commit()

    async def get(self, user_id: uuid.UUID):
        query = sa.select(User).where(User.id==user_id)
        
        async with self.session() as session:
            user_data = await session.scalar(query)
        
        return user_data
    
    
    async def list_all_users(self):
        query = sa.select(User)
        
        async with self.session() as session:
            users = await session.scalars(query)
            users = users.all()
        if users: users = [ListAllUsersOutput(**i.__dict__) for i in users]
        return users





class UserUploadedDatasetOperation:
    def __init__(self) -> None:
        self.session = get_sqlalchemy_db
    
    
    
    async def create(self, dataset_type: UserUploadedDatasetType, dataset_content: bytes, user_id: uuid.UUID):
        user_upload = UserUploadedDataset(
            dataset_type=dataset_type,
            dataset_content=dataset_content,
            user_id=user_id,
        )
        
        async with self.session() as session:
            session.add(user_upload)
            await session.commit()
        
        return user_upload
    
    async def delete(self, dataset_id: uuid.UUID):
        query = sa.delete(UserUploadedDataset).where(UserUploadedDataset.id==dataset_id)
        
        async with self.session() as session:
            _ = await session.execute(query)
            await session.commit()
    
    async def get_by_dataset_id(self, dataset_id: uuid.UUID):
        query = sa.select(UserUploadedDataset).where(UserUploadedDataset.id==dataset_id)
        
        async with self.session() as session:
            dataset = await session.scalar(query)
        
        return dataset
    
    async def list_by_user_id(self, user_id: uuid.UUID):
        query = sa.select(UserUploadedDataset).where(UserUploadedDataset.user_id==user_id)
        
        async with self.session() as session:
            datasets = await session.scalars(query)
        
        return datasets.all()
    
    async def list_by_vectorize_status(self, is_vectorized: bool):
        query = sa.select(UserUploadedDataset).where(UserUploadedDataset.is_vectorized==is_vectorized)
        
        async with self.session() as session:
            datasets = await session.scalars(query)
        
        return datasets.all()
    
    async def change_vectorize_status(self, dataset_id:uuid.UUID, is_vectorized: bool):
        select_query = sa.select(UserUploadedDataset).where(UserUploadedDataset.id==dataset_id)
        update_query = sa.update(UserUploadedDataset).where(UserUploadedDataset.id==dataset_id).values(is_vectorized=is_vectorized)
        
        async with self.session() as session:
            dataset = await session.scalar(select_query)
            if dataset:
                _ = await session.execute(update_query)
                await session.commit()
                dataset.is_vectorized = is_vectorized
                return dataset
            else:
                raise ValueError(f"Upload with ID {dataset_id} not found")


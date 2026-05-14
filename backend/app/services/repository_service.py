from ..models.repository import Repository
from ..core import db


class RepositoryService:
    @staticmethod
    async def create_repository(repo_data: dict) -> Repository:
        async for session in db.get_db():
            from sqlalchemy import select
            stmt = select(Repository).where(
                Repository.full_name == repo_data["full_name"],
                Repository.user_id == repo_data.get("user_id")
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                return existing

            repo = Repository(
                owner=repo_data["owner"],
                name=repo_data["name"],
                full_name=repo_data["full_name"],
                user_id=repo_data.get("user_id"),
                description=repo_data.get("description"),
                html_url=repo_data["html_url"],
                visibility=repo_data.get("visibility"),
            )
            session.add(repo)
            await session.commit()
            await session.refresh(repo)
            return repo

from ..models.repository import Repository
from ..core import db


class RepositoryService:
    @staticmethod
    async def create_repository(repo_data: dict) -> Repository:
        async for session in db.get_db():
            repo = Repository(
                owner=repo_data["owner"],
                name=repo_data["name"],
                full_name=repo_data["full_name"],
                description=repo_data.get("description"),
                html_url=repo_data["html_url"],
                visibility=repo_data.get("visibility"),
            )
            session.add(repo)
            await session.commit()
            await session.refresh(repo)
            return repo

from neo4j import GraphDatabase
from ..core.config import settings


class Neo4jClient:
    def __init__(self):
        uri = settings.NEO4J_URI
        user = settings.NEO4J_USER
        pwd = settings.NEO4J_PASSWORD
        if uri and user and pwd:
            self._driver = GraphDatabase.driver(uri, auth=(user, pwd))
        else:
            self._driver = None

    def close(self):
        if self._driver:
            self._driver.close()

    def ping(self) -> bool:
        if not self._driver:
            return False
        try:
            with self._driver.session() as s:
                s.run("RETURN 1")
            return True
        except Exception:
            return False

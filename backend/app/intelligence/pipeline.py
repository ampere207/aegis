import os
import logging
import uuid
import asyncio
from typing import List, Dict, Any
from .parser.engine import ParserEngine, SemanticEntity
from .parser.extractors.python import PythonExtractor
from .parser.extractors.typescript import TypeScriptExtractor
from .graph.builder import GraphBuilder
from .reasoning.workflow import ReasoningWorkflow, AgentState
from ..services.neo4j_service import Neo4jService
from ..core import db
from ..core.config import settings
from ..models.analysis import Analysis
from ..models.finding import Finding

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    def __init__(self, repo_id: int, repo_path: str):
        self.repo_id = repo_id
        self.repo_path = repo_path
        self.parser_engine = ParserEngine()
        self.extractors = {
            "python": PythonExtractor(self.parser_engine),
            "typescript": TypeScriptExtractor(self.parser_engine),
            "tsx": TypeScriptExtractor(self.parser_engine),
            "javascript": TypeScriptExtractor(self.parser_engine),
        }
        self.graph_builder = GraphBuilder(repo_id)
        self.reasoning_workflow = ReasoningWorkflow()

    async def run(self):
        """Execute the full semantic analysis pipeline."""
        logger.info(f"Starting analysis for repo {self.repo_id} at {self.repo_path}")
        
        if not os.path.exists(self.repo_path):
            logger.error(f"Repository path does not exist: {self.repo_path}")
            return [{"title": "Error", "description": f"Repository path not found: {self.repo_path}. Ensure the repository is cloned."}]

        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. Skipping AI reasoning.")
            # Return some placeholder findings
            return [{"title": "AI Reasoning Disabled", "description": "Please set GEMINI_API_KEY to enable architectural reasoning."}]
        
        # 1. Scan and Parse
        entities = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.repo_path)
                
                # Language detection
                _, ext = os.path.splitext(file)
                lang = self.parser_engine.get_language(ext)
                if not lang:
                    continue
                
                # Parse
                logger.info(f"Parsing file: {rel_path} (lang: {lang})")
                try:
                    tree = self.parser_engine.parse_file(file_path)
                    if not tree:
                        logger.warning(f"Failed to parse {rel_path}: Parser returned no tree.")
                        continue
                except Exception as e:
                    logger.error(f"Parser crash on {rel_path}: {e}")
                    continue
                
                # Extract
                extractor = self.extractors.get(lang)
                if extractor:
                    try:
                        file_entities = extractor.extract(rel_path, tree)
                        entities.extend(file_entities)
                    except Exception as e:
                        logger.error(f"Extraction failed for {rel_path}: {e}")
        
        logger.info(f"Extracted {len(entities)} semantic entities")

        # 2. Build Graph
        try:
            await self.graph_builder.build_graph(entities)
            logger.info("Semantic graph generated")
        except Exception as e:
            logger.error(f"Graph building failed: {e}")

        # 3. Security Reasoning
        graph_context = [e.model_dump() for e in entities]
        
        state: AgentState = {
            "repo_context": f"Repository ID: {self.repo_id}",
            "graph_context": graph_context,
            "findings": [],
            "analysis_depth": 1
        }
        
        try:
            reasoner = self.reasoning_workflow.create_graph()
            final_state = await reasoner.ainvoke(state)
            findings_data = final_state["findings"]
            
            # 4. Persistence
            await self._persist_findings(findings_data)
            await self._index_entities(entities)
            
            logger.info("AI Reasoning and Persistence complete")
            return findings_data
        except Exception as e:
            logger.error(f"AI Reasoning failed: {e}")
            return [{"title": "AI Error", "description": f"Failed to generate AI insights: {str(e)}"}]

    async def _persist_findings(self, findings_data: List[Dict[str, Any]]):
        """Save findings to PostgreSQL."""
        async for session in db.get_db():
            # Create a new analysis record
            from ..models.analysis import AnalysisStatus
            analysis = Analysis(repository_id=self.repo_id, status=AnalysisStatus.COMPLETED)
            session.add(analysis)
            await session.flush()
            
            for f in findings_data:
                finding = Finding(
                    analysis_id=analysis.id,
                    title=f.get("title", "Unknown Finding"),
                    description=f.get("description", ""),
                    severity=f.get("severity", "medium"),
                    type=f.get("type", "architectural"),
                    extra_data = f.get("metadata", {})
                )
                session.add(finding)
            
            await session.commit()
            break

    async def _index_entities(self, entities: List[SemanticEntity]):
        """Index semantic entities in Qdrant for vector intelligence."""
        from ..services.qdrant_service import QdrantService
        from qdrant_client.models import PointStruct
        
        points = []
        for entity in entities:
            # Simple hash-based vector for now (in real system, use Gemini embeddings)
            # Placeholder 1536-dim vector
            vector = [0.0] * 1536 
            point_id = str(uuid.uuid4())
            points.append(PointStruct(
                id=point_id,
                vector=vector,
                payload=entity.model_dump()
            ))
        
        if points:
            await QdrantService.upsert_points(points)
            logger.info(f"Indexed {len(points)} entities in Qdrant")



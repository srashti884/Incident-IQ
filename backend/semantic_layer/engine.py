"""
IncidentIQ - Semantic Data Layer Engine
Loads and caches semantic metadata (glossary, mappings, metrics).
Provides synonym resolution, entity normalization, and canonical definitions.
"""
import os
import json
from typing import Dict, Any, Optional, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SEMANTIC_DIR = os.path.join(BASE_DIR, "semantic")

class SemanticEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticEngine, cls).__new__(cls)
            cls._instance._load_all()
        return cls._instance

    def _load_all(self):
        try:
            with open(os.path.join(SEMANTIC_DIR, "glossary.json"), "r", encoding="utf-8") as f:
                self.glossary = json.load(f)
        except Exception:
            self.glossary = {}

        try:
            with open(os.path.join(SEMANTIC_DIR, "mappings.json"), "r", encoding="utf-8") as f:
                self.mappings = json.load(f)
        except Exception:
            self.mappings = {}

        try:
            with open(os.path.join(SEMANTIC_DIR, "metrics.json"), "r", encoding="utf-8") as f:
                self.metrics = json.load(f).get("metrics", {})
        except Exception:
            self.metrics = {}

    def reload(self):
        self._load_all()

    def resolve_application(self, term: str) -> Optional[str]:
        term_clean = term.lower().strip()
        app_aliases = self.mappings.get("entity_mappings", {}).get("application", {}).get("aliases", {})
        if term_clean in app_aliases:
            return app_aliases[term_clean]
        for alias, canon in app_aliases.items():
            if alias in term_clean or term_clean in alias:
                return canon
        return None

    def resolve_service(self, term: str) -> Optional[str]:
        term_clean = term.lower().strip()
        svc_aliases = self.mappings.get("service_mappings", {})
        if term_clean in svc_aliases:
            return svc_aliases[term_clean]
        for alias, canon in svc_aliases.items():
            if alias in term_clean:
                return canon
        return None

    def resolve_severity(self, term: str) -> Optional[str]:
        term_clean = term.lower().strip()
        sev_aliases = self.mappings.get("entity_mappings", {}).get("severity", {}).get("aliases", {})
        return sev_aliases.get(term_clean)

    def resolve_status(self, term: str) -> Optional[List[str]]:
        term_clean = term.lower().strip()
        stat_aliases = self.mappings.get("entity_mappings", {}).get("status", {}).get("aliases", {})
        return stat_aliases.get(term_clean)

    def resolve_sla(self, term: str) -> Optional[int]:
        term_clean = term.lower().strip()
        sla_aliases = self.mappings.get("entity_mappings", {}).get("sla", {}).get("aliases", {})
        return sla_aliases.get(term_clean)

    def get_metric(self, metric_id: str) -> Optional[Dict[str, Any]]:
        return self.metrics.get(metric_id)

    def get_all_metrics(self) -> Dict[str, Any]:
        return self.metrics

    def get_glossary(self) -> Dict[str, Any]:
        return self.glossary

semantic_engine = SemanticEngine()

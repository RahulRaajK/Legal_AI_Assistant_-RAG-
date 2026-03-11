"""In-memory legal knowledge graph using NetworkX."""
import networkx as nx
import json
from typing import Optional


class LegalKnowledgeGraph:
    """Knowledge graph for legal entity relationships.
    
    Nodes: Acts, Sections, Cases, Judges, Legal Principles
    Edges: cites, belongs_to, judged_by, similar_to, amends, repeals
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.graph = nx.DiGraph()
        return cls._instance
    
    def add_act(self, act_id: str, name: str, year: int = None, **kwargs):
        """Add a legislative act node."""
        self.graph.add_node(act_id, type="act", name=name, year=year, **kwargs)
    
    def add_section(self, section_id: str, title: str, act_id: str, number: str, **kwargs):
        """Add a section node and link to its act."""
        self.graph.add_node(section_id, type="section", title=title, number=number, **kwargs)
        self.graph.add_edge(section_id, act_id, relationship="belongs_to")
    
    def add_case(self, case_id: str, title: str, year: int = None, court: str = None, **kwargs):
        """Add a case/judgment node."""
        self.graph.add_node(case_id, type="case", title=title, year=year, court=court, **kwargs)
    
    def add_judge(self, judge_id: str, name: str, court: str = None, **kwargs):
        """Add a judge node."""
        self.graph.add_node(judge_id, type="judge", name=name, court=court, **kwargs)
    
    def add_citation(self, case_id: str, section_id: str):
        """Create a 'cites' relationship from case to section/act."""
        self.graph.add_edge(case_id, section_id, relationship="cites")
    
    def add_judgment(self, case_id: str, judge_id: str):
        """Create a 'judged_by' relationship."""
        self.graph.add_edge(case_id, judge_id, relationship="judged_by")
    
    def add_case_similarity(self, case1_id: str, case2_id: str, score: float = 0.0):
        """Link two similar cases."""
        self.graph.add_edge(case1_id, case2_id, relationship="similar_to", score=score)
    
    def add_amendment(self, new_act_id: str, old_act_id: str):
        """Link an amending act to the original."""
        self.graph.add_edge(new_act_id, old_act_id, relationship="amends")
    
    def add_repeal(self, new_act_id: str, old_act_id: str):
        """Link a repealing act to the repealed one."""
        self.graph.add_edge(new_act_id, old_act_id, relationship="repeals")
    
    def get_sections_of_act(self, act_id: str) -> list[dict]:
        """Get all sections belonging to an act."""
        sections = []
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "section":
                for _, target, edge_data in self.graph.edges(node, data=True):
                    if target == act_id and edge_data.get("relationship") == "belongs_to":
                        sections.append({"id": node, **data})
        return sorted(sections, key=lambda x: x.get("number", ""))
    
    def get_cases_citing_section(self, section_id: str) -> list[dict]:
        """Get all cases that cite a particular section."""
        cases = []
        for source, target, data in self.graph.edges(data=True):
            if target == section_id and data.get("relationship") == "cites":
                node_data = self.graph.nodes[source]
                if node_data.get("type") == "case":
                    cases.append({"id": source, **node_data})
        return cases
    
    def get_related_cases(self, case_id: str) -> list[dict]:
        """Get cases similar to a given case."""
        related = []
        for source, target, data in self.graph.edges(data=True):
            if data.get("relationship") == "similar_to":
                if source == case_id:
                    related.append({"id": target, **self.graph.nodes[target], "score": data.get("score", 0)})
                elif target == case_id:
                    related.append({"id": source, **self.graph.nodes[source], "score": data.get("score", 0)})
        return related
    
    def get_graph_stats(self) -> dict:
        """Get knowledge graph statistics."""
        type_counts = {}
        for _, data in self.graph.nodes(data=True):
            node_type = data.get("type", "unknown")
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        rel_counts = {}
        for _, _, data in self.graph.edges(data=True):
            rel = data.get("relationship", "unknown")
            rel_counts[rel] = rel_counts.get(rel, 0) + 1
        
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": type_counts,
            "relationship_types": rel_counts,
        }
    
    def search_nodes(self, query: str, node_type: Optional[str] = None, limit: int = 20) -> list[dict]:
        """Search nodes by name/title."""
        results = []
        query_lower = query.lower()
        for node_id, data in self.graph.nodes(data=True):
            if node_type and data.get("type") != node_type:
                continue
            name = data.get("name", data.get("title", "")).lower()
            if query_lower in name or query_lower in node_id.lower():
                results.append({"id": node_id, **data})
                if len(results) >= limit:
                    break
        return results


# Singleton
knowledge_graph = LegalKnowledgeGraph()

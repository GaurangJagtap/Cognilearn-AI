"""
Visual Classifier Module for AI Teacher.

Determines the optimal visual representation type (diagram, graph, code, timeline, equation)
for any given educational concept, implementing Section 2.7 & Section 10 of the architecture.
"""

import re
from typing import Dict, Any, Optional

# Strict visual types allowed in Gaurang's Lesson Plan JSON
VALID_VISUAL_TYPES = {"diagram", "graph", "code", "timeline", "equation"}

# Keyword heuristic mappings (checked with regex word boundaries)
PROGRAMMING_KEYWORDS = [
    r"\bcode\b", r"\bpython\b", r"\bjavascript\b", r"\bjava\b", r"\bc\+\+\b",
    r"\bfunction\b", r"\bvariable\b", r"\barray\b", r"\bfor loop\b", r"\bwhile loop\b",
    r"\balgorithm\b", r"\brecursion\b", r"\bclass\b", r"\bobject\b", r"\bapi\b",
    r"\bdatabase\b", r"\bsql\b", r"\bcompiler\b", r"\bdata structure\b", r"\bpointer\b",
    r"\bstack\b", r"\bqueue\b", r"\bbinary tree\b", r"\breact\b"
]

TIMELINE_KEYWORDS = [
    r"\bhistory\b", r"\bwar\b", r"\bcentury\b", r"\bera\b", r"\brevolution\b",
    r"\btimeline\b", r"\bchronology\b", r"\bdynasty\b", r"\bancient\b", r"\bmedieval\b",
    r"\bmodern era\b", r"\bindependence\b", r"\bevolution\b", r"\bhistorical\b",
    r"\btreaty\b", r"\bempire\b", r"\bperiod\b"
]

EQUATION_KEYWORDS = [
    r"\bequation\b", r"\bformula\b", r"\bderivation\b", r"\bintegral\b", r"\bderivative\b",
    r"\bcalculus\b", r"\balgebra\b", r"\bquadratic\b", r"\btheorem\b", r"\bpythagorean\b",
    r"\bschrod[i|o]nger\b", r"\bmaxwell\b", r"\bmatrix\b", r"\bpolynomial\b", r"\bstoichiometry\b"
]

GRAPH_KEYWORDS = [
    r"\bgraph\b", r"\bcurve\b", r"\bplot\b", r"\bchart\b", r"\bscatter\b",
    r"\bhistogram\b", r"\bslope\b", r"\blinear relationship\b", r"\bexponential growth\b",
    r"\bparabola\b", r"\bsine wave\b", r"\bv-i characteristics\b", r"\bfrequency response\b",
    r"\bdistribution\b"
]

PHYSICS_DIAGRAM_KEYWORDS = [
    r"\bcircuit\b", r"\bcurrent\b", r"\bvoltage\b", r"\bohm'?s law\b", r"\bresistor\b",
    r"\bcapacitor\b", r"\btransformer\b", r"\bmagnet\w*\b", r"\bforce\b",
    r"\bnewton'?s law\w*\b", r"\bgravity\b", r"\boptics\b", r"\bray diagram\b"
]

BIOLOGY_DIAGRAM_KEYWORDS = [
    r"\bcell\b", r"\banatomy\b", r"\borgan\b", r"\bphotosynthesis\b", r"\brespiration\b",
    r"\bheart\b", r"\bdigestive\b", r"\bdna\b", r"\bplant\b", r"\bmitochondria\b"
]


def _matches_any(patterns: list, text: str) -> bool:
    """Checks if any regex pattern matches in the text."""
    lower_text = text.lower()
    return any(re.search(p, lower_text) for p in patterns)


def infer_subject(concept: str, subject_hint: Optional[str] = None) -> str:
    """Infers the high-level subject area from concept text and hint."""
    if subject_hint and subject_hint.strip():
        hint = subject_hint.lower().strip()
        if "math" in hint:
            return "mathematics"
        if "phys" in hint or "electr" in hint:
            return "physics"
        if "bio" in hint or "chem" in hint:
            return "biology"
        if "hist" in hint:
            return "history"
        if "code" in hint or "prog" in hint or "soft" in hint or "comp" in hint:
            return "programming"

    if _matches_any(PROGRAMMING_KEYWORDS, concept):
        return "programming"
    if _matches_any(TIMELINE_KEYWORDS, concept):
        return "history"
    if _matches_any(BIOLOGY_DIAGRAM_KEYWORDS, concept):
        return "biology"
    if _matches_any(PHYSICS_DIAGRAM_KEYWORDS, concept):
        return "physics"
    if _matches_any(EQUATION_KEYWORDS, concept) or _matches_any(GRAPH_KEYWORDS, concept):
        return "mathematics"

    return "general"


def classify_visual_with_reasoning(concept: str, subject_hint: Optional[str] = None) -> Dict[str, str]:
    """
    Classifies visual representation type and provides instructional reasoning.
    
    Returns:
        Dict with keys: 'subject_area', 'visual_type', 'reasoning'
    """
    subject = infer_subject(concept, subject_hint)

    # 1. Subject is Physics
    if subject == "physics":
        if _matches_any(GRAPH_KEYWORDS, concept):
            return {
                "subject_area": "physics",
                "visual_type": "graph",
                "reasoning": "Physics concept highlights parametric dependency across variables, best visualized as an analytical graph with formula annotation."
            }
        if _matches_any(EQUATION_KEYWORDS, concept):
            return {
                "subject_area": "physics",
                "visual_type": "equation",
                "reasoning": "Concept focuses on mathematical physics relations, best rendered as a clear LaTeX equation."
            }
        return {
            "subject_area": "physics",
            "visual_type": "diagram",
            "reasoning": "Concept involves physical components or circuit relationships, best shown as a clear labeled schematic diagram."
        }

    # 2. Subject is Biology
    if subject == "biology":
        return {
            "subject_area": "biology",
            "visual_type": "diagram",
            "reasoning": "Biological structures and physiological pathways are best comprehended through labeled anatomical diagrams."
        }

    # 3. Subject is History
    if subject == "history" or _matches_any(TIMELINE_KEYWORDS, concept):
        return {
            "subject_area": "history",
            "visual_type": "timeline",
            "reasoning": "Concept involves chronological sequence and historical events, best represented as an interactive milestone timeline."
        }

    # 4. Subject is Programming
    if subject == "programming" or _matches_any(PROGRAMMING_KEYWORDS, concept):
        return {
            "subject_area": "programming",
            "visual_type": "code",
            "reasoning": "Concept involves programming logic and execution syntax, best demonstrated via syntax-highlighted code block and terminal output."
        }

    # 5. Subject is Mathematics / Derivations / Equations
    if _matches_any(EQUATION_KEYWORDS, concept):
        return {
            "subject_area": "mathematics",
            "visual_type": "equation",
            "reasoning": "Concept involves formal symbolic proofs and algebraic relations, best rendered as a step-by-step LaTeX formula."
        }

    # 6. Graphs & Curves
    if _matches_any(GRAPH_KEYWORDS, concept):
        return {
            "subject_area": "mathematics" if subject == "general" else subject,
            "visual_type": "graph",
            "reasoning": "Concept represents continuous mathematical relationships or empirical measurements, best illustrated with a 2D coordinate graph."
        }

    # Default fallback
    return {
        "subject_area": subject,
        "visual_type": "diagram",
        "reasoning": "Visual schematic and structured diagram effectively clarifies core conceptual relationships."
    }


def classify_visual(concept: str, subject_hint: Optional[str] = None) -> str:
    """
    Classifies visual type for a given concept.
    
    Guarantees returning strictly one of: 'diagram', 'graph', 'code', 'timeline', 'equation'.
    Adheres strictly to Gaurang's Handover Contract signature.
    """
    result = classify_visual_with_reasoning(concept, subject_hint)
    v_type = result.get("visual_type", "diagram")
    return v_type if v_type in VALID_VISUAL_TYPES else "diagram"

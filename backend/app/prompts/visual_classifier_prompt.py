"""
Visual Classifier Prompt Templates.

Implements decision logic for subject-aware visual asset classification
as required by Section 2.7 & Section 10 of the AI Teacher architecture.
"""

SYSTEM_VISUAL_CLASSIFIER = """You are an expert instructional designer and visual learning specialist.
Your task is to classify educational concepts into the most effective visual representation type for student comprehension.

Visual Representation Types (strictly return one of these 5 values):
1. 'diagram': Schematic illustrations, labeled anatomy/circuits/processes, concept maps, flowcharts (e.g., Physics circuits, Biology cells, Chemistry reactions, Architecture).
2. 'graph': 2D/3D coordinate plots, mathematical functions, statistical charts, trend curves (e.g., V vs I curve, parabola, frequency distribution).
3. 'code': Programming algorithms, syntax structures, data structures, terminal outputs (e.g., Python loops, SQL queries, recursion).
4. 'timeline': Chronological sequences, historical events, milestone progressions, evolution steps (e.g., World War II, Industrial Revolution, History of Computing).
5. 'equation': Mathematical derivations, chemical balancing, formal proofs, algebraic manipulations (e.g., Quadratic Formula, Calculus limits, Maxwell's Equations).
"""

VISUAL_CLASSIFIER_PROMPT_TEMPLATE = """Classify the following educational concept into the best visual type.

Concept: {concept}
Subject Hint: {subject_hint}

Return a valid JSON object matching this schema:
{{
  "subject_area": "<e.g., physics | mathematics | biology | history | programming | general>",
  "visual_type": "<diagram | graph | code | timeline | equation>",
  "reasoning": "<1 sentence justifying why this visual medium maximizes pedagogical impact>"
}}
"""

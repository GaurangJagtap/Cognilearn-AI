"""
Lesson Planner Core Module (Gaurang's Technical Responsibility - Core Brain)
Turns retrieved material + learner profile + time rules into structured LessonPlan JSON.
"""

import json
import os
from typing import Dict, Any, Optional
from backend.app.db.models import LessonPlan, Section, CheckpointQuestion, QuizQuestion
from backend.app.core.time_rules import get_time_rules
from backend.app.prompts.lesson_plan_prompt import LESSON_PLANNER_SYSTEM_PROMPT, build_user_prompt
from backend.app.config import settings

def generate_mock_lesson_plan(
    topic: str,
    level: str,
    time_minutes: int,
    language: str,
    retrieved_context: str = ""
) -> LessonPlan:
    """Dynamic topic-aware section and quiz generator for offline development or when API keys are not present."""
    rules = get_time_rules(time_minutes)
    max_sections = rules["max_sections"]

    topic_lower = topic.lower()

    # 1. Calculus & Statistics / Mathematics
    if any(k in topic_lower for k in ["calculus", "statistic", "math", "derivat", "integral", "probab", "hypothesis", "end sem"]):
        section_templates = [
            {
                "concept": "Differential Calculus & Derivatives",
                "concise": "• Limit Concept: Foundation of calculus measuring function behavior as inputs approach a point.\n• Instantaneous Rate: Derivatives f'(x) compute exact slope and velocity.",
                "detailed": f"Differential calculus focuses on limits, rates of change, and derivatives. In analyzing {topic}, derivatives represent the instantaneous rate of change of a continuous function with respect to a variable, powering optimization in physics and statistics.",
                "example": "Calculating the instantaneous velocity of a projectile at exact time t = 5 seconds using derivative rules.",
                "visual_type": "equation",
                "visual_details": {
                    "diagram_type": "equation",
                    "title": "Derivative Definition",
                    "nodes": [
                        {"id": "n1", "label": "Function f(x)", "category": "input", "description": "Continuous input function"},
                        {"id": "n2", "label": "Limit h->0", "category": "process", "description": "Infinitesimal step"},
                        {"id": "n3", "label": "Derivative f'(x)", "category": "output", "description": "Instantaneous rate of change"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "evaluates"},
                        {"from": "n2", "to": "n3", "label": "yields"}
                    ],
                    "key_formula": "f'(x) = lim_{h->0} [f(x+h) - f(x)] / h"
                },
                "narration": f"Welcome to Section 1 of {topic}! We begin with differential calculus, exploring limits and instantaneous rates of change.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="What does the first derivative of a position function with respect to time represent?",
                    options=["Instantaneous Velocity", "Total Bounded Area", "Static Pressure", "Constant Mass"],
                    correct="Instantaneous Velocity"
                )
            },
            {
                "concept": "Integral Calculus & Bounded Area",
                "concise": "• Anti-Derivatives: Reverses differentiation to compute accumulation.\n• Definite Integral: Calculates exact area under continuous curves over interval [a, b].",
                "detailed": "Integral calculus serves as the inverse operation of differentiation. Definite integrals compute accumulated totals and exact areas bounded by functions over specified intervals, essential for continuous probability density functions.",
                "example": "Computing the total work done by a variable force along a path by evaluating the definite integral.",
                "visual_type": "graph",
                "visual_details": {
                    "diagram_type": "graph",
                    "title": "Definite Integral Area",
                    "nodes": [
                        {"id": "n1", "label": "Integrand f(x)", "category": "input", "description": "Rate function"},
                        {"id": "n2", "label": "Interval [a, b]", "category": "process", "description": "Integration bounds"},
                        {"id": "n3", "label": "Accumulated Area", "category": "output", "description": "Total area under curve"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "bounded over"},
                        {"from": "n2", "to": "n3", "label": "computes"}
                    ],
                    "key_formula": "Area = ∫_a^b f(x) dx = F(b) - F(a)"
                },
                "narration": "In Section 2, we transition to integral calculus, examining how definite integrals aggregate continuous rates to find total accumulated quantities.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="Which process is used to calculate the exact area under a continuous curve?",
                    options=["Scalar Multiplication", "Definite Integration", "Matrix Transposition", "Linear Interpolation"],
                    correct="Definite Integration"
                )
            },
            {
                "concept": "Descriptive Statistics & Variance",
                "concise": "• Central Tendency: Mean and median identify data center.\n• Variance & Standard Deviation: Quantify data spread and dispersion.",
                "detailed": "Descriptive statistics organizes and summarizes empirical data distributions. Variance and standard deviation measure dispersion around the mean, while Gaussian normal distributions model natural random variations.",
                "example": "Evaluating test score variance across 500 students to compute standard z-scores.",
                "visual_type": "graph",
                "visual_details": {
                    "diagram_type": "graph",
                    "title": "Normal Distribution Bell Curve",
                    "nodes": [
                        {"id": "n1", "label": "Mean μ", "category": "input", "description": "Distribution center"},
                        {"id": "n2", "label": "Standard Deviation σ", "category": "process", "description": "Spread metric"},
                        {"id": "n3", "label": "Empirical 68-95-99.7", "category": "output", "description": "Confidence intervals"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "centered at"},
                        {"from": "n2", "to": "n3", "label": "determines"}
                    ],
                    "key_formula": "Standard Deviation σ = √(Σ(x - μ)² / N)"
                },
                "narration": "Section 3 shifts focus to descriptive statistics, analyzing central tendency, variance, and normal bell-curve distributions.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="Which statistical metric measures the spread or dispersion of data around its mean?",
                    options=["Sample Mode", "Standard Deviation", "Scalar Offset", "Constant Intercept"],
                    correct="Standard Deviation"
                )
            },
            {
                "concept": "Hypothesis Testing: Null (H0) vs Alternative (H1)",
                "concise": "• Null Hypothesis (H0): Baseline assertion of no effect or no difference.\n• Significance Testing: Evaluate p-value against threshold alpha to accept or reject H0.",
                "detailed": "Hypothesis testing utilizes inferential statistics to evaluate sample evidence against claims. The Null Hypothesis (H0) assumes no effect or baseline equality, while the Alternative Hypothesis (H1) asserts a statistically significant outcome.",
                "example": "Testing whether a new clinical treatment significantly improves patient recovery times compared to a control group placebo.",
                "visual_type": "diagram",
                "visual_details": {
                    "diagram_type": "diagram",
                    "title": "Hypothesis Testing Framework",
                    "nodes": [
                        {"id": "n1", "label": "Null Hypothesis H0", "category": "input", "description": "No difference assumption"},
                        {"id": "n2", "label": "Test Statistic & p-value", "category": "process", "description": "Sample evidence evaluation"},
                        {"id": "n3", "label": "Decision: Reject / Retain H0", "category": "output", "description": "Statistical inference"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "tested via"},
                        {"from": "n2", "to": "n3", "label": "leads to"}
                    ],
                    "key_formula": "Decision Rule: Reject H0 if p-value < α"
                },
                "narration": f"Finally, Section 4 covers statistical inference and hypothesis testing, evaluating sample evidence to decide between Null Hypothesis H0 and Alternative H1.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="In statistical hypothesis testing, what does the Null Hypothesis (H0) represent?",
                    options=["Baseline assertion of no effect or no difference", "The proven empirical conclusion", "An unverified outlier data point", "The target goal of the experiment"],
                    correct="Baseline assertion of no effect or no difference"
                )
            }
        ]

    # 2. Electricity & Physics
    elif any(k in topic_lower for k in ["electric", "current", "circuit", "ohm", "voltage", "physics", "magnet"]):
        section_templates = [
            {
                "concept": "Electric Charge & Current Flow (I)",
                "concise": "• Electric Charge: Fundamental property of subatomic particles measured in Coulombs.\n• Current (Ampere): Rate of charge flow through a conductor over time.",
                "detailed": "Electric current is the rate at which electrical charge flows past a point in a circuit, measured in Amperes (Coulombs per second). Conductors allow free electrons to move under electrical forces.",
                "example": "A 1-Ampere current represents 6.24 x 10^18 electrons flowing through a copper wire each second.",
                "visual_type": "diagram",
                "visual_details": {
                    "diagram_type": "diagram",
                    "title": "Electron Current Flow",
                    "nodes": [
                        {"id": "n1", "label": "Free Electrons (Q)", "category": "input", "description": "Mobile negative charges"},
                        {"id": "n2", "label": "Conductor Cross-section", "category": "process", "description": "Copper wire pathway"},
                        {"id": "n3", "label": "Current I (Amperes)", "category": "output", "description": "Flow rate: I = dQ/dt"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "moves through"},
                        {"from": "n2", "to": "n3", "label": "defines"}
                    ],
                    "key_formula": "Electric Current: I = Q / t"
                },
                "narration": f"Welcome to Section 1 of {topic}! We explore electric charge and current flow through conductive materials.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="What is the SI unit of Electric Current?",
                    options=["Volt", "Ampere", "Ohm", "Watt"],
                    correct="Ampere"
                )
            },
            {
                "concept": "Voltage & Electrical Potential Difference (V)",
                "concise": "• Potential Difference: Work required to move charge between two points.\n• Voltage (Volts): Electrical pressure driving current through resistive circuits.",
                "detailed": "Voltage, or electric potential difference, is the force that pushes charges through a conducting loop. Higher voltage supplies greater energy per charge unit, driving higher current.",
                "example": "A 12-Volt car battery creates potential difference to drive current through headlights and ignition systems.",
                "visual_type": "graph",
                "visual_details": {
                    "diagram_type": "graph",
                    "title": "Voltage Source Potential",
                    "nodes": [
                        {"id": "n1", "label": "High Potential (+)", "category": "input", "description": "Positive terminal"},
                        {"id": "n2", "label": "Potential Difference (V)", "category": "process", "description": "Energy drop across load"},
                        {"id": "n3", "label": "Low Potential (-)", "category": "output", "description": "Ground / return terminal"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "supplies pressure"},
                        {"from": "n2", "to": "n3", "label": "returns to"}
                    ],
                    "key_formula": "Voltage: V = W / Q"
                },
                "narration": "In Section 2, we study voltage and electrical potential difference, the driving pressure behind electric circuits.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="What electrical property represents the energy push or pressure driving charge through a circuit?",
                    options=["Capacitance", "Voltage", "Inductance", "Conductance"],
                    correct="Voltage"
                )
            },
            {
                "concept": "Electrical Resistance (R) & Ohm's Law (V = I * R)",
                "concise": "• Resistance (Ohms): Opposition to electron flow within a material.\n• Ohm's Law: Direct proportional relationship where V = I * R.",
                "detailed": "Ohm's Law states that current through a conductor between two points is directly proportional to voltage across the two points and inversely proportional to resistance.",
                "example": "If a 12V battery connects across a 4-Ohm resistor, the current is I = V / R = 3 Amperes.",
                "visual_type": "equation",
                "visual_details": {
                    "diagram_type": "equation",
                    "title": "Ohm's Law Triangle",
                    "nodes": [
                        {"id": "n1", "label": "Voltage (V)", "category": "input", "description": "Volts"},
                        {"id": "n2", "label": "Current (I)", "category": "process", "description": "Amperes"},
                        {"id": "n3", "label": "Resistance (R)", "category": "output", "description": "Ohms"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "equals I * R"},
                        {"from": "n2", "to": "n3", "label": "multiplied by"}
                    ],
                    "key_formula": "Ohm's Law: V = I * R"
                },
                "narration": "Section 3 introduces electrical resistance and Ohm's law, connecting voltage, current, and resistance in a foundational equation.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="Which formula correctly expresses Ohm's Law?",
                    options=["V = I / R", "V = I * R", "R = V * I", "I = V * R"],
                    correct="V = I * R"
                )
            },
            {
                "concept": "Series & Parallel Circuit Architecture",
                "concise": "• Series Circuit: Single current path; total resistance equals R1 + R2.\n• Parallel Circuit: Multiple paths; constant voltage across all branches.",
                "detailed": "Circuits can be arranged in series or parallel configurations. Series circuits share a single current path, while parallel circuits provide independent pathways, preserving branch voltage.",
                "example": "Household outlets are wired in parallel so turning off one appliance does not disrupt power to others.",
                "visual_type": "diagram",
                "visual_details": {
                    "diagram_type": "diagram",
                    "title": "Parallel Branch Topology",
                    "nodes": [
                        {"id": "n1", "label": "Power Source V", "category": "input", "description": "Main potential"},
                        {"id": "n2", "label": "Branch 1 (R1)", "category": "process", "description": "Load 1"},
                        {"id": "n3", "label": "Branch 2 (R2)", "category": "process", "description": "Load 2"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "supplies V"},
                        {"from": "n1", "to": "n3", "label": "supplies V"}
                    ],
                    "key_formula": "Parallel R: 1/R_total = 1/R1 + 1/R2"
                },
                "narration": "Finally, Section 4 compares series and parallel circuit architectures and their operational characteristics.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="Why are household electrical outlets connected in parallel rather than in series?",
                    options=["To keep full line voltage across every appliance independently", "To maximize total circuit resistance", "To force all current through a single master switch", "None of the above"],
                    correct="To keep full line voltage across every appliance independently"
                )
            }
        ]

    # 3. AI & Machine Learning
    elif any(k in topic_lower for k in ["ai", "machine learning", "neural", "deep learning", "algorithm", "data science"]):
        section_templates = [
            {
                "concept": "Foundational AI Paradigms & Data Formulations",
                "concise": "• AI Scope: Creating systems capable of performing tasks requiring human-like intelligence.\n• Data Representation: Converting raw text, images, or numerical tables into feature vectors.",
                "detailed": f"Artificial Intelligence encompasses systems designed to perceive, reason, and make autonomous decisions. In studying {topic}, raw unstructured data is converted into normalized feature vectors for algorithmic processing.",
                "example": "Converting raw customer reviews into numerical TF-IDF or embedding vectors for sentiment analysis.",
                "visual_type": "diagram",
                "visual_details": {
                    "diagram_type": "diagram",
                    "title": "AI Data Pipeline",
                    "nodes": [
                        {"id": "n1", "label": "Raw Inputs", "category": "input", "description": "Unstructured data"},
                        {"id": "n2", "label": "Feature Vectorizer", "category": "process", "description": "Embedding pipeline"},
                        {"id": "n3", "label": "AI Model Input", "category": "output", "description": "Normalized matrix"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "ingests"},
                        {"from": "n2", "to": "n3", "label": "produces"}
                    ],
                    "key_formula": "Vector x ∈ R^d"
                },
                "narration": f"Welcome to Section 1 of {topic}! We explore AI paradigms and how raw data is transformed into feature vectors.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="What is the first step in preparing unstructured text or image data for an AI model?",
                    options=["Converting raw data into numerical feature vectors", "Deleting all outlier datasets", "Manual hardcoded rule creation", "Ignoring input dimensions"],
                    correct="Converting raw data into numerical feature vectors"
                )
            },
            {
                "concept": "Supervised Learning: Regression & Classification",
                "concise": "• Supervised Paradigm: Training models using labeled (input x, target y) pairs.\n• Task Types: Regression predicts continuous values; classification predicts discrete categories.",
                "detailed": "Supervised learning learns a mapping function from input variables to target outputs using labeled historical training examples. Regression models predict continuous numbers, while classification assigns discrete class labels.",
                "example": "Predicting house prices (Regression) vs classifying emails as Spam or Not Spam (Classification).",
                "visual_type": "graph",
                "visual_details": {
                    "diagram_type": "graph",
                    "title": "Decision Boundary Classification",
                    "nodes": [
                        {"id": "n1", "label": "Training Dataset (x, y)", "category": "input", "description": "Labeled pairs"},
                        {"id": "n2", "label": "Model Training", "category": "process", "description": "Boundary optimization"},
                        {"id": "n3", "label": "Predictions y_hat", "category": "output", "description": "Class labels / values"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "feeds into"},
                        {"from": "n2", "to": "n3", "label": "generates"}
                    ],
                    "key_formula": "y_hat = f(x; θ)"
                },
                "narration": "Section 2 focuses on supervised learning, contrasting continuous regression models with discrete classification algorithms.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="Which supervised learning task type is used to predict continuous numerical values?",
                    options=["Cluster Grouping", "Regression", "Categorical Classification", "Dimensionality Reduction"],
                    correct="Regression"
                )
            },
            {
                "concept": "Neural Networks & Backpropagation Optimization",
                "concise": "• Artificial Neurons: Weighted sums passed through non-linear activation functions.\n• Backpropagation: Calculating gradients via chain rule to update weights via Gradient Descent.",
                "detailed": "Deep neural networks consist of layered artificial neurons. Backpropagation computes the gradient of the loss function with respect to each weight using the chain rule, iteratively minimizing prediction error.",
                "example": "Adjusting synaptic weights in a convolutional network to improve image recognition accuracy.",
                "visual_type": "diagram",
                "visual_details": {
                    "diagram_type": "diagram",
                    "title": "Neural Network Layer Architecture",
                    "nodes": [
                        {"id": "n1", "label": "Input Layer X", "category": "input", "description": "Feature inputs"},
                        {"id": "n2", "label": "Hidden Layers (W, b)", "category": "process", "description": "Non-linear transformations"},
                        {"id": "n3", "label": "Output Layer Y", "category": "output", "description": "Final logits"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "forward pass"},
                        {"from": "n2", "to": "n3", "label": "activation"}
                    ],
                    "key_formula": "Weight Update: θ = θ - α * ∇L(θ)"
                },
                "narration": "Section 3 examines neural network architectures and the backpropagation algorithm driven by gradient descent.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="What algorithm calculates loss gradients through network layers using the calculus chain rule?",
                    options=["K-Means Clustering", "Backpropagation", "Random Forest Pruning", "Binary Search"],
                    correct="Backpropagation"
                )
            },
            {
                "concept": "Model Evaluation Metrics & Generalization",
                "concise": "• Generalization: Model performance on unseen test datasets.\n• Key Metrics: Precision, Recall, F1-Score, and Mean Squared Error (MSE).",
                "detailed": "Evaluating AI models requires assessing generalization on unseen validation data to prevent overfitting. Standard metrics include Accuracy, Precision, Recall, F1-score, and ROC-AUC for classification tasks.",
                "example": "Evaluating a medical diagnostic model using Recall to minimize dangerous false negative errors.",
                "visual_type": "graph",
                "visual_details": {
                    "diagram_type": "graph",
                    "title": "Confusion Matrix & ROC Curve",
                    "nodes": [
                        {"id": "n1", "label": "Test Predictions", "category": "input", "description": "Model outputs"},
                        {"id": "n2", "label": "Ground Truth Labels", "category": "process", "description": "Actual targets"},
                        {"id": "n3", "label": "F1-Score / Accuracy", "category": "output", "description": "Performance summary"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "compared against"},
                        {"from": "n2", "to": "n3", "label": "yields metric"}
                    ],
                    "key_formula": "F1-Score = 2 * (Precision * Recall) / (Precision + Recall)"
                },
                "narration": f"Finally, Section 4 covers evaluation metrics and generalization techniques to ensure robust model performance on real-world test data.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question="Which evaluation metric balances both Precision and Recall into a single harmonic mean score?",
                    options=["Root Mean Square", "F1-Score", "Linear Intercept", "Covariance"],
                    correct="F1-Score"
                )
            }
        ]

    # 4. General / Fallback for any other Topic
    else:
        section_templates = [
            {
                "concept": f"Foundational Principles of {topic}",
                "concise": f"• Primary Mechanism: Core operational scope and guidelines of {topic}.\n• Framework Objectives: Standardizing procedures to ensure clarity and alignment.",
                "detailed": f"This section establishes the foundational principles of {topic}. It covers the primary mechanisms, core definitions, and operational scope required to build domain mastery at a {level} level.",
                "example": f"Real-world application of {topic} in modern organizations: Establishing standardized execution guidelines reduced setup overhead by 35%.",
                "visual_type": "diagram",
                "visual_details": {
                    "diagram_type": "diagram",
                    "title": f"{topic} Core Principles",
                    "nodes": [
                        {"id": "n1", "label": f"{topic} Inputs", "category": "input", "description": "Baseline parameters"},
                        {"id": "n2", "label": "Execution Engine", "category": "process", "description": "Operational workflow"},
                        {"id": "n3", "label": "Target Outcomes", "category": "output", "description": "Primary deliverables"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "initiates"},
                        {"from": "n2", "to": "n3", "label": "delivers"}
                    ],
                    "key_formula": f"Core Principle: {topic} Standard"
                },
                "narration": f"Welcome to Section 1! We begin by establishing the foundational principles and core scope of {topic}.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question=f"What is the primary objective of establishing foundational principles for {topic}?",
                    options=["Standardizing procedures and operational clarity", "Creating static unverified archives", "Bypassing quality checks", "None of the above"],
                    correct="Standardizing procedures and operational clarity"
                )
            },
            {
                "concept": f"Core Architecture & Workflow Strategy for {topic}",
                "concise": f"• Architectural Design: Structuring key components for efficiency.\n• Workflow Strategy: Optimizing step-by-step execution pathways.",
                "detailed": f"Section 2 explores the core architecture and workflow strategy governing {topic}. By organizing key processes into structured execution phases, teams maintain high performance and quality assurance.",
                "example": f"Implementing structured workflow pathways under {topic} eliminated bottleneck delays across cross-functional teams.",
                "visual_type": "graph",
                "visual_details": {
                    "diagram_type": "graph",
                    "title": f"{topic} Architecture Topology",
                    "nodes": [
                        {"id": "n1", "label": "Phase 1: Ingestion", "category": "input", "description": "Requirements gathering"},
                        {"id": "n2", "label": "Phase 2: Processing", "category": "process", "description": "Core transformations"},
                        {"id": "n3", "label": "Phase 3: Deployment", "category": "output", "description": "Final integration"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "transitions to"},
                        {"from": "n2", "to": "n3", "label": "results in"}
                    ],
                    "key_formula": "Efficiency Index = Output / Resource Usage"
                },
                "narration": f"In Section 2, we examine the core architectural components and workflow strategies driving {topic}.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question=f"How does a structured workflow strategy benefit implementation of {topic}?",
                    options=["By eliminating procedural bottlenecks and optimizing execution", "By increasing unnecessary documentation steps", "By restricting project visibility", "By delaying final delivery"],
                    correct="By eliminating procedural bottlenecks and optimizing execution"
                )
            },
            {
                "concept": f"Practical Real-World Deployment & Case Studies of {topic}",
                "concise": f"• Practical Deployment: Applying theoretical principles in active environments.\n• Case Analysis: Evaluating real-world implementation scenarios.",
                "detailed": f"Section 3 transitions from theory to practical deployment of {topic}. Through real-world case studies, we examine how leading practitioners solve operational challenges and optimize resource usage.",
                "example": f"A major case study demonstrating how adaptive strategies under {topic} improved operational throughput by 50%.",
                "visual_type": "diagram",
                "visual_details": {
                    "diagram_type": "diagram",
                    "title": f"{topic} Deployment Flow",
                    "nodes": [
                        {"id": "n1", "label": "Pilot Testing", "category": "input", "description": "Initial staging environment"},
                        {"id": "n2", "label": "Full Scale Rollout", "category": "process", "description": "Production integration"},
                        {"id": "n3", "label": "Impact Validation", "category": "output", "description": "Performance tracking"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "scales up"},
                        {"from": "n2", "to": "n3", "label": "validates"}
                    ],
                    "key_formula": "Deployment ROI = Net Benefit / Implementation Cost"
                },
                "narration": f"Section 3 focuses on practical deployment, examining active case studies and real-world implementation scenarios of {topic}.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question=f"What is the primary focus of practical case study analysis in {topic}?",
                    options=["Evaluating real-world implementation scenarios and performance gains", "Memorizing static definition lists", "Ignoring deployment feedback", "None of the above"],
                    correct="Evaluating real-world implementation scenarios and performance gains"
                )
            },
            {
                "concept": f"Evaluation, Governance & Sustainable Impact of {topic}",
                "concise": f"• Performance Analytics: Tracking key metrics and continuous improvement.\n• Sustainable Governance: Maintaining compliance and long-term viability.",
                "detailed": f"Section 4 synthesizes evaluation metrics and governance frameworks for {topic}. Continuous monitoring, multi-tier audits, and KPI tracking ensure long-term sustainability and compliance.",
                "example": f"Establishing quarterly performance reviews under {topic} guaranteed continuous quality improvements year over year.",
                "visual_type": "graph",
                "visual_details": {
                    "diagram_type": "graph",
                    "title": f"{topic} KPI Evaluation Matrix",
                    "nodes": [
                        {"id": "n1", "label": "KPI Data Sources", "category": "input", "description": "Continuous telemetry"},
                        {"id": "n2", "label": "Audit & Compliance Engine", "category": "process", "description": "Governance check"},
                        {"id": "n3", "label": "Continuous Improvement", "category": "output", "description": "Sustainable impact"}
                    ],
                    "edges": [
                        {"from": "n1", "to": "n2", "label": "monitored by"},
                        {"from": "n2", "to": "n3", "label": "drives"}
                    ],
                    "key_formula": "Sustainability Index = Compliance Rate * Quality Score"
                },
                "narration": f"Finally, Section 4 covers evaluation metrics and governance frameworks to guarantee sustainable long-term impact for {topic}.",
                "checkpoint": CheckpointQuestion(
                    type="mcq",
                    question=f"Which method best ensures the long-term sustainability of implementations under {topic}?",
                    options=["Continuous KPI tracking, multi-tier audits, and governance reviews", "Discontinuing post-implementation reviews", "Restricting data monitoring to initial setup", "Forcing unmonitored overrides"],
                    correct="Continuous KPI tracking, multi-tier audits, and governance reviews"
                )
            }
        ]

    sections = []
    num_to_use = min(max_sections, len(section_templates))
    for i in range(num_to_use):
        tmpl = section_templates[i]
        sections.append(
            Section(
                id=f"s{i+1}",
                concept=tmpl["concept"],
                explanation=tmpl["detailed"],
                concise_explanation=tmpl["concise"],
                detailed_explanation=tmpl["detailed"],
                example=tmpl["example"],
                visual_type=tmpl["visual_type"],
                visual_details=tmpl["visual_details"],
                narration_script=tmpl["narration"],
                checkpoint_question=tmpl["checkpoint"]
            )
        )
        
    final_quiz = [
        # Easy Level - q1 (Correct: Option A)
        QuizQuestion(
            id="q1",
            question=f"[Easy] What is the primary definition or focus of {topic}?",
            options=[
                f"A structured framework to streamline implementation and deliver targeted outcomes for {topic}",
                f"A temporary administrative memo with no operational guidelines",
                f"A manual data entry tool used exclusively for archiving historical documents",
                f"An unverified guideline with no measurable objectives"
            ],
            correct=f"A structured framework to streamline implementation and deliver targeted outcomes for {topic}",
            difficulty="easy",
            concept_category=f"{topic} Fundamentals"
        ),
        # Easy Level - q2 (Correct: Option B)
        QuizQuestion(
            id="q2",
            question=f"[Easy] Which primary stakeholder group directly benefits from {topic}?",
            options=[
                f"External unverified third-party entities",
                f"Target beneficiaries and ecosystem participants designated under {topic}",
                f"Legacy archival systems with no active users",
                f"None of the above"
            ],
            correct=f"Target beneficiaries and ecosystem participants designated under {topic}",
            difficulty="easy",
            concept_category=f"{topic} Stakeholders"
        ),
        # Medium Level - q3 (Correct: Option C)
        QuizQuestion(
            id="q3",
            question=f"[Medium] How does {topic} optimize operational workflows?",
            options=[
                f"By bypassing compliance audits and removing performance metrics",
                f"By relying on manual paper filing without verification checks",
                f"By establishing standardized guidelines and structured execution steps",
                f"By delegating authority without defined responsibility"
            ],
            correct=f"By establishing standardized guidelines and structured execution steps",
            difficulty="medium",
            concept_category=f"{topic} Workflow Optimization"
        ),
        # Medium Level - q4 (Correct: Option D)
        QuizQuestion(
            id="q4",
            question=f"[Medium] Which key metric validates successful execution of {topic}?",
            options=[
                f"Indefinite delay of project documentation approval",
                f"Reduction of public transparency and reporting frequency",
                f"Increase in unresolved procedural bottlenecks",
                f"Measurable adoption rate and positive impact across target groups"
            ],
            correct=f"Measurable adoption rate and positive impact across target groups",
            difficulty="medium",
            concept_category=f"{topic} Impact Metrics"
        ),
        # Hard Level - q5 (Correct: Option B)
        QuizQuestion(
            id="q5",
            question=f"[Hard] In a complex deployment scenario, how should edge cases under {topic} be handled?",
            options=[
                f"Ignore edge case data and force standard default overrides",
                f"Apply adaptive policy rules, evaluate systemic impact, and escalate to governance review",
                f"Halt all system processes indefinitely without logging issues",
                f"Revert to unmonitored legacy procedures"
            ],
            correct=f"Apply adaptive policy rules, evaluate systemic impact, and escalate to governance review",
            difficulty="hard",
            concept_category=f"{topic} Governance & Risk"
        ),
        # Hard Level - q6 (Correct: Option C)
        QuizQuestion(
            id="q6",
            question=f"[Hard] What analytical method best evaluates long-term sustainability of {topic}?",
            options=[
                f"Single-instance opinion sampling without baseline comparisons",
                f"Restricting data collection to initial onboarding phases",
                f"Multi-tier impact assessment combining qualitative feedback and quantitative KPI tracking",
                f"Discontinuing post-implementation audits"
            ],
            correct=f"Multi-tier impact assessment combining qualitative feedback and quantitative KPI tracking",
            difficulty="hard",
            concept_category=f"{topic} Analytics & Evaluation"
        )
    ]
    
    return LessonPlan(
        title=f"Lesson: {topic}",
        level=level,
        time_minutes=time_minutes,
        language=language,
        topic_or_chapter=topic,
        sections=sections,
        final_quiz=final_quiz
    )

def generate_lesson_plan(
    topic: str,
    profile: Optional[Dict[str, Any]] = None,
    time_minutes: int = 20,
    language: str = "en",
    retrieved_context: str = ""
) -> LessonPlan:
    """
    Primary Lesson Planner function.
    Calls OpenAI / Gemini LLM if API key is available; falls back to mock generator otherwise.
    """
    profile = profile or {}
    level = profile.get("preferred_level", "beginner")
    weak_concepts = profile.get("weak_concepts", [])
    strong_concepts = profile.get("strong_concepts", [])
    
    rules = get_time_rules(time_minutes)
    
    # Check if OpenAI API key is set
    openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            user_prompt = build_user_prompt(
                topic=topic,
                level=level,
                time_minutes=time_minutes,
                language=language,
                retrieved_context=retrieved_context,
                weak_concepts=weak_concepts,
                strong_concepts=strong_concepts,
                structure_rule=rules["structure_rule"]
            )
            
            response = client.chat.completions.create(
                model=settings.DEFAULT_LLM_MODEL,
                messages=[
                    {"role": "system", "content": LESSON_PLANNER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            plan_dict = json.loads(content)
            return LessonPlan(**plan_dict)
            
        except Exception as e:
            print(f"[WARNING] OpenAI LLM call failed ({e}). Falling back to deterministic mock generator.")
            return generate_mock_lesson_plan(topic, level, time_minutes, language, retrieved_context=retrieved_context)
    else:
        print("[INFO] No OpenAI API Key found. Operating in mock offline generator mode.")
        return generate_mock_lesson_plan(topic, level, time_minutes, language, retrieved_context=retrieved_context)

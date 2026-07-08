import logging
import json
import os
import re
import time
import random
from typing import Dict, Any
import requests
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class RateLimitError(Exception):
    pass


class GroqService:
    def __init__(self):
        env_loaded = load_dotenv(dotenv_path=_ENV_FILE, override=True)
        if env_loaded:
            print(f"[GroqService] Loaded env from {_ENV_FILE}")
        else:
            print(f"[GroqService] WARNING: Could not load {_ENV_FILE}")

        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        mock_raw = os.getenv("RABBITHOLE_MOCK", "false").strip().lower()
        self.mock_mode = mock_raw == "true"

        print(f"[GroqService] mock={self.mock_mode} raw='{mock_raw}' key_set={bool(self.api_key)}")
        logger.info(f"GroqService init: mock={self.mock_mode}, key_set={bool(self.api_key)}")

        if not self.api_key or self.api_key == "your_groq_api_key_here":
            logger.warning("GROQ_API_KEY not set or placeholder detected")
            if not self.mock_mode:
                logger.warning("RABBITHOLE_MOCK not enabled, will try real API but may fail")
                raise ValueError("GROQ_API_KEY environment variable is required when RABBITHOLE_MOCK is not true")

        if self.mock_mode:
            logger.info("RabbitHole running in MOCK mode")
        else:
            key_preview = self.api_key[:10] + "..." + self.api_key[-5:] if len(self.api_key) > 15 else "***"
            logger.info(f"Groq API configured with key: {key_preview}")

        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        self.max_retries = 3

    def generate(self, prompt: str) -> Dict[str, Any]:
        if self.mock_mode:
            logger.info("Using mock response")
            return self._get_mock_response(prompt)

        logger.info(f"Starting Groq request for prompt length: {len(prompt)}")

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Groq API request attempt {attempt}/{self.max_retries}")
                response = self._call_groq_api(prompt)
                logger.info(f"Groq API request successful on attempt {attempt}")
                return response
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed on attempt {attempt}: {str(e)}")
                if attempt == self.max_retries:
                    logger.error(f"Failed to parse JSON after {self.max_retries} attempts")
                    raise ValueError(f"Could not parse JSON from Groq response after {self.max_retries} retries")
                prompt = self._get_stricter_prompt(prompt)
                continue
            except RateLimitError:
                if attempt == self.max_retries:
                    logger.error(f"Rate limited after {self.max_retries} attempts")
                    raise
                delay = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limited, retrying in {delay:.1f}s (attempt {attempt}/{self.max_retries})")
                time.sleep(delay)
                continue
            except Exception as e:
                logger.error(f"Error on attempt {attempt}: {str(e)}", exc_info=True)
                if attempt == self.max_retries:
                    raise

        raise ValueError("Failed to get response from Groq API")

    def _call_groq_api(self, prompt: str) -> Dict[str, Any]:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 8000,
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            logger.info("Response received from Groq API")
            content = response.json()["choices"][0]["message"]["content"]

            parsed = self._extract_and_parse_json(content)
            logger.info("JSON parsing successful")
            return parsed

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                logger.warning(f"Rate limited (429): {str(e)}")
                raise RateLimitError(str(e))
            logger.error(f"Groq API request failed: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to communicate with Groq API: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to communicate with Groq API: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Groq service: {str(e)}", exc_info=True)
            raise

    def _extract_and_parse_json(self, response_text: str) -> Dict[str, Any]:
        logger.info("Attempting to extract JSON from response")

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.debug("Direct JSON parse failed, attempting cleanup")

        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.debug("After fence removal, still failing - trying largest JSON extraction")

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            logger.debug("Found potential JSON object, attempting parse")

            fixed_json = re.sub(r',(\s*[}\]])', r'\1', json_str)

            try:
                parsed = json.loads(fixed_json)
                logger.info("JSON parsing successful after cleanup")
                return parsed
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse even after cleanup: {str(e)}")

        logger.error("Unable to extract valid JSON from response")
        raise ValueError("Could not parse JSON from Groq response")

    def _get_stricter_prompt(self, prompt: str) -> str:
        stricter_note = "\n\nIMPORTANT: Your previous response could not be parsed as valid JSON. Return ONLY a raw JSON object with no markdown formatting, no code fences, no backticks, no explanations. Just the JSON."
        return prompt + stricter_note

    def _get_mock_response(self, prompt: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        if "expand" in prompt_lower:
            return self._get_mock_expansion()
        elif "knowledge gap" in prompt_lower or "gap" in prompt_lower:
            return self._get_mock_knowledge_gap()
        else:
            return self._get_mock_graph(prompt)

    def _get_mock_graph(self, prompt: str = "") -> Dict[str, Any]:
        topic = "Machine Learning"
        mode = "learn"
        if prompt:
            for line in prompt.split("\n"):
                s = line.strip()
                if "research" in s.lower() and ("knowledge graph" in s.lower() or "graph for" in s.lower()):
                    mode = "research"
                elif "interview" in s.lower() and ("knowledge graph" in s.lower() or "graph for" in s.lower()):
                    mode = "interview"
                elif "project" in s.lower() and ("knowledge graph" in s.lower() or "graph for" in s.lower()):
                    mode = "project"
                elif "quick" in s.lower() and ("knowledge graph" in s.lower() or "graph for" in s.lower()):
                    mode = "quick"
                if "topic:" in s or "topic:" in s.lower() or "for:" in s:
                    _, after = s.split(":", 1)
                    topic = after.strip()
                    break

        if mode == "research":
            return self._get_mock_research_graph(topic)
        elif mode == "interview":
            return self._get_mock_interview_graph(topic)
        elif mode == "project":
            return self._get_mock_project_graph(topic)
        elif mode == "quick":
            return self._get_mock_quick_graph(topic)
        else:
            return self._get_mock_learn_graph(topic)

    def _get_mock_learn_graph(self, topic: str) -> Dict[str, Any]:
        slug = topic.lower().replace(" ", "_").replace("/", "_")[:20]

        def tn(id_suffix):
            return f"{slug}_{id_suffix}"

        nodes_raw = [
            {"id": tn("python"), "name": topic if i == 0 else f"{topic}: {n}", "type": t, "difficulty": d, "importance_score": s, "depth": dep, "prerequisites": [tn(p) if p else "" for p in prereqs], "unlocks": [tn(u) if u else "" for u in unlocks]}
            for i, (n, t, d, s, dep, prereqs, unlocks) in enumerate([
                ("Python", "prerequisite", "Beginner", 9.5, 0, [], ["numpy", "pandas", "ml_basics"]),
                ("NumPy", "core_concept", "Beginner", 9.0, 1, ["python"], ["scipy", "pandas", "linear_algebra"]),
                ("Pandas", "core_concept", "Beginner", 8.5, 1, ["python", "numpy"], ["data_cleaning", "feature_engineering"]),
                ("Linear Algebra", "mathematical_foundation", "Intermediate", 9.5, 0, [], ["probability", "calculus", "neural_networks"]),
                ("Probability & Statistics", "mathematical_foundation", "Intermediate", 8.5, 0, [], ["ml_basics", "bayesian"]),
                ("ML Basics", "core_concept", "Intermediate", 9.0, 1, ["python", "linear_algebra", "probability"], ["supervised_learning", "unsupervised_learning"]),
                ("Supervised Learning", "core_concept", "Intermediate", 8.5, 2, ["ml_basics"], ["regression", "classification", "neural_networks"]),
                ("Unsupervised Learning", "core_concept", "Intermediate", 7.5, 2, ["ml_basics"], ["clustering", "dimensionality_reduction"]),
                ("Neural Networks", "advanced_concept", "Advanced", 9.5, 2, ["linear_algebra", "supervised_learning"], ["deep_learning", "cnn", "rnn"]),
                ("Deep Learning", "advanced_concept", "Advanced", 9.0, 3, ["neural_networks"], ["cnn", "rnn", "transformers"]),
                ("Attention Mechanism", "advanced_concept", "Advanced", 8.5, 4, ["neural_networks"], ["transformers"]),
                ("Transformers", "advanced_concept", "Advanced", 9.5, 5, ["deep_learning", "attention_mechanism"], ["llms", "nlp"]),
                ("Scikit-Learn", "tool", "Beginner", 8.0, 1, ["python", "numpy", "pandas"], ["supervised_learning", "unsupervised_learning"]),
                ("TensorFlow", "framework", "Intermediate", 8.5, 3, ["deep_learning"], ["neural_networks", "nlp"]),
            ])
        ]

        nodes = []
        for nd in nodes_raw:
            nd["description"] = f"{nd['name']} related to {topic}"
            nd["estimated_learning_time"] = "varies"
            nd["applications"] = []
            nd["why_it_matters"] = f"Important concept in {topic}"
            nd["resources"] = {}
            nd["prerequisites"] = [p for p in nd["prerequisites"] if p]
            nd["unlocks"] = [u for u in nd["unlocks"] if u]
            nodes.append(nd)

        edges_raw = [
            (tn("python"), tn("numpy"), "prerequisite"),
            (tn("python"), tn("pandas"), "prerequisite"),
            (tn("numpy"), tn("linear_algebra"), "related_concept"),
            (tn("pandas"), tn("numpy"), "prerequisite"),
            (tn("linear_algebra"), tn("ml_basics"), "mathematical_foundation"),
            (tn("probability"), tn("ml_basics"), "mathematical_foundation"),
            (tn("ml_basics"), tn("supervised_learning"), "prerequisite"),
            (tn("ml_basics"), tn("unsupervised_learning"), "prerequisite"),
            (tn("supervised_learning"), tn("neural_networks"), "advanced_concept"),
            (tn("neural_networks"), tn("deep_learning"), "advanced_concept"),
            (tn("deep_learning"), tn("attention_mechanism"), "related_concept"),
            (tn("attention_mechanism"), tn("transformers"), "prerequisite"),
            (tn("sklearn"), tn("supervised_learning"), "tool"),
            (tn("tensorflow"), tn("neural_networks"), "framework"),
        ]
        edges = [{"id": f"e{i}", "source": s, "target": t, "relationship": r} for i, (s, t, r) in enumerate(edges_raw)]

        return {
            "overview": {
                "topic": topic,
                "domain": "Artificial Intelligence",
                "difficulty": "Advanced",
                "estimated_learning_time": "3-6 months",
                "popularity": "Very High",
                "importance_level": "High",
                "applications": ["ChatGPT", "Claude", "Gemini", "GitHub Copilot"],
                "summary": "Machine Learning is a subset of AI that focuses on algorithms learning patterns from data without explicit programming."
            },
            "nodes": [
                {"id": "python", "name": "Python", "type": "prerequisite", "description": "Python is a programming language essential for ML development", "difficulty": "Beginner", "importance_score": 9.5, "estimated_learning_time": "2-4 weeks", "prerequisites": [], "unlocks": ["numpy", "pandas", "ml_basics"], "applications": ["Data Science", "Web Development", "Automation"], "why_it_matters": "Python is the de facto standard language for ML and data science", "resources": {}, "depth": 0},
                {"id": "numpy", "name": "NumPy", "type": "core_concept", "description": "NumPy provides efficient numerical computing with arrays and matrices", "difficulty": "Beginner", "importance_score": 9.0, "estimated_learning_time": "1-2 weeks", "prerequisites": ["python"], "unlocks": ["scipy", "pandas", "linear_algebra"], "applications": ["Data Processing", "Scientific Computing"], "why_it_matters": "NumPy is the foundation for numerical computing in Python", "resources": {}, "depth": 1},
                {"id": "pandas", "name": "Pandas", "type": "core_concept", "description": "Pandas enables data manipulation and analysis with DataFrames", "difficulty": "Beginner", "importance_score": 8.5, "estimated_learning_time": "1-2 weeks", "prerequisites": ["python", "numpy"], "unlocks": ["data_cleaning", "feature_engineering"], "applications": ["Data Analysis", "Data Cleaning"], "why_it_matters": "Pandas is essential for data preparation and exploration", "resources": {}, "depth": 1},
                {"id": "linear_algebra", "name": "Linear Algebra", "type": "mathematical_foundation", "description": "Mathematical study of vectors, matrices, and transformations", "difficulty": "Intermediate", "importance_score": 9.5, "estimated_learning_time": "3-4 weeks", "prerequisites": [], "unlocks": ["probability", "calculus", "neural_networks"], "applications": ["ML Algorithms", "Computer Graphics"], "why_it_matters": "Linear Algebra is the mathematical foundation of ML", "resources": {}, "depth": 0},
                {"id": "probability", "name": "Probability & Statistics", "type": "mathematical_foundation", "description": "Study of randomness, distributions, and statistical inference", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "2-3 weeks", "prerequisites": [], "unlocks": ["ml_basics", "bayesian"], "applications": ["ML Algorithms", "Decision Making"], "why_it_matters": "Probability is crucial for understanding ML algorithms", "resources": {}, "depth": 0},
                {"id": "ml_basics", "name": "ML Basics", "type": "core_concept", "description": "Fundamentals of supervised and unsupervised learning", "difficulty": "Intermediate", "importance_score": 9.0, "estimated_learning_time": "2-3 weeks", "prerequisites": ["python", "linear_algebra", "probability"], "unlocks": ["supervised_learning", "unsupervised_learning"], "applications": ["Classification", "Regression"], "why_it_matters": "ML Basics provide foundation for all ML algorithms", "resources": {}, "depth": 1},
                {"id": "supervised_learning", "name": "Supervised Learning", "type": "core_concept", "description": "Learning from labeled data", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "2-3 weeks", "prerequisites": ["ml_basics"], "unlocks": ["regression", "classification", "neural_networks"], "applications": ["Prediction", "Classification"], "why_it_matters": "Supervised learning is the most common ML paradigm", "resources": {}, "depth": 2},
                {"id": "unsupervised_learning", "name": "Unsupervised Learning", "type": "core_concept", "description": "Finding patterns in unlabeled data", "difficulty": "Intermediate", "importance_score": 7.5, "estimated_learning_time": "2-3 weeks", "prerequisites": ["ml_basics"], "unlocks": ["clustering", "dimensionality_reduction"], "applications": ["Clustering", "Pattern Discovery"], "why_it_matters": "Unsupervised learning reveals hidden patterns", "resources": {}, "depth": 2},
                {"id": "neural_networks", "name": "Neural Networks", "type": "advanced_concept", "description": "Interconnected networks inspired by biological neurons", "difficulty": "Advanced", "importance_score": 9.5, "estimated_learning_time": "3-4 weeks", "prerequisites": ["linear_algebra", "supervised_learning"], "unlocks": ["deep_learning", "cnn", "rnn"], "applications": ["Image Recognition", "NLP", "Time Series"], "why_it_matters": "Neural networks are the foundation of deep learning", "resources": {}, "depth": 2},
                {"id": "deep_learning", "name": "Deep Learning", "type": "advanced_concept", "description": "Neural networks with multiple layers", "difficulty": "Advanced", "importance_score": 9.0, "estimated_learning_time": "3-4 weeks", "prerequisites": ["neural_networks"], "unlocks": ["cnn", "rnn", "transformers"], "applications": ["AI Applications", "Computer Vision", "NLP"], "why_it_matters": "Deep learning powers modern AI", "resources": {}, "depth": 3},
                {"id": "attention_mechanism", "name": "Attention Mechanism", "type": "advanced_concept", "description": "Mechanism allowing models to focus on important parts", "difficulty": "Advanced", "importance_score": 8.5, "estimated_learning_time": "1-2 weeks", "prerequisites": ["neural_networks"], "unlocks": ["transformers"], "applications": ["Seq2Seq", "Machine Translation"], "why_it_matters": "Attention is key to modern NLP", "resources": {}, "depth": 4},
                {"id": "transformers", "name": "Transformers", "type": "advanced_concept", "description": "State-of-the-art architecture using attention mechanisms", "difficulty": "Advanced", "importance_score": 9.5, "estimated_learning_time": "2-3 weeks", "prerequisites": ["deep_learning", "attention_mechanism"], "unlocks": ["llms", "nlp"], "applications": ["NLP", "Machine Translation", "Text Generation"], "why_it_matters": "Transformers are the foundation of modern LLMs", "resources": {}, "depth": 5},
                {"id": "sklearn", "name": "Scikit-Learn", "type": "tool", "description": "Python library for classical ML algorithms", "difficulty": "Beginner", "importance_score": 8.0, "estimated_learning_time": "1-2 weeks", "prerequisites": ["python", "numpy", "pandas"], "unlocks": ["supervised_learning", "unsupervised_learning"], "applications": ["Prototyping", "Classical ML"], "why_it_matters": "Scikit-learn is essential for classical ML", "resources": {}, "depth": 1},
                {"id": "tensorflow", "name": "TensorFlow", "type": "framework", "description": "Deep learning framework by Google", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "2-3 weeks", "prerequisites": ["deep_learning"], "unlocks": ["neural_networks", "nlp"], "applications": ["Production ML", "Research"], "why_it_matters": "TensorFlow is widely used in production", "resources": {}, "depth": 3}
            ],
            "edges": [
                {"id": "e1", "source": "python", "target": "numpy", "relationship": "prerequisite"},
                {"id": "e2", "source": "python", "target": "pandas", "relationship": "prerequisite"},
                {"id": "e3", "source": "numpy", "target": "linear_algebra", "relationship": "related_concept"},
                {"id": "e4", "source": "pandas", "target": "numpy", "relationship": "prerequisite"},
                {"id": "e5", "source": "linear_algebra", "target": "ml_basics", "relationship": "mathematical_foundation"},
                {"id": "e6", "source": "probability", "target": "ml_basics", "relationship": "mathematical_foundation"},
                {"id": "e7", "source": "ml_basics", "target": "supervised_learning", "relationship": "prerequisite"},
                {"id": "e8", "source": "ml_basics", "target": "unsupervised_learning", "relationship": "prerequisite"},
                {"id": "e9", "source": "supervised_learning", "target": "neural_networks", "relationship": "advanced_concept"},
                {"id": "e10", "source": "neural_networks", "target": "deep_learning", "relationship": "advanced_concept"},
                {"id": "e11", "source": "deep_learning", "target": "attention_mechanism", "relationship": "related_concept"},
                {"id": "e12", "source": "attention_mechanism", "target": "transformers", "relationship": "prerequisite"},
                {"id": "e13", "source": "sklearn", "target": "supervised_learning", "relationship": "tool"},
                {"id": "e14", "source": "tensorflow", "target": "neural_networks", "relationship": "framework"}
            ]
        }

    def _get_mock_research_graph(self, topic: str) -> Dict[str, Any]:
        slug = topic.lower().replace(" ", "_").replace("/", "_")[:20]
        def tn(s): return f"{slug}_{s}"

        nodes = [
            {"id": tn("research_overview"), "name": f"Research Overview: {topic}", "type": "foundation", "description": f"Comprehensive research landscape of {topic} covering seminal works, SOTA methods, open problems, and future directions.", "difficulty": "Intermediate", "importance_score": 9.5, "estimated_learning_time": "Comprehensive", "prerequisites": [], "unlocks": [tn("early_foundations"), tn("key_theoretical_frameworks")], "applications": ["Research Planning", "Literature Review", "Thesis Development"], "why_it_matters": "Provides the complete research context needed to understand where the field stands and where it is heading", "resources": {"key_papers": [{"title": "A Survey of the Field", "authors": ["Multiple Researchers"], "year": 2023, "venue": "ACM Computing Surveys", "impact": "highly influential"}], "key_researchers": ["Leading Researchers"], "leading_labs": ["Top Research Labs"]}, "depth": 0},
            {"id": tn("early_foundations"), "name": "Early Foundations & Pioneering Work", "type": "foundation", "description": f"Foundational theories and early breakthroughs that established {topic} as a research discipline. Includes the original formulations, key theorems, and seminal experiments.", "difficulty": "Intermediate", "importance_score": 9.0, "estimated_learning_time": "4-6 weeks", "prerequisites": [tn("research_overview")], "unlocks": [tn("seminal_papers_2010s"), tn("theoretical_underpinnings")], "applications": ["Understanding Origins", "Historical Context"], "why_it_matters": "Foundational work underpins all modern advances in the field", "resources": {"key_papers": [{"title": "Original Formulation", "authors": ["Pioneer A", "Pioneer B"], "year": 1998, "venue": "Nature", "impact": "field-defining"}], "key_researchers": ["Pioneer A", "Pioneer B"]}, "depth": 1},
            {"id": tn("key_theoretical_frameworks"), "name": "Key Theoretical Frameworks", "type": "methodology", "description": "Core mathematical and conceptual frameworks that define how research in this field is conducted. Includes formal models, assumptions, and theoretical guarantees.", "difficulty": "Advanced", "importance_score": 9.5, "estimated_learning_time": "6-8 weeks", "prerequisites": [tn("early_foundations")], "unlocks": [tn("state_of_art_approaches"), tn("evaluation_methodologies")], "applications": ["Theory Development", "Proofs & Analysis"], "why_it_matters": "Theoretical frameworks provide the lens through which all research contributions are evaluated", "resources": {"key_papers": [{"title": "Theoretical Framework Paper", "authors": ["Theorist A"], "year": 2005, "venue": "JMLR", "impact": "highly cited"}], "key_researchers": ["Theorist A"]}, "depth": 1},
            {"id": tn("theoretical_underpinnings"), "name": "Theoretical Underpinnings & Formal Models", "type": "methodology", "description": "Deep mathematical foundations including complexity analysis, convergence guarantees, and information-theoretic bounds that guide research.", "difficulty": "Advanced", "importance_score": 8.5, "estimated_learning_time": "4-6 weeks", "prerequisites": [tn("early_foundations")], "unlocks": [tn("seminal_papers_2010s"), tn("modern_architectures")], "applications": ["Theoretical Analysis", "Proof Techniques"], "why_it_matters": "Understanding formal models is essential for developing novel research contributions", "resources": {"key_papers": [{"title": "Foundational Theory Paper", "authors": ["Theorist B"], "year": 2008, "venue": "NeurIPS", "impact": "seminal"}], "key_researchers": ["Theorist B"]}, "depth": 2},
            {"id": tn("seminal_papers_2010s"), "name": "Seminal Papers (2010-2018)", "type": "seminal_paper", "description": "Landmark papers from 2010-2018 that fundamentally shifted the research trajectory. Each introduced paradigm-changing ideas, novel architectures, or breakthrough results.", "difficulty": "Advanced", "importance_score": 9.5, "estimated_learning_time": "6-8 weeks", "prerequisites": [tn("early_foundations"), tn("key_theoretical_frameworks")], "unlocks": [tn("state_of_art_approaches"), tn("modern_architectures"), tn("breakthrough_techniques")], "applications": ["Literature Review", "Method Development"], "why_it_matters": "These papers defined modern research directions and opened entirely new subfields", "resources": {"key_papers": [{"title": "Breakthrough Paper 2012", "authors": ["Innovator A", "Innovator B"], "year": 2012, "venue": "NeurIPS", "impact": "field-defining"}, {"title": "Breakthrough Paper 2014", "authors": ["Innovator C"], "year": 2014, "venue": "ICML", "impact": "highly influential"}, {"title": "Breakthrough Paper 2017", "authors": ["Innovator D"], "year": 2017, "venue": "Nature", "impact": "paradigm-shifting"}], "key_researchers": ["Innovator A", "Innovator C", "Innovator D"]}, "depth": 2},
            {"id": tn("state_of_art_approaches"), "name": "State-of-the-Art Approaches (Current)", "type": "state_of_art", "description": "Current best-performing methods, models, and systems. Includes benchmark-topping architectures, SOTA performance metrics, and production-grade implementations.", "difficulty": "Advanced", "importance_score": 9.5, "estimated_learning_time": "4-6 weeks", "prerequisites": [tn("seminal_papers_2010s"), tn("modern_architectures")], "unlocks": [tn("recent_breakthroughs"), tn("benchmark_datasets")], "applications": ["Practical Implementation", "Benchmarking", "Production Systems"], "why_it_matters": "SOTA defines the current frontier — all new research must be compared against these baselines", "resources": {"key_papers": [{"title": "SOTA Model 2023", "authors": ["Team A"], "year": 2023, "venue": "NeurIPS", "impact": "SOTA"}, {"title": "SOTA Model 2024", "authors": ["Team B"], "year": 2024, "venue": "ICLR", "impact": "new SOTA"}], "key_researchers": ["Team A", "Team B"], "leading_labs": ["Top Industry Lab", "Top Academic Lab"]}, "depth": 3},
            {"id": tn("modern_architectures"), "name": "Modern Architectures & Design Paradigms", "type": "methodology", "description": "Contemporary architectural patterns and design principles including attention mechanisms, residual connections, normalization techniques, and modular design.", "difficulty": "Advanced", "importance_score": 9.0, "estimated_learning_time": "4-6 weeks", "prerequisites": [tn("seminal_papers_2010s")], "unlocks": [tn("state_of_art_approaches"), tn("recent_breakthroughs")], "applications": ["Model Design", "Architecture Search"], "why_it_matters": "Architectural innovations drive the majority of performance improvements in the field", "resources": {"key_papers": [{"title": "Architecture Design Paper", "authors": ["Architect A"], "year": 2019, "venue": "ICLR", "impact": "highly influential"}], "key_researchers": ["Architect A"]}, "depth": 3},
            {"id": tn("breakthrough_techniques"), "name": "Breakthrough Techniques & Methods", "type": "recent_advance", "description": "Novel techniques that have dramatically improved performance or enabled new capabilities. Includes training innovations, optimization breakthroughs, and algorithmic advances.", "difficulty": "Advanced", "importance_score": 9.0, "estimated_learning_time": "3-4 weeks", "prerequisites": [tn("seminal_papers_2010s"), tn("theoretical_underpinnings")], "unlocks": [tn("recent_breakthroughs"), tn("emerging_research_directions")], "applications": ["Method Innovation", "Performance Improvement"], "why_it_matters": "These techniques represent the cutting edge of methodological innovation", "resources": {"key_papers": [{"title": "Novel Technique Paper", "authors": ["Method Researcher A"], "year": 2022, "venue": "ICML", "impact": "breakthrough"}], "key_researchers": ["Method Researcher A"]}, "depth": 3},
            {"id": tn("recent_breakthroughs"), "name": "Recent Breakthroughs (2022-2025)", "type": "recent_advance", "description": "The most impactful recent advances including novel architectures, training paradigms, and applications that have emerged in the last 2-3 years.", "difficulty": "Advanced", "importance_score": 9.5, "estimated_learning_time": "3-4 weeks", "prerequisites": [tn("state_of_art_approaches"), tn("modern_architectures")], "unlocks": [tn("emerging_research_directions"), tn("open_problems")], "applications": ["Cutting-edge Research", "Novel Applications"], "why_it_matters": "Recent breakthroughs define where the field is heading next", "resources": {"key_papers": [{"title": "2024 Breakthrough", "authors": ["Recent Researcher A"], "year": 2024, "venue": "Nature", "impact": "high-impact"}, {"title": "2025 Advance", "authors": ["Recent Researcher B"], "year": 2025, "venue": "NeurIPS", "impact": "significant"}], "key_researchers": ["Recent Researcher A", "Recent Researcher B"]}, "depth": 4},
            {"id": tn("evaluation_methodologies"), "name": "Evaluation Methodologies & Protocols", "type": "methodology", "description": "Standard evaluation practices, experimental protocols, statistical testing methods, and reproducibility guidelines that ensure rigorous research.", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "2-3 weeks", "prerequisites": [tn("key_theoretical_frameworks")], "unlocks": [tn("benchmark_datasets"), tn("reproducibility_practices")], "applications": ["Experimental Design", "Paper Writing"], "why_it_matters": "Rigorous evaluation is essential for credible research contributions", "resources": {"key_papers": [{"title": "Evaluation Best Practices", "authors": ["Meta Researcher"], "year": 2020, "venue": "NeurIPS", "impact": "widely adopted"}], "key_researchers": ["Meta Researcher"]}, "depth": 2},
            {"id": tn("benchmark_datasets"), "name": "Benchmarks & Standard Datasets", "type": "benchmark", "description": "Widely-used benchmark datasets, evaluation metrics, leaderboards, and challenge competitions that define progress in the field.", "difficulty": "Beginner", "importance_score": 8.5, "estimated_learning_time": "1-2 weeks", "prerequisites": [tn("evaluation_methodologies")], "unlocks": [tn("state_of_art_approaches"), tn("reproducibility_practices")], "applications": ["Benchmarking", "Model Comparison"], "why_it_matters": "Standardized benchmarks enable fair comparison and track field progress", "resources": {"key_papers": [{"title": "Dataset Paper", "authors": ["Dataset Creator A"], "year": 2019, "venue": "NeurIPS Datasets", "impact": "widely used"}], "key_researchers": ["Dataset Creator A"]}, "depth": 2},
            {"id": tn("reproducibility_practices"), "name": "Reproducibility & Open Science", "type": "challenge", "description": "Current challenges and best practices around research reproducibility, code release, data sharing, and open science initiatives.", "difficulty": "Intermediate", "importance_score": 8.0, "estimated_learning_time": "1-2 weeks", "prerequisites": [tn("evaluation_methodologies")], "unlocks": [tn("open_problems")], "applications": ["Open Research", "Peer Review"], "why_it_matters": "Reproducibility crisis is a major concern affecting research credibility", "resources": {"key_papers": [{"title": "Reproducibility Study", "authors": ["Reproducibility Researcher"], "year": 2021, "venue": "Science", "impact": "highly influential"}], "key_researchers": ["Reproducibility Researcher"]}, "depth": 2},
            {"id": tn("emerging_research_directions"), "name": "Emerging Research Directions", "type": "emerging_trend", "description": "Promising new research directions including interdisciplinary approaches, novel paradigms, and underexplored areas with high potential impact.", "difficulty": "Advanced", "importance_score": 9.0, "estimated_learning_time": "3-4 weeks", "prerequisites": [tn("recent_breakthroughs"), tn("state_of_art_approaches")], "unlocks": [tn("future_outlook"), tn("open_problems")], "applications": ["Research Planning", "Grant Proposals"], "why_it_matters": "Identifying emerging directions early can define a research career", "resources": {"key_papers": [{"title": "Future Directions Survey", "authors": ["Visionary Researcher"], "year": 2024, "venue": "arXiv", "impact": "widely discussed"}], "key_researchers": ["Visionary Researcher"], "leading_labs": ["Forward-thinking Lab"]}, "depth": 4},
            {"id": tn("open_problems"), "name": "Open Problems & Grand Challenges", "type": "open_problem", "description": "Key unsolved problems, theoretical limitations, practical challenges, and ethical considerations that define the research frontier.", "difficulty": "Advanced", "importance_score": 9.5, "estimated_learning_time": "4-6 weeks", "prerequisites": [tn("emerging_research_directions"), tn("state_of_art_approaches")], "unlocks": [tn("future_outlook")], "applications": ["PhD Topics", "Research Agenda"], "why_it_matters": "Open problems represent the highest-impact research opportunities", "resources": {"key_papers": [{"title": "Open Problems Paper", "authors": ["Leading Expert A", "Leading Expert B"], "year": 2023, "venue": "Nature Reviews", "impact": "highly cited"}], "key_researchers": ["Leading Expert A", "Leading Expert B"]}, "depth": 5},
            {"id": tn("future_outlook"), "name": "Future Outlook & Predictions", "type": "emerging_trend", "description": "Expert predictions on where the field is heading, anticipated breakthroughs, potential paradigm shifts, and long-term research trajectories.", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "1-2 weeks", "prerequisites": [tn("open_problems"), tn("emerging_research_directions")], "unlocks": [], "applications": ["Strategic Planning", "Career Decisions"], "why_it_matters": "Understanding future trajectories helps researchers choose impactful directions", "resources": {"key_papers": [{"title": "Field Outlook Report", "authors": ["Industry Think Tank"], "year": 2025, "venue": "Report", "impact": "influential"}], "key_researchers": ["Industry Think Tank"]}, "depth": 5},
            {"id": tn("research_communities"), "name": "Research Communities & Conferences", "type": "research_group", "description": "Major conferences, workshops, research communities, and academic-industry partnerships that drive the field forward.", "difficulty": "Beginner", "importance_score": 7.5, "estimated_learning_time": "Ongoing", "prerequisites": [tn("research_overview")], "unlocks": [tn("emerging_research_directions")], "applications": ["Networking", "Collaboration"], "why_it_matters": "Active community participation is essential for research impact and career growth", "resources": {"key_researchers": ["Community Leaders"], "leading_labs": ["Major Research Groups"]}, "depth": 1},
            {"id": tn("interdisciplinary_connections"), "name": "Interdisciplinary Connections", "type": "related_field", "description": "How this field connects to and influences adjacent disciplines including neuroscience, physics, cognitive science, and other areas of computer science.", "difficulty": "Intermediate", "importance_score": 8.0, "estimated_learning_time": "2-3 weeks", "prerequisites": [tn("research_overview")], "unlocks": [tn("emerging_research_directions"), tn("future_outlook")], "applications": ["Cross-disciplinary Research", "Novel Applications"], "why_it_matters": "The most impactful research often happens at the intersection of disciplines", "resources": {"key_papers": [{"title": "Interdisciplinary Survey", "authors": ["Cross-disciplinary Researcher"], "year": 2022, "venue": "Science", "impact": "influential"}], "key_researchers": ["Cross-disciplinary Researcher"]}, "depth": 1},
            {"id": tn("ethical_considerations"), "name": "Ethical Considerations & Societal Impact", "type": "challenge", "description": "Ethical challenges including bias, fairness, transparency, accountability, environmental impact, and societal implications of research advances.", "difficulty": "Intermediate", "importance_score": 9.0, "estimated_learning_time": "2-3 weeks", "prerequisites": [tn("state_of_art_approaches"), tn("open_problems")], "unlocks": [], "applications": ["Responsible Research", "Policy Development"], "why_it_matters": "Ethical considerations are increasingly central to research funding and public trust", "resources": {"key_papers": [{"title": "AI Ethics Framework", "authors": ["Ethics Researcher"], "year": 2023, "venue": "Nature Machine Intelligence", "impact": "highly influential"}], "key_researchers": ["Ethics Researcher"]}, "depth": 4},
            {"id": tn("key_datasets"), "name": "Key Datasets & Data Resources", "type": "dataset", "description": "Essential datasets that have driven research progress, including their size, composition, collection methodology, and known limitations.", "difficulty": "Beginner", "importance_score": 8.0, "estimated_learning_time": "1-2 weeks", "prerequisites": [tn("research_overview")], "unlocks": [tn("benchmark_datasets")], "applications": ["Data Collection", "Research Experiments"], "why_it_matters": "Dataset quality directly impacts research validity and reproducibility", "resources": {"key_papers": [{"title": "Dataset Paper", "authors": ["Dataset Creator"], "year": 2020, "venue": "NeurIPS", "impact": "widely used"}], "key_researchers": ["Dataset Creator"]}, "depth": 1},
        ]

        edges = [
            {"id": "re1", "source": tn("research_overview"), "target": tn("early_foundations"), "relationship": "foundation"},
            {"id": "re2", "source": tn("research_overview"), "target": tn("key_theoretical_frameworks"), "relationship": "foundation"},
            {"id": "re3", "source": tn("research_overview"), "target": tn("research_communities"), "relationship": "related_to"},
            {"id": "re4", "source": tn("research_overview"), "target": tn("interdisciplinary_connections"), "relationship": "related_to"},
            {"id": "re5", "source": tn("research_overview"), "target": tn("key_datasets"), "relationship": "related_to"},
            {"id": "re6", "source": tn("early_foundations"), "target": tn("seminal_papers_2010s"), "relationship": "builds_upon"},
            {"id": "re7", "source": tn("early_foundations"), "target": tn("theoretical_underpinnings"), "relationship": "foundation"},
            {"id": "re8", "source": tn("key_theoretical_frameworks"), "target": tn("evaluation_methodologies"), "relationship": "foundation"},
            {"id": "re9", "source": tn("key_theoretical_frameworks"), "target": tn("seminal_papers_2010s"), "relationship": "foundation"},
            {"id": "re10", "source": tn("theoretical_underpinnings"), "target": tn("modern_architectures"), "relationship": "foundation"},
            {"id": "re11", "source": tn("theoretical_underpinnings"), "target": tn("breakthrough_techniques"), "relationship": "foundation"},
            {"id": "re12", "source": tn("seminal_papers_2010s"), "target": tn("state_of_art_approaches"), "relationship": "builds_upon"},
            {"id": "re13", "source": tn("seminal_papers_2010s"), "target": tn("modern_architectures"), "relationship": "inspires"},
            {"id": "re14", "source": tn("seminal_papers_2010s"), "target": tn("breakthrough_techniques"), "relationship": "inspires"},
            {"id": "re15", "source": tn("evaluation_methodologies"), "target": tn("benchmark_datasets"), "relationship": "method"},
            {"id": "re16", "source": tn("evaluation_methodologies"), "target": tn("reproducibility_practices"), "relationship": "related_to"},
            {"id": "re17", "source": tn("benchmark_datasets"), "target": tn("state_of_art_approaches"), "relationship": "evaluated_by"},
            {"id": "re18", "source": tn("modern_architectures"), "target": tn("state_of_art_approaches"), "relationship": "improves"},
            {"id": "re19", "source": tn("modern_architectures"), "target": tn("recent_breakthroughs"), "relationship": "builds_upon"},
            {"id": "re20", "source": tn("breakthrough_techniques"), "target": tn("recent_breakthroughs"), "relationship": "improves"},
            {"id": "re21", "source": tn("reproducibility_practices"), "target": tn("open_problems"), "relationship": "related_to"},
            {"id": "re22", "source": tn("state_of_art_approaches"), "target": tn("recent_breakthroughs"), "relationship": "contrasts_with"},
            {"id": "re23", "source": tn("state_of_art_approaches"), "target": tn("open_problems"), "relationship": "challenges"},
            {"id": "re24", "source": tn("recent_breakthroughs"), "target": tn("emerging_research_directions"), "relationship": "extends"},
            {"id": "re25", "source": tn("recent_breakthroughs"), "target": tn("ethical_considerations"), "relationship": "related_to"},
            {"id": "re26", "source": tn("emerging_research_directions"), "target": tn("open_problems"), "relationship": "related_to"},
            {"id": "re27", "source": tn("emerging_research_directions"), "target": tn("future_outlook"), "relationship": "extends"},
            {"id": "re28", "source": tn("open_problems"), "target": tn("future_outlook"), "relationship": "challenges"},
            {"id": "re29", "source": tn("research_communities"), "target": tn("emerging_research_directions"), "relationship": "related_to"},
            {"id": "re30", "source": tn("interdisciplinary_connections"), "target": tn("emerging_research_directions"), "relationship": "extends"},
            {"id": "re31", "source": tn("key_datasets"), "target": tn("benchmark_datasets"), "relationship": "foundation"},
        ]

        return {
            "overview": {
                "topic": topic,
                "domain": "Research",
                "difficulty": "Advanced",
                "estimated_learning_time": "6-12 months",
                "popularity": "High",
                "importance_level": "Very High",
                "applications": ["Academic Research", "PhD Studies", "Literature Review", "Grant Writing"],
                "summary": f"Comprehensive research landscape analysis of {topic} covering foundational theories, seminal papers, current state-of-the-art, recent breakthroughs, open problems, and future research directions. This graph provides researchers with a complete roadmap of the field."
            },
            "nodes": nodes,
            "edges": edges
        }

    def _get_mock_interview_graph(self, topic: str) -> Dict[str, Any]:
        slug = topic.lower().replace(" ", "_").replace("/", "_")[:20]
        def tn(s): return f"{slug}_{s}"

        nodes = [
            {"id": tn("overview"), "name": f"Interview Prep: {topic}", "type": "must_know", "description": f"Comprehensive interview preparation guide for {topic}. Covers all essential topics, frequently asked questions, coding patterns, system design concepts, and behavioral frameworks.", "difficulty": "Intermediate", "importance_score": 10.0, "estimated_learning_time": "4-8 weeks", "prerequisites": [], "unlocks": [tn("data_structures"), tn("algorithms_fundamentals")], "applications": ["Technical Interviews", "Coding Assessments", "System Design Rounds"], "why_it_matters": "Acing the interview requires systematic preparation across all key areas", "resources": {"interview_questions": ["Q: Walk me through your approach to preparing for this technical interview?", "Q: What are your strengths and weaknesses in this topic area?"]}, "depth": 0},
            {"id": tn("data_structures"), "name": "Data Structures", "type": "must_know", "description": "Essential data structures asked in 90% of interviews. Master arrays, hash tables, linked lists, stacks, queues, trees, graphs, and heaps with time/space complexity for each operation.", "difficulty": "Beginner", "importance_score": 10.0, "estimated_learning_time": "2-3 weeks", "prerequisites": [tn("overview")], "unlocks": [tn("algorithms_fundamentals"), tn("coding_patterns"), tn("problem_solving_strategies")], "applications": ["Coding Interviews", "Problem Solving"], "why_it_matters": "Data structures are the #1 most tested topic across all interview levels", "resources": {"interview_questions": ["Q: Implement a HashMap from scratch. How would you handle collisions?", "Q: Design a Least Recently Used (LRU) cache with O(1) operations.", "Q: What is the difference between an array and a linked list? When would you use each?", "Q: Implement a Min Stack that supports push, pop, top, and getMin in O(1) time."]}, "depth": 1},
            {"id": tn("algorithms_fundamentals"), "name": "Algorithms Fundamentals", "type": "must_know", "description": "Core algorithms every candidate must know: sorting (quick, merge, heap), searching (binary search variants), two pointers, sliding window, recursion, and backtracking.", "difficulty": "Beginner", "importance_score": 9.5, "estimated_learning_time": "2-3 weeks", "prerequisites": [tn("data_structures"), tn("overview")], "unlocks": [tn("coding_patterns"), tn("dynamic_programming"), tn("graph_algorithms")], "applications": ["Coding Interviews", "Algorithm Design"], "why_it_matters": "Algorithmic thinking is the core skill interviews evaluate", "resources": {"interview_questions": ["Q: Implement binary search. What edge cases must you handle?", "Q: Find the kth largest element in an array. Optimize from O(n log n) to O(n).", "Q: Given a sorted array rotated at an unknown pivot, search for a target value.", "Q: Implement merge sort in-place. What is the space complexity?"]}, "depth": 1},
            {"id": tn("coding_patterns"), "name": "Coding Patterns", "type": "coding_pattern", "description": "Reusable problem-solving patterns: Fast & Slow Pointers, Merge Intervals, Cyclic Sort, Tree BFS/DFS, Two Heaps, Subsets, Modified Binary Search, Top K Elements, K-way Merge, 0/1 Knapsack.", "difficulty": "Intermediate", "importance_score": 9.5, "estimated_learning_time": "2-3 weeks", "prerequisites": [tn("data_structures"), tn("algorithms_fundamentals")], "unlocks": [tn("dynamic_programming"), tn("problem_solving_strategies")], "applications": ["LeetCode Patterns", "Competitive Programming"], "why_it_matters": "Most interview problems follow recognizable patterns — mastering them multiplies your effectiveness", "resources": {"interview_questions": ["Q: Detect a cycle in a linked list using O(1) space (Fast & Slow Pointer pattern).", "Q: Merge overlapping intervals. What if intervals are unsorted?", "Q: Find all subsets of a set that sum to a target (Subsets pattern with backtracking).", "Q: Top K frequent elements — solve with heap, then optimize with bucket sort."]}, "depth": 2},
            {"id": tn("dynamic_programming"), "name": "Dynamic Programming", "type": "frequently_asked", "description": "DP patterns: memoization vs tabulation, 0/1 Knapsack, Longest Common Subsequence, Longest Increasing Subsequence, Edit Distance, Matrix Chain Multiplication, and state transition optimization.", "difficulty": "Advanced", "importance_score": 9.0, "estimated_learning_time": "3-4 weeks", "prerequisites": [tn("algorithms_fundamentals"), tn("coding_patterns")], "unlocks": [tn("advanced_topics")], "applications": ["Senior Interviews", "Hard Problems"], "why_it_matters": "DP separates senior candidates — mastering the patterns is essential for top-tier companies", "resources": {"interview_questions": ["Q: Solve the coin change problem. How would you optimize for minimum number of coins?", "Q: Longest palindromic substring — solve with DP and then optimize to O(n) with expand around center.", "Q: 0/1 Knapsack problem — how does the recurrence relation work?", "Q: Given two strings, find the minimum edit distance to convert one to another."]}, "depth": 3},
            {"id": tn("graph_algorithms"), "name": "Graph Algorithms", "type": "frequently_asked", "description": "Graph fundamentals: BFS, DFS, Dijkstra, Bellman-Ford, Topological Sort, Union-Find, Minimum Spanning Tree (Kruskal/Prim), and graph coloring. Detect cycles, find connected components.", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "2-3 weeks", "prerequisites": [tn("data_structures"), tn("algorithms_fundamentals")], "unlocks": [tn("advanced_topics"), tn("system_design_fundamentals")], "applications": ["Graph Problems", "Network Analysis"], "why_it_matters": "Graph problems test both data structure knowledge and algorithmic thinking simultaneously", "resources": {"interview_questions": ["Q: Clone a graph (deep copy) using BFS or DFS.", "Q: Find the shortest path in a grid with obstacles (BFS with modifications).", "Q: Detect a cycle in a directed graph using DFS with coloring.", "Q: Number of connected components in an undirected graph using Union-Find."]}, "depth": 2},
            {"id": tn("problem_solving_strategies"), "name": "Problem-Solving Strategies", "type": "coding_pattern", "description": "Meta-strategies: breaking down problems, brute force first, optimal vs feasible, time-space tradeoffs, handling edge cases, test-driven problem solving, and communication during coding.", "difficulty": "Intermediate", "importance_score": 9.0, "estimated_learning_time": "1-2 weeks", "prerequisites": [tn("coding_patterns"), tn("algorithms_fundamentals")], "unlocks": [tn("advanced_topics")], "applications": ["Interview Strategy", "Whiteboard Coding"], "why_it_matters": "How you solve is as important as what you solve — strategy and communication matter greatly", "resources": {"interview_questions": ["Q: Walk me through your problem-solving approach before writing any code.", "Q: How would you handle edge cases and test your solution?", "Q: Your solution works but is slow — how would you optimize it?"]}, "depth": 2},
            {"id": tn("system_design_fundamentals"), "name": "System Design Fundamentals", "type": "system_design_fundamental", "description": "Core concepts: scalability (horizontal vs vertical), load balancing, caching (CDN, Redis), databases (SQL vs NoSQL, indexing, sharding), message queues, CAP theorem, consistent hashing, rate limiting.", "difficulty": "Advanced", "importance_score": 9.5, "estimated_learning_time": "3-4 weeks", "prerequisites": [tn("data_structures"), tn("graph_algorithms")], "unlocks": [tn("advanced_system_design")], "applications": ["Senior/Staff Interviews", "Architecture Design"], "why_it_matters": "System design rounds determine senior-level hiring decisions at top tech companies", "resources": {"interview_questions": ["Q: Design a URL shortening service like TinyURL. How would you handle 100M+ URLs?", "Q: Design a real-time chat system supporting millions of concurrent users.", "Q: How would you design a distributed key-value store with high availability?", "Q: Explain CAP theorem. How would you make tradeoffs for a social media feed?"]}, "depth": 2},
            {"id": tn("advanced_system_design"), "name": "Advanced System Design", "type": "system_design_fundamental", "description": "Complex system design scenarios: designing WhatsApp, Uber, Netflix, YouTube, Twitter, and Google Docs. Deep dive into data flow, storage strategies, and fault tolerance patterns.", "difficulty": "Advanced", "importance_score": 9.0, "estimated_learning_time": "3-4 weeks", "prerequisites": [tn("system_design_fundamentals")], "unlocks": [], "applications": ["Staff+ Interviews", "Architecture Reviews"], "why_it_matters": "Designing large-scale systems is the ultimate test of engineering maturity", "resources": {"interview_questions": ["Q: Design WhatsApp — how would you handle end-to-end encryption and message delivery?", "Q: Design Netflix's video streaming architecture. How would you reduce buffering?", "Q: Design a ride-sharing system like Uber. How do you handle real-time location updates?", "Q: Design a distributed rate limiter that works across multiple data centers."]}, "depth": 3},
            {"id": tn("complexity_analysis"), "name": "Complexity Analysis & Optimization", "type": "optimization_tip", "description": "Big O notation (time and space), best/average/worst case analysis, amortized analysis, space-time tradeoffs, and optimization techniques. Learn to analyze and improve algorithm efficiency.", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "1-2 weeks", "prerequisites": [tn("algorithms_fundamentals")], "unlocks": [tn("dynamic_programming"), tn("problem_solving_strategies")], "applications": ["Interview Analysis", "Code Optimization"], "why_it_matters": "Every interview answer must include complexity analysis — it is non-negotiable", "resources": {"interview_questions": ["Q: What is the time and space complexity of your solution? Can you prove it?", "Q: How would you optimize a solution from O(n^2) to O(n log n) or O(n)?", "Q: Explain amortized analysis using the example of dynamic array resizing."]}, "depth": 1},
            {"id": tn("common_pitfalls"), "name": "Common Pitfalls & Edge Cases", "type": "common_pitfall", "description": "Frequent interview mistakes: off-by-one errors, integer overflow, null pointer dereference, empty collections, single-element cases, duplicate handling, concurrent modification, and floating point precision.", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "1 week", "prerequisites": [tn("problem_solving_strategies")], "unlocks": [tn("advanced_topics")], "applications": ["Bug Prevention", "Test Coverage"], "why_it_matters": "Avoiding common pitfalls separates good candidates from great ones", "resources": {"interview_questions": ["Q: What edge cases would you test for a function that finds the median of two sorted arrays?", "Q: How would you handle integer overflow in a binary search implementation?", "Q: Find all the bugs in this implementation of a queue using two stacks."]}, "depth": 2},
            {"id": tn("behavioral_framework"), "name": "Behavioral Interview Framework", "type": "behavioral", "description": "STAR method (Situation, Task, Action, Result), leadership principles, conflict resolution, teamwork stories, failure narratives, and career progression stories for behavioral rounds.", "difficulty": "Beginner", "importance_score": 8.0, "estimated_learning_time": "1-2 weeks", "prerequisites": [tn("overview")], "unlocks": [tn("advanced_topics")], "applications": ["Behavioral Rounds", "Leadership Assessment"], "why_it_matters": "Behavioral rounds can make or break your offer — prepare stories that demonstrate impact", "resources": {"interview_questions": ["Q: Tell me about a time you had a conflict with a teammate. How did you resolve it?", "Q: Describe a project where you had to influence without authority.", "Q: Tell me about a failure and what you learned from it. Use the STAR framework.", "Q: Describe a time you went above and beyond expectations."]}, "depth": 1},
            {"id": tn("object_oriented_design"), "name": "Object-Oriented Design", "type": "frequently_asked", "description": "SOLID principles, design patterns (Singleton, Factory, Observer, Strategy, Decorator), OOD interview problems: Parking Lot, Elevator System, Library Management, Amazon Shopping Cart.", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "2-3 weeks", "prerequisites": [tn("data_structures"), tn("problem_solving_strategies")], "unlocks": [tn("advanced_topics"), tn("system_design_fundamentals")], "applications": ["OOD Interviews", "API Design"], "why_it_matters": "OOD interviews test your ability to write maintainable, extensible code", "resources": {"interview_questions": ["Q: Design a Parking Lot system. How would you handle different vehicle sizes?", "Q: Design an Elevator control system — what design patterns would you use?", "Q: Design a chess game with all the rules. How would you handle moves and validation?"]}, "depth": 2},
            {"id": tn("advanced_topics"), "name": "Advanced Topics & Differentiation", "type": "optimization_tip", "description": "Topics that differentiate senior candidates: multi-threading and concurrency, distributed systems fundamentals, advanced data structures (Trie, Segment Tree, Fenwick Tree, Disjoint Set Union), and recent industry trends.", "difficulty": "Advanced", "importance_score": 8.0, "estimated_learning_time": "3-4 weeks", "prerequisites": [tn("dynamic_programming"), tn("system_design_fundamentals"), tn("behavioral_framework")], "unlocks": [], "applications": ["Senior+ Roles", "Differentiation"], "why_it_matters": "These topics separate senior/staff-level candidates from mid-level", "resources": {"interview_questions": ["Q: Implement a thread-safe singleton. What are the different approaches?", "Q: Design a Trie for autocomplete. How would you handle memory optimization?", "Q: What is the difference between process and thread? When would you use each?", "Q: Explain the concepts of mutex, semaphore, and deadlock with examples."]}, "depth": 3},
        ]

        edges = [
            {"id": "ie1", "source": tn("overview"), "target": tn("data_structures"), "relationship": "must_know_before"},
            {"id": "ie2", "source": tn("overview"), "target": tn("algorithms_fundamentals"), "relationship": "must_know_before"},
            {"id": "ie3", "source": tn("data_structures"), "target": tn("algorithms_fundamentals"), "relationship": "prerequisite"},
            {"id": "ie4", "source": tn("data_structures"), "target": tn("coding_patterns"), "relationship": "prerequisite"},
            {"id": "ie5", "source": tn("algorithms_fundamentals"), "target": tn("coding_patterns"), "relationship": "prerequisite"},
            {"id": "ie6", "source": tn("algorithms_fundamentals"), "target": tn("graph_algorithms"), "relationship": "builds_upon"},
            {"id": "ie7", "source": tn("coding_patterns"), "target": tn("dynamic_programming"), "relationship": "builds_upon"},
            {"id": "ie8", "source": tn("coding_patterns"), "target": tn("problem_solving_strategies"), "relationship": "builds_upon"},
            {"id": "ie9", "source": tn("algorithms_fundamentals"), "target": tn("complexity_analysis"), "relationship": "builds_upon"},
            {"id": "ie10", "source": tn("problem_solving_strategies"), "target": tn("common_pitfalls"), "relationship": "related_to"},
            {"id": "ie11", "source": tn("data_structures"), "target": tn("object_oriented_design"), "relationship": "prerequisite"},
            {"id": "ie12", "source": tn("graph_algorithms"), "target": tn("system_design_fundamentals"), "relationship": "builds_upon"},
            {"id": "ie13", "source": tn("system_design_fundamentals"), "target": tn("advanced_system_design"), "relationship": "deep_dive"},
            {"id": "ie14", "source": tn("overview"), "target": tn("behavioral_framework"), "relationship": "must_know_before"},
            {"id": "ie15", "source": tn("dynamic_programming"), "target": tn("advanced_topics"), "relationship": "builds_upon"},
            {"id": "ie16", "source": tn("system_design_fundamentals"), "target": tn("advanced_topics"), "relationship": "builds_upon"},
            {"id": "ie17", "source": tn("behavioral_framework"), "target": tn("advanced_topics"), "relationship": "builds_upon"},
            {"id": "ie18", "source": tn("common_pitfalls"), "target": tn("advanced_topics"), "relationship": "builds_upon"},
            {"id": "ie19", "source": tn("object_oriented_design"), "target": tn("system_design_fundamentals"), "relationship": "builds_upon"},
            {"id": "ie20", "source": tn("complexity_analysis"), "target": tn("problem_solving_strategies"), "relationship": "builds_upon"},
        ]

        return {
            "overview": {
                "topic": topic,
                "domain": "Interview Preparation",
                "difficulty": "Intermediate",
                "estimated_learning_time": "4-8 weeks",
                "popularity": "Very High",
                "importance_level": "Very High",
                "applications": ["Technical Interview Prep", "Coding Assessments", "System Design Rounds", "Behavioral Rounds"],
                "summary": f"Complete interview preparation checklist for {topic}. Covers 15 essential topic areas: data structures, algorithms, coding patterns, dynamic programming, graph algorithms, system design, complexity analysis, common pitfalls, behavioral frameworks, OOD, and advanced differentiation topics. Each node includes specific interview questions and answer strategies."
            },
            "nodes": nodes,
            "edges": edges
        }

    def _get_mock_project_graph(self, topic: str) -> Dict[str, Any]:
        slug = topic.lower().replace(" ", "_").replace("/", "_")[:20]
        def tn(s): return f"{slug}_{s}"

        nodes = [
            {"id": tn("goal"), "name": f"Build: {topic}", "type": "goal", "description": f"Project goal: Build a complete {topic} application from scratch. This roadmap covers planning, technology selection, implementation, testing, deployment, and scaling.", "difficulty": "Intermediate", "importance_score": 10.0, "estimated_learning_time": "Project Overview", "prerequisites": [], "unlocks": [tn("planning_architecture")], "applications": ["Portfolio Project", "Learning"], "why_it_matters": "Building a complete project end-to-end is the best way to master full-stack development", "resources": {"technology_alternatives": [], "execution_guide": {"languages": [], "frameworks": [], "tools": [], "setup_commands": "", "how_to_execute": "Start by understanding the full project scope and requirements before writing any code.", "verification": "You should have a clear mental model of the entire architecture before proceeding."}}, "depth": 0},
            {"id": tn("planning_architecture"), "name": "Planning & Architecture", "type": "phase", "description": "Define requirements, choose architecture pattern (monolith vs microservices), design system architecture, and plan the tech stack. Document API contracts and data flow.", "difficulty": "Intermediate", "importance_score": 9.5, "estimated_learning_time": "2-3 days", "prerequisites": [tn("goal")], "unlocks": [tn("frontend_setup"), tn("backend_setup"), tn("database_design")], "applications": ["System Design", "Tech Stack Selection"], "why_it_matters": "Good planning prevents costly rework — 80% of project success comes from architecture decisions", "resources": {"technology_alternatives": [{"name": "Monolithic Architecture", "pros": ["Simpler to develop and deploy", "Better for small teams", "Single codebase"], "cons": ["Harder to scale independently", "Tech stack coupling"], "best_for": "MVP and small-to-medium projects"}, {"name": "Microservices Architecture", "pros": ["Independent scaling", "Tech stack flexibility", "Team autonomy"], "cons": ["Operational complexity", "Network latency", "Distributed system challenges"], "best_for": "Large-scale applications with multiple teams"}], "execution_guide": {"languages": ["Python 3.11+", "JavaScript (ES6+)"], "frameworks": ["Django 5.0 / FastAPI", "React 18 with TypeScript"], "tools": ["Figma for wireframes", "Draw.io for architecture diagrams", "Notion/Miro for requirements"], "setup_commands": "mkdir project-name && cd project-name && git init", "how_to_execute": "1. Write a PRD (Product Requirements Document)\n2. Design system architecture diagram\n3. Choose tech stack for each layer\n4. Define 5-10 core user stories\n5. Plan database schema on paper first\n6. Set up project boards (GitHub Projects / Jira)", "common_mistakes": ["Starting to code before understanding the full scope", "Over-engineering with microservices for a simple app", "Not documenting API contracts upfront"], "verification": "You should have: architecture diagram, tech stack decisions documented, core user stories written, and folder structure planned."}}, "depth": 1},
            {"id": tn("frontend_setup"), "name": "Frontend Setup & Foundation", "type": "step", "description": "Initialize React project with Vite, configure TypeScript, set up Tailwind CSS for styling, create folder structure (components, pages, hooks, utils, services), and set up routing with React Router.", "difficulty": "Beginner", "importance_score": 8.5, "estimated_learning_time": "1-2 days", "prerequisites": [tn("planning_architecture")], "unlocks": [tn("frontend_core_features")], "applications": ["UI Development"], "why_it_matters": "A solid frontend foundation ensures maintainable and scalable UI code", "resources": {"technology_alternatives": [{"name": "React + Vite + TypeScript", "pros": ["Fast HMR", "Excellent DX", "Strongly typed"], "cons": ["TypeScript learning curve"], "best_for": "Most web applications"}, {"name": "Next.js 14", "pros": ["SSR/SSG built-in", "File-based routing", "SEO friendly"], "cons": ["Heavier than Vite", "More opinionated"], "best_for": "Content-heavy and SEO-required apps"}, {"name": "Vue 3 + Vite", "pros": ["Gentler learning curve", "Good documentation", "Lightweight"], "cons": ["Smaller ecosystem than React"], "best_for": "Teams preferring Vue's simplicity"}], "execution_guide": {"languages": ["TypeScript 5.x", "JavaScript (ES6+)"], "frameworks": ["React 18", "Vite 5", "Tailwind CSS 3"], "tools": ["VS Code", "ESLint", "Prettier", "Chrome DevTools"], "setup_commands": "npm create vite@latest frontend -- --template react-ts\ncd frontend\nnpm install react-router-dom tailwindcss @tailwindcss/vite\nnpm install axios @tanstack/react-query\nmkdir -p src/{components,pages,hooks,utils,services,types}", "how_to_execute": "1. Run the Vite create command to scaffold the project\n2. Install all dependencies\n3. Configure Tailwind in vite.config.ts\n4. Create folder structure following the commands above\n5. Set up React Router with lazy loading\n6. Create a base API service layer with axios\n7. Set up ESLint and Prettier config\n8. Create a basic layout component with header/footer", "code_snippet": "// vite.config.ts\nimport { defineConfig } from 'vite'\nimport react from '@vitejs/plugin-react'\nimport tailwindcss from '@tailwindcss/vite'\n\nexport default defineConfig({\n  plugins: [react(), tailwindcss()],\n})", "common_mistakes": ["Skipping TypeScript — it saves time in the long run", "Not setting up ESLint/Prettier from day one", "Putting all components in one folder without structure"], "verification": "Run 'npm run dev' — you should see a blank React app with Tailwind styles working and routing functional."}}, "depth": 2},
            {"id": tn("backend_setup"), "name": "Backend Setup & API Foundation", "type": "step", "description": "Initialize backend project with chosen framework, set up project structure, configure database connection, create base models, set up authentication, and create RESTful API endpoints.", "difficulty": "Intermediate", "importance_score": 9.0, "estimated_learning_time": "2-3 days", "prerequisites": [tn("planning_architecture")], "unlocks": [tn("backend_core_features"), tn("api_integration")], "applications": ["API Development", "Server Logic"], "why_it_matters": "The backend is the brain of your application — all business logic lives here", "resources": {"technology_alternatives": [{"name": "Django + Django REST Framework", "pros": ["Batteries included", "Admin panel built-in", "ORM is excellent", "Great for CRUD apps"], "cons": ["Heavier than Flask/FastAPI", "Less control over architecture"], "best_for": "Data-driven apps, CMS, admin-heavy apps"}, {"name": "FastAPI", "pros": ["Async support", "Automatic OpenAPI docs", "Very fast", "Pydantic validation"], "cons": ["Smaller ecosystem", "Less built-in functionality"], "best_for": "APIs, real-time apps, ML backends"}, {"name": "Node.js + Express", "pros": ["JavaScript everywhere", "Huge ecosystem", "Non-blocking I/O"], "cons": ["Callback hell", "Less structured than Django"], "best_for": "Real-time apps, startups, full-stack JS teams"}], "execution_guide": {"languages": ["Python 3.11+ / Node.js 20 LTS"], "frameworks": ["Django 5.0 + DRF / FastAPI 0.110+"], "tools": ["Postman/Insomnia for API testing", "pgAdmin/DBeaver for DB", "Docker for containerization"], "setup_commands": "# Django setup\npython -m venv venv\nsource venv/bin/activate  # or `venv\\Scripts\\activate` on Windows\npip install django djangorestframework django-cors-headers python-decouple psycopg2-binary\ndjango-admin startproject backend .\npython manage.py startapp api\n\n# FastAPI setup\npip install fastapi uvicorn sqlalchemy psycopg2-binary python-decouple alembic", "how_to_execute": "1. Create virtual environment and activate it\n2. Install Django/FastAPI and all dependencies\n3. Set up project structure\n4. Configure database connection in settings (use PostgreSQL)\n5. Create initial models for your core entities\n6. Set up CORS headers for frontend communication\n7. Create base API endpoints (CRUD for main models)\n8. Set up JWT authentication\n9. Test all endpoints with Postman", "code_snippet": "# Django settings.py database config\nDATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.postgresql',\n        'NAME': 'your_db_name',\n        'USER': 'your_db_user',\n        'PASSWORD': 'your_db_password',\n        'HOST': 'localhost',\n        'PORT': '5432',\n    }\n}\n\n# Sample model\nfrom django.db import models\n\nclass Item(models.Model):\n    name = models.CharField(max_length=200)\n    description = models.TextField(blank=True)\n    created_at = models.DateTimeField(auto_now_add=True)\n    updated_at = models.DateTimeField(auto_now=True)\n\n    def __str__(self):\n        return self.name", "common_mistakes": ["Hardcoding secrets in settings files — use environment variables", "Not using database migrations properly", "Forgetting to set up CORS for frontend access", "Exposing sensitive data through API responses"], "verification": "Run the dev server and hit the health check endpoint. All base models should be migrated and API should return valid JSON responses."}}, "depth": 2},
            {"id": tn("database_design"), "name": "Database Design & Setup", "type": "step", "description": "Design database schema, choose database type (SQL vs NoSQL), set up PostgreSQL/MongoDB, create migrations, define relationships (1:1, 1:M, M:M), indexes, and seed data.", "difficulty": "Intermediate", "importance_score": 9.0, "estimated_learning_time": "1-2 days", "prerequisites": [tn("planning_architecture")], "unlocks": [tn("backend_setup")], "applications": ["Data Modeling", "Storage"], "why_it_matters": "Database design decisions affect every layer of your application forever", "resources": {"technology_alternatives": [{"name": "PostgreSQL", "pros": ["ACID compliant", "Powerful querying", "JSON support", "Excellent extensions"], "cons": ["Heavier than MySQL", "Replication setup complex"], "best_for": "Most web applications"}, {"name": "MongoDB", "pros": ["Flexible schema", "Easy to scale", "Great for rapid prototyping"], "cons": ["No joins", "Eventual consistency", "Less mature tooling"], "best_for": "Content management, real-time analytics, IoT"}], "execution_guide": {"languages": ["SQL"], "tools": ["pgAdmin", "DBeaver", "TablePlus", "Prisma Studio"], "setup_commands": "# PostgreSQL setup (Windows)\n# Download installer from https://www.postgresql.org/download/windows/\n# Or use Docker:\ndocker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:16\n\n# Create database\npsql -U postgres\nCREATE DATABASE project_db;", "how_to_execute": "1. Design your ER diagram first (using dbdiagram.io or Draw.io)\n2. Choose between SQL and NoSQL based on your data relationships\n3. Set up PostgreSQL via Docker or local install\n4. Create database and user\n5. Define models/migrations in your backend framework\n6. Add proper indexes for frequently queried fields\n7. Create seed data for development", "code_snippet": "-- Example schema\nCREATE TABLE users (\n    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n    email VARCHAR(255) UNIQUE NOT NULL,\n    username VARCHAR(100) UNIQUE NOT NULL,\n    password_hash VARCHAR(255) NOT NULL,\n    created_at TIMESTAMP DEFAULT NOW(),\n    updated_at TIMESTAMP DEFAULT NOW()\n);\n\nCREATE TABLE projects (\n    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n    user_id UUID REFERENCES users(id),\n    title VARCHAR(200) NOT NULL,\n    description TEXT,\n    status VARCHAR(20) DEFAULT 'draft',\n    created_at TIMESTAMP DEFAULT NOW()\n);\n\nCREATE INDEX idx_projects_user_id ON projects(user_id);\nCREATE INDEX idx_projects_status ON projects(status);", "common_mistakes": ["Not using indexes on foreign keys", "Forgetting to add created_at/updated_at timestamps", "Making columns nullable when they shouldn't be", "Not planning for soft deletes"], "verification": "Connect to your database with a GUI tool. All tables should be created, relationships should be visible, and seed data should be queryable."}}, "depth": 2},
            {"id": tn("frontend_core_features"), "name": "Frontend Core Features", "type": "step", "description": "Build core UI components: authentication pages (login/register), main dashboard, CRUD interfaces, forms with validation, search/filter functionality, and responsive layouts.", "difficulty": "Intermediate", "importance_score": 9.0, "estimated_learning_time": "1-2 weeks", "prerequisites": [tn("frontend_setup")], "unlocks": [tn("api_integration"), tn("testing_qa")], "applications": ["UI Features", "User Experience"], "why_it_matters": "Core features are what users actually interact with — they must be polished and functional", "resources": {"technology_alternatives": [{"name": "React Context + useReducer", "pros": ["No extra dependencies", "Simple for small apps", "Built into React"], "cons": ["Performance with large state", "Boilerplate code"], "best_for": "Small-to-medium apps"}, {"name": "Redux Toolkit + RTK Query", "pros": ["Predictable state management", "Built-in caching", "DevTools"], "cons": ["More boilerplate", "Learning curve"], "best_for": "Large apps with complex state"}], "execution_guide": {"languages": ["TypeScript 5.x"], "frameworks": ["React 18", "React Router 6", "React Hook Form", "Zod validation"], "tools": ["Storybook for component development", "React DevTools", "Chrome DevTools"], "setup_commands": "npm install react-hook-form @hookform/resolvers zod @tanstack/react-query\n# For state management:\nnpm install @reduxjs/toolkit react-redux  # if using Redux", "how_to_execute": "1. Build authentication components (LoginForm, RegisterForm, ProtectedRoute)\n2. Create shared UI components (Button, Input, Modal, Card, Table)\n3. Implement main layout with navigation sidebar\n4. Build CRUD pages for each main entity\n5. Add form validation with React Hook Form + Zod\n6. Implement search, sort, and filter functionality\n7. Add loading states and error boundaries\n8. Make all pages responsive with Tailwind breakpoints", "code_snippet": "// Example protected route component\nimport { Navigate } from 'react-router-dom'\nimport { useAuth } from '../hooks/useAuth'\n\nfunction ProtectedRoute({ children }: { children: React.ReactNode }) {\n  const { user, isLoading } = useAuth()\n\n  if (isLoading) return <Spinner />\n  if (!user) return <Navigate to=\"/login\" replace />\n\n  return <>{children}</>\n}", "common_mistakes": ["Not handling loading/error states for every API call", "Building too-specific components that can't be reused", "Forgetting mobile responsiveness", "Not using React.memo for expensive renders"], "verification": "All core features should work end-to-end: user can register, log in, view dashboard, and perform CRUD operations on main entities."}}, "depth": 3},
            {"id": tn("backend_core_features"), "name": "Backend Core Features & Business Logic", "type": "step", "description": "Implement business logic: authentication (JWT/OAuth), CRUD API endpoints with pagination/sorting/filtering, file upload handling, email services, background tasks, and webhook support.", "difficulty": "Intermediate", "importance_score": 9.0, "estimated_learning_time": "1-2 weeks", "prerequisites": [tn("backend_setup")], "unlocks": [tn("api_integration"), tn("testing_qa")], "applications": ["Business Logic", "API Development"], "why_it_matters": "Well-designed APIs with proper error handling and validation make frontend development smooth", "resources": {"technology_alternatives": [{"name": "JWT Authentication", "pros": ["Stateless", "Scalable", "Simple to implement"], "cons": ["Token revocation is complex", "Token size"], "best_for": "REST APIs"}, {"name": "Session-based Auth", "pros": ["Server-controlled", "Easy to revoke", "Traditional"], "cons": ["Requires server state", "Not ideal for mobile"], "best_for": "Server-rendered apps"}], "execution_guide": {"languages": ["Python 3.11+ / Node.js 20"], "frameworks": ["Django REST Framework / FastAPI"], "tools": ["Celery (background tasks)", "Redis (caching/queues)", "Sentry (error tracking)"], "setup_commands": "# Django: Add to INSTALLED_APPS\npip install djangorestframework-simplejwt django-filter celery redis\n\n# Create serializer, viewset, and URL patterns for each model", "how_to_execute": "1. Implement JWT authentication (access + refresh tokens)\n2. Create serializers for all models with validation\n3. Build ViewSets with pagination, filtering, ordering\n4. Implement file upload endpoints\n5. Set up Celery for background tasks (email, reports)\n6. Add rate limiting to public endpoints\n7. Implement caching for frequently accessed data\n8. Add comprehensive error handling and logging", "code_snippet": "# Django ViewSet example\nfrom rest_framework import viewsets, filters\nfrom django_filters.rest_framework import DjangoFilterBackend\n\nclass ItemViewSet(viewsets.ModelViewSet):\n    queryset = Item.objects.all()\n    serializer_class = ItemSerializer\n    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]\n    filterset_fields = ['status', 'category']\n    search_fields = ['name', 'description']\n    ordering_fields = ['created_at', 'updated_at', 'name']\n    \n    def perform_create(self, serializer):\n        serializer.save(user=self.request.user)", "common_mistakes": ["Not paginating list endpoints (causes timeouts)", "Exposing internal IDs in API responses", "Not validating input data thoroughly", "Missing proper HTTP status codes"], "verification": "Test all endpoints: authentication flow works, CRUD operations return correct data, pagination and filtering work, error cases return proper status codes."}}, "depth": 3},
            {"id": tn("api_integration"), "name": "API Integration & Data Flow", "type": "step", "description": "Connect frontend to backend: set up axios interceptors for auth, implement React Query for data fetching and caching, handle loading/error states, optimistic updates, and real-time updates via WebSockets.", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "3-4 days", "prerequisites": [tn("frontend_core_features"), tn("backend_core_features")], "unlocks": [tn("testing_qa"), tn("deployment")], "applications": ["Frontend-Backend Integration"], "why_it_matters": "The quality of API integration determines the user experience more than any other factor", "resources": {"technology_alternatives": [{"name": "React Query (TanStack Query)", "pros": ["Automatic caching", "Background refetching", "Optimistic updates"], "cons": ["Learning curve", "Extra bundle size"], "best_for": "Data-heavy applications"}, {"name": "RTK Query", "pros": ["Integrated with Redux", "TypeScript-first", "Mature"], "cons": ["Redux dependency", "More boilerplate"], "best_for": "Redux-based projects"}], "execution_guide": {"languages": ["TypeScript 5.x", "Python 3.11+"], "frameworks": ["React 18 + TanStack Query", "Django REST Framework"], "tools": ["Axios", "React Query DevTools", "Postman"], "setup_commands": "npm install @tanstack/react-query axios\nnpm install @tanstack/react-query-devtools", "how_to_execute": "1. Create an axios instance with base URL and interceptors\n2. Add auth token interceptor (attach JWT to all requests)\n3. Set up React Query provider in your app\n4. Create custom hooks for each API endpoint (useItems, useCreateItem, etc.)\n5. Implement optimistic updates for create/update/delete\n6. Add error boundaries and toast notifications for API errors\n7. Implement WebSocket connection for real-time features", "code_snippet": "// API service layer\nimport axios from 'axios'\n\nconst api = axios.create({\n  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',\n})\n\napi.interceptors.request.use((config) => {\n  const token = localStorage.getItem('access_token')\n  if (token) {\n    config.headers.Authorization = `Bearer ${token}`\n  }\n  return config\n})\n\napi.interceptors.response.use(\n  (response) => response,\n  async (error) => {\n    if (error.response?.status === 401) {\n      // Handle token refresh or redirect to login\n    }\n    return Promise.reject(error)\n  }\n)", "common_mistakes": ["Not handling token expiration gracefully", "Forgetting to invalidate cache after mutations", "Not showing loading states during data fetch", "Ignoring error responses from the API"], "verification": "Full data flow works: frontend fetches data from backend, displays it, mutations update the UI immediately (optimistic), and errors are handled gracefully."}}, "depth": 3},
            {"id": tn("testing_qa"), "name": "Testing & Quality Assurance", "type": "step", "description": "Write comprehensive tests: unit tests for models and utilities, integration tests for API endpoints, component tests with React Testing Library, E2E tests with Playwright, and performance testing.", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "3-5 days", "prerequisites": [tn("api_integration")], "unlocks": [tn("deployment")], "applications": ["Quality Assurance", "CI/CD"], "why_it_matters": "Tests are not optional — they protect against regressions and ensure your project works correctly", "resources": {"technology_alternatives": [{"name": "pytest (backend)", "pros": ["Powerful fixtures", "Great plugins", "Simple syntax"], "cons": ["Some pytest-django learning"], "best_for": "Python backends"}, {"name": "Jest + React Testing Library (frontend)", "pros": ["Industry standard", "Good React support", "Fast"], "cons": ["Setup can be complex"], "best_for": "React frontends"}], "execution_guide": {"languages": ["Python 3.11+", "TypeScript 5.x"], "frameworks": ["pytest + pytest-django", "Vitest + React Testing Library"], "tools": ["Playwright for E2E", "Coverage.py", "Postman/Newman for API tests"], "setup_commands": "# Backend testing\npip install pytest pytest-django pytest-cov factory-boy\n# Frontend testing\nnpm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom", "how_to_execute": "1. Write model tests (validation, string representation, constraints)\n2. Write API tests for each endpoint (success and failure cases)\n3. Write component tests for key UI components\n4. Write integration tests for critical user flows\n5. Set up Playwright for E2E tests (login -> create -> verify)\n6. Run tests with coverage and aim for 80%+ coverage\n7. Add test CI pipeline in GitHub Actions", "code_snippet": "# pytest example\nimport pytest\nfrom rest_framework.test import APIClient\nfrom django.contrib.auth import get_user_model\n\n@pytest.mark.django_db\ndef test_create_item_authenticated():\n    client = APIClient()\n    user = get_user_model().objects.create_user(username='test', password='pass123')\n    client.force_authenticate(user=user)\n    \n    response = client.post('/api/items/', {'name': 'Test Item', 'description': 'Test'})\n    assert response.status_code == 201\n    assert response.data['name'] == 'Test Item'", "common_mistakes": ["Writing tests after bugs are discovered (TDD prevents this)", "Testing implementation details instead of behavior", "Not testing error/edge cases", "Low coverage in critical business logic"], "verification": "All tests pass with 80%+ coverage. CI pipeline runs tests automatically on each push."}}, "depth": 3},
            {"id": tn("deployment"), "name": "Deployment & DevOps", "type": "step", "description": "Containerize with Docker, set up CI/CD pipeline, deploy backend to cloud platform, deploy frontend to static hosting, configure custom domain and SSL, set up monitoring and error tracking.", "difficulty": "Advanced", "importance_score": 9.0, "estimated_learning_time": "3-5 days", "prerequisites": [tn("testing_qa"), tn("api_integration")], "unlocks": [tn("maintenance_scaling")], "applications": ["Production Launch", "DevOps"], "why_it_matters": "A project isn't complete until it's deployed and accessible to users", "resources": {"technology_alternatives": [{"name": "Docker + Render/Railway", "pros": ["Easy setup", "Free tier available", "Auto-deploy from GitHub"], "cons": ["Less control than AWS", "Cold starts on free tier"], "best_for": "MVP and small projects"}, {"name": "Docker + AWS (ECS/EC2)", "pros": ["Full control", "Scalable", "All services integrated"], "cons": ["Complex setup", "Cost management"], "best_for": "Production applications"}, {"name": "Vercel (Frontend) + Railway (Backend)", "pros": ["Optimized for frontend", "Simple backend deploy", "Good DX"], "cons": ["Vendor lock-in", "Limited backend resources"], "best_for": "Full-stack JS/TS apps"}], "execution_guide": {"languages": ["Dockerfile", "YAML (CI/CD)"], "tools": ["Docker", "GitHub Actions", "Render/Railway/AWS", "Nginx"], "setup_commands": "# Create Dockerfile for backend\nFROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"gunicorn\", \"backend.wsgi:application\", \"--bind\", \"0.0.0.0:8000\"]\n\n# Create docker-compose.yml\nversion: '3.8'\nservices:\n  db:\n    image: postgres:16\n    environment:\n      POSTGRES_DB: project_db\n      POSTGRES_USER: user\n      POSTGRES_PASSWORD: password\n  backend:\n    build: ./backend\n    ports:\n      - \"8000:8000\"\n    depends_on:\n      - db\n  frontend:\n    build: ./frontend\n    ports:\n      - \"80:80\"", "how_to_execute": "1. Create Dockerfile for backend and frontend\n2. Create docker-compose.yml for local testing\n3. Set up GitHub Actions workflow for CI/CD\n4. Create production environment on chosen platform\n5. Set up PostgreSQL database (managed service)\n6. Configure environment variables (secrets, DB URL, API keys)\n7. Deploy backend first, then frontend\n8. Set up custom domain and SSL via Cloudflare\n9. Configure Sentry for error monitoring\n10. Set up uptime monitoring (UptimeRobot, Better Stack)", "common_mistakes": ["Hardcoding environment variables in code", "Not using .dockerignore (huge image sizes)", "Deploying without proper health checks", "Forgetting to set up database backups"], "verification": "Both frontend and backend are live on production URLs. Full user flow works in production. SSL certificate is valid. Monitoring is configured and reporting."}}, "depth": 3},
            {"id": tn("maintenance_scaling"), "name": "Maintenance & Scaling", "type": "step", "description": "Post-launch activities: set up monitoring dashboards, performance optimization (caching, CDN, lazy loading), database optimization (query optimization, connection pooling), scaling strategy, and feature roadmap.", "difficulty": "Advanced", "importance_score": 8.0, "estimated_learning_time": "Ongoing", "prerequisites": [tn("deployment")], "unlocks": [], "applications": ["Production Operations", "Growth"], "why_it_matters": "Launch is just the beginning — real engineering is in keeping the system running and scaling", "resources": {"technology_alternatives": [{"name": "Redis Caching", "pros": ["In-memory speed", "Simple API", "Widely supported"], "cons": ["RAM cost", "Cache invalidation complexity"], "best_for": "Frequently accessed, rarely changed data"}, {"name": "CDN (Cloudflare)", "pros": ["Global edge network", "DDoS protection", "SSL management"], "cons": ["Cache invalidation", "Cost at scale"], "best_for": "Static assets and global audience"}], "execution_guide": {"languages": ["Python", "TypeScript", "SQL"], "tools": ["Sentry", "Datadog/Grafana", "Redis", "Cloudflare", "New Relic"], "setup_commands": "# Redis setup in Django\npip install django-redis\n# settings.py\nCACHES = {\n    'default': {\n        'BACKEND': 'django_redis.cache.RedisCache',\n        'LOCATION': 'redis://127.0.0.1:6379/1',\n    }\n}", "how_to_execute": "1. Set up performance monitoring (Sentry, Datadog)\n2. Implement Redis caching for database queries\n3. Add CDN for static assets\n4. Optimize database queries (add missing indexes, N+1 fixes)\n5. Implement lazy loading for images and components\n6. Set up database connection pooling\n7. Create scaling plan (vertical -> horizontal -> microservices)\n8. Set up automated backups\n9. Plan feature roadmap for next iteration\n10. Write documentation and setup guide", "common_mistakes": ["Scaling prematurely (optimize when you have data)", "Ignoring database query performance", "Not monitoring before optimizing", "Skipping documentation"], "verification": "App runs smoothly under load tests. Monitoring dashboards show healthy metrics. Page load times are under 2 seconds. Database queries are optimized (< 100ms)."}}, "depth": 4},
        ]

        edges = [
            {"id": "pe1", "source": tn("goal"), "target": tn("planning_architecture"), "relationship": "next_step"},
            {"id": "pe2", "source": tn("planning_architecture"), "target": tn("frontend_setup"), "relationship": "next_step"},
            {"id": "pe3", "source": tn("planning_architecture"), "target": tn("backend_setup"), "relationship": "next_step"},
            {"id": "pe4", "source": tn("planning_architecture"), "target": tn("database_design"), "relationship": "next_step"},
            {"id": "pe5", "source": tn("database_design"), "target": tn("backend_setup"), "relationship": "prerequisite"},
            {"id": "pe6", "source": tn("frontend_setup"), "target": tn("frontend_core_features"), "relationship": "next_step"},
            {"id": "pe7", "source": tn("backend_setup"), "target": tn("backend_core_features"), "relationship": "next_step"},
            {"id": "pe8", "source": tn("frontend_core_features"), "target": tn("api_integration"), "relationship": "builds_upon"},
            {"id": "pe9", "source": tn("backend_core_features"), "target": tn("api_integration"), "relationship": "builds_upon"},
            {"id": "pe10", "source": tn("api_integration"), "target": tn("testing_qa"), "relationship": "next_step"},
            {"id": "pe11", "source": tn("testing_qa"), "target": tn("deployment"), "relationship": "next_step"},
            {"id": "pe12", "source": tn("deployment"), "target": tn("maintenance_scaling"), "relationship": "next_step"},
        ]

        return {
            "overview": {
                "topic": topic,
                "domain": "Software Development",
                "difficulty": "Intermediate",
                "estimated_learning_time": "4-8 weeks",
                "popularity": "High",
                "importance_level": "High",
                "applications": ["Web Development", "Portfolio Project", "Learning Full-stack"],
                "summary": f"Complete project roadmap for building {topic}. Covers all phases from planning and architecture through deployment and scaling. Each step specifies exact technologies (languages, frameworks, tools), setup commands, implementation instructions, code examples, and verification steps."
            },
            "nodes": nodes,
            "edges": edges
        }

    def _get_mock_quick_graph(self, topic: str) -> Dict[str, Any]:
        slug = topic.lower().replace(" ", "_").replace("/", "_")[:20]
        def tn(s): return f"{slug}_{s}"

        nodes = [
            {"id": tn("overview"), "name": topic, "type": "core_concept", "description": f"Quick overview of {topic} covering the essential concepts you need to know.", "difficulty": "Beginner", "importance_score": 9.0, "estimated_learning_time": "1-2 hours", "prerequisites": [], "unlocks": [tn("core_concept_1"), tn("core_concept_2")], "applications": ["Quick Learning", "Overview"], "why_it_matters": f"Understanding {topic} is valuable for modern technology work", "resources": {}, "depth": 0},
            {"id": tn("core_concept_1"), "name": "Core Concepts", "type": "core_concept", "description": f"The fundamental ideas and principles that define {topic}.", "difficulty": "Beginner", "importance_score": 8.5, "estimated_learning_time": "30 min", "prerequisites": [tn("overview")], "unlocks": [tn("applications")], "applications": ["Understanding", "Foundation"], "why_it_matters": "Core concepts provide the foundation for everything else", "resources": {}, "depth": 1},
            {"id": tn("core_concept_2"), "name": "Key Components", "type": "core_concept", "description": f"Major components and building blocks of {topic}.", "difficulty": "Beginner", "importance_score": 8.0, "estimated_learning_time": "30 min", "prerequisites": [tn("overview")], "unlocks": [tn("applications")], "applications": ["Architecture", "Design"], "why_it_matters": "Understanding components helps you see how things fit together", "resources": {}, "depth": 1},
            {"id": tn("prerequisite_1"), "name": "Fundamentals Needed", "type": "prerequisite", "description": f"Background knowledge recommended before diving into {topic}.", "difficulty": "Beginner", "importance_score": 7.5, "estimated_learning_time": "varies", "prerequisites": [], "unlocks": [tn("overview")], "applications": ["Preparation"], "why_it_matters": "Right prerequisites ensure you can follow the material", "resources": {}, "depth": 0},
            {"id": tn("applications"), "name": "Real-World Applications", "type": "application", "description": f"How {topic} is used in industry and real-world scenarios.", "difficulty": "Beginner", "importance_score": 7.5, "estimated_learning_time": "20 min", "prerequisites": [tn("core_concept_1"), tn("core_concept_2")], "unlocks": [], "applications": ["Industry Use", "Problem Solving"], "why_it_matters": "Real-world context helps you understand why this matters", "resources": {}, "depth": 2},
            {"id": tn("related_1"), "name": "Related Technologies", "type": "related_concept", "description": f"Technologies and concepts related to {topic}.", "difficulty": "Beginner", "importance_score": 6.5, "estimated_learning_time": "15 min", "prerequisites": [tn("overview")], "unlocks": [], "applications": ["Broader Context"], "why_it_matters": "Related concepts help you see the bigger picture", "resources": {}, "depth": 1},
        ]

        edges = [
            {"id": "qe1", "source": tn("overview"), "target": tn("core_concept_1"), "relationship": "prerequisite"},
            {"id": "qe2", "source": tn("overview"), "target": tn("core_concept_2"), "relationship": "prerequisite"},
            {"id": "qe3", "source": tn("prerequisite_1"), "target": tn("overview"), "relationship": "prerequisite"},
            {"id": "qe4", "source": tn("core_concept_1"), "target": tn("applications"), "relationship": "application"},
            {"id": "qe5", "source": tn("core_concept_2"), "target": tn("applications"), "relationship": "application"},
            {"id": "qe6", "source": tn("overview"), "target": tn("related_1"), "relationship": "related_concept"},
        ]

        return {
            "overview": {
                "topic": topic,
                "domain": "General",
                "difficulty": "Beginner",
                "estimated_learning_time": "1-2 hours",
                "popularity": "Medium",
                "importance_level": "Medium",
                "applications": ["Quick Learning", "Overview"],
                "summary": f"A quick overview of {topic} with the most essential concepts."
            },
            "nodes": nodes,
            "edges": edges
        }

    def _get_mock_expansion(self) -> Dict[str, Any]:
        return {
            "new_nodes": [
                {"id": "gpt2", "name": "GPT-2", "type": "advanced_concept", "description": "Second generation GPT model with 1.5B parameters", "difficulty": "Advanced", "importance_score": 7.5, "estimated_learning_time": "1-2 weeks", "prerequisites": ["transformers"], "unlocks": ["gpt3", "nlp_advances"], "applications": ["Text Generation", "Language Understanding"], "why_it_matters": "GPT-2 demonstrated the power of scaling transformers", "resources": {}, "depth": 6},
                {"id": "gpt3", "name": "GPT-3", "type": "advanced_concept", "description": "Third generation GPT model with 175B parameters", "difficulty": "Advanced", "importance_score": 9.0, "estimated_learning_time": "2-3 weeks", "prerequisites": ["gpt2"], "unlocks": ["gpt4", "few_shot_learning"], "applications": ["ChatGPT", "Code Generation", "Translation"], "why_it_matters": "GPT-3 introduced few-shot learning at scale", "resources": {}, "depth": 7},
                {"id": "gpt4", "name": "GPT-4", "type": "advanced_concept", "description": "Fourth generation GPT model with multimodal capabilities", "difficulty": "Advanced", "importance_score": 9.5, "estimated_learning_time": "3-4 weeks", "prerequisites": ["gpt3"], "unlocks": ["multimodal_ai", "agents"], "applications": ["Advanced Chat", "Image Understanding", "Reasoning"], "why_it_matters": "GPT-4 introduced multimodal understanding and improved reasoning", "resources": {}, "depth": 8},
                {"id": "rag", "name": "RAG (Retrieval Augmented Generation)", "type": "application", "description": "Technique combining retrieval with generation for grounded outputs", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "1-2 weeks", "prerequisites": ["transformers", "information_retrieval"], "unlocks": ["knowledge_bases", "enterprise_ai"], "applications": ["Question Answering", "Enterprise Search", "Document Analysis"], "why_it_matters": "RAG enables LLMs to access external knowledge", "resources": {}, "depth": 6},
                {"id": "agents", "name": "AI Agents", "type": "application", "description": "Autonomous AI systems that can plan and execute tasks", "difficulty": "Advanced", "importance_score": 9.0, "estimated_learning_time": "3-4 weeks", "prerequisites": ["gpt4", "tool_use"], "unlocks": ["autonomous_systems", "multi_agent"], "applications": ["Automation", "Code Development", "Research"], "why_it_matters": "Agents represent the next frontier in AI capabilities", "resources": {}, "depth": 8}
            ],
            "new_edges": [
                {"id": "ee1", "source": "transformers", "target": "gpt2", "relationship": "advanced_concept"},
                {"id": "ee2", "source": "gpt2", "target": "gpt3", "relationship": "advanced_concept"},
                {"id": "ee3", "source": "gpt3", "target": "gpt4", "relationship": "advanced_concept"},
                {"id": "ee4", "source": "transformers", "target": "rag", "relationship": "application"},
                {"id": "ee5", "source": "gpt4", "target": "agents", "relationship": "advanced_concept"}
            ],
            "new_node_details": {}
        }

    def _get_mock_knowledge_gap(self) -> Dict[str, Any]:
        return {
            "known": ["Python", "NumPy"],
            "missing": ["Linear Algebra", "Probability", "Neural Networks", "Attention Mechanism", "Transformers"],
            "learning_path": ["Linear Algebra", "Probability", "Neural Networks", "Attention Mechanism", "Transformers"]
        }

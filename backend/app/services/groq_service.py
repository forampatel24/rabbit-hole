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

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    pass


class GroqService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        self.mock_mode = os.getenv("RABBITHOLE_MOCK", "false").lower() == "true"

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
        logger.debug(f"Prompt preview: {prompt[:200]}...")

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
            return self._get_mock_graph()

    def _get_mock_graph(self) -> Dict[str, Any]:
        return {
            "overview": {
                "topic": "Machine Learning",
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

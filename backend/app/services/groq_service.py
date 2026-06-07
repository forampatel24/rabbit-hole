"""
Groq AI service for knowledge generation
Handles communication with Groq API and JSON parsing
"""

import logging
import json
import os
import re
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)


class GroqService:
    """Service for communicating with Groq API"""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "mock_key_for_dev")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        self.is_mock = self.api_key == "mock_key_for_dev"

    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Send a prompt to Groq and get a response

        Args:
            prompt: The prompt to send to Groq

        Returns:
            Parsed JSON response from Groq
        """
        logger.info("Sending request to Groq API")
        logger.debug(f"Prompt: {prompt[:200]}...")

        if self.is_mock:
            logger.info("Running in mock mode - no actual API call")
            return self._get_mock_response(prompt)

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
            logger.debug(f"Raw response: {content[:200]}...")

            # Parse JSON from response
            parsed = self._extract_and_parse_json(content)
            logger.info("JSON parsing successful")
            return parsed

        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to communicate with Groq API: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Groq service: {str(e)}", exc_info=True)
            raise

    def _extract_and_parse_json(self, response_text: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from Groq response
        Handles markdown fences, trailing commas, and malformed JSON

        Args:
            response_text: Raw response from Groq

        Returns:
            Parsed JSON dictionary
        """
        logger.info("Attempting to extract JSON from response")

        # Try direct parse first
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.debug("Direct JSON parse failed, attempting cleanup")

        # Remove markdown code fences
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # Try parsing again
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.debug("After fence removal, still failing - trying largest JSON extraction")

        # Extract the largest JSON object
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            logger.debug("Found potential JSON object, attempting parse")

            # Try to fix trailing commas
            fixed_json = re.sub(r',(\s*[}\]])', r'\1', json_str)

            try:
                parsed = json.loads(fixed_json)
                logger.info("JSON parsing successful after cleanup")
                return parsed
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse even after cleanup: {str(e)}")

        logger.error("Unable to extract valid JSON from response")
        raise ValueError("Could not parse JSON from Groq response")

    def _get_mock_response(self, prompt: str) -> Dict[str, Any]:
        """
        Get a mock response for development/testing

        Args:
            prompt: The prompt (used to determine which mock to return)

        Returns:
            Mock JSON response with correct structure
        """
        logger.info("Generating mock response")
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
                {"id": "regression", "name": "Regression", "type": "core_concept", "description": "Predicting continuous values", "difficulty": "Intermediate", "importance_score": 8.0, "estimated_learning_time": "1-2 weeks", "prerequisites": ["supervised_learning"], "unlocks": ["linear_regression", "polynomial_regression"], "applications": ["Price Prediction", "Trend Analysis"], "why_it_matters": "Regression is fundamental to predictive modeling", "resources": {}, "depth": 3},
                {"id": "classification", "name": "Classification", "type": "core_concept", "description": "Predicting categories or classes", "difficulty": "Intermediate", "importance_score": 8.5, "estimated_learning_time": "1-2 weeks", "prerequisites": ["supervised_learning"], "unlocks": ["logistic_regression", "decision_trees"], "applications": ["Spam Detection", "Image Recognition"], "why_it_matters": "Classification is widely used in practice", "resources": {}, "depth": 3},
                {"id": "neural_networks", "name": "Neural Networks", "type": "advanced_concept", "description": "Interconnected networks inspired by biological neurons", "difficulty": "Advanced", "importance_score": 9.5, "estimated_learning_time": "3-4 weeks", "prerequisites": ["linear_algebra", "supervised_learning"], "unlocks": ["deep_learning", "cnn", "rnn"], "applications": ["Image Recognition", "NLP", "Time Series"], "why_it_matters": "Neural networks are the foundation of deep learning", "resources": {}, "depth": 2},
                {"id": "deep_learning", "name": "Deep Learning", "type": "advanced_concept", "description": "Neural networks with multiple layers", "difficulty": "Advanced", "importance_score": 9.0, "estimated_learning_time": "3-4 weeks", "prerequisites": ["neural_networks"], "unlocks": ["cnn", "rnn", "transformers"], "applications": ["AI Applications", "Computer Vision", "NLP"], "why_it_matters": "Deep learning powers modern AI", "resources": {}, "depth": 3},
                {"id": "cnn", "name": "Convolutional Neural Networks", "type": "advanced_concept", "description": "Neural networks optimized for image processing", "difficulty": "Advanced", "importance_score": 8.5, "estimated_learning_time": "2-3 weeks", "prerequisites": ["deep_learning"], "unlocks": ["computer_vision"], "applications": ["Image Recognition", "Object Detection"], "why_it_matters": "CNNs are essential for computer vision", "resources": {}, "depth": 4},
                {"id": "rnn", "name": "Recurrent Neural Networks", "type": "advanced_concept", "description": "Neural networks for sequential data", "difficulty": "Advanced", "importance_score": 8.0, "estimated_learning_time": "2-3 weeks", "prerequisites": ["deep_learning"], "unlocks": ["lstm", "nlp"], "applications": ["Time Series", "Language Modeling"], "why_it_matters": "RNNs handle sequential data effectively", "resources": {}, "depth": 4},
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
                {"id": "e9", "source": "supervised_learning", "target": "regression", "relationship": "core_concept"},
                {"id": "e10", "source": "supervised_learning", "target": "classification", "relationship": "core_concept"},
                {"id": "e11", "source": "supervised_learning", "target": "neural_networks", "relationship": "advanced_concept"},
                {"id": "e12", "source": "neural_networks", "target": "deep_learning", "relationship": "advanced_concept"},
                {"id": "e13", "source": "deep_learning", "target": "cnn", "relationship": "advanced_concept"},
                {"id": "e14", "source": "deep_learning", "target": "rnn", "relationship": "advanced_concept"},
                {"id": "e15", "source": "rnn", "target": "attention_mechanism", "relationship": "prerequisite"},
                {"id": "e16", "source": "attention_mechanism", "target": "transformers", "relationship": "prerequisite"},
                {"id": "e17", "source": "deep_learning", "target": "attention_mechanism", "relationship": "related_concept"},
                {"id": "e18", "source": "sklearn", "target": "supervised_learning", "relationship": "tool"},
                {"id": "e19", "source": "tensorflow", "target": "neural_networks", "relationship": "framework"}
            ]
        }


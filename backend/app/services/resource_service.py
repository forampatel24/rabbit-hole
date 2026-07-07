import asyncio
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.orm import Session

from ..models.resource_cache import ResourceCache
from .groq_service import GroqService

logger = logging.getLogger(__name__)

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class ResourceService:
    def __init__(self):
        load_dotenv(dotenv_path=_ENV_FILE, override=True)

        self.groq_service = GroqService()
        self.youtube_api_key = os.getenv("Youtube_API_KEY", "")
        self.serp_api_key = os.getenv("Serp_Api_KEY", "")
        self.openalex_api_key = os.getenv("OpenAlex_API_KEY", "")
        self.github_token = os.getenv("GitHub_API_KEY", "")

        logger.info("ResourceService initialized")

    async def get_resources(self, concept_name: str, db: Session) -> Dict[str, Any]:
        cached = db.query(ResourceCache).filter(
            ResourceCache.concept_name == concept_name
        ).first()

        if cached:
            age = datetime.utcnow() - cached.last_updated
            if age < timedelta(hours=24):
                logger.info(f"Cache hit for '{concept_name}'")
                return self._deserialize_cache(cached)
            logger.info(f"Cache expired for '{concept_name}', refreshing")

        logger.info(f"Fetching resources for '{concept_name}'")
        recommendations = await self._get_recommendations(concept_name)
        resources = await self._fetch_all_resources(recommendations)

        self._save_cache(db, concept_name, resources)
        return resources

    async def _get_recommendations(self, concept_name: str) -> Dict[str, Any]:
        prompt = (
            f"You are a learning resource recommender. "
            f"For the concept \"{concept_name}\", recommend the best learning resources.\n\n"
            f"Return a JSON object with EXACTLY this structure:\n"
            f"{{\n"
            f'  "youtube": ["title 1", "title 2", "title 3"],\n'
            f'  "coursera": "course name",\n'
            f'  "udemy": "course name",\n'
            f'  "papers": ["paper title 1", "paper title 2"],\n'
            f'  "github": ["repo name 1", "repo name 2"]\n'
            f"}}\n\n"
            f"Rules:\n"
            f"- youtube: Recommend exactly 3 educational YouTube videos or playlists. "
            f"Prefer channels like 3Blue1Brown, Andrej Karpathy, StatQuest, freeCodeCamp, DeepLearningAI.\n"
            f"- coursera: Recommend exactly 1 Coursera course that best covers this concept.\n"
            f"- udemy: Recommend exactly 1 Udemy course that best covers this concept.\n"
            f"- papers: Recommend exactly 2 important research papers related to this concept.\n"
            f"- github: Recommend exactly 2 GitHub repositories (format \"owner/repo\"). "
            f"Prefer official repos like tensorflow/tensorflow, huggingface/transformers, facebookresearch/..., fastapi/fastapi.\n\n"
            f"Return ONLY valid JSON. No explanations. No markdown. No code fences."
        )

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.groq_service.generate, prompt)
            if isinstance(result, dict) and ("youtube" in result or "coursera" in result):
                return result
            logger.warning(f"Groq returned unexpected format for '{concept_name}', using fallback")
        except Exception as e:
            logger.warning(f"Groq recommendation failed for '{concept_name}': {e}")

        return {
            "youtube": [f"{concept_name} tutorial", f"{concept_name} explained", f"Learn {concept_name}"],
            "coursera": f"{concept_name} course",
            "udemy": f"{concept_name} course",
            "papers": [f"{concept_name}", f"{concept_name} survey"],
            "github": [f"topic/{concept_name.lower().replace(' ', '-')}", f"awesome-{concept_name.lower().replace(' ', '-')}"],
        }

    async def _fetch_all_resources(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=20) as client:
            youtube_task = self._fetch_youtube(client, recommendations.get("youtube", []))
            courses_task = self._fetch_courses(client, recommendations)
            papers_task = self._fetch_papers(client, recommendations.get("papers", []))
            github_task = self._fetch_github(client, recommendations.get("github", []))

            results = await asyncio.gather(
                youtube_task, courses_task, papers_task, github_task,
                return_exceptions=True
            )

        resources = {
            "youtube": self._dedup(self._safe_result(results, 0), "url"),
            "courses": self._safe_result(results, 1),
            "papers": self._dedup(self._safe_result(results, 2), "doi"),
            "github": self._dedup(self._safe_result(results, 3), "repo_name"),
        }
        return resources

    def _dedup(self, items: list, key: str) -> list:
        seen = set()
        unique = []
        for item in items:
            val = item.get(key, "")
            if val and val not in seen:
                seen.add(val)
                unique.append(item)
            elif not val and id(item) not in seen:
                seen.add(id(item))
                unique.append(item)
        return unique

    def _safe_result(self, results: List, index: int) -> list:
        if index < len(results) and not isinstance(results[index], Exception):
            return results[index]
        if index < len(results):
            logger.warning(f"Resource fetch failed for index {index}: {results[index]}")
        return []

    async def _fetch_youtube(self, client: httpx.AsyncClient, titles: List[str]) -> list:
        results = []
        for title in titles[:3]:
            try:
                search_url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": title,
                    "key": self.youtube_api_key,
                    "maxResults": 1,
                    "type": "video",
                    "videoEmbeddable": "true",
                    "relevanceLanguage": "en",
                }
                search_resp = await client.get(search_url, params=params)
                search_resp.raise_for_status()
                search_data = search_resp.json()

                items = search_data.get("items", [])
                if not items:
                    continue

                item = items[0]
                video_id = item["id"]["videoId"]

                details_url = "https://www.googleapis.com/youtube/v3/videos"
                details_params = {
                    "part": "contentDetails",
                    "id": video_id,
                    "key": self.youtube_api_key,
                }
                details_resp = await client.get(details_url, params=details_params)
                duration = ""
                if details_resp.status_code == 200:
                    details_data = details_resp.json()
                    items_d = details_data.get("items", [])
                    if items_d:
                        raw_duration = items_d[0]["contentDetails"]["duration"]
                        duration = self._parse_duration(raw_duration)

                results.append({
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "duration": duration,
                })

                if len(results) >= 3:
                    break

            except Exception as e:
                logger.warning(f"YouTube fetch failed for '{title}': {e}")
                continue

        return results

    def _parse_duration(self, iso_duration: str) -> str:
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, iso_duration)
        if not match:
            return iso_duration
        parts = []
        if match.group(1):
            parts.append(f"{int(match.group(1))}h")
        if match.group(2):
            parts.append(f"{int(match.group(2))}m")
        if match.group(3):
            parts.append(f"{int(match.group(3))}s")
        return " ".join(parts) if parts else iso_duration

    async def _fetch_courses(self, client: httpx.AsyncClient, recommendations: Dict[str, Any]) -> list:
        results = []
        coursera_name = recommendations.get("coursera", "")
        udemy_name = recommendations.get("udemy", "")

        if coursera_name:
            try:
                course = await self._search_serp_course(client, coursera_name, "coursera.org")
                if course:
                    course["provider"] = "Coursera"
                    results.append(course)
            except Exception as e:
                logger.warning(f"Coursera search failed: {e}")

        if udemy_name:
            try:
                course = await self._search_serp_course(client, udemy_name, "udemy.com")
                if course:
                    course["provider"] = "Udemy"
                    results.append(course)
            except Exception as e:
                logger.warning(f"Udemy search failed: {e}")

        return results

    async def _search_serp_course(self, client: httpx.AsyncClient, course_name: str, site: str) -> Optional[Dict]:
        query = f"site:{site} {course_name}"
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": self.serp_api_key,
            "engine": "google",
            "num": 3,
        }

        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        organic = data.get("organic_results", [])
        for result in organic:
            title = result.get("title", "")
            link = result.get("link", "")
            thumbnail = None
            if "thumbnail" in result:
                thumbnail = result["thumbnail"]
            elif "favicon" in result:
                thumbnail = result["favicon"]

            if title and link:
                return {
                    "title": title,
                    "url": link,
                    "thumbnail": thumbnail or "",
                }

        return None

    async def _fetch_papers(self, client: httpx.AsyncClient, titles: List[str]) -> list:
        results = []
        for title in titles[:2]:
            try:
                query = quote(title)
                url = f"https://api.openalex.org/works?search={query}&per_page=1"
                headers = {}
                if self.openalex_api_key:
                    headers["api_key"] = self.openalex_api_key

                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                items = data.get("results", [])
                if not items:
                    continue

                work = items[0]
                authors = []
                for auth in work.get("authorships", []):
                    author_name = auth.get("author", {}).get("display_name", "")
                    if author_name:
                        authors.append(author_name)

                doi = work.get("doi", "")
                doi_id = doi.replace("https://doi.org/", "") if doi else ""

                pdf_url = ""
                for loc in work.get("locations", []):
                    if loc.get("is_accepted") or loc.get("pdf_url"):
                        pdf_url = loc.get("pdf_url", "")
                        if pdf_url:
                            break
                if not pdf_url:
                    for loc in work.get("locations", []):
                        landing = loc.get("landing_page_url", "")
                        if landing:
                            pdf_url = landing
                            break

                results.append({
                    "title": work.get("title", title),
                    "authors": authors[:5],
                    "year": work.get("publication_year"),
                    "citation_count": work.get("cited_by_count", 0),
                    "doi": doi_id,
                    "openalex_url": f"https://openalex.org/{work.get('id', '').split('/')[-1]}" if work.get("id") else "",
                    "pdf_url": pdf_url,
                })

            except Exception as e:
                logger.warning(f"OpenAlex fetch failed for '{title}': {e}")
                continue

        return results

    async def _fetch_github(self, client: httpx.AsyncClient, repo_names: List[str]) -> list:
        results = []
        for repo in repo_names[:2]:
            try:
                query = quote(repo)
                url = f"https://api.github.com/search/repositories?q={query}&per_page=1"
                headers = {}
                if self.github_token:
                    headers["Authorization"] = f"token {self.github_token}"
                headers["Accept"] = "application/vnd.github.v3+json"

                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                items = data.get("items", [])
                if not items:
                    continue

                item = items[0]
                results.append({
                    "repo_name": item.get("full_name", repo),
                    "description": item.get("description") or "",
                    "stars": item.get("stargazers_count", 0),
                    "language": item.get("language") or "",
                    "url": item.get("html_url", f"https://github.com/{repo}"),
                })

            except Exception as e:
                logger.warning(f"GitHub fetch failed for '{repo}': {e}")
                continue

        return results

    def _save_cache(self, db: Session, concept_name: str, resources: Dict[str, Any]):
        try:
            existing = db.query(ResourceCache).filter(
                ResourceCache.concept_name == concept_name
            ).first()

            if existing:
                existing.youtube_json = json.dumps(resources.get("youtube", []))
                existing.courses_json = json.dumps(resources.get("courses", []))
                existing.papers_json = json.dumps(resources.get("papers", []))
                existing.github_json = json.dumps(resources.get("github", []))
                existing.last_updated = datetime.utcnow()
            else:
                cache_entry = ResourceCache(
                    concept_name=concept_name,
                    youtube_json=json.dumps(resources.get("youtube", [])),
                    courses_json=json.dumps(resources.get("courses", [])),
                    papers_json=json.dumps(resources.get("papers", [])),
                    github_json=json.dumps(resources.get("github", [])),
                    last_updated=datetime.utcnow(),
                )
                db.add(cache_entry)

            db.commit()
            logger.info(f"Cached resources for '{concept_name}'")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cache resources for '{concept_name}': {e}")

    def _deserialize_cache(self, cached: ResourceCache) -> Dict[str, Any]:
        return {
            "youtube": json.loads(cached.youtube_json) if cached.youtube_json else [],
            "courses": json.loads(cached.courses_json) if cached.courses_json else [],
            "papers": json.loads(cached.papers_json) if cached.papers_json else [],
            "github": json.loads(cached.github_json) if cached.github_json else [],
        }

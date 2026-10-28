import asyncio
import json
import logging
import re
import time
from typing import Dict, List, Set, Any, Optional
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class CrawlPageResult:
    def __init__(self, url: str):
        self.url = url
        self.status_code: int = 0
        self.response_time_ms: float = 0.0
        self.title: Optional[str] = None
        self.meta_description: Optional[str] = None
        self.robots_meta: Optional[str] = None
        self.canonical_url: Optional[str] = None
        self.h1_tags: List[str] = []
        self.h2_tags: List[str] = []
        self.images_without_alt: List[str] = []
        self.internal_links: Set[str] = set()
        self.external_links: Set[str] = set()
        self.has_json_ld: bool = False
        self.json_ld_valid: bool = False
        self.og_title: Optional[str] = None
        self.og_description: Optional[str] = None
        self.og_image: Optional[str] = None
        self.is_https: bool = url.startswith("https://")
        self.issues: List[Dict[str, Any]] = []

class SEOCrawlerService:
    def __init__(self, base_url: str, max_pages: int = 30, timeout: int = 4):
        self.base_url = base_url.rstrip("/")
        parsed = urlparse(self.base_url)
        self.base_domain = parsed.netloc
        self.scheme = parsed.scheme or "http"
        self.max_pages = max_pages
        self.timeout = timeout
        self.visited_urls: Set[str] = set()
        self.crawled_results: List[CrawlPageResult] = []

    async def crawl_site(self) -> Dict[str, Any]:
        """Crawl website starting from canonical base_url up to max_pages."""
        to_visit: List[str] = [self.base_url]
        client_headers = {
            "User-Agent": "SEOPilotAI-Crawler/1.0 (+https://github.com/seopilot-ai/bot)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        # Check robots.txt and sitemap.xml first
        robots_txt_status, sitemap_status = await self._check_site_assets(client_headers)

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers=client_headers) as client:
            while to_visit and len(self.visited_urls) < self.max_pages:
                current_url = to_visit.pop(0)
                norm_url = self._normalize_url(current_url)
                
                if norm_url in self.visited_urls:
                    continue
                self.visited_urls.add(norm_url)

                page_res = await self._crawl_page(client, norm_url)
                self.crawled_results.append(page_res)

                # Queue newly found internal links within the same domain
                for link in page_res.internal_links:
                    norm_link = self._normalize_url(link)
                    if norm_link not in self.visited_urls and norm_link not in to_visit:
                        if len(to_visit) + len(self.visited_urls) < self.max_pages * 2:
                            to_visit.append(norm_link)

        # Aggregate issues and compute health score
        return self._generate_audit_summary(robots_txt_status, sitemap_status)

    async def _check_site_assets(self, headers: Dict[str, str]) -> tuple[bool, bool]:
        """Verify robots.txt and sitemap.xml presence."""
        robots_url = f"{self.scheme}://{self.base_domain}/robots.txt"
        sitemap_url = f"{self.scheme}://{self.base_domain}/sitemap.xml"
        robots_ok = False
        sitemap_ok = False

        async with httpx.AsyncClient(timeout=5, follow_redirects=True, headers=headers) as client:
            try:
                res_robots = await client.get(robots_url)
                robots_ok = (res_robots.status_code == 200)
            except Exception:
                robots_ok = False

            try:
                res_sitemap = await client.get(sitemap_url)
                sitemap_ok = (res_sitemap.status_code == 200)
            except Exception:
                sitemap_ok = False

        return robots_ok, sitemap_ok

    async def _crawl_page(self, client: httpx.AsyncClient, url: str) -> CrawlPageResult:
        result = CrawlPageResult(url)
        start_time = time.time()

        try:
            resp = await client.get(url)
            result.response_time_ms = round((time.time() - start_time) * 1000, 2)
            result.status_code = resp.status_code

            if not result.is_https:
                result.issues.append({
                    "category": "security",
                    "severity": "high",
                    "title": "Insecure HTTP Protocol",
                    "url_or_file": url,
                    "evidence": f"URL loaded over HTTP instead of HTTPS",
                    "root_cause_hypothesis": "Missing SSL/TLS redirect enforcement on server.",
                    "recommended_fix": "Enforce HTTP to HTTPS 301 redirection and update canonical URLs."
                })

            if resp.status_code >= 400:
                result.issues.append({
                    "category": "technical",
                    "severity": "critical" if resp.status_code == 404 else "high",
                    "title": f"HTTP Error Status {resp.status_code}",
                    "url_or_file": url,
                    "evidence": f"Server responded with HTTP {resp.status_code}",
                    "root_cause_hypothesis": "Broken link or deleted resource without proper redirect.",
                    "recommended_fix": "Fix internal references or implement a 301 redirect to relevant page."
                })
                return result

            content_type = resp.headers.get("content-type", "")
            if "text/html" not in content_type:
                return result

            # Parse HTML
            soup = BeautifulSoup(resp.text, "html.parser")
            self._analyze_html_page(soup, result)

        except httpx.RequestError as exc:
            result.status_code = 0
            result.issues.append({
                "category": "technical",
                "severity": "critical",
                "title": "Failed to Fetch URL (Connection Error)",
                "url_or_file": url,
                "evidence": str(exc),
                "root_cause_hypothesis": "Host unreachable, DNS failure, or port closed.",
                "recommended_fix": "Verify domain availability and network configurations."
            })

        return result

    def _analyze_html_page(self, soup: BeautifulSoup, res: CrawlPageResult):
        # 1. Title tag analysis
        title_tag = soup.find("title")
        if not title_tag or not title_tag.text.strip():
            res.issues.append({
                "category": "meta",
                "severity": "critical",
                "title": "Missing Page Title",
                "url_or_file": res.url,
                "evidence": "<title> tag is absent or completely empty",
                "root_cause_hypothesis": "Page template does not supply a title variable.",
                "recommended_fix": "Add a descriptive, keyword-rich <title> tag between 30 and 60 characters."
            })
        else:
            res.title = title_tag.text.strip()
            title_len = len(res.title)
            if title_len < 30:
                res.issues.append({
                    "category": "meta",
                    "severity": "medium",
                    "title": "Page Title Too Short",
                    "url_or_file": res.url,
                    "evidence": f"Title '{res.title}' is {title_len} characters (< 30 characters recommended)",
                    "root_cause_hypothesis": "Title lacks brand or keyword context.",
                    "recommended_fix": "Expand title with brand name or primary search intent keywords."
                })
            elif title_len > 60:
                res.issues.append({
                    "category": "meta",
                    "severity": "low",
                    "title": "Page Title Exceeds Recommended Length",
                    "url_or_file": res.url,
                    "evidence": f"Title '{res.title}' is {title_len} characters (> 60 chars may truncate in SERPs)",
                    "root_cause_hypothesis": "Overly verbose title.",
                    "recommended_fix": "Shorten title to under 60 characters to avoid SERP truncation."
                })

        # 2. Meta description analysis
        desc_meta = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        if not desc_meta or not desc_meta.get("content", "").strip():
            res.issues.append({
                "category": "meta",
                "severity": "high",
                "title": "Missing Meta Description",
                "url_or_file": res.url,
                "evidence": "No <meta name='description'> tag found",
                "root_cause_hypothesis": "SEO metadata component is missing description prop.",
                "recommended_fix": "Add a compelling meta description summarizing the page content (120-155 characters)."
            })
        else:
            res.meta_description = desc_meta.get("content", "").strip()
            desc_len = len(res.meta_description)
            if desc_len < 60:
                res.issues.append({
                    "category": "meta",
                    "severity": "low",
                    "title": "Meta Description Too Short",
                    "url_or_file": res.url,
                    "evidence": f"Meta description is only {desc_len} characters.",
                    "root_cause_hypothesis": "Incomplete summary in metadata.",
                    "recommended_fix": "Expand meta description to 120-155 characters with targeted call-to-action."
                })

        # 3. Canonical tag analysis
        canonical_link = soup.find("link", attrs={"rel": "canonical"})
        if not canonical_link or not canonical_link.get("href"):
            res.issues.append({
                "category": "indexing",
                "severity": "medium",
                "title": "Missing Canonical Tag",
                "url_or_file": res.url,
                "evidence": "No <link rel='canonical'> tag present",
                "root_cause_hypothesis": "Template does not specify canonical self-referencing link.",
                "recommended_fix": f"Add <link rel='canonical' href='{res.url}' /> to prevent duplicate content ambiguity."
            })
        else:
            res.canonical_url = canonical_link.get("href")

        # 4. Robots meta tag
        robots_meta = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
        if robots_meta and robots_meta.get("content"):
            res.robots_meta = robots_meta.get("content").strip()
            if "noindex" in res.robots_meta.lower():
                res.issues.append({
                    "category": "indexing",
                    "severity": "high",
                    "title": "Page Marked Noindex",
                    "url_or_file": res.url,
                    "evidence": f"Robots meta directive contains: {res.robots_meta}",
                    "root_cause_hypothesis": "Accidentally left noindex from staging/development.",
                    "recommended_fix": "Remove 'noindex' if this page is intended for organic search indexing."
                })

        # 5. Heading Structure
        h1s = [h.text.strip() for h in soup.find_all("h1") if h.text.strip()]
        res.h1_tags = h1s
        if len(h1s) == 0:
            res.issues.append({
                "category": "content",
                "severity": "high",
                "title": "Missing H1 Heading",
                "url_or_file": res.url,
                "evidence": "No <h1> element detected on the page",
                "root_cause_hypothesis": "Hero component uses generic <div> or <h2> instead of semantic <h1>.",
                "recommended_fix": "Wrap main page title in a single semantic <h1> tag."
            })
        elif len(h1s) > 1:
            res.issues.append({
                "category": "content",
                "severity": "low",
                "title": "Multiple H1 Headings Found",
                "url_or_file": res.url,
                "evidence": f"Found {len(h1s)} <h1> elements: {h1s[:3]}",
                "root_cause_hypothesis": "Sub-sections incorrectly styled with <h1>.",
                "recommended_fix": "Consolidate into one primary <h1> and use <h2>/<h3> for subsections."
            })

        # 6. Images Alt Text
        imgs = soup.find_all("img")
        for img in imgs:
            src = img.get("src", "unknown")
            alt = img.get("alt")
            if alt is None or alt.strip() == "":
                res.images_without_alt.append(src)

        if res.images_without_alt:
            res.issues.append({
                "category": "content",
                "severity": "medium",
                "title": f"Images Missing Alt Attribute ({len(res.images_without_alt)} images)",
                "url_or_file": res.url,
                "evidence": f"Images lacking alt attribute: {res.images_without_alt[:3]}",
                "root_cause_hypothesis": "Images added without descriptive alt attributes.",
                "recommended_fix": "Add meaningful descriptive alt tags to all informational images."
            })

        # 7. Schema / JSON-LD Validation
        scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
        if scripts:
            res.has_json_ld = True
            for script in scripts:
                try:
                    if script.string:
                        json.loads(script.string)
                        res.json_ld_valid = True
                except Exception as err:
                    res.issues.append({
                        "category": "technical",
                        "severity": "high",
                        "title": "Invalid JSON-LD Structured Data",
                        "url_or_file": res.url,
                        "evidence": f"JSON syntax error in structured data: {str(err)}",
                        "root_cause_hypothesis": "Malformed JSON template or unescaped quotes in schema.",
                        "recommended_fix": "Fix JSON syntax in structured data block to adhere to Schema.org standards."
                    })
        else:
            res.issues.append({
                "category": "technical",
                "severity": "low",
                "title": "Missing Structured Data (Schema.org)",
                "url_or_file": res.url,
                "evidence": "No application/ld+json script tags found",
                "root_cause_hypothesis": "Structured data schema not yet implemented.",
                "recommended_fix": "Add JSON-LD schema (WebSite, WebPage, Article, or Organization)."
            })

        # 8. OpenGraph / Social Metadata
        og_t = soup.find("meta", attrs={"property": "og:title"})
        og_d = soup.find("meta", attrs={"property": "og:description"})
        og_i = soup.find("meta", attrs={"property": "og:image"})
        res.og_title = og_t.get("content") if og_t else None
        res.og_description = og_d.get("content") if og_d else None
        res.og_image = og_i.get("content") if og_i else None

        if not og_t or not og_i:
            res.issues.append({
                "category": "meta",
                "severity": "low",
                "title": "Incomplete OpenGraph Tags",
                "url_or_file": res.url,
                "evidence": "Missing og:title or og:image tags",
                "root_cause_hypothesis": "Social sharing metadata neglected in document head.",
                "recommended_fix": "Add complete OpenGraph tags (og:title, og:description, og:image, og:url)."
            })

        # 9. Extract Links
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            abs_url = urljoin(res.url, href)
            parsed_abs = urlparse(abs_url)
            if parsed_abs.netloc == self.base_domain:
                res.internal_links.add(abs_url)
            elif parsed_abs.netloc:
                res.external_links.add(abs_url)

    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path or "/"
        if path.endswith("/") and len(path) > 1:
            path = path[:-1]
        return f"{parsed.scheme}://{parsed.netloc}{path}"

    def _generate_audit_summary(self, robots_txt_ok: bool, sitemap_ok: bool) -> Dict[str, Any]:
        all_issues: List[Dict[str, Any]] = []

        if not robots_txt_ok:
            all_issues.append({
                "category": "technical",
                "severity": "high",
                "title": "Missing or Inaccessible robots.txt",
                "url_or_file": f"{self.scheme}://{self.base_domain}/robots.txt",
                "evidence": "HTTP request to /robots.txt failed or returned non-200 status",
                "root_cause_hypothesis": "robots.txt file was not published to the public root directory.",
                "recommended_fix": "Create a robots.txt file at webroot specifying crawl rules and sitemap location."
            })

        if not sitemap_ok:
            all_issues.append({
                "category": "indexing",
                "severity": "high",
                "title": "Missing or Inaccessible sitemap.xml",
                "url_or_file": f"{self.scheme}://{self.base_domain}/sitemap.xml",
                "evidence": "HTTP request to /sitemap.xml returned non-200 status",
                "root_cause_hypothesis": "XML sitemap generator is missing or not deployed.",
                "recommended_fix": "Generate and host an XML sitemap at /sitemap.xml and submit it to Search Console."
            })

        crit_count = 0
        high_count = 0
        med_count = 0
        low_count = 0

        for r in self.crawled_results:
            all_issues.extend(r.issues)

        for iss in all_issues:
            sev = iss.get("severity")
            if sev == "critical":
                crit_count += 1
            elif sev == "high":
                high_count += 1
            elif sev == "medium":
                med_count += 1
            elif sev == "low":
                low_count += 1

        # Calculate SEO health score
        # Base 100 - (critical * 15 + high * 8 + med * 3 + low * 1)
        deduction = (crit_count * 15) + (high_count * 8) + (med_count * 3) + (low_count * 1)
        score = max(5.0, round(100.0 - deduction, 1))

        return {
            "health_score": score,
            "pages_crawled": len(self.crawled_results),
            "total_issues": len(all_issues),
            "critical_issues": crit_count,
            "high_issues": high_count,
            "medium_issues": med_count,
            "low_issues": low_count,
            "issues": all_issues,
            "crawled_urls": [r.url for r in self.crawled_results]
        }

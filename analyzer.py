import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteRater:
    def __init__(self, timeout: int = 10, max_workers: int = 5):
        self.timeout = timeout
        self.max_workers = max_workers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def analyze_websites(self, urls: List[str]) -> Dict:
        """
        Analyze multiple websites concurrently and generate a comprehensive report
        """
        logger.info(f"Starting analysis of {len(urls)} websites")
        start_time = time.time()
        
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.analyze_website, url): url for url in urls}
            for future in future_to_url:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing {future_to_url[future]}: {str(e)}")
                    results.append({
                        'success': False,
                        'url': future_to_url[future],
                        'error': str(e)
                    })

        successful_results = [r for r in results if r['success']]
        
        # Calculate averages
        average_scores = {}
        if successful_results:
            score_keys = ['performance_score', 'design_score', 'seo_score', 'accessibility_score', 'overall_score']
            average_scores = {
                key: round(sum(r['scores'][key] for r in successful_results) / len(successful_results), 2)
                for key in score_keys
            }

        # Generate report
        report_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_sites': len(urls),
            'successful_analyses': len(successful_results),
            'analysis_time': f"{time.time() - start_time:.2f} seconds",
            'average_scores': average_scores,
            'detailed_results': results,
            'top_performers': self._get_top_performers(results),
            'needs_improvement': self._get_needs_improvement(results)
        }
        
        logger.info(f"Analysis completed in {report_data['analysis_time']}")
        return report_data

    def analyze_website(self, url: str) -> Dict:
        """
        Analyzes a single website with enhanced metrics
        """
        try:
            logger.info(f"Analyzing website: {url}")
            
            # Normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            start_time = time.time()
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            load_time = time.time() - start_time
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Collect metrics
            performance_metrics = self._check_performance(response, load_time)
            design_metrics = self._analyze_design(soup)
            seo_metrics = self._check_seo_basics(soup)
            accessibility_metrics = self._check_accessibility(soup)
            
            # Calculate scores
            scores = {
                'performance_score': round(sum(performance_metrics.values()) / len(performance_metrics), 2),
                'design_score': round(sum(design_metrics.values()) / len(design_metrics), 2),
                'seo_score': round(sum(seo_metrics.values()) / len(seo_metrics), 2),
                'accessibility_score': round(sum(accessibility_metrics.values()) / len(accessibility_metrics), 2)
            }
            
            # Calculate overall score
            scores['overall_score'] = round(sum(scores.values()) / len(scores), 2)
            
            return {
                'success': True,
                'url': url,
                'scores': scores,
                'metrics': {
                    'performance': performance_metrics,
                    'design': design_metrics,
                    'seo': seo_metrics,
                    'accessibility': accessibility_metrics
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }

    def _check_performance(self, response, load_time: float) -> Dict:
        return {
            'load_time': self._rate_metric(load_time, [1, 2, 3, 4, 5]),
            'response_size': self._rate_metric(len(response.content) / 1024 / 1024, [1, 2, 5, 10, 20], reverse=True),
            'ttfb': self._rate_metric(response.elapsed.total_seconds(), [0.1, 0.3, 0.5, 0.8, 1], reverse=True),
            'compression': 10 if 'gzip' in response.headers.get('Content-Encoding', '') else 0
        }

    def _analyze_design(self, soup: BeautifulSoup) -> Dict:
        return {
            'color_contrast': self._analyze_color_contrast(soup),
            'typography': self._analyze_typography(soup),
            'layout_structure': self._analyze_layout(soup),
            'responsive_design': self._check_responsive_design(soup),
            'visual_hierarchy': self._analyze_visual_hierarchy(soup)
        }

    def _check_seo_basics(self, soup: BeautifulSoup) -> Dict:
        return {
            'title': 10 if soup.title else 0,
            'meta_description': 10 if soup.find('meta', {'name': 'description'}) else 0,
            'headings': self._analyze_headings(soup),
            'img_alt': self._check_img_alt(soup),
            'canonical': 10 if soup.find('link', {'rel': 'canonical'}) else 0
        }

    def _check_accessibility(self, soup: BeautifulSoup) -> Dict:
        return {
            'lang_attribute': 10 if soup.html.get('lang') else 0,
            'aria_landmarks': self._check_aria_landmarks(soup),
            'form_labels': self._check_form_labels(soup),
            'alt_texts': self._check_img_alt(soup),
            'heading_structure': self._analyze_headings(soup)
        }

    def _analyze_color_contrast(self, soup) -> float:
        score = 0
        if soup.find_all(['style', 'link']):
            score += 5
        if 'prefers-color-scheme' in str(soup):
            score += 5
        return score

    def _analyze_typography(self, soup) -> float:
        score = 0
        fonts = set()
        for elem in soup.find_all(['style', 'link']):
            if 'font-family' in str(elem):
                fonts.add(str(elem))
        score += min(len(fonts) * 2, 5)
        if soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            score += 5
        return score

    def _analyze_layout(self, soup) -> float:
        score = 0
        semantic_elements = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
        for element in semantic_elements:
            if soup.find(element):
                score += 1.5
        return min(score, 10)

    def _check_responsive_design(self, soup) -> float:
        score = 0
        if soup.find('meta', {'name': 'viewport'}):
            score += 4
        if '@media' in str(soup):
            score += 3
        if soup.find_all(['picture', 'source']):
            score += 3
        return score

    def _analyze_visual_hierarchy(self, soup) -> float:
        score = 0
        if soup.find('h1'):
            score += 3
        if soup.find_all(['ul', 'ol']):
            score += 2
        if soup.find_all(['strong', 'em']):
            score += 2
        if soup.find_all(['blockquote', 'figure']):
            score += 3
        return score

    def _analyze_headings(self, soup) -> float:
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if not headings:
            return 0
        return min(len(headings) * 2, 10)

    def _check_img_alt(self, soup) -> float:
        images = soup.find_all('img')
        if not images:
            return 10
        images_with_alt = [img for img in images if img.get('alt')]
        return round((len(images_with_alt) / len(images)) * 10, 2)

    def _check_aria_landmarks(self, soup) -> float:
        landmarks = soup.find_all(role=True)
        return min(len(landmarks) * 2, 10)

    def _check_form_labels(self, soup) -> float:
        forms = soup.find_all('form')
        if not forms:
            return 10
        score = 0
        for form in forms:
            inputs = form.find_all(['input', 'select', 'textarea'])
            labels = form.find_all('label')
            if inputs and len(inputs) <= len(labels):
                score += 5
        return min(score, 10)

    def _rate_metric(self, value: float, thresholds: List[float], reverse: bool = False) -> float:
        for i, threshold in enumerate(thresholds):
            if reverse:
                if value <= threshold:
                    return 10 - (i * 2)
            else:
                if value <= threshold:
                    return (i + 1) * 2
        return 0 if reverse else 10

    def _get_top_performers(self, results: List[Dict], threshold: float = 8.0) -> List[Dict]:
        return [
            r for r in results 
            if r['success'] and r['scores']['overall_score'] >= threshold
        ]

    def _get_needs_improvement(self, results: List[Dict], threshold: float = 5.0) -> List[Dict]:
        return [
            r for r in results 
            if r['success'] and r['scores']['overall_score'] <= threshold
        ]
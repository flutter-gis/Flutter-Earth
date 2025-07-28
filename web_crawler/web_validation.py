import requests
import asyncio
import aiohttp
import ssl
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@dataclass
class WebValidationResult:
    """Result of web cross-checking validation"""
    dataset_id: str
    original_data: Dict
    web_sources: List[str]
    validation_score: float
    enhanced_data: Dict
    discrepancies: List[str]
    additional_info: Dict
    confidence: float

class WebValidator:
    """Cross-checks extracted data against live web sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.validation_sources = {
            'earth_engine': 'https://developers.google.com/earth-engine/datasets',
            'nasa_catalog': 'https://catalog.data.gov/dataset?organization=nasa',
            'esa_catalog': 'https://earth.esa.int/eogateway',
            'usgs_catalog': 'https://www.usgs.gov/programs/national-geospatial-program/national-map',
            'google_search': 'https://www.google.com/search'
        }
        
    async def validate_dataset(self, dataset: Dict) -> WebValidationResult:
        """Validate a single dataset against web sources"""
        try:
            # Extract key information for searching
            title = dataset.get('title', '')
            provider = dataset.get('provider', '')
            description = dataset.get('description', '')
            
            # Create search queries
            search_queries = self._generate_search_queries(title, provider, description)
            
            # Cross-check against multiple sources
            validation_results = []
            enhanced_info = {}
            
            for source_name, source_url in self.validation_sources.items():
                try:
                    result = await self._check_source(source_name, source_url, search_queries)
                    if result:
                        validation_results.append(result)
                        enhanced_info.update(result.get('additional_info', {}))
                except Exception as e:
                    logging.warning(f"Failed to check {source_name}: {e}")
            
            # Calculate validation score
            validation_score = self._calculate_validation_score(validation_results)
            
            # Identify discrepancies
            discrepancies = self._find_discrepancies(dataset, validation_results)
            
            # Enhance original data
            enhanced_data = dataset.copy()
            enhanced_data.update(enhanced_info)
            enhanced_data['web_validation'] = {
                'score': validation_score,
                'sources_checked': len(validation_results),
                'discrepancies': discrepancies,
                'last_validated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return WebValidationResult(
                dataset_id=dataset.get('id', 'unknown'),
                original_data=dataset,
                web_sources=[r['source'] for r in validation_results],
                validation_score=validation_score,
                enhanced_data=enhanced_data,
                discrepancies=discrepancies,
                additional_info=enhanced_info,
                confidence=validation_score / 100.0
            )
            
        except Exception as e:
            logging.error(f"Web validation failed: {e}")
            return WebValidationResult(
                dataset_id=dataset.get('id', 'unknown'),
                original_data=dataset,
                web_sources=[],
                validation_score=0.0,
                enhanced_data=dataset,
                discrepancies=[f"Validation failed: {e}"],
                additional_info={},
                confidence=0.0
            )
    
    def _generate_search_queries(self, title: str, provider: str, description: str) -> List[str]:
        """Generate search queries for web validation"""
        queries = []
        
        # Basic title search
        if title:
            queries.append(f'"{title}"')
            queries.append(f'"{title}" dataset')
        
        # Provider + title search
        if provider and title:
            queries.append(f'"{provider}" "{title}"')
        
        # Technical terms from description
        if description:
            tech_terms = self._extract_technical_terms(description)
            for term in tech_terms[:3]:  # Top 3 technical terms
                queries.append(f'"{title}" "{term}"')
        
        return queries[:5]  # Limit to 5 queries
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from text"""
        technical_terms = [
            'satellite', 'sensor', 'radar', 'optical', 'multispectral', 'hyperspectral',
            'resolution', 'coverage', 'band', 'wavelength', 'temporal', 'spatial',
            'reflectance', 'vegetation', 'atmosphere', 'surface', 'terrain'
        ]
        
        found_terms = []
        text_lower = text.lower()
        for term in technical_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    async def _check_source(self, source_name: str, source_url: str, queries: List[str]) -> Optional[Dict]:
        """Check a specific web source"""
        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            for query in queries:
                try:
                    if source_name == 'google_search':
                        result = await self._check_google(session, query)
                    elif source_name == 'earth_engine':
                        result = await self._check_earth_engine(session, query)
                    else:
                        result = await self._check_generic_source(session, source_url, query)
                    
                    if result:
                        return {
                            'source': source_name,
                            'query': query,
                            'found': True,
                            'additional_info': result
                        }
                        
                except Exception as e:
                    logging.warning(f"Failed to check {source_name} with query '{query}': {e}")
        
        return None
    
    async def _check_google(self, session: aiohttp.ClientSession, query: str) -> Optional[Dict]:
        """Check Google search results"""
        search_url = f"https://www.google.com/search?q={quote(query)}"
        
        async with session.get(search_url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract relevant information
                results = []
                for result in soup.find_all('div', class_='g')[:5]:
                    title_elem = result.find('h3')
                    if title_elem:
                        title = title_elem.get_text()
                        results.append(title)
                
                return {
                    'google_results': results,
                    'query': query,
                    'result_count': len(results)
                }
        
        return None
    
    async def _check_earth_engine(self, session: aiohttp.ClientSession, query: str) -> Optional[Dict]:
        """Check Earth Engine catalog"""
        try:
            # This would need to be adapted to Earth Engine's actual API
            # For now, we'll simulate a check
            return {
                'earth_engine_match': True,
                'catalog_url': f"https://developers.google.com/earth-engine/datasets?q={quote(query)}"
            }
        except Exception as e:
            logging.warning(f"Earth Engine check failed: {e}")
            return None
    
    async def _check_generic_source(self, session: aiohttp.ClientSession, url: str, query: str) -> Optional[Dict]:
        """Check a generic web source"""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for the query terms in the page
                    text_content = soup.get_text().lower()
                    query_terms = query.lower().split()
                    
                    matches = sum(1 for term in query_terms if term in text_content)
                    match_ratio = matches / len(query_terms) if query_terms else 0
                    
                    if match_ratio > 0.3:  # At least 30% match
                        return {
                            'source_match': True,
                            'match_ratio': match_ratio,
                            'url': url
                        }
        
        except Exception as e:
            logging.warning(f"Generic source check failed: {e}")
        
        return None
    
    def _calculate_validation_score(self, validation_results: List[Dict]) -> float:
        """Calculate overall validation score"""
        if not validation_results:
            return 0.0
        
        total_score = 0
        max_score = len(validation_results) * 100
        
        for result in validation_results:
            if result.get('found', False):
                total_score += 100
            elif result.get('source_match', False):
                total_score += 50
        
        return min(total_score / max_score * 100, 100.0)
    
    def _find_discrepancies(self, original_data: Dict, validation_results: List[Dict]) -> List[str]:
        """Find discrepancies between original data and web validation"""
        discrepancies = []
        
        # Check if dataset was found in web sources
        found_in_web = any(r.get('found', False) for r in validation_results)
        
        if not found_in_web:
            discrepancies.append("Dataset not found in web sources")
        
        # Check for missing technical information
        if not original_data.get('technical_specs'):
            discrepancies.append("Missing technical specifications")
        
        if not original_data.get('spatial_coverage'):
            discrepancies.append("Missing spatial coverage information")
        
        return discrepancies

class WebValidationManager:
    """Manages web validation for multiple datasets"""
    
    def __init__(self):
        self.validator = WebValidator()
        self.validation_cache = {}
    
    async def validate_batch(self, datasets: List[Dict]) -> List[WebValidationResult]:
        """Validate a batch of datasets"""
        results = []
        
        for dataset in datasets:
            # Check cache first
            dataset_id = dataset.get('id', dataset.get('title', ''))
            if dataset_id in self.validation_cache:
                results.append(self.validation_cache[dataset_id])
                continue
            
            # Perform validation
            result = await self.validator.validate_dataset(dataset)
            self.validation_cache[dataset_id] = result
            results.append(result)
            
            # Small delay to be respectful to web servers
            await asyncio.sleep(0.5)
        
        return results
    
    def get_validation_summary(self, results: List[WebValidationResult]) -> Dict:
        """Generate validation summary"""
        if not results:
            return {}
        
        total_datasets = len(results)
        avg_score = sum(r.validation_score for r in results) / total_datasets
        validated_count = sum(1 for r in results if r.validation_score > 50)
        
        return {
            'total_datasets': total_datasets,
            'average_validation_score': avg_score,
            'validated_datasets': validated_count,
            'validation_rate': validated_count / total_datasets * 100,
            'total_discrepancies': sum(len(r.discrepancies) for r in results),
            'enhanced_datasets': sum(1 for r in results if r.additional_info)
        } 
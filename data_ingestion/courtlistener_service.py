import requests
import time
from typing import Dict, List, Optional, Generator
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CourtListenerAPIService:
    """Service class for interacting with CourtListener API"""
    
    def __init__(self):
        self.base_url = settings.COURTLISTENER_BASE_URL
        self.api_key = settings.COURTLISTENER_API_KEY
        self.headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, max_retries: int = 3) -> Dict:
        """Make a request to the CourtListener API with rate limiting and retry logic"""
        url = f"{self.base_url}/{endpoint}/"
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                # Rate limiting - be respectful to the API
                time.sleep(0.5)
                
                return response.json()
            
            except requests.exceptions.HTTPError as e:
                # Handle server errors (502, 503, 504) with retry
                if e.response.status_code in [502, 503, 504]:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                        logger.warning(f"Server error {e.response.status_code} for {url}. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"API request failed after {max_retries} attempts for {url}: {str(e)}")
                        raise
                else:
                    # For other HTTP errors, don't retry
                    logger.error(f"API request failed for {url}: {str(e)}")
                    raise
            
            except requests.exceptions.RequestException as e:
                # For connection errors, retry
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Connection error for {url}. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"API request failed after {max_retries} attempts for {url}: {str(e)}")
                    raise
        
        # Should never reach here, but just in case
        raise Exception(f"Unexpected error in _make_request for {url}")
    
    def _paginate(self, endpoint: str, params: Optional[Dict] = None, max_results: Optional[int] = None) -> Generator[Dict, None, None]:
        """Generator to handle pagination for API requests"""
        if params is None:
            params = {}
        
        params['page'] = 1
        count = 0
        
        while True:
            data = self._make_request(endpoint, params)
            results = data.get('results', [])
            
            if not results:
                break
            
            for result in results:
                if max_results and count >= max_results:
                    return
                yield result
                count += 1
            
            # Check if there's a next page
            if not data.get('next'):
                break
            
            params['page'] += 1
            logger.info(f"Fetching page {params['page']} from {endpoint}")
    
    # ============================================
    # Court Methods
    # ============================================
    
    def fetch_courts(self, max_results: Optional[int] = None) -> Generator[Dict, None, None]:
        """Fetch all courts from CourtListener"""
        logger.info("Fetching courts from CourtListener")
        return self._paginate('courts', max_results=max_results)
    
    def fetch_court_by_id(self, court_id: str) -> Dict:
        """Fetch a specific court by ID"""
        logger.info(f"Fetching court: {court_id}")
        return self._make_request(f'courts/{court_id}')
    
    # ============================================
    # Judge Methods
    # ============================================
    
    def fetch_judges(self, max_results: Optional[int] = None, **filters) -> Generator[Dict, None, None]:
        """
        Fetch judges from CourtListener
        
        Args:
            max_results: Maximum number of results to fetch
            **filters: Additional filters like name_last, appointer, etc.
        """
        logger.info("Fetching judges from CourtListener")
        return self._paginate('people', params=filters, max_results=max_results)
    
    def fetch_judge_by_id(self, judge_id: int) -> Dict:
        """Fetch a specific judge by ID"""
        logger.info(f"Fetching judge: {judge_id}")
        return self._make_request(f'people/{judge_id}')
    
    def fetch_judge_positions(self, judge_id: int) -> List[Dict]:
        """Fetch all positions for a judge"""
        logger.info(f"Fetching positions for judge: {judge_id}")
        params = {'person': judge_id}
        return list(self._paginate('positions', params=params))
    
    def fetch_judge_educations(self, judge_id: int) -> List[Dict]:
        """Fetch all education records for a judge"""
        logger.info(f"Fetching education for judge: {judge_id}")
        params = {'person': judge_id}
        return list(self._paginate('educations', params=params))
    
    # ============================================
    # Docket (Case) Methods
    # ============================================
    
    def fetch_dockets(self, max_results: Optional[int] = None, **filters) -> Generator[Dict, None, None]:
        """
        Fetch dockets (cases) from CourtListener
        
        Args:
            max_results: Maximum number of results to fetch
            **filters: Filters like court, case_name, date_filed__gte, etc.
        """
        logger.info("Fetching dockets from CourtListener")
        return self._paginate('dockets', params=filters, max_results=max_results)
    
    def fetch_docket_by_id(self, docket_id: int) -> Dict:
        """Fetch a specific docket by ID"""
        logger.info(f"Fetching docket: {docket_id}")
        return self._make_request(f'dockets/{docket_id}')
    
    def search_dockets(self, query: str, max_results: Optional[int] = None) -> Generator[Dict, None, None]:
        """Search for dockets by query string"""
        logger.info(f"Searching dockets with query: {query}")
        params = {'q': query}
        return self._paginate('search', params=params, max_results=max_results)
    
    # ============================================
    # Opinion Methods
    # ============================================
    
    def fetch_opinions(self, max_results: Optional[int] = None, **filters) -> Generator[Dict, None, None]:
        """
        Fetch opinions from CourtListener
        
        Args:
            max_results: Maximum number of results to fetch
            **filters: Filters like cluster, author, type, date_filed__gte, etc.
        """
        logger.info("Fetching opinions from CourtListener")
        return self._paginate('opinions', params=filters, max_results=max_results)
    
    def fetch_opinion_by_id(self, opinion_id: int) -> Dict:
        """Fetch a specific opinion by ID"""
        logger.info(f"Fetching opinion: {opinion_id}")
        return self._make_request(f'opinions/{opinion_id}')
    
    def fetch_opinions_by_docket(self, docket_id: int) -> List[Dict]:
        """Fetch all opinions for a specific docket"""
        logger.info(f"Fetching opinions for docket: {docket_id}")
        # First get clusters for this docket
        clusters = list(self._paginate('clusters', params={'docket': docket_id}))
        
        opinions = []
        for cluster in clusters:
            cluster_opinions = list(self._paginate('opinions', params={'cluster': cluster['id']}))
            opinions.extend(cluster_opinions)
        
        return opinions
    
    def fetch_opinion_clusters(self, max_results: Optional[int] = None, **filters) -> Generator[Dict, None, None]:
        """
        Fetch opinion clusters (groups of related opinions)
        
        Args:
            max_results: Maximum number of results to fetch
            **filters: Filters like docket, date_filed__gte, etc.
        """
        logger.info("Fetching opinion clusters from CourtListener")
        return self._paginate('clusters', params=filters, max_results=max_results)
    
    # ============================================
    # Citation Methods
    # ============================================
    
    def fetch_citations_for_opinion(self, opinion_id: int) -> Dict:
        """
        Fetch citation information for an opinion
        Returns both opinions this opinion cites and opinions that cite this opinion
        """
        logger.info(f"Fetching citations for opinion: {opinion_id}")
        
        # Get opinions this opinion cites
        cites_to = []
        try:
            params = {'citing_opinion': opinion_id}
            cites_to = list(self._paginate('opinions-cited', params=params))
        except Exception as e:
            logger.error(f"Error fetching cites_to for opinion {opinion_id}: {str(e)}")
        
        # Get opinions that cite this opinion
        cited_by = []
        try:
            params = {'cited_opinion': opinion_id}
            cited_by = list(self._paginate('opinions-cited', params=params))
        except Exception as e:
            logger.error(f"Error fetching cited_by for opinion {opinion_id}: {str(e)}")
        
        return {
            'opinion_id': opinion_id,
            'cites_to': cites_to,
            'cited_by': cited_by,
        }
    
    def fetch_opinion_citations(self, max_results: Optional[int] = None) -> Generator[Dict, None, None]:
        """Fetch all opinion citation relationships"""
        logger.info("Fetching opinion citations from CourtListener")
        return self._paginate('opinions-cited', max_results=max_results)
    
    # ============================================
    # Search Methods
    # ============================================
    
    def search_cases(self, query: str, court: Optional[str] = None, 
                     date_filed_after: Optional[str] = None,
                     max_results: Optional[int] = None) -> Generator[Dict, None, None]:
        """
        Search for cases with various filters
        
        Args:
            query: Search query string
            court: Court ID to filter by
            date_filed_after: Date in format YYYY-MM-DD
            max_results: Maximum number of results
        """
        params = {'q': query, 'type': 'o'}  # 'o' for opinions
        
        if court:
            params['court'] = court
        if date_filed_after:
            params['filed_after'] = date_filed_after
        
        logger.info(f"Searching cases with params: {params}")
        return self._paginate('search', params=params, max_results=max_results)
    
    def search_judges(self, name: Optional[str] = None, court: Optional[str] = None,
                     max_results: Optional[int] = None) -> Generator[Dict, None, None]:
        """Search for judges by name or court"""
        params = {}
        
        if name:
            params['name'] = name
        if court:
            params['court'] = court
        
        logger.info(f"Searching judges with params: {params}")
        return self._paginate('people', params=params, max_results=max_results)
    
    # ============================================
    # Bulk Data Methods
    # ============================================
    
    def fetch_recent_opinions(self, days: int = 7, max_results: Optional[int] = None) -> Generator[Dict, None, None]:
        """Fetch opinions filed in the last N days"""
        from datetime import datetime, timedelta
        
        date_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        logger.info(f"Fetching opinions filed after {date_threshold}")
        
        params = {'date_filed__gte': date_threshold}
        return self._paginate('clusters', params=params, max_results=max_results)
    
    def fetch_judge_with_cases(self, judge_id: int, max_cases: Optional[int] = None) -> Dict:
        """
        Fetch a judge along with all their cases
        
        Returns a comprehensive dict with judge info and associated cases
        """
        logger.info(f"Fetching judge {judge_id} with cases")
        
        # Get judge information
        judge_data = self.fetch_judge_by_id(judge_id)
        
        # Get judge positions
        positions = self.fetch_judge_positions(judge_id)
        
        # Get judge educations
        educations = self.fetch_judge_educations(judge_id)
        
        # Get opinions authored by this judge
        opinions = list(self._paginate('opinions', params={'author': judge_id}, max_results=max_cases))
        
        return {
            'judge': judge_data,
            'positions': positions,
            'educations': educations,
            'opinions': opinions,
            'total_opinions': len(opinions),
        }
    
    def fetch_case_with_citations(self, docket_id: int) -> Dict:
        """
        Fetch a case with all its opinions and citation relationships
        
        Returns a comprehensive dict with case, opinions, and citations
        """
        logger.info(f"Fetching case {docket_id} with citations")
        
        # Get docket information
        docket_data = self.fetch_docket_by_id(docket_id)
        
        # Get opinions for this docket
        opinions = self.fetch_opinions_by_docket(docket_id)
        
        # Get citations for each opinion
        all_citations = []
        for opinion in opinions:
            citations = self.fetch_citations_for_opinion(opinion['id'])
            all_citations.append(citations)
        
        return {
            'docket': docket_data,
            'opinions': opinions,
            'citations': all_citations,
        }


# Singleton instance
courtlistener_service = CourtListenerAPIService()

# Alias for convenience (used in docs)
CourtListenerService = CourtListenerAPIService


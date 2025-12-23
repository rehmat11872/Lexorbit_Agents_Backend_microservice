import logging
from typing import Dict, List, Optional
from data_ingestion.courtlistener_service import courtlistener_service
from data_ingestion.data_processors import data_processor
from court_data.models import Judge, Court, Docket

logger = logging.getLogger(__name__)

class IngestionManager:
    """Orchestrates complex data ingestion flows involving multiple API calls"""

    @staticmethod
    def ingest_judge_complete(judge_id: int, max_opinions: Optional[int] = None) -> Judge:
        """
        Performs a 'deep fetch' for a single judge:
        1. Bio and Education
        2. Career Positions
        3. Historic Opinions
        4. Associated Clusters and Dockets (with outcomes)
        """
        logger.info(f"Starting complete ingestion for judge {judge_id}")

        # 1. Fetch judge basic info (includes education in some API versions)
        judge_data = courtlistener_service.fetch_judge_by_id(judge_id)
        
        # 2. Fetch judge positions and educations separately to ensure completeness
        positions = courtlistener_service.fetch_judge_positions(judge_id)
        educations = courtlistener_service.fetch_judge_educations(judge_id)
        
        # 3. Save Judge with all gathered metadata
        # Combine nested data with separately fetched data if needed
        if educations and not judge_data.get('educations'):
            judge_data['educations'] = educations
            
        judge = data_processor.process_judge(judge_data, positions=positions)
        
        # 4. Fetch opinions authored by this judge
        opinions_data = list(courtlistener_service.fetch_opinions(
            author=judge_id,
            max_results=max_opinions
        ))
        
        logger.info(f"Found {len(opinions_data)} opinions for judge {judge.full_name}")

        # 5. Process each opinion and its related cluster/docket
        for opinion_data in opinions_data:
            try:
                # Extract cluster ID from opinion data
                cluster_url = opinion_data.get('cluster')
                cluster_id = cluster_url.split('/')[-2] if isinstance(cluster_url, str) else cluster_url
                
                if not cluster_id:
                    continue
                
                # Fetch full cluster to get docket ID and disposition
                cluster_data = courtlistener_service._make_request(f'clusters/{cluster_id}')
                
                # Fetch docket to get court and nature of suit
                docket_url = cluster_data.get('docket')
                docket_id = docket_url.split('/')[-2] if isinstance(docket_url, str) else docket_url
                
                if not docket_id:
                    continue
                    
                docket_data = courtlistener_service.fetch_docket_by_id(docket_id)
                
                # Process Docket (extracts amount)
                docket = data_processor.process_docket(docket_data)
                
                if docket:
                    # Process Cluster (extracts outcome/disposition)
                    cluster = data_processor.process_opinion_cluster(cluster_data, docket=docket)
                    
                    # Process Opinion
                    data_processor.process_opinion(opinion_data, cluster=cluster)
                    
                    # Create many-to-many relationship
                    data_processor.process_judge_docket_relation(
                        judge=judge,
                        docket=docket,
                        role='author',
                        outcome=docket.outcome_status
                    )
                    
            except Exception as e:
                logger.error(f"Error processing opinion for judge {judge_id}: {str(e)}")
                continue

        return judge

# Singleton instance
ingestion_manager = IngestionManager()

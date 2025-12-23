from datetime import datetime
from typing import Dict, List, Optional
import logging
from django.db import transaction
from django.conf import settings
from court_data.models import (
    Court, Judge, Docket, OpinionCluster, Opinion, OpinionsCited, 
    JudgeDocketRelation, CaseOutcome, Statute
)

logger = logging.getLogger(__name__)

# Import OpenAI client if available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for text using OpenAI"""
    if not OPENAI_AVAILABLE:
        return None
    
    api_key = settings.OPENAI_API_KEY
    if not api_key or api_key == 'your-openai-api-key-here':
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            input=text[:8000],  # Limit text length
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.warning(f"Error generating embedding: {str(e)}")
        return None


class DataProcessor:
    """Process and save CourtListener API data to database"""
    
    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[datetime.date]:
        """Parse date string from API"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    @transaction.atomic
    def process_court(data: Dict) -> Court:
        """Process and save court data"""
        court_id = data.get('id')
        
        court, created = Court.objects.update_or_create(
            court_id=court_id,
            defaults={
                'name': data.get('full_name', ''),
                'short_name': data.get('short_name', ''),
                'jurisdiction': data.get('jurisdiction', ''),
                'court_type': data.get('position', ''),
                'citation_string': data.get('citation_string', ''),
                'notes': data.get('notes', ''),
            }
        )
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} court: {court.name}")
        return court
    
    @staticmethod
    @transaction.atomic
    def process_judge(data: Dict) -> Judge:
        """Process and save judge data"""
        judge_id = data.get('id')
        
        # Build full name
        name_parts = [
            data.get('name_first', ''),
            data.get('name_middle', ''),
            data.get('name_last', ''),
            data.get('name_suffix', ''),
        ]
        full_name = ' '.join(filter(None, name_parts))
        
        # Extract education if available
        education = []
        if 'educations' in data and isinstance(data.get('educations'), list):
            education = [
                {
                    'school': edu.get('school', {}).get('name', '') if isinstance(edu.get('school'), dict) else str(edu.get('school', '')),
                    'degree': str(edu.get('degree_level', '')),
                    'year': edu.get('degree_year'),
                }
                for edu in data.get('educations', []) if isinstance(edu, dict)
            ]
        
        # Extract positions if available
        positions = []
        if 'positions' in data and isinstance(data['positions'], list):
            positions = [
                {
                    'court': pos.get('court', {}).get('short_name', '') if isinstance(pos.get('court'), dict) else str(pos.get('court', '')),
                    'position_type': str(pos.get('position_type', '')),
                    'date_start': str(pos.get('date_start', '')),
                    'date_termination': str(pos.get('date_termination', '')),
                    'appointer': pos.get('appointer', {}).get('name_full', '') if isinstance(pos.get('appointer'), dict) else str(pos.get('appointer', '')),
                }
                for pos in data.get('positions', []) if isinstance(pos, dict)
            ]
        
        # Generate embedding for judge
        bio_text = f"{full_name}. {data.get('bio', '')}"
        embedding = generate_embedding(bio_text)
        
        defaults_dict = {
            'name_first': data.get('name_first', ''),
            'name_middle': data.get('name_middle', ''),
            'name_last': data.get('name_last', ''),
            'name_suffix': data.get('name_suffix', ''),
            'full_name': full_name,
            'date_birth': DataProcessor.parse_date(data.get('date_dob')),
            'date_death': DataProcessor.parse_date(data.get('date_dod')),
            'gender': data.get('gender', ''),
            'race': ', '.join(data.get('race', [])) if isinstance(data.get('race'), list) else data.get('race', ''),
            'dob_city': data.get('dob_city', ''),
            'dob_state': data.get('dob_state', ''),
            'biography': data.get('bio', ''),
            'education': education,
            'positions': positions,
        }
        
        if embedding:
            defaults_dict['embedding'] = embedding
        
        judge, created = Judge.objects.update_or_create(
            judge_id=judge_id,
            defaults=defaults_dict
        )
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} judge: {judge.full_name} (ID: {judge_id})")
        return judge
    
    @staticmethod
    @transaction.atomic
    def process_docket(data: Dict, court: Optional[Court] = None) -> Docket:
        """Process and save docket data"""
        docket_id = data.get('id')
        
        # Get or create court if not provided
        if not court and data.get('court'):
            court_url = data['court']
            if isinstance(court_url, str):
                # Extract court ID from URL (handle both /id/ and /id formats)
                court_id = court_url.rstrip('/').split('/')[-1]
            else:
                court_id = court_url
            try:
                court = Court.objects.get(court_id=court_id)
            except Court.DoesNotExist:
                logger.warning(f"Court {court_id} not found, skipping docket {docket_id}")
                return None
        
        if not court:
            logger.warning(f"No court for docket {docket_id}, skipping")
            return None
        
        # Extract parties if available
        parties = []
        if 'parties' in data:
            parties = [
                {
                    'name': party.get('name', ''),
                    'type': party.get('party_type', {}).get('name', '') if isinstance(party.get('party_type'), dict) else '',
                }
                for party in data.get('parties', [])
            ]
        
        # Generate embedding for docket
        case_text = f"{data.get('case_name', '')}. {data.get('nature_of_suit', '')}"
        embedding = generate_embedding(case_text)
        
        defaults_dict = {
            'court': court,
            'case_name': data.get('case_name', ''),
            'case_name_short': data.get('case_name_short', ''),
            'case_name_full': data.get('case_name_full', ''),
            'docket_number': data.get('docket_number', ''),
            'date_filed': DataProcessor.parse_date(data.get('date_filed')),
            'date_terminated': DataProcessor.parse_date(data.get('date_terminated')),
            'date_last_filing': DataProcessor.parse_date(data.get('date_last_filing')),
            'nature_of_suit': data.get('nature_of_suit', ''),
            'cause': data.get('cause', ''),
            'jury_demand': data.get('jury_demand', ''),
            'jurisdiction_type': data.get('jurisdiction_type', ''),
            'parties': parties,
            'pacer_case_id': data.get('pacer_case_id', ''),
        }
        
        if embedding:
            defaults_dict['embedding'] = embedding
        
        docket, created = Docket.objects.update_or_create(
            docket_id=docket_id,
            defaults=defaults_dict
        )
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} docket: {docket.case_name_short}")
        
        # Create case outcome for analytics if case is terminated
        if docket.date_terminated:
            try:
                # Determine outcome type based on available data
                outcome_type = 'decided'  # Default
                if 'disposition' in data:
                    disposition = data['disposition'].lower()
                    if any(word in disposition for word in ['grant', 'favor', 'win']):
                        outcome_type = 'granted'
                    elif any(word in disposition for word in ['deny', 'dismiss', 'reject']):
                        outcome_type = 'denied'
                
                DataProcessor.process_case_outcome(
                    docket=docket,
                    outcome_type=outcome_type,
                    disposition=data.get('disposition', ''),
                    precedential_status=data.get('precedential_status', '')
                )
            except Exception as e:
                logger.warning(f"Failed to create case outcome for docket {docket_id}: {str(e)}")
        return docket
    
    @staticmethod
    @transaction.atomic
    def process_opinion_cluster(cluster_data: Dict, docket: Optional[Docket] = None) -> Optional[OpinionCluster]:
        """Process and save opinion cluster"""
        cluster_id = cluster_data.get('id')
        
        # Get docket if not provided
        if not docket:
            docket_url = cluster_data.get('docket')
            if docket_url:
                if isinstance(docket_url, str):
                    docket_id = docket_url.rstrip('/').split('/')[-1]
                else:
                    docket_id = docket_url
                try:
                    docket = Docket.objects.get(docket_id=docket_id)
                except Docket.DoesNotExist:
                    logger.warning(f"Docket {docket_id} not found for cluster {cluster_id}")
                    return None
        
        if not docket:
            logger.warning(f"No docket provided for cluster {cluster_id}")
            return None
        
        defaults_dict = {
            'docket': docket,
            'case_name': cluster_data.get('case_name', '')[:1000],
            'case_name_short': cluster_data.get('case_name_short', '')[:500],
            'case_name_full': cluster_data.get('case_name_full', '')[:2000],
            'date_filed': DataProcessor.parse_date(cluster_data.get('date_filed')),
            'citation_count': cluster_data.get('citation_count', 0),
        }
        
        cluster, created = OpinionCluster.objects.update_or_create(
            cluster_id=cluster_id,
            defaults=defaults_dict
        )
        
        # Process panel judges if provided
        panel_judges = cluster_data.get('panel', [])
        if panel_judges:
            for judge_ref in panel_judges:
                judge_id = judge_ref.split('/')[-2] if isinstance(judge_ref, str) else judge_ref
                try:
                    judge = Judge.objects.get(judge_id=judge_id)
                    cluster.panel.add(judge)
                except Judge.DoesNotExist:
                    logger.warning(f"Judge {judge_id} not found for cluster panel")
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} cluster: {cluster_id} - {cluster.case_name_short}")
        return cluster
    
    @staticmethod
    @transaction.atomic
    def process_opinion(data: Dict, cluster: Optional[OpinionCluster] = None, cluster_id: Optional[int] = None) -> Optional[Opinion]:
        """Process and save opinion data"""
        opinion_id = data.get('id')
        
        # Get cluster if not provided
        if not cluster:
            if cluster_id:
                try:
                    cluster = OpinionCluster.objects.get(cluster_id=cluster_id)
                except OpinionCluster.DoesNotExist:
                    logger.warning(f"Cluster {cluster_id} not found for opinion {opinion_id}")
                    return None
            else:
                cluster_url = data.get('cluster')
                if cluster_url:
                    extracted_id = cluster_url.split('/')[-2] if isinstance(cluster_url, str) else cluster_url
                    try:
                        cluster = OpinionCluster.objects.get(cluster_id=extracted_id)
                    except OpinionCluster.DoesNotExist:
                        logger.warning(f"Cluster {extracted_id} not found for opinion {opinion_id}")
                        return None
        
        if not cluster:
            logger.warning(f"No cluster provided for opinion {opinion_id}")
            return None
        
        # Get or create author (judge)
        author = None
        if data.get('author'):
            author_id = data['author'].split('/')[-2] if isinstance(data['author'], str) else data['author']
            try:
                author = Judge.objects.get(judge_id=author_id)
            except Judge.DoesNotExist:
                logger.warning(f"Judge {author_id} not found for opinion {opinion_id}")
        
        # Generate embedding for opinion (use first 8000 chars)
        opinion_text = data.get('plain_text', '')[:8000]
        embedding = generate_embedding(opinion_text) if opinion_text else None
        
        defaults_dict = {
            'cluster': cluster,  # Changed from 'docket' to 'cluster'
            'type': data.get('type', '010combined'),
            'author': author,
            'plain_text': data.get('plain_text', ''),
            'html': data.get('html', ''),
            'html_lawbox': data.get('html_lawbox', ''),
            'html_columbia': data.get('html_columbia', ''),
            'html_anon_2020': data.get('html_anon_2020', ''),
            'date_filed': DataProcessor.parse_date(data.get('date_filed')),
            'page_count': data.get('page_count'),
            'download_url': data.get('download_url', ''),
        }
        
        if embedding:
            defaults_dict['embedding'] = embedding
        
        opinion, created = Opinion.objects.update_or_create(
            opinion_id=opinion_id,
            defaults=defaults_dict
        )
        
        # Process joined_by judges
        if 'joined_by' in data and data['joined_by']:
            for judge_url in data['joined_by']:
                judge_id = judge_url.split('/')[-2] if isinstance(judge_url, str) else judge_url
                try:
                    judge = Judge.objects.get(judge_id=judge_id)
                    opinion.joined_by.add(judge)
                except Judge.DoesNotExist:
                    logger.warning(f"Judge {judge_id} not found for joined_by")
        
        # Create judge-docket relation for analytics
        if author and cluster and cluster.docket:
            try:
                DataProcessor.process_judge_docket_relation(
                    judge=author,
                    docket=cluster.docket,
                    role='author',
                    outcome=''
                )
            except Exception as e:
                logger.warning(f"Failed to create judge-docket relation: {str(e)}")
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} opinion: {opinion_id}")
        return opinion
    
    @staticmethod
    @transaction.atomic
    def process_citation(citing_opinion_id: int, cited_opinion_id: int, 
                        depth: int = 1) -> Optional[OpinionsCited]:
        """Process and save citation relationship"""
        try:
            citing_opinion = Opinion.objects.get(opinion_id=citing_opinion_id)
            cited_opinion = Opinion.objects.get(opinion_id=cited_opinion_id)
        except Opinion.DoesNotExist as e:
            logger.warning(f"Opinion not found for citation: {str(e)}")
            return None
        
        citation, created = OpinionsCited.objects.get_or_create(
            citing_opinion=citing_opinion,
            cited_opinion=cited_opinion,
            defaults={
                'depth': depth,
            }
        )
        
        action = "Created" if created else "Found"
        logger.debug(f"{action} citation: {citing_opinion_id} -> {cited_opinion_id}")
        return citation
    
    @staticmethod
    @transaction.atomic
    def process_judge_docket_relation(judge: Judge, docket: Docket, 
                                     role: str = '', outcome: str = '') -> JudgeDocketRelation:
        """Create relationship between judge and docket"""
        relation, created = JudgeDocketRelation.objects.get_or_create(
            judge=judge,
            docket=docket,
            role=role,
            defaults={
                'outcome': outcome,
            }
        )
        
        action = "Created" if created else "Found"
        logger.debug(f"{action} judge-docket relation: {judge.full_name} - {docket.case_name_short}")
        return relation
    
    @staticmethod
    @transaction.atomic
    def process_case_outcome(docket: Docket, outcome_type: str, 
                           disposition: str = '', precedential_status: str = '') -> CaseOutcome:
        """Process and save case outcome"""
        # Calculate decision days
        decision_days = None
        if docket.date_filed and docket.date_terminated:
            delta = docket.date_terminated - docket.date_filed
            decision_days = delta.days
        
        outcome, created = CaseOutcome.objects.update_or_create(
            docket=docket,
            defaults={
                'outcome_type': outcome_type,
                'decision_days': decision_days,
                'disposition': disposition,
                'precedential_status': precedential_status,
            }
        )
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} case outcome: {docket.case_name_short} - {outcome_type}")
        return outcome
    
    @staticmethod
    def batch_process_courts(courts_data: List[Dict]) -> int:
        """Batch process multiple courts"""
        count = 0
        for court_data in courts_data:
            try:
                DataProcessor.process_court(court_data)
                count += 1
            except Exception as e:
                logger.error(f"Error processing court: {str(e)}")
        
        logger.info(f"Processed {count} courts")
        return count
    
    @staticmethod
    def batch_process_judges(judges_data: List[Dict]) -> int:
        """Batch process multiple judges"""
        count = 0
        for judge_data in judges_data:
            try:
                DataProcessor.process_judge(judge_data)
                count += 1
            except Exception as e:
                logger.error(f"Error processing judge: {str(e)}")
        
        logger.info(f"Processed {count} judges")
        return count
    
    @staticmethod
    def batch_process_dockets(dockets_data: List[Dict]) -> int:
        """Batch process multiple dockets"""
        count = 0
        for docket_data in dockets_data:
            try:
                DataProcessor.process_docket(docket_data)
                count += 1
            except Exception as e:
                logger.error(f"Error processing docket: {str(e)}")
        
        logger.info(f"Processed {count} dockets")
        return count


# Singleton instance
data_processor = DataProcessor()


from datetime import datetime
from typing import Dict, List, Optional
import logging
import re
from decimal import Decimal
from django.db import transaction
from django.conf import settings
from court_data.models import (
    Court, Judge, Docket, OpinionCluster, Opinion, OpinionsCited, 
    JudgeDocketRelation
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
    def extract_monetary_amount(text: str) -> Optional[Decimal]:
        """Extract dollar amount from text (e.g. '$2,500,000.00')"""
        if not text:
            return None
        
        # Regex for currency pattern
        matches = re.findall(r'\$\s?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)', text)
        if matches:
            try:
                # Use the first/largest match
                clean_amount = matches[0].replace(',', '')
                return Decimal(clean_amount)
            except:
                pass
        return None
    
    @staticmethod
    @transaction.atomic
    def process_court(data: Dict) -> Court:
        """Process and save court data"""
        court_id = data.get('id')
        
        court, created = Court.objects.update_or_create(
            court_id=court_id,
            defaults={
                'name': data.get('full_name', '') or data.get('name', ''),
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
    def generate_synthetic_bio(name: str, educations: List[Dict], positions: List[Dict], gender: str = '') -> str:
        """Generate a biography from available structured data when bio is missing"""
        
        # Gender-aware pronouns
        if gender and gender.lower() in ['m', 'male']:
            pronoun = 'He'
            pronoun_obj = 'his'
        elif gender and gender.lower() in ['f', 'female']:
            pronoun = 'She'
            pronoun_obj = 'her'
        else:
            pronoun = 'They'
            pronoun_obj = 'their'
        
        parts = [f"{name} is a judicial officer."]
        
        # Position type expansion map
        pos_map = {
            'jud': 'Judge',
            'jus': 'Justice',
            'chj': 'Chief Judge',
            'mag': 'Magistrate',
            'scj': 'Senior Circuit Judge',
            'sdj': 'Senior District Judge',
            'pro': 'Prosecutor',
            'att': 'Attorney',
        }
        
        # Education (deduplicate by normalized school name)
        if educations:
            seen_schools = set()
            edu_strings = []
            for edu in educations:
                school = edu.get('school') or edu.get('school_name')
                if school:
                    # Normalize for dedup check
                    norm_school = school.lower().replace(' school of law', ' law school').replace('yale college', 'yale university')
                    degree = (edu.get('degree') or edu.get('degree_level') or 'Degree').upper()
                    year = edu.get('year') or edu.get('degree_year')
                    key = f"{norm_school}|{degree}"
                    if key not in seen_schools:
                        seen_schools.add(key)
                        year_str = f" ({year})" if year else ""
                        edu_strings.append(f"{degree} from {school}{year_str}")
            if edu_strings:
                parts.append(f"Education: {'; '.join(edu_strings)}.")
        
        # Current positions (exclude empty courts)
        current = [p for p in positions if not p.get('date_termination') and p.get('court')]
        if current:
            current_parts = []
            for pos in current:
                court = pos.get('court')
                pos_code = (pos.get('position_type') or '').lower()
                pos_type = pos_map.get(pos_code, pos_code.capitalize() or 'Judge')
                start = pos.get('date_start', '')
                if start:
                    current_parts.append(f"serves as {pos_type} at {court} (since {start})")
                else:
                    current_parts.append(f"serves as {pos_type} at {court}")
            
            if current_parts:
                parts.append(f"{pronoun} currently {', and '.join(current_parts)}.")
        
        # Past judicial positions (only count those with actual court assignments)
        past = [p for p in positions if p.get('date_termination') and p.get('court')]
        if past:
            parts.append(f"{pronoun} previously held {len(past)} other judicial position(s).")
        
        return ' '.join(parts) if len(parts) > 1 else f"{name} is a judicial officer with the court system."

    @staticmethod
    @transaction.atomic
    def process_judge(data: Dict, positions: Optional[List[Dict]] = None) -> Judge:
        """Process and save judge data with synthetic bio fallback"""
        judge_id = data.get('id')
        
        # Build full name
        name_parts = [
            data.get('name_first', ''),
            data.get('name_middle', ''),
            data.get('name_last', ''),
            data.get('name_suffix', ''),
        ]
        full_name = ' '.join(filter(None, name_parts))
        
        # Extract education (v4 API nests this)
        education_list = []
        for edu in data.get('educations', []):
            school_data = edu.get('school', {})
            if isinstance(school_data, dict):
                school_name = school_data.get('name', '')
            else:
                school_name = str(school_data) if school_data else ''
            
            education_list.append({
                'school': school_name,
                'degree_level': edu.get('degree_level', ''),
                'degree_year': edu.get('degree_year'),
            })
        
        # Format positions
        position_list = []
        for pos in (positions or data.get('positions', [])):
            court_data = pos.get('court', {})
            if isinstance(court_data, dict):
                court_name = court_data.get('full_name', '') or court_data.get('short_name', '')
            else:
                court_name = str(court_data) if court_data else ''
            
            position_list.append({
                'position_type': pos.get('position_type', ''),
                'court': court_name,
                'date_start': pos.get('date_start', ''),
                'date_termination': pos.get('date_termination'),
            })
        
        # Check for provided bio or generate one
        bio = data.get('biography') or data.get('bio') or data.get('description') or ''
        gender = data.get('gender', '')
        if not bio:
            bio = DataProcessor.generate_synthetic_bio(full_name, education_list, position_list, gender)
        
        # Generate embedding for judge
        bio_text = f"{full_name}. {bio}"
        embedding = generate_embedding(bio_text)
        
        defaults_dict = {
            'name_first': data.get('name_first', ''),
            'name_middle': data.get('name_middle', ''),
            'name_last': data.get('name_last', ''),
            'name_suffix': data.get('name_suffix', ''),
            'full_name': full_name,
            'fjc_id': data.get('fjc_id'),
            'date_birth': DataProcessor.parse_date(data.get('date_dob')),
            'date_death': DataProcessor.parse_date(data.get('date_dod')),
            'gender': data.get('gender', ''),
            'race': ', '.join(data.get('race', [])) if isinstance(data.get('race'), list) else data.get('race', ''),
            'dob_city': data.get('dob_city', ''),
            'dob_state': data.get('dob_state', ''),
            'biography': bio,
            'education': education_list,
            'positions': position_list,
        }
        
        if embedding:
            defaults_dict['embedding'] = embedding
        
        judge, created = Judge.objects.update_or_create(
            judge_id=judge_id,
            defaults=defaults_dict
        )
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} judge: {judge.full_name} (FJC ID: {judge.fjc_id})")
        return judge
    
    @staticmethod
    @transaction.atomic
    def process_docket(data: Dict, court: Optional[Court] = None) -> Docket:
        """Process and save docket data"""
        docket_id = data.get('id')
        
        # Get or create court if not provided
        if not court and data.get('court'):
            court_id = data['court'].split('/')[-2] if isinstance(data['court'], str) else data['court']
            try:
                court = Court.objects.get(court_id=court_id)
            except Court.DoesNotExist:
                # Proactively fetch court if missing
                try:
                    from data_ingestion.courtlistener_service import courtlistener_service
                    logger.info(f"Court {court_id} missing for docket {docket_id}. Fetching...")
                    court_data = courtlistener_service.fetch_court_by_id(court_id)
                    court = DataProcessor.process_court(court_data)
                except Exception as e:
                    logger.warning(f"Court {court_id} not found and could not be fetched: {str(e)}")
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
        
        # Calculate decision days if possible
        filed = DataProcessor.parse_date(data.get('date_filed'))
        terminated = DataProcessor.parse_date(data.get('date_terminated'))
        decision_days = None
        if filed and terminated:
            decision_days = (terminated - filed).days

        # Extract monetary amount from suit details or snippet if available
        nature = data.get('nature_of_suit', '')
        amount = DataProcessor.extract_monetary_amount(nature)
        
        # Fallback for case_name_short
        case_name_short = data.get('case_name_short', '') or data.get('case_name', '')
        if case_name_short and len(case_name_short) > 255:
            case_name_short = case_name_short[:252] + '...'
            
        # Generate embedding for docket
        case_text = f"{data.get('case_name', '')}. {nature}"
        embedding = generate_embedding(case_text)
        
        defaults_dict = {
            'court': court,
            'case_name': data.get('case_name', ''),
            'case_name_short': case_name_short,
            'case_name_full': data.get('case_name_full', ''),
            'docket_number': data.get('docket_number', ''),
            'date_filed': filed,
            'date_terminated': terminated,
            'date_last_filing': DataProcessor.parse_date(data.get('date_last_filing')),
            'nature_of_suit': nature,
            'cause': data.get('cause', ''),
            'jury_demand': data.get('jury_demand', ''),
            'jurisdiction_type': data.get('jurisdiction_type', ''),
            'parties': parties,
            'pacer_case_id': data.get('pacer_case_id', ''),
            'monetary_amount': amount,
            'decision_days': decision_days,
        }
        
        if embedding:
            defaults_dict['embedding'] = embedding
        
        docket, created = Docket.objects.update_or_create(
            docket_id=docket_id,
            defaults=defaults_dict
        )
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} docket: {docket.case_name_short}")
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
                docket_id = docket_url.split('/')[-2] if isinstance(docket_url, str) else docket_url
                try:
                    docket = Docket.objects.get(docket_id=docket_id)
                except Docket.DoesNotExist:
                    logger.warning(f"Docket {docket_id} not found for cluster {cluster_id}")
                    return None
        
        if not docket:
            logger.warning(f"No docket provided for cluster {cluster_id}")
            return None
        
        # ENHANCED: Update docket details from cluster metadata if missing
        disposition = cluster_data.get('disposition', '')
        cluster_date = DataProcessor.parse_date(cluster_data.get('date_filed'))
        precedential = cluster_data.get('precedential_status', '')
        
        update_docket = False
        if disposition and not docket.outcome_status:
            docket.outcome_status = disposition[:100]
            update_docket = True
        
        if cluster_date and not docket.date_filed:
            docket.date_filed = cluster_date
            update_docket = True
            
        if precedential and not docket.precedential_status:
            docket.precedential_status = precedential[:50]
            update_docket = True
            
        if update_docket:
            # Recalculate decision days if dates were updated
            if docket.date_filed and docket.date_terminated:
                docket.decision_days = (docket.date_terminated - docket.date_filed).days
            docket.save()
        
        defaults_dict = {
            'docket': docket,
            'case_name': cluster_data.get('case_name', '')[:1000],
            'case_name_short': cluster_data.get('case_name_short', '')[:500],
            'case_name_full': cluster_data.get('case_name_full', '')[:2000],
            'date_filed': cluster_date,
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
            'cluster': cluster,
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


# Singleton instance
data_processor = DataProcessor()

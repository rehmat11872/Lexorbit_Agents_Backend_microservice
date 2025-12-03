"""
AI Services for semantic search and embeddings using OpenAI
"""
from openai import OpenAI
from django.conf import settings
from typing import List, Dict, Optional
import logging
from django.db.models import Q
from court_data.models import Judge, Docket, Opinion, Statute

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and using embeddings"""
    
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != 'your-openai-api-key-here':
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a text using OpenAI"""
        if not self.client:
            logger.warning("OpenAI client not initialized")
            return None
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    def semantic_search_opinions(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Semantic search across opinions using embeddings
        Falls back to keyword search if embeddings not available
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)
        
        if query_embedding:
            # Use vector similarity search
            opinions = self._vector_search_opinions(query_embedding, max_results)
        else:
            # Fall back to keyword search
            opinions = self._keyword_search_opinions(query, max_results)
        
        return self._format_opinion_results(opinions)
    
    def _vector_search_opinions(self, query_embedding: List[float], max_results: int):
        """Search opinions using vector similarity"""
        # Use pgvector's <-> operator for L2 distance
        # Or <=> for cosine distance
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Convert embedding to PostgreSQL array format
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Use pgvector's cosine distance operator
            cursor.execute("""
                SELECT 
                    id,
                    opinion_id,
                    embedding <=> %s::vector AS distance
                FROM opinions
                WHERE embedding IS NOT NULL
                ORDER BY distance
                LIMIT %s
            """, [embedding_str, max_results])
            
            results = cursor.fetchall()
            
            # Get full Opinion objects
            opinion_ids = [row[0] for row in results]
            opinions = Opinion.objects.filter(id__in=opinion_ids).select_related('cluster__docket', 'author')
            
            # Preserve order from similarity search
            opinion_dict = {op.id: op for op in opinions}
            return [opinion_dict[id] for id in opinion_ids if id in opinion_dict]
    
    def _keyword_search_opinions(self, query: str, max_results: int):
        """Fallback keyword search"""
        return Opinion.objects.filter(
            Q(plain_text__icontains=query) |
            Q(cluster__docket__case_name__icontains=query)
        ).select_related('cluster__docket', 'author')[:max_results]
    
    def _format_opinion_results(self, opinions) -> List[Dict]:
        """Format opinions for response"""
        return [{
            'type': 'opinion',
            'id': op.opinion_id,
            'title': op.cluster.docket.case_name_short if op.cluster and op.cluster.docket else 'Unknown',
            'author': op.author.full_name if op.author else 'Unknown',
            'date': op.date_filed,
            'court': op.cluster.docket.court.short_name if op.cluster and op.cluster.docket and op.cluster.docket.court else 'Unknown',
            'excerpt': op.plain_text[:300] + '...' if op.plain_text else '',
        } for op in opinions]
    
    def semantic_search_judges(self, query: str, max_results: int = 20) -> List[Dict]:
        """Semantic search for judges"""
        query_embedding = self.generate_embedding(query)
        
        if query_embedding:
            judges = self._vector_search_judges(query_embedding, max_results)
        else:
            judges = Judge.objects.filter(
                Q(full_name__icontains=query) |
                Q(biography__icontains=query)
            )[:max_results]
        
        return [{
            'type': 'judge',
            'id': judge.judge_id,
            'name': judge.full_name,
            'biography': judge.biography[:200] + '...' if judge.biography else '',
        } for judge in judges]
    
    def _vector_search_judges(self, query_embedding: List[float], max_results: int):
        """Search judges using vector similarity"""
        from django.db import connection
        
        with connection.cursor() as cursor:
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            cursor.execute("""
                SELECT 
                    id,
                    embedding <=> %s::vector AS distance
                FROM judges
                WHERE embedding IS NOT NULL
                ORDER BY distance
                LIMIT %s
            """, [embedding_str, max_results])
            
            results = cursor.fetchall()
            judge_ids = [row[0] for row in results]
            judges = Judge.objects.filter(id__in=judge_ids)
            
            judge_dict = {j.id: j for j in judges}
            return [judge_dict[id] for id in judge_ids if id in judge_dict]
    
    def semantic_search_cases(self, query: str, max_results: int = 50) -> List[Dict]:
        """Semantic search for cases/dockets"""
        query_embedding = self.generate_embedding(query)
        
        if query_embedding:
            dockets = self._vector_search_dockets(query_embedding, max_results)
        else:
            dockets = Docket.objects.filter(
                Q(case_name__icontains=query) |
                Q(nature_of_suit__icontains=query)
            ).select_related('court')[:max_results]
        
        return [{
            'type': 'case',
            'id': docket.docket_id,
            'name': docket.case_name_short,
            'court': docket.court.short_name if docket.court else 'Unknown',
            'date_filed': docket.date_filed,
            'nature_of_suit': docket.nature_of_suit,
        } for docket in dockets]
    
    def _vector_search_dockets(self, query_embedding: List[float], max_results: int):
        """Search dockets using vector similarity"""
        from django.db import connection
        
        with connection.cursor() as cursor:
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            cursor.execute("""
                SELECT 
                    id,
                    embedding <=> %s::vector AS distance
                FROM dockets
                WHERE embedding IS NOT NULL
                ORDER BY distance
                LIMIT %s
            """, [embedding_str, max_results])
            
            results = cursor.fetchall()
            docket_ids = [row[0] for row in results]
            dockets = Docket.objects.filter(id__in=docket_ids).select_related('court')
            
            docket_dict = {d.id: d for d in dockets}
            return [docket_dict[id] for id in docket_ids if id in docket_dict]
    
    def comprehensive_search(self, query: str, max_results: int = 50) -> Dict:
        """
        Search across all entity types and return comprehensive results
        """
        return {
            'query': query,
            'opinions': self.semantic_search_opinions(query, max_results // 2),
            'cases': self.semantic_search_cases(query, max_results // 4),
            'judges': self.semantic_search_judges(query, max_results // 4),
        }
    
    def find_similar_cases(self, case_id: int, max_results: int = 10) -> List[Dict]:
        """Find similar cases based on embeddings"""
        try:
            docket = Docket.objects.get(docket_id=case_id)
            
            if not docket.embedding:
                # No embedding, fall back to keyword search
                return self.semantic_search_cases(docket.case_name, max_results)
            
            # Use the case's embedding to find similar cases
            similar_dockets = self._vector_search_dockets(docket.embedding, max_results + 1)
            
            # Exclude the original case
            similar_dockets = [d for d in similar_dockets if d.docket_id != case_id][:max_results]
            
            return [{
                'id': d.docket_id,
                'name': d.case_name_short,
                'court': d.court.short_name if d.court else 'Unknown',
                'date_filed': d.date_filed,
                'nature_of_suit': d.nature_of_suit,
            } for d in similar_dockets]
            
        except Docket.DoesNotExist:
            return []


class LegalResearchService:
    """Service for AI-powered legal research"""
    
    def __init__(self):
        self.client = None
        self.embedding_service = EmbeddingService()
        
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != 'your-openai-api-key-here':
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def research_question(self, question: str, jurisdiction: str = '', 
                         case_type: str = '') -> Dict:
        """
        Research a legal question using semantic search and AI analysis
        """
        # Step 1: Find relevant cases using semantic search
        search_results = self.embedding_service.comprehensive_search(question, max_results=20)
        
        # Step 2: If OpenAI available, generate AI analysis
        if self.client:
            analysis = self._generate_ai_analysis(question, search_results)
        else:
            analysis = {
                'summary': 'Semantic search results based on your query.',
                'analysis': 'AI analysis requires OpenAI API key.',
            }
        
        # Step 3: Format response
        key_authorities = []
        for opinion in search_results['opinions'][:5]:
            key_authorities.append({
                'case_name': opinion['title'],
                'citation': f"Opinion ID: {opinion['id']}",
                'date': str(opinion['date']),
                'relevance': 'High',
                'summary': opinion['excerpt'],
            })
        
        return {
            'query': question,
            'summary': analysis.get('summary', ''),
            'key_authorities': key_authorities,
            'analysis': analysis.get('analysis', ''),
            'citations': key_authorities,
            'related_statutes': [],
            'search_results': search_results,
        }
    
    def _generate_ai_analysis(self, question: str, search_results: Dict) -> Dict:
        """Generate AI analysis using OpenAI"""
        try:
            # Build context from search results
            context = self._build_context(search_results)
            
            # Create prompt
            prompt = f"""You are a legal research assistant. Analyze the following legal question and provide a comprehensive answer based on the provided case law.

Question: {question}

Relevant Cases:
{context}

Provide:
1. A clear summary answering the question
2. Detailed legal analysis referencing the cases
3. Key legal principles involved

Format your response as JSON with 'summary' and 'analysis' fields."""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal research expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI analysis: {str(e)}")
            return {
                'summary': 'Error generating AI analysis',
                'analysis': 'Please try again or check your OpenAI API key.',
            }
    
    def _build_context(self, search_results: Dict) -> str:
        """Build context string from search results"""
        context_parts = []
        
        for opinion in search_results['opinions'][:5]:
            context_parts.append(
                f"Case: {opinion['title']}\n"
                f"Date: {opinion['date']}\n"
                f"Excerpt: {opinion['excerpt']}\n"
            )
        
        return "\n---\n".join(context_parts)


# Singleton instances
embedding_service = EmbeddingService()
legal_research_service = LegalResearchService()


from django.core.management.base import BaseCommand
from court_data.models import Judge, Docket, Opinion, Statute
from openai import OpenAI
from django.conf import settings
import time


class Command(BaseCommand):
    help = 'Generate embeddings for existing data using OpenAI'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            choices=['judges', 'cases', 'opinions', 'statutes', 'all'],
            default='all',
            help='Which model to generate embeddings for',
        )
        parser.add_argument(
            '--max-items',
            type=int,
            default=None,
            help='Maximum number of items to process',
        )
    
    def handle(self, *args, **options):
        model_type = options['model']
        max_items = options['max_items']
        
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'your-openai-api-key-here':
            self.stdout.write(
                self.style.ERROR('OpenAI API key not configured in .env file')
            )
            return
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        if model_type in ['judges', 'all']:
            self._generate_judge_embeddings(client, max_items)
        
        if model_type in ['cases', 'all']:
            self._generate_docket_embeddings(client, max_items)
        
        if model_type in ['opinions', 'all']:
            self._generate_opinion_embeddings(client, max_items)
        
        if model_type in ['statutes', 'all']:
            self._generate_statute_embeddings(client, max_items)
    
    def _generate_judge_embeddings(self, client, max_items):
        judges = Judge.objects.filter(embedding__isnull=True)
        if max_items:
            judges = judges[:max_items]
        
        total = judges.count()
        self.stdout.write(f'Generating embeddings for {total} judges...')
        
        for i, judge in enumerate(judges, 1):
            try:
                # Create text to embed
                text = f"{judge.full_name}. {judge.biography or ''}"
                
                # Generate embedding
                response = client.embeddings.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
                
                # Save embedding
                judge.embedding = response.data[0].embedding
                judge.save(update_fields=['embedding'])
                
                if i % 10 == 0:
                    self.stdout.write(f'Processed {i}/{total} judges')
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error processing judge {judge.id}: {str(e)}')
                )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generated embeddings for {total} judges'))
    
    def _generate_docket_embeddings(self, client, max_items):
        dockets = Docket.objects.filter(embedding__isnull=True)
        if max_items:
            dockets = dockets[:max_items]
        
        total = dockets.count()
        self.stdout.write(f'Generating embeddings for {total} cases...')
        
        for i, docket in enumerate(dockets, 1):
            try:
                # Create text to embed
                text = f"{docket.case_name}. {docket.nature_of_suit or ''}"
                
                # Generate embedding
                response = client.embeddings.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
                
                # Save embedding
                docket.embedding = response.data[0].embedding
                docket.save(update_fields=['embedding'])
                
                if i % 10 == 0:
                    self.stdout.write(f'Processed {i}/{total} cases')
                
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error processing case {docket.id}: {str(e)}')
                )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generated embeddings for {total} cases'))
    
    def _generate_opinion_embeddings(self, client, max_items):
        opinions = Opinion.objects.filter(embedding__isnull=True)
        if max_items:
            opinions = opinions[:max_items]
        
        total = opinions.count()
        self.stdout.write(f'Generating embeddings for {total} opinions...')
        
        for i, opinion in enumerate(opinions, 1):
            try:
                # Create text to embed (truncate long texts)
                text = opinion.plain_text[:2000] if opinion.plain_text else ""
                if not text:
                    continue
                
                # Generate embedding
                response = client.embeddings.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
                
                # Save embedding
                opinion.embedding = response.data[0].embedding
                opinion.save(update_fields=['embedding'])
                
                if i % 10 == 0:
                    self.stdout.write(f'Processed {i}/{total} opinions')
                
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error processing opinion {opinion.id}: {str(e)}')
                )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generated embeddings for {total} opinions'))
    
    def _generate_statute_embeddings(self, client, max_items):
        statutes = Statute.objects.filter(embedding__isnull=True)
        if max_items:
            statutes = statutes[:max_items]
        
        total = statutes.count()
        self.stdout.write(f'Generating embeddings for {total} statutes...')
        
        for i, statute in enumerate(statutes, 1):
            try:
                # Create text to embed
                text = f"{statute.title}. {statute.text[:2000]}"
                
                # Generate embedding
                response = client.embeddings.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
                
                # Save embedding
                statute.embedding = response.data[0].embedding
                statute.save(update_fields=['embedding'])
                
                if i % 10 == 0:
                    self.stdout.write(f'Processed {i}/{total} statutes')
                
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error processing statute {statute.id}: {str(e)}')
                )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generated embeddings for {total} statutes'))


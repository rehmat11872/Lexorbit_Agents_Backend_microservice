from django.core.management.base import BaseCommand
from data_ingestion.ingestion_manager import ingestion_manager


class Command(BaseCommand):
    help = 'Fetch complete judge data including all cases, opinions, and citations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--judge-id',
            type=int,
            required=True,
            help='Judge ID from CourtListener',
        )
        parser.add_argument(
            '--max-opinions',
            type=int,
            default=None,
            help='Maximum number of opinions to fetch',
        )
    
    def handle(self, *args, **options):
        judge_id = options['judge_id']
        max_opinions = options['max_opinions']
        
        self.stdout.write(self.style.SUCCESS(f'Fetching complete data for judge {judge_id}...'))
        
        try:
            judge = ingestion_manager.ingest_judge_complete(judge_id, max_opinions=max_opinions)
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully ingested complete data for {judge.full_name}'))
            self.stdout.write(f'   - Positions: {len(judge.positions)}')
            self.stdout.write(f'   - Opinions: {judge.authored_opinions.count()}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error during ingestion: {str(e)}'))

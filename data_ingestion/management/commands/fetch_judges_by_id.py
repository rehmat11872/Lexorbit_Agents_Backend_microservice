from django.core.management.base import BaseCommand
from data_ingestion.courtlistener_service import courtlistener_service
from data_ingestion.data_processors import data_processor
from court_data.models import Judge


class Command(BaseCommand):
    help = 'Fetch judges by specific ID range from CourtListener API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--start-id',
            type=int,
            default=1,
            help='Starting judge ID',
        )
        parser.add_argument(
            '--end-id',
            type=int,
            default=100,
            help='Ending judge ID',
        )
    
    def handle(self, *args, **options):
        start_id = options['start_id']
        end_id = options['end_id']
        
        self.stdout.write(f'Fetching judges from ID {start_id} to {end_id}')
        
        count = 0
        for judge_id in range(start_id, end_id + 1):
            try:
                judge_data = courtlistener_service.fetch_judge_by_id(judge_id)
                if judge_data:
                    result = data_processor.process_judge(judge_data)
                    if result:
                        count += 1
                        self.stdout.write(f'Fetched: {result.full_name} (ID: {judge_id})')
            except Exception as e:
                continue  # Skip missing judges
        
        self.stdout.write(self.style.SUCCESS(f'Successfully fetched {count} judges'))
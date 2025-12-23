from django.core.management.base import BaseCommand
from data_ingestion.courtlistener_service import courtlistener_service
from data_ingestion.data_processors import data_processor


class Command(BaseCommand):
    help = 'Fetch judges from CourtListener API and save to database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-results',
            type=int,
            default=None,
            help='Maximum number of judges to fetch (default: all)',
        )
        parser.add_argument(
            '--name',
            type=str,
            default=None,
            help='Filter judges by name',
        )
        parser.add_argument(
            '--court',
            type=str,
            default=None,
            help='Filter judges by court',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force fetch even if judges exist (will update existing)',
        )
    
    def handle(self, *args, **options):
        from django.db import connection
        from court_data.models import Judge
        
        self.stdout.write(f'Database: {connection.settings_dict["NAME"]} on {connection.settings_dict["HOST"]}')
        
        # Get existing judge IDs to skip duplicates
        existing_ids = set(Judge.objects.values_list('judge_id', flat=True))
        self.stdout.write(f'Found {len(existing_ids)} existing judges in database')
        
        max_results = options['max_results']
        filters = {}
        
        if options['name']:
            filters['name'] = options['name']
        if options['court']:
            filters['court'] = options['court']
        
        self.stdout.write(self.style.SUCCESS('Starting to fetch judges from CourtListener...'))
        if filters:
            self.stdout.write(f'Filters: {filters}')
        
        count = 0
        skipped = 0
        try:
            # Try different approach - fetch judges from specific courts or with filters
            if not filters.get('court'):
                filters['court'] = 'ca9'  # 9th Circuit Court of Appeals
            
            for judge_data in courtlistener_service.fetch_judges(max_results=max_results*5, **filters):
                try:
                    judge_id = judge_data.get('id') if isinstance(judge_data, dict) else None
                    
                    if not options['force'] and judge_id in existing_ids:
                        skipped += 1
                        continue  # Skip existing judges unless force is used
                    
                    result = data_processor.process_judge(judge_data)
                    if result:
                        count += 1
                        self.stdout.write(f'NEW judge: {result.full_name} (ID: {result.judge_id})')
                        
                        if count >= max_results:
                            break  # Stop when we have enough new judges
                    
                    if count % 10 == 0:
                        self.stdout.write(f'Processed {count} new judges...')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing judge {judge_data.get("id")}: {str(e)}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully fetched {count} NEW judges (skipped {skipped} existing)')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching judges: {str(e)}')
            )


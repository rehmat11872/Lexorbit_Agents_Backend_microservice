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
    
    def handle(self, *args, **options):
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
        try:
            for judge_data in courtlistener_service.fetch_judges(max_results=max_results, **filters):
                try:
                    data_processor.process_judge(judge_data)
                    count += 1
                    
                    if count % 10 == 0:
                        self.stdout.write(f'Processed {count} judges...')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing judge {judge_data.get("id")}: {str(e)}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully fetched and saved {count} judges')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching judges: {str(e)}')
            )


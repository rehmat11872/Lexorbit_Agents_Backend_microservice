from django.core.management.base import BaseCommand
from data_ingestion.courtlistener_service import courtlistener_service
from data_ingestion.data_processors import data_processor


class Command(BaseCommand):
    help = 'Fetch cases (dockets) from CourtListener API and save to database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-results',
            type=int,
            default=None,
            help='Maximum number of cases to fetch (default: all)',
        )
        parser.add_argument(
            '--court',
            type=str,
            default=None,
            help='Filter by court ID',
        )
        parser.add_argument(
            '--date-filed-after',
            type=str,
            default=None,
            help='Filter by cases filed after this date (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--case-name',
            type=str,
            default=None,
            help='Filter by case name (partial match)',
        )
    
    def handle(self, *args, **options):
        max_results = options['max_results']
        filters = {}
        
        if options['court']:
            filters['court'] = options['court']
        if options['date_filed_after']:
            filters['date_filed__gte'] = options['date_filed_after']
        if options['case_name']:
            filters['case_name__icontains'] = options['case_name']
        
        self.stdout.write(self.style.SUCCESS('Starting to fetch cases from CourtListener...'))
        if filters:
            self.stdout.write(f'Filters: {filters}')
        
        count = 0
        try:
            for docket_data in courtlistener_service.fetch_dockets(max_results=max_results, **filters):
                try:
                    docket = data_processor.process_docket(docket_data)
                    if docket:
                        count += 1
                        
                        if count % 10 == 0:
                            self.stdout.write(f'Processed {count} cases...')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing case {docket_data.get("id")}: {str(e)}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully fetched and saved {count} cases')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching cases: {str(e)}')
            )


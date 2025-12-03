from django.core.management.base import BaseCommand
from data_ingestion.courtlistener_service import courtlistener_service
from data_ingestion.data_processors import data_processor


class Command(BaseCommand):
    help = 'Fetch all courts from CourtListener API and save to database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-results',
            type=int,
            default=None,
            help='Maximum number of courts to fetch (default: all)',
        )
    
    def handle(self, *args, **options):
        max_results = options['max_results']
        
        self.stdout.write(self.style.SUCCESS('Starting to fetch courts from CourtListener...'))
        
        count = 0
        try:
            for court_data in courtlistener_service.fetch_courts(max_results=max_results):
                try:
                    data_processor.process_court(court_data)
                    count += 1
                    
                    if count % 10 == 0:
                        self.stdout.write(f'Processed {count} courts...')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing court {court_data.get("id")}: {str(e)}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully fetched and saved {count} courts')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching courts: {str(e)}')
            )


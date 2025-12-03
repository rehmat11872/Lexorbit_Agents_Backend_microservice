from django.core.management.base import BaseCommand
from data_ingestion.courtlistener_service import courtlistener_service
from data_ingestion.data_processors import data_processor
from court_data.models import Docket


class Command(BaseCommand):
    help = 'Fetch opinions from CourtListener API and save to database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-results',
            type=int,
            default=None,
            help='Maximum number of opinions to fetch (default: all)',
        )
        parser.add_argument(
            '--docket-id',
            type=int,
            default=None,
            help='Fetch opinions for a specific docket ID',
        )
        parser.add_argument(
            '--author',
            type=int,
            default=None,
            help='Filter by judge ID (author)',
        )
        parser.add_argument(
            '--date-filed-after',
            type=str,
            default=None,
            help='Filter by opinions filed after this date (YYYY-MM-DD)',
        )
    
    def handle(self, *args, **options):
        max_results = options['max_results']
        docket_id = options['docket_id']
        
        if docket_id:
            # Fetch opinions for specific docket
            self.stdout.write(f'Fetching opinions for docket {docket_id}...')
            try:
                docket = Docket.objects.get(docket_id=docket_id)
                opinions_data = courtlistener_service.fetch_opinions_by_docket(docket_id)
                
                count = 0
                for opinion_data in opinions_data:
                    try:
                        data_processor.process_opinion(opinion_data, docket=docket)
                        count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error processing opinion: {str(e)}')
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully fetched and saved {count} opinions for docket {docket_id}')
                )
                
            except Docket.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Docket {docket_id} not found in database')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error fetching opinions: {str(e)}')
                )
        else:
            # Fetch opinions with filters
            filters = {}
            if options['author']:
                filters['author'] = options['author']
            if options['date_filed_after']:
                filters['date_filed__gte'] = options['date_filed_after']
            
            self.stdout.write(self.style.SUCCESS('Starting to fetch opinions from CourtListener...'))
            if filters:
                self.stdout.write(f'Filters: {filters}')
            
            count = 0
            skipped = 0
            try:
                # First fetch opinion clusters
                for cluster_data in courtlistener_service.fetch_opinion_clusters(max_results=max_results, **filters):
                    try:
                        # Get docket for this cluster
                        docket_url = cluster_data.get('docket')
                        if not docket_url:
                            skipped += 1
                            continue
                        
                        docket_id = docket_url.split('/')[-2] if isinstance(docket_url, str) else docket_url
                        
                        try:
                            docket = Docket.objects.get(docket_id=docket_id)
                        except Docket.DoesNotExist:
                            skipped += 1
                            continue
                        
                        # Fetch opinions for this cluster
                        cluster_id = cluster_data.get('id')
                        opinions_data = list(courtlistener_service._paginate('opinions', params={'cluster': cluster_id}))
                        
                        for opinion_data in opinions_data:
                            try:
                                data_processor.process_opinion(opinion_data, docket=docket)
                                count += 1
                                
                                if count % 10 == 0:
                                    self.stdout.write(f'Processed {count} opinions...')
                            except Exception as e:
                                self.stdout.write(
                                    self.style.WARNING(f'Error processing opinion: {str(e)}')
                                )
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Error processing cluster: {str(e)}')
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully fetched and saved {count} opinions (skipped {skipped} without dockets)'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error fetching opinions: {str(e)}')
                )


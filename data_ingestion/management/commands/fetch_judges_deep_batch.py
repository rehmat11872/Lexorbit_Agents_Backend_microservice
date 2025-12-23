from django.core.management.base import BaseCommand
from data_ingestion.courtlistener_service import courtlistener_service
from data_ingestion.ingestion_manager import ingestion_manager


class Command(BaseCommand):
    help = 'Bulk fetch multiple judges with their COMPLETE history (bio, education, positions, cases, opinions)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of judges to fetch in this batch (default: 10)',
        )
        parser.add_argument(
            '--max-opinions-per-judge',
            type=int,
            default=20,
            help='Max opinions to fetch for each judge (default: 20)',
        )
        parser.add_argument(
            '--court',
            type=str,
            default=None,
            help='Filter judges by court ID',
        )
        parser.add_argument(
            '--name',
            type=str,
            default=None,
            help='Filter judges by name',
        )
    
    def handle(self, *args, **options):
        limit = options['limit']
        max_opinions = options['max_opinions_per_judge']
        
        filters = {}
        if options['court']:
            filters['court'] = options['court']
        if options['name']:
            filters['name'] = options['name']
            
        self.stdout.write(self.style.SUCCESS(f'🚀 Starting Deep Batch Fetch for {limit} judges...'))
        
        count = 0
        try:
            # 1. Discover judges using the People API
            judges_to_fetch = list(courtlistener_service.fetch_judges(max_results=limit, **filters))
            self.stdout.write(f'✅ Discovered {len(judges_to_fetch)} judges matching criteria.\n')
            
            for judge_basic_data in judges_to_fetch:
                judge_id = judge_basic_data.get('id')
                judge_name = f"{judge_basic_data.get('name_first', '')} {judge_basic_data.get('name_last', '')}"
                
                self.stdout.write(f'[{count+1}/{len(judges_to_fetch)}] Processing {judge_name} (ID: {judge_id})...')
                
                try:
                    # 2. Perform deep ingestion using the IngestionManager
                    ingestion_manager.ingest_judge_complete(judge_id, max_opinions=max_opinions)
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'   ✓ Successfully ingested {judge_name}\n'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Error processing judge {judge_id}: {str(e)}\n'))
                    continue
            
            self.stdout.write(self.style.SUCCESS(f'🎊 Batch complete! Successfully ingested {count} judges.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'CRITICAL ERROR during batch process: {str(e)}'))

# from django.core.management.base import BaseCommand
# from data_ingestion.courtlistener_service import courtlistener_service
# from data_ingestion.ingestion_manager import ingestion_manager


# class Command(BaseCommand):
#     help = 'Bulk fetch multiple judges with their COMPLETE history (bio, education, positions, cases, opinions)'
    
#     def add_arguments(self, parser):
#         parser.add_argument(
#             '--limit',
#             type=int,
#             default=10,
#             help='Maximum number of judges to fetch in this batch (default: 10)',
#         )
#         parser.add_argument(
#             '--max-opinions-per-judge',
#             type=int,
#             default=20,
#             help='Max opinions to fetch for each judge (default: 20)',
#         )
#         parser.add_argument(
#             '--court',
#             type=str,
#             default=None,
#             help='Filter judges by court ID',
#         )
#         parser.add_argument(
#             '--name',
#             type=str,
#             default=None,
#             help='Filter judges by name',
#         )
    
#     def handle(self, *args, **options):
#         limit = options['limit']
#         max_opinions = options['max_opinions_per_judge']
        
#         filters = {}
#         if options['court']:
#             filters['court'] = options['court']
#         if options['name']:
#             filters['name'] = options['name']
            
#         self.stdout.write(self.style.SUCCESS(f'🚀 Starting Deep Batch Fetch for {limit} judges...'))
        
#         count = 0
#         try:
#             # 1. Discover judges using the People API
#             judges_to_fetch = list(courtlistener_service.fetch_judges(max_results=limit, **filters))
#             self.stdout.write(f'✅ Discovered {len(judges_to_fetch)} judges matching criteria.\n')
            
#             for judge_basic_data in judges_to_fetch:
#                 judge_id = judge_basic_data.get('id')
#                 judge_name = f"{judge_basic_data.get('name_first', '')} {judge_basic_data.get('name_last', '')}"
                
#                 self.stdout.write(f'[{count+1}/{len(judges_to_fetch)}] Processing {judge_name} (ID: {judge_id})...')
                
#                 try:
#                     # 2. Perform deep ingestion using the IngestionManager
#                     ingestion_manager.ingest_judge_complete(judge_id, max_opinions=max_opinions)
#                     count += 1
#                     self.stdout.write(self.style.SUCCESS(f'   ✓ Successfully ingested {judge_name}\n'))
#                 except Exception as e:
#                     self.stdout.write(self.style.ERROR(f'   ❌ Error processing judge {judge_id}: {str(e)}\n'))
#                     continue
            
#             self.stdout.write(self.style.SUCCESS(f'🎊 Batch complete! Successfully ingested {count} judges.'))
            
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f'CRITICAL ERROR during batch process: {str(e)}'))


from django.core.management.base import BaseCommand
from data_ingestion.courtlistener_service import courtlistener_service
from data_ingestion.ingestion_manager import ingestion_manager
from court_data.models import Judge


class Command(BaseCommand):
    help = 'Bulk fetch multiple judges with their COMPLETE history (bio, education, positions, cases, opinions) - skips existing judges'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of NEW judges to fetch in this batch (default: 10)',
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
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Re-fetch and update existing judges instead of skipping them',
        )
    
    def handle(self, *args, **options):
        limit = options['limit']
        max_opinions = options['max_opinions_per_judge']
        force_update = options['force_update']
        
        filters = {}
        if options['court']:
            filters['court'] = options['court']
        if options['name']:
            filters['name'] = options['name']
        
        # Get existing judge IDs from database
        existing_judge_ids = set(Judge.objects.values_list('judge_id', flat=True))
        self.stdout.write(f'📊 Currently have {len(existing_judge_ids)} judges in database')
        
        if force_update:
            self.stdout.write(self.style.WARNING('⚠️  Force update mode: will re-fetch existing judges'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Skip mode: will only fetch NEW judges'))
        
        self.stdout.write(self.style.SUCCESS(f'\n🚀 Starting Deep Batch Fetch for {limit} {"new " if not force_update else ""}judges...\n'))
        
        new_count = 0
        skipped_count = 0
        updated_count = 0
        page = 1
        
        try:
            while new_count < limit:
                self.stdout.write(f'📄 Fetching page {page} from CourtListener API...')
                
                # Fetch judges with pagination
                page_filters = filters.copy()
                page_filters['page'] = page
                
                # Get one page of results
                judges_page = []
                for judge_data in courtlistener_service.fetch_judges(max_results=20, **page_filters):
                    judges_page.append(judge_data)
                
                if not judges_page:
                    self.stdout.write(self.style.WARNING('   No more judges available from API'))
                    break
                
                self.stdout.write(f'   Found {len(judges_page)} judges on page {page}')
                
                # Process each judge on this page
                for judge_basic_data in judges_page:
                    judge_id = judge_basic_data.get('id')
                    judge_name = f"{judge_basic_data.get('name_first', '')} {judge_basic_data.get('name_last', '')}"
                    
                    # Skip logic: check if judge already exists
                    if judge_id in existing_judge_ids and not force_update:
                        skipped_count += 1
                        self.stdout.write(f'   ⏭️  Skipping existing judge: {judge_name} (ID: {judge_id})')
                        continue
                    
                    # Process judge
                    is_update = judge_id in existing_judge_ids
                    action_prefix = "Updating" if is_update else "Processing NEW"
                    
                    self.stdout.write(f'\n[{new_count + 1}/{limit}] {action_prefix} judge: {judge_name} (ID: {judge_id})...')
                    
                    try:
                        # Perform deep ingestion
                        ingestion_manager.ingest_judge_complete(judge_id, max_opinions=max_opinions)
                        
                        if is_update:
                            updated_count += 1
                            self.stdout.write(self.style.SUCCESS(f'   ✓ Successfully updated {judge_name}'))
                        else:
                            new_count += 1
                            existing_judge_ids.add(judge_id)  # Track so we don't process again in this run
                            self.stdout.write(self.style.SUCCESS(f'   ✓ Successfully ingested NEW judge {judge_name}'))
                        
                        # Check if we've reached the limit of NEW judges
                        if new_count >= limit:
                            break
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'   ❌ Error processing judge {judge_id}: {str(e)}'))
                        continue
                
                # Check if we've reached the limit
                if new_count >= limit:
                    break
                
                # Move to next page
                page += 1
            
            # Final summary
            self.stdout.write('\n' + '='*70)
            self.stdout.write(self.style.SUCCESS(f'🎊 Batch Complete!'))
            self.stdout.write(f'   📊 Statistics:')
            self.stdout.write(f'      • New judges ingested: {new_count}')
            if force_update:
                self.stdout.write(f'      • Existing judges updated: {updated_count}')
            else:
                self.stdout.write(f'      • Existing judges skipped: {skipped_count}')
            self.stdout.write(f'      • Total judges in database: {Judge.objects.count()}')
            self.stdout.write('='*70)
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n\n⚠️  Process interrupted by user'))
            self.stdout.write(f'   Processed {new_count} new judges before interruption')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ CRITICAL ERROR during batch process: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())

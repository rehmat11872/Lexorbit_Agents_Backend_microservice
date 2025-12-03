from django.core.management.base import BaseCommand
from data_ingestion.courtlistener_service import courtlistener_service
from data_ingestion.data_processors import data_processor
from court_data.models import Judge, Court


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
            # Step 1: Fetch judge basic info
            self.stdout.write('\n1️⃣  Fetching judge information...')
            judge_data = courtlistener_service.fetch_judge_by_id(judge_id)
            judge = data_processor.process_judge(judge_data)
            self.stdout.write(self.style.SUCCESS(f'   ✓ Judge: {judge.full_name}'))
            self.stdout.write(f'   - Gender: {judge.gender}')
            self.stdout.write(f'   - Birth: {judge.date_birth}')
            self.stdout.write(f'   - Location: {judge.dob_city}, {judge.dob_state}')
            if judge.biography:
                self.stdout.write(f'   - Bio: {judge.biography[:100]}...')
            else:
                self.stdout.write('   - Bio: (none in CourtListener)')
            
            # Step 2: Fetch judge positions
            self.stdout.write('\n2️⃣  Fetching judge positions/appointments...')
            positions = courtlistener_service.fetch_judge_positions(judge_id)
            self.stdout.write(f'   ✓ Found {len(positions)} positions')
            
            # Display positions with better info
            position_types = {
                'Judge': 'Judge',
                'jud-gt-judge': 'Judge',
                'jud-ap-judge': 'Appellate Judge',
                'jud-dc-judge': 'District Court Judge',
                'jud-mag-judge': 'Magistrate Judge',
                'jud-cc-judge': 'Circuit Court Judge',
                'jud-tc-judge': 'Trial Court Judge',
                'pres': 'President',
                'sen': 'Senator',
                'rep': 'Representative',
                'att-gen': 'Attorney General',
                'c-jud': 'Chief Judge',
                'jus': 'Justice',
                'c-jus': 'Chief Justice',
                'act-jus': 'Acting Justice',
                'ret-jus': 'Retired Justice',
                'prac': 'Private Practice',
                'prof': 'Professor',
                'pros': 'Prosecutor',
                'pub_def': 'Public Defender',
            }
            
            for pos in positions[:5]:  # Show first 5 positions
                position_type = pos.get('position_type', 'Unknown')
                position_name = position_types.get(position_type, position_type)
                date_start = pos.get('date_start', 'Unknown')
                date_end = pos.get('date_termination', 'Present')
                
                # Try to get court info if available
                court_id = pos.get('court', {})
                if isinstance(court_id, dict):
                    court_name = court_id.get('short_name', 'Unknown Court')
                elif isinstance(court_id, str) and '/' in court_id:
                    # It's a URL, extract ID
                    court_id_str = court_id.split('/')[-2] if court_id else 'Unknown'
                    court_name = f"Court {court_id_str}"
                else:
                    court_name = 'Unknown Court'
                
                self.stdout.write(f'   - {position_name} at {court_name}')
                self.stdout.write(f'     ({date_start} to {date_end})')
            
            # Step 3: Fetch opinions authored by this judge
            self.stdout.write('\n3️⃣  Fetching opinions authored by judge...')
            opinions_data = list(courtlistener_service.fetch_opinions(
                author=judge_id,
                max_results=max_opinions
            ))
            self.stdout.write(f'   ✓ Found {len(opinions_data)} opinions')
            
            # Step 4: Process each opinion and its related case
            self.stdout.write('\n4️⃣  Processing opinions and cases...')
            opinions_processed = 0
            cases_processed = 0
            
            for opinion_data in opinions_data:
                try:
                    # Get cluster (opinion group)
                    cluster_url = opinion_data.get('cluster')
                    if not cluster_url:
                        continue
                    
                    cluster_id = int(cluster_url.split('/')[-2])
                    
                    # Fetch cluster to get docket info
                    cluster_data = courtlistener_service._make_request(f'clusters/{cluster_id}')
                    
                    # Get docket (case) info
                    docket_url = cluster_data.get('docket')
                    if not docket_url:
                        continue
                    
                    docket_id = int(docket_url.split('/')[-2])
                    docket_data = courtlistener_service.fetch_docket_by_id(docket_id)
                    
                    # Step 1: Process docket (case)
                    docket = data_processor.process_docket(docket_data)
                    if docket:
                        cases_processed += 1
                        self.stdout.write(f'   ✓ Case: {docket.case_name_short}')
                        self.stdout.write(f'     - Type: {docket.nature_of_suit or "Unknown"}')
                        self.stdout.write(f'     - Court: {docket.court.short_name if docket.court else "Unknown"}')
                        self.stdout.write(f'     - Filed: {docket.date_filed}')
                    
                    # Step 2: Process cluster (links docket to opinions)
                    cluster = data_processor.process_opinion_cluster(cluster_data, docket=docket)
                    if not cluster:
                        self.stdout.write(self.style.WARNING(f'   ✗ Failed to create cluster {cluster_id}'))
                        continue
                    
                    # Step 3: Process opinion (links to cluster)
                    opinion = data_processor.process_opinion(opinion_data, cluster=cluster)
                    if opinion:
                        opinions_processed += 1
                    
                    # Create judge-docket relationship
                    if docket:
                        data_processor.process_judge_docket_relation(
                            judge=judge,
                            docket=docket,
                            role='author'
                        )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'   ✗ Error processing opinion: {str(e)}')
                    )
            
            # Step 5: Summary
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('✓ COMPLETE DATA FETCHED!'))
            self.stdout.write('='*60)
            self.stdout.write(f'\nJudge: {judge.full_name}')
            self.stdout.write(f'  - Positions: {len(positions)}')
            self.stdout.write(f'  - Cases: {cases_processed}')
            self.stdout.write(f'  - Opinions: {opinions_processed}')
            
            self.stdout.write('\n📊 View complete data:')
            self.stdout.write(f'   API: http://localhost:8000/api/judges/{judge.id}/')
            self.stdout.write(f'   Analytics: http://localhost:8000/api/judges/{judge.id}/analytics/')
            self.stdout.write(f'   Cases: http://localhost:8000/api/judges/{judge.id}/cases/')
            self.stdout.write(f'   Admin: http://localhost:8000/admin/court_data/judge/{judge.id}/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )


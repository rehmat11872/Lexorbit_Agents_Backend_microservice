from django.core.management.base import BaseCommand
from data_ingestion.courtlistener_service import courtlistener_service
from data_ingestion.data_processors import data_processor
from court_data.models import Opinion


class Command(BaseCommand):
    help = 'Fetch citation relationships from CourtListener API and save to database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-results',
            type=int,
            default=None,
            help='Maximum number of citation relationships to fetch (default: all)',
        )
        parser.add_argument(
            '--opinion-id',
            type=int,
            default=None,
            help='Fetch citations for a specific opinion ID',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update citations for all existing opinions in database',
        )
    
    def handle(self, *args, **options):
        max_results = options['max_results']
        opinion_id = options['opinion_id']
        update_existing = options['update_existing']
        
        if opinion_id:
            # Fetch citations for specific opinion
            self.stdout.write(f'Fetching citations for opinion {opinion_id}...')
            try:
                citations_data = courtlistener_service.fetch_citations_for_opinion(opinion_id)
                count = self._process_citations_for_opinion(opinion_id, citations_data)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully processed {count} citations for opinion {opinion_id}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error fetching citations: {str(e)}')
                )
        
        elif update_existing:
            # Update citations for all opinions in database
            self.stdout.write('Updating citations for all opinions in database...')
            
            opinions = Opinion.objects.all()
            total = opinions.count()
            processed = 0
            total_citations = 0
            
            for opinion in opinions:
                try:
                    citations_data = courtlistener_service.fetch_citations_for_opinion(opinion.opinion_id)
                    count = self._process_citations_for_opinion(opinion.opinion_id, citations_data)
                    total_citations += count
                    processed += 1
                    
                    if processed % 10 == 0:
                        self.stdout.write(f'Processed {processed}/{total} opinions, {total_citations} total citations...')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error processing opinion {opinion.opinion_id}: {str(e)}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated citations for {processed} opinions ({total_citations} total citations)'
                )
            )
        
        else:
            # Fetch all citations
            self.stdout.write(self.style.SUCCESS('Starting to fetch citations from CourtListener...'))
            
            count = 0
            skipped = 0
            try:
                for citation_data in courtlistener_service.fetch_opinion_citations(max_results=max_results):
                    try:
                        citing_opinion_id = citation_data.get('citing_opinion')
                        cited_opinion_id = citation_data.get('cited_opinion')
                        
                        if not citing_opinion_id or not cited_opinion_id:
                            skipped += 1
                            continue
                        
                        # Extract IDs if they're URLs
                        if isinstance(citing_opinion_id, str):
                            citing_opinion_id = int(citing_opinion_id.split('/')[-2])
                        if isinstance(cited_opinion_id, str):
                            cited_opinion_id = int(cited_opinion_id.split('/')[-2])
                        
                        citation = data_processor.process_citation(
                            source_opinion_id=citing_opinion_id,
                            target_opinion_id=cited_opinion_id,
                            citation_type='cites_to',
                        )
                        
                        if citation:
                            count += 1
                            
                            if count % 50 == 0:
                                self.stdout.write(f'Processed {count} citations...')
                        else:
                            skipped += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Error processing citation: {str(e)}')
                        )
                        skipped += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully fetched and saved {count} citations (skipped {skipped})'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error fetching citations: {str(e)}')
                )
    
    def _process_citations_for_opinion(self, opinion_id: int, citations_data: dict) -> int:
        """Process citation data for a single opinion"""
        count = 0
        
        # Process cites_to
        for citation in citations_data.get('cites_to', []):
            try:
                cited_opinion_id = citation.get('cited_opinion')
                if isinstance(cited_opinion_id, str):
                    cited_opinion_id = int(cited_opinion_id.split('/')[-2])
                
                data_processor.process_citation(
                    source_opinion_id=opinion_id,
                    target_opinion_id=cited_opinion_id,
                    citation_type='cites_to',
                )
                count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error processing cites_to citation: {str(e)}')
                )
        
        # Process cited_by
        for citation in citations_data.get('cited_by', []):
            try:
                citing_opinion_id = citation.get('citing_opinion')
                if isinstance(citing_opinion_id, str):
                    citing_opinion_id = int(citing_opinion_id.split('/')[-2])
                
                data_processor.process_citation(
                    source_opinion_id=citing_opinion_id,
                    target_opinion_id=opinion_id,
                    citation_type='cited_by',
                )
                count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error processing cited_by citation: {str(e)}')
                )
        
        return count


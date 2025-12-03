from django.core.management.base import BaseCommand
from data_ingestion.data_processors import DataProcessor
from datetime import datetime


class Command(BaseCommand):
    help = 'Load sample data for testing (no API required)'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading sample data...'))
        
        # Sample court data
        courts_data = [
            {
                'id': 'ca9',
                'full_name': 'Court of Appeals for the Ninth Circuit',
                'short_name': 'CA9',
                'jurisdiction': 'F',
                'position': 'Appellate',
                'citation_string': 'CA9',
                'notes': 'Federal appellate court'
            },
            {
                'id': 'dcd',
                'full_name': 'U.S. District Court for the District of Columbia',
                'short_name': 'D.D.C.',
                'jurisdiction': 'FD',
                'position': 'District',
                'citation_string': 'D.D.C.',
                'notes': 'Federal district court'
            },
            {
                'id': 'scotus',
                'full_name': 'Supreme Court of the United States',
                'short_name': 'SCOTUS',
                'jurisdiction': 'F',
                'position': 'Supreme',
                'citation_string': 'U.S.',
                'notes': 'Highest federal court'
            },
        ]
        
        # Sample judge data with full details
        judges_data = [
            {
                'id': 10001,
                'name_first': 'Ruth',
                'name_middle': 'Bader',
                'name_last': 'Ginsburg',
                'name_suffix': '',
                'date_dob': '1933-03-15',
                'date_dod': '2020-09-18',
                'gender': 'f',
                'race': ['w'],
                'dob_city': 'Brooklyn',
                'dob_state': 'NY',
                'bio': 'Ruth Bader Ginsburg was an Associate Justice of the Supreme Court. She served from 1993 to 2020 and was known for her advocacy for gender equality and civil rights.',
                'educations': [
                    {'school': {'name': 'Harvard Law School'}, 'degree_level': 'JD', 'degree_year': 1959},
                    {'school': {'name': 'Columbia Law School'}, 'degree_level': 'JD', 'degree_year': 1959},
                ],
            },
            {
                'id': 10002,
                'name_first': 'Sonia',
                'name_middle': '',
                'name_last': 'Sotomayor',
                'name_suffix': '',
                'date_dob': '1954-06-25',
                'gender': 'f',
                'race': ['h'],
                'dob_city': 'Bronx',
                'dob_state': 'NY',
                'bio': 'Sonia Sotomayor is an Associate Justice of the Supreme Court, serving since 2009. She was the first Hispanic and Latina justice.',
                'educations': [
                    {'school': {'name': 'Yale Law School'}, 'degree_level': 'JD', 'degree_year': 1979},
                ],
            },
            {
                'id': 10003,
                'name_first': 'Merrick',
                'name_middle': 'Brian',
                'name_last': 'Garland',
                'name_suffix': '',
                'date_dob': '1952-11-13',
                'gender': 'm',
                'race': ['w'],
                'dob_city': 'Chicago',
                'dob_state': 'IL',
                'bio': 'Merrick Garland serves as the 86th United States Attorney General. He previously served as Chief Judge of the U.S. Court of Appeals for the D.C. Circuit.',
                'educations': [
                    {'school': {'name': 'Harvard Law School'}, 'degree_level': 'JD', 'degree_year': 1977},
                ],
            },
        ]
        
        # Sample case/docket data
        dockets_data = [
            {
                'id': 20001,
                'case_name': 'Brown v. Board of Education',
                'case_name_short': 'Brown v. Board of Education',
                'case_name_full': 'Brown v. Board of Education of Topeka',
                'docket_number': '1',
                'date_filed': '1952-10-08',
                'date_terminated': '1954-05-17',
                'nature_of_suit': 'Civil Rights',
                'cause': 'Racial segregation in public schools',
                'jurisdiction_type': 'Federal Question',
                'court': 'scotus',
                'parties': [
                    {'name': 'Oliver Brown', 'type': 'Plaintiff'},
                    {'name': 'Board of Education of Topeka', 'type': 'Defendant'},
                ],
            },
            {
                'id': 20002,
                'case_name': 'Miranda v. Arizona',
                'case_name_short': 'Miranda v. Arizona',
                'case_name_full': 'Miranda v. Arizona',
                'docket_number': '759',
                'date_filed': '1965-02-01',
                'date_terminated': '1966-06-13',
                'nature_of_suit': 'Criminal',
                'cause': 'Self-incrimination and right to counsel',
                'jurisdiction_type': 'Federal Question',
                'court': 'scotus',
                'parties': [
                    {'name': 'Ernesto Miranda', 'type': 'Petitioner'},
                    {'name': 'State of Arizona', 'type': 'Respondent'},
                ],
            },
            {
                'id': 20003,
                'case_name': 'United States v. Nixon',
                'case_name_short': 'United States v. Nixon',
                'case_name_full': 'United States v. Richard Nixon',
                'docket_number': '73-1766',
                'date_filed': '1974-05-24',
                'date_terminated': '1974-07-24',
                'nature_of_suit': 'Executive Privilege',
                'cause': 'Presidential privilege and subpoena compliance',
                'jurisdiction_type': 'Federal Question',
                'court': 'scotus',
                'parties': [
                    {'name': 'United States', 'type': 'Petitioner'},
                    {'name': 'Richard Nixon', 'type': 'Respondent'},
                ],
            },
        ]
        
        # Sample opinions
        opinions_data = [
            {
                'id': 30001,
                'cluster': 20001,
                'type': '010combined',
                'author': 10001,
                'plain_text': 'We conclude that in the field of public education the doctrine of "separate but equal" has no place. Separate educational facilities are inherently unequal.',
                'date_filed': '1954-05-17',
                'page_count': 11,
            },
            {
                'id': 30002,
                'cluster': 20002,
                'type': '010combined',
                'author': 10002,
                'plain_text': 'The person in custody must, prior to interrogation, be clearly informed that he has the right to remain silent, and that anything he says will be used against him in court.',
                'date_filed': '1966-06-13',
                'page_count': 60,
            },
        ]
        
        # Process courts
        self.stdout.write('Creating courts...')
        for court_data in courts_data:
            court = DataProcessor.process_court(court_data)
            self.stdout.write(f'  ✓ {court.name}')
        
        # Process judges
        self.stdout.write('\nCreating judges...')
        for judge_data in judges_data:
            judge = DataProcessor.process_judge(judge_data)
            self.stdout.write(f'  ✓ {judge.full_name}')
        
        # Process dockets
        self.stdout.write('\nCreating cases...')
        for docket_data in dockets_data:
            docket = DataProcessor.process_docket(docket_data)
            if docket:
                self.stdout.write(f'  ✓ {docket.case_name_short}')
        
        # Process opinions
        self.stdout.write('\nCreating opinions...')
        from court_data.models import Docket, Judge
        for opinion_data in opinions_data:
            try:
                docket = Docket.objects.get(docket_id=opinion_data['cluster'])
                opinion = DataProcessor.process_opinion(opinion_data, docket=docket)
                if opinion:
                    self.stdout.write(f'  ✓ Opinion for {opinion.docket.case_name_short}')
            except Exception as e:
                self.stdout.write(f'  ✗ Error: {str(e)}')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✓ Sample data loaded successfully!'))
        self.stdout.write('='*60)
        self.stdout.write('\nYou now have:')
        self.stdout.write('  - 3 Courts (SCOTUS, CA9, D.D.C.)')
        self.stdout.write('  - 3 Judges (Ginsburg, Sotomayor, Garland)')
        self.stdout.write('  - 3 Famous Cases (Brown, Miranda, Nixon)')
        self.stdout.write('  - 2 Opinions')
        self.stdout.write('\nView in Django Admin: http://localhost:8000/admin/')


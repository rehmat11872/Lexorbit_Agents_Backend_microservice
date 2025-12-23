import csv
import os
import logging
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from court_data.models import Judge
from data_ingestion.data_processors import data_processor

logger = logging.getLogger(__name__)


def normalize_school_name(name: str) -> str:
    """Normalize school names for deduplication"""
    if not name:
        return ''
    name = name.strip().lower()
    # Common variations
    name = name.replace(' school of law', ' law school')
    name = name.replace('yale college', 'yale university')
    name = name.replace('harvard college', 'harvard university')
    return name


def deduplicate_education(education_list: list) -> list:
    """Remove duplicate education entries based on normalized school + degree"""
    seen = set()
    unique = []
    for edu in education_list:
        school = normalize_school_name(edu.get('school', ''))
        degree = (edu.get('degree_level') or edu.get('degree') or '').lower()
        year = str(edu.get('degree_year') or edu.get('year') or '')
        key = f"{school}|{degree}|{year}"
        if key not in seen:
            seen.add(key)
            unique.append(edu)
    return unique


class Command(BaseCommand):
    help = 'Enrich judge data using FJC judges.csv (FALLBACK only - does not overwrite existing data)'

    def add_arguments(self, parser):
        parser.add_argument('--csv-path', type=str, default='judges.csv', help='Path to judges.csv')
        parser.add_argument('--dry-run', action='store_true', help='Do not save changes')
        parser.add_argument('--force', action='store_true', help='Overwrite existing data')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        dry_run = options['dry_run']
        force = options['force']

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"CSV file not found: {csv_path}"))
            return

        self.stdout.write(f"Enriching judges from {csv_path} (fallback mode)...")

        updated_count = 0
        not_found_count = 0

        try:
            with open(csv_path, mode='r', encoding='latin-1') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fjc_id = row.get('jid')
                    first_name = row.get('First Name', '').strip()
                    last_name = row.get('Last Name', '').strip()
                    
                    if not fjc_id and not last_name:
                        continue

                    judge = None
                    
                    # Try to match by fjc_id first
                    if fjc_id:
                        try:
                            judge = Judge.objects.get(fjc_id=fjc_id)
                        except Judge.DoesNotExist:
                            pass
                    
                    # Fallback: Match by name if fjc_id not found
                    if not judge and first_name and last_name:
                        try:
                            judge = Judge.objects.get(
                                name_first__iexact=first_name,
                                name_last__iexact=last_name
                            )
                            # Set the fjc_id for future lookups
                            if fjc_id and not judge.fjc_id:
                                judge.fjc_id = int(fjc_id)
                        except Judge.DoesNotExist:
                            not_found_count += 1
                            continue
                        except Judge.MultipleObjectsReturned:
                            continue
                    
                    if not judge:
                        not_found_count += 1
                        continue

                    changed = False

                    # 1. Update Birth/Death Info (ONLY if missing)
                    if not judge.date_birth or force:
                        birth_year = row.get('Birth Year')
                        birth_month = row.get('Birth Month')
                        birth_day = row.get('Birth Day')
                        if birth_year:
                            try:
                                month = int(birth_month) if birth_month else 1
                                day = int(birth_day) if birth_day else 1
                                judge.date_birth = date(int(birth_year), month, day)
                                changed = True
                            except ValueError:
                                pass
                    
                    if not judge.date_death or force:
                        death_year = row.get('Death Year')
                        death_month = row.get('Death Month')
                        death_day = row.get('Death Day')
                        if death_year:
                            try:
                                month = int(death_month) if death_month else 1
                                day = int(death_day) if death_day else 1
                                judge.date_death = date(int(death_year), month, day)
                                changed = True
                            except ValueError:
                                pass

                    # City/State - only if missing
                    if not judge.dob_city or force:
                        if row.get('Birth City'):
                            judge.dob_city = row.get('Birth City')
                            changed = True
                    
                    if not judge.dob_state or force:
                        if row.get('Birth State'):
                            judge.dob_state = row.get('Birth State')
                            changed = True

                    # 2. Enrich Education (merge and deduplicate)
                    fjc_education = []
                    for i in range(1, 6):
                        school = row.get(f'School ({i})')
                        degree = row.get(f'Degree ({i})')
                        year = row.get(f'Degree Year ({i})')
                        if school:
                            fjc_education.append({
                                'school': school,
                                'degree_level': degree,
                                'degree_year': year
                            })
                    
                    if fjc_education:
                        # Combine and deduplicate
                        combined = list(judge.education) + fjc_education
                        deduped = deduplicate_education(combined)
                        if len(deduped) != len(judge.education):
                            judge.education = deduped
                            changed = True

                    # 3. Enrich Biography ONLY if empty or very short
                    career = row.get('Professional Career', '')
                    if career and (not judge.biography or len(judge.biography) < 50 or force):
                        # Re-generate synthetic bio with gender-aware pronouns
                        new_bio = data_processor.generate_synthetic_bio(
                            judge.full_name, 
                            judge.education, 
                            judge.positions,
                            judge.gender
                        )
                        judge.biography = f"{new_bio}\n\nProfessional Career:\n{career}"
                        changed = True

                    if changed and not dry_run:
                        judge.save()
                        updated_count += 1
                        if updated_count % 10 == 0:
                            self.stdout.write(f"Processed {updated_count} judges...")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error processing CSV: {str(e)}"))
            import traceback
            traceback.print_exc()

        self.stdout.write(self.style.SUCCESS(
            f"Enrichment complete. Updated: {updated_count}, Not in DB: {not_found_count}"
        ))

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legal_agent_platform.settings')
django.setup()

from data_ingestion.courtlistener_service import courtlistener_service

docket_id = 70760169
docket_data = courtlistener_service.fetch_docket_by_id(docket_id)
print(json.dumps(docket_data, indent=2))

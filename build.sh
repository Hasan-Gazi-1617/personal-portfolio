#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Intentionally clear legacy TKI records on every deployment.
# The fresh /tki/ dashboard is temporary and does not persist entries.
python manage.py shell -c "from portfolio.models import ComplaintTicket, TicketActivity; TicketActivity.objects.all().delete(); ComplaintTicket.objects.all().delete()"

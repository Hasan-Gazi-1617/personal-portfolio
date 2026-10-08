from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from portfolio.models import ComplaintTicket


RECORDS = [
    (1,"MIT-CPID2648","08-Oct-2026","Md Fahim","No Connection","abir","01302111298",""),
    (2,"MIT-CPID2648","08-Oct-2026","Md Fahim","Router Reset","abir","",""),
    (3,"MIT-CPID3776","08-Oct-2026","Koyes Ahmed","Cable Cut","rukunuzzaman","01740069292","PDB Offices Cable Cut"),
    (4,"MIT-CPID3801","08-Oct-2026","Saifur Rahman","Cable Cut","rukunuzzaman","","PDB Offices Cable Cut"),
    (5,"MIT-CPID4074","08-Oct-2026","Md Sakif Nayeem Ratul","Cable Cut","rukunuzzaman","01717929746","ONU red light on"),
    (6,"MIT-CPID2258","08-Oct-2026","Md Jalal Ahmed","Cable Cut","faruk","",""),
    (7,"MIT-CPID4155","08-Oct-2026","M/S Boshor Store (Sadik Miah)","Slow Internet","faruk","","Tenda single-band router; ONU troubleshooting provided; service working"),
    (8,"MIT-CPID2211","08-Oct-2026","Shohel Ahmed","No Connection","faruk","","Router and ONU offline"),
    (9,"MIT-CPID1843","08-Oct-2026","Md Saiful Islam(C)","Down for Resource Work","faruk","",""),
    (10,"MIT-CPID2128","08-Oct-2026","Tawhid Islam Jisan","Down for Resource Work","faruk","",""),
    (11,"MIT-CPID1351","08-Oct-2026","Raju Ahmed(C)","Down for Resource Work","abir","",""),
    (12,"MIT-CPID909","08-Oct-2026","Mahin Sajib","Slow Internet","abir","","User router issue"),
    (13,"MIT-CPID3725","08-Oct-2026","Aminuzzaman","Wireless Password Change","abir","01336635852",""),
    (14,"MIT-CPID1034","08-Oct-2026","Alauddin Ahmed","No Connection","abir","","Router LAN cable disconnected"),
    (15,"MIT-CPID1802","08-Oct-2026","Nargish Begum","Down for Resource Work","abir","","Salek vai resource work; line down for 2 hours"),
    (16,"MIT-CPID507","08-Oct-2026","Amin Brothers (Mohajon Mart, Amin Uddin)","No Connection","abir","","ONU offline"),
    (17,"MIT-CPID3089","08-Oct-2026","Md. Mahmudul Hasan","No Connection","abir","","Power issue"),
    (18,"MIT-CPID1300","08-Oct-2026","Md. Emon Sardar Rakib","Down for Resource Work","faruk","",""),
    (19,"MIT-CPID1939","08-Oct-2026","Suyeb Ahmed Raju","Auto Disconnected","faruk","","Router disconnecting from ONU"),
    (20,"MIT-CPID361","08-Oct-2026","Joynul","No Connection","prodosh","","Red light at ONU"),
    (21,"MIT-CPID2211","08-Oct-2026","Shohel Ahmed","Down for Resource Work","rukunuzzaman","01716073420","Salek vai resource work; line down for 2 hours"),
    (22,"MIT-CPID2934","08-Oct-2026","Mohammad Atiqur Reza Chy.","Buffering","rukunuzzaman","01712986848","Intermittent issue; Farzana reviewed DB-17; TP-Link C6 firmware updated; follow-up required"),
    (23,"MIT-CPID362","08-Oct-2026","Parvez-01","Cable Cut","rukunuzzaman","01732734715","BDB cable cut"),
    (24,"MIT-CPID1802","08-Oct-2026","Nargish Begum","Cable Cut","rukunuzzaman","01346094772","BDB Offices cable cut"),
    (25,"MIT-CPID3640","08-Oct-2026","MD. Uzzal Mia","Cable Cut","rukunuzzaman","01991774958","BDB Offices cable cut"),
    (26,"MIT-CPID3254","07-Oct-2026","Janat","Slow Internet","prodosh","","Contact client before physical visit"),
    (27,"MIT-CPID2338","07-Oct-2026","MD Alauddin","Down for Resource Work","riaz","","Line down"),
    (28,"MIT-CPID4414","07-Oct-2026","K.M Nozrul Islam","Buffering","rukunuzzaman","Muhib","-13.86 dBm online; troubleshooting provided; follow-up required"),
    (29,"MIT-CPID4158","07-Oct-2026","Ma Enterprise (Shakil Ahmed)","Slow Internet","faruk","","Router hang; basic router/ONU troubleshooting; 8 devices connected"),
    (30,"MIT-CPID4148","07-Oct-2026","Habibur Rahman Anam","Slow Internet","abir","","Troubleshooting provided"),
    (31,"MIT-CPID4432","07-Oct-2026","Abu Ali","No Connection","rukunuzzaman","01351818236","Router disconnected; morning field visit requested"),
    (32,"MIT-CPID1686","06-Oct-2026","Rajad Ahmed","No Connection","rukunuzzaman","","Billing issue; -12.90 dBm online"),
    (33,"MIT-CPID1044","06-Oct-2026","Shimul Ahmed Jony","Router Issue","abir","",""),
    (34,"MIT-CPID4405","05-Oct-2026","Md. Rakibul Amin","No Connection","rukunuzzaman","01304855467 / 01999049269","Router offline; service active after ONU reboot"),
    (35,"MIT-CPID1379","04-Oct-2026","Efty Rahman","Auto Disconnected","riaz","","ONU power off"),
    (36,"MIT-CPID1868","04-Oct-2026","Arjit Paul","Slow Internet","hasan","01898859689","Test router support planned; Prodosh called several times but client did not answer"),
    (37,"MIT-CPID2516","01-Oct-2026","Shahan Ahmed","Buffering","rukunuzzaman","","-19.59 dBm online; client absent; advised LAN cable and quality router"),
    (38,"MIT-CPID4337","01-Oct-2026","Samar Deb","No Connection","rukunuzzaman","01608625142","Power outage; ask client to call after power returns; -10.57 dBm"),
    (39,"MIT-CPID3500","30-Sep-2026","Mosharrof Hossain","Buffering","rukunuzzaman","01303896049","-20.61 dBm online; present issue resolved; follow-up required"),
    (40,"MIT-CPID3523","29-Sep-2026","Mak Talha Enterprise","Auto Disconnected","rukunuzzaman","01606977545","-22.29 dBm online; router disconnected"),
    (41,"MIT-CPID4012","26-Jul-2026","Mohammad Forhad","Router Issue","riaz","","Test router unrecovered after repeated visits; management escalation required"),
]


class Command(BaseCommand):
    help = "Idempotently import the initial Manor IT TKI register"

    def handle(self, *args, **options):
        created = 0
        field_engineers = {value for value, _ in ComplaintTicket.SupportEngineer.choices}
        noc_engineers = {value for value, _ in ComplaintTicket.NocEngineer.choices}
        for serial, cpid, raw_date, customer, issue, support, contact, detail in RECORDS:
            opened = timezone.make_aware(datetime.strptime(raw_date, "%d-%b-%Y").replace(hour=12))
            tki_id = f"TKI-{opened:%Y%m%d}-{serial:03d}"
            support_key = support.lower()
            dependency = ComplaintTicket.Dependency.TECHNICIAN if issue in {"Cable Cut", "Down for Resource Work"} else ComplaintTicket.Dependency.SUPPORT
            defaults = {
                "client_id": cpid,
                "opened_at": opened,
                "status": ComplaintTicket.Status.PENDING,
                "dependency": dependency,
                "field_support_engineer": support_key if support_key in field_engineers else "",
                "higher_level_noc": support_key if support_key in noc_engineers else "",
                "priority": ComplaintTicket.Priority.HIGH if serial in {3,4,5,15,23,25,34,36,37,38,39,40} else ComplaintTicket.Priority.MEDIUM,
                "category": ComplaintTicket.Category.FIBER if issue in {"Cable Cut", "Down for Resource Work", "No Connection"} else ComplaintTicket.Category.ROUTER,
                "complaint": f"{issue} — {customer}",
                "remarks": " | ".join(part for part in (contact and f"Contact: {contact}", detail) if part),
                "attention": issue in {"Cable Cut", "Down for Resource Work"},
            }
            _, was_created = ComplaintTicket.objects.update_or_create(tki_id=tki_id, defaults=defaults)
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"TKI import complete: {created} created, {len(RECORDS) - created} updated"))

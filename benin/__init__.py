import reports

CUSTOM_REPORTS = (
    ('CARE Benin Reports', (
        reports.MEGeneral,
        reports.MEMedical,
        reports.Nurse,
        reports.Outcomes,
        reports.DangerSigns,
        reports.Referrals,
    )),
)

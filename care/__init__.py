import reports

CUSTOM_REPORTS = (
    ('CARE Benin Reports', (
        reports.MonitoringAndEvaluation,
        reports.Nurse,
        reports.Outcomes,
        reports.DangerSigns,
        reports.Referrals,
    )),
)

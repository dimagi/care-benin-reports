import datetime
from corehq.apps.reports.basic import BasicTabularReport, Column
from corehq.apps.reports.datatables import DataTablesHeader, DataTablesColumnGroup
from corehq.apps.reports.standard import ProjectReportParametersMixin, CustomProjectReport
from corehq.apps.reports.fields import FilterUsersField, YearField, MonthField

def username(key, report):
    return report.usernames[key[0]]

class MonitoringAndEvaluation(BasicTabularReport, CustomProjectReport, ProjectReportParametersMixin):
    name = "CARE M&E"
    slug = "cb_me"
    field_classes = (FilterUsersField, YearField, MonthField)

    couch_view = "care/care_benin"

    default_column_order = (
        'village',
        'newlyRegisteredPregnant',
        'postPartumRegistration',
        'postPartumRegistration1'
    )

    village = Column(
        "Village", calculate_fn=username)

    newlyRegisteredPregnant = Column(
        "Newly Registered Women who are Pregnant", key="newly_registered_pregnant", rotate=True)

    postPartumRegistration = Column(
        "Post-partum mothers/newborn registrations", key="post_partum_registration", rotate=True)

    postPartumRegistration1 = Column(
        "Post-partum mothers/newborn registrations", key="post_partum_registration", rotate=True)

    column_group = DataTablesColumnGroup("Test group",
                                         newlyRegisteredPregnant.data_tables_column,
                                         postPartumRegistration.data_tables_column)
    column_group.css_span = 2

    @property
    def headers(self):
        return DataTablesHeader(self.village.data_tables_column,
                                self.column_group,
                                self.postPartumRegistration1.data_tables_column)

    @property
    def start_and_end_keys(self):
        return ([self.year, self.month - 1],
                [self.year, self.month])

    @property
    def keys(self):
        for user in self.users:
            yield [user['user_id']]

    @property
    def month(self):
        return int(self.request.GET.get('month', datetime.datetime.utcnow().month))

    @property
    def year(self):
        return int(self.request.GET.get('year', datetime.datetime.utcnow().year))
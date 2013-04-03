from corehq.apps.reports.basic import BasicTabularReport, Column
from corehq.apps.reports.datatables import DataTablesHeader, DataTablesColumnGroup
from corehq.apps.reports.standard import ProjectReportParametersMixin, CustomProjectReport, DatespanMixin
from corehq.apps.reports.fields import FilterUsersField, DatespanField
from corehq.apps.groups.models import Group
from couchdbkit_aggregate import KeyView
from dimagi.utils.decorators.memoized import memoized


def groupname(key, report):
    return report.groupnames[key[0]]

class MonitoringAndEvaluation(BasicTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    name = "CARE M&E"
    slug = "cb_me"
    field_classes = (FilterUsersField, DatespanField)
    datespan_default_days = 30

    couch_view = "care/care_benin"

    default_column_order = (
        'village',
        'newlyRegisteredPregnant',
        'postPartumRegistration',
        'births_one_month_ago_follow_up_x0',
        'births_one_month_ago_follow_up_x1',
        'births_one_month_ago_follow_up_x2',
        'births_one_month_ago_follow_up_x3',
        'births_one_month_ago_follow_up_x4',
        'births_one_month_ago_follow_up_gt4'
    )

    village = Column(
        "Village", calculate_fn=groupname)

    newlyRegisteredPregnant = Column(
        "Newly Registered Women who are Pregnant", key="newly_registered_pregnant", rotate=True)

    postPartumRegistration = Column(
        "Post-partum mothers/newborn registrations", key="post_partum_registration", rotate=True)

    births_one_month_ago_view = KeyView(key="births_one_month_ago")

    births_one_month_ago_follow_up_x0 = Column(
        "Birth followups X0", key="birth_one_month_ago_followup_x0", rotate=True, denominator=births_one_month_ago_view)
    births_one_month_ago_follow_up_x1 = Column(
        "Birth followups X1", key="birth_one_month_ago_followup_x1", rotate=True, denominator=births_one_month_ago_view)
    births_one_month_ago_follow_up_x2 = Column(
        "Birth followups X2", key="birth_one_month_ago_followup_x2", rotate=True, denominator=births_one_month_ago_view)
    births_one_month_ago_follow_up_x3 = Column(
        "Birth followups X3", key="birth_one_month_ago_followup_x3", rotate=True, denominator=births_one_month_ago_view)
    births_one_month_ago_follow_up_x4 = Column(
        "Birth followups X4", key="birth_one_month_ago_followup_x4", rotate=True, denominator=births_one_month_ago_view)
    births_one_month_ago_follow_up_gt4 = Column(
        "Birth followups >4", key="birth_one_month_ago_followup_x4+", rotate=True, denominator=births_one_month_ago_view)

    birth_followups = DataTablesColumnGroup("Birth followup percentages",
                                            births_one_month_ago_follow_up_x0.data_tables_column,
                                            births_one_month_ago_follow_up_x1.data_tables_column,
                                            births_one_month_ago_follow_up_x2.data_tables_column,
                                            births_one_month_ago_follow_up_x3.data_tables_column,
                                            births_one_month_ago_follow_up_x4.data_tables_column,
                                            births_one_month_ago_follow_up_gt4.data_tables_column,)
    birth_followups.css_span = 2

    @property
    def headers(self):
        return DataTablesHeader(self.village.data_tables_column,
                                self.newlyRegisteredPregnant.data_tables_column,
                                self.postPartumRegistration.data_tables_column,
                                self.birth_followups,
                                )

    @property
    def start_and_end_keys(self):
        return ([self.datespan.startdate_param_utc],
                [self.datespan.enddate_param_utc])

    @property
    def keys(self):
        for group in self.groups:
            yield [group._id]

    @property
    def groups(self):
        return Group.by_domain(self.domain)

    @property
    @memoized
    def groupnames(self):
        return dict([(group._id, group.name) for group in self.groups])

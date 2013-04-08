from numbers import Number
from corehq.apps.reports.basic import BasicTabularReport, Column
from corehq.apps.reports.datatables import DataTablesHeader, DataTablesColumnGroup
from corehq.apps.reports.standard import ProjectReportParametersMixin, CustomProjectReport, DatespanMixin
from corehq.apps.reports.fields import FilterUsersField, DatespanField, GroupField
from corehq.apps.groups.models import Group
from couchdbkit_aggregate import KeyView, AggregateKeyView
from dimagi.utils.decorators.memoized import memoized
from couchdbkit_aggregate.fn import NO_VALUE


def username(key, report):
    return report.usernames[key[0]]


def groupname(key, report):
    return report.groupnames[key[0]]


def combine_indicator(num, denom):
    if isinstance(num, Number) and isinstance(denom, Number):
        return num * 100 / denom
    else:
        return NO_VALUE


class MonitoringAndEvaluation(BasicTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    name = "CARE M&E"
    slug = "cb_me"
    field_classes = (DatespanField,)
    datespan_default_days = 30

    couch_view = "care/care_benin"

    default_column_order = (
        'village',
        'newlyRegisteredPregnant',
        'postPartumRegistration',
        'pregnant_followed_up',
        'births_one_month_ago_follow_up_x0',
        'births_one_month_ago_follow_up_x1',
        'births_one_month_ago_follow_up_x2',
        'births_one_month_ago_follow_up_x3',
        'births_one_month_ago_follow_up_x4',
        'births_one_month_ago_follow_up_gt4',
        'danger_sign_knowledge_pregnancy',
        'danger_sign_knowledge_post_partum',
        'danger_sign_knowledge_newborn',
        'births_cpn0',
        'births_cpn1',
        'births_cpn2',
        'births_cpn4',
        'births_vat2',
        'births_tpi2',
        'referrals_open_30_days',
    )

    village = Column(
        "Village", calculate_fn=groupname)

    # pregnancy
    newlyRegisteredPregnant = Column(
        "Newly Registered Women who are Pregnant", key="newly_registered_pregnant", rotate=True)

    pregnant_followed_up = Column(
        "Pregnant Women", key="pregnant_followed_up", rotate=True, startkey_fn=lambda x: [])

    pregnancy_followup = KeyView(key="pregnancy_followup")

    # birth
    postPartumRegistration = Column(
        "Post-partum mothers/newborn registrations", key="post_partum_registration", rotate=True)

    births_total_view = KeyView(key="births_one_month_ago")

    births_view_x0 = AggregateKeyView(combine_indicator,
                                      KeyView(key="birth_one_month_ago_followup_x0"),
                                      births_total_view)
    births_view_x1 = AggregateKeyView(combine_indicator,
                                      KeyView(key="birth_one_month_ago_followup_x1"),
                                      births_total_view)
    births_view_x2 = AggregateKeyView(combine_indicator,
                                      KeyView(key="birth_one_month_ago_followup_x2"),
                                      births_total_view)
    births_view_x3 = AggregateKeyView(combine_indicator,
                                      KeyView(key="birth_one_month_ago_followup_x3"),
                                      births_total_view)
    births_view_x4 = AggregateKeyView(combine_indicator,
                                      KeyView(key="birth_one_month_ago_followup_x4"),
                                      births_total_view)
    births_view_gt4 = AggregateKeyView(combine_indicator,
                                       KeyView(key="birth_one_month_ago_followup_x4+"),
                                       births_total_view)

    births_one_month_ago_follow_up_x0 = Column(
        "Birth followups X0", key=births_view_x0, rotate=True)
    births_one_month_ago_follow_up_x1 = Column(
        "Birth followups X1", key=births_view_x1, rotate=True)
    births_one_month_ago_follow_up_x2 = Column(
        "Birth followups X2", key=births_view_x2, rotate=True)
    births_one_month_ago_follow_up_x3 = Column(
        "Birth followups X3", key=births_view_x3, rotate=True)
    births_one_month_ago_follow_up_x4 = Column(
        "Birth followups X4", key=births_view_x4, rotate=True)
    births_one_month_ago_follow_up_gt4 = Column(
        "Birth followups >4", key=births_view_gt4, rotate=True)

    births_cpn0_view = AggregateKeyView(combine_indicator,
                                        KeyView(key='birth_cpn_0'),
                                        pregnancy_followup)
    births_cpn1_view = AggregateKeyView(combine_indicator,
                                        KeyView(key='birth_cpn_1'),
                                        pregnancy_followup)
    births_cpn2_view = AggregateKeyView(combine_indicator,
                                        KeyView(key='birth_cpn_2'),
                                        pregnancy_followup)
    births_cpn4_view = AggregateKeyView(combine_indicator,
                                        KeyView(key='birth_cpn_4'),
                                        pregnancy_followup)

    births_cpn0 = Column("Birth with CPN0", key=births_cpn0_view, rotate=True)
    births_cpn1 = Column("Birth with CPN1", key=births_cpn1_view, rotate=True)
    births_cpn2 = Column("Birth with CPN2", key=births_cpn2_view, rotate=True)
    births_cpn4 = Column("Birth with CPN4", key=births_cpn4_view, rotate=True)

    births_vat2 = Column("Birth with VAT2", key="birth_vat_2", rotate=True)
    births_tpi2 = Column("Birth with TPI2", key="birth_tpi_2", rotate=True)

    referrals_open_30_days = Column(
        "Referrals open for more than one month", key="referrals_open_30_days", rotate=True, startkey_fn=lambda x: [])

    #danger signs
    danger_sign_knowledge_pregnancy = Column("Pregnancy danger sign knowledge",
                                             key="danger_sign_knowledge_pregnancy", rotate=True,
                                             startkey_fn=lambda x: [])
    danger_sign_knowledge_post_partum = Column("Post-partum danger sign knowledge",
                                               key="danger_sign_knowledge_post_partum", rotate=True,
                                               startkey_fn=lambda x: [])
    danger_sign_knowledge_newborn = Column("Newborn danger sign knowledge",
                                           key="danger_sign_knowledge_newborn", rotate=True,
                                           startkey_fn=lambda x: [])

    @property
    def headers(self):
        birth_followups_group = DataTablesColumnGroup("Birth followup percentages",
                                                      self.births_one_month_ago_follow_up_x0.data_tables_column,
                                                      self.births_one_month_ago_follow_up_x1.data_tables_column,
                                                      self.births_one_month_ago_follow_up_x2.data_tables_column,
                                                      self.births_one_month_ago_follow_up_x3.data_tables_column,
                                                      self.births_one_month_ago_follow_up_x4.data_tables_column,
                                                      self.births_one_month_ago_follow_up_gt4.data_tables_column)

        danger_signs_group = DataTablesColumnGroup("Danger sign knowledge",
                                                   self.danger_sign_knowledge_pregnancy.data_tables_column,
                                                   self.danger_sign_knowledge_post_partum.data_tables_column,
                                                   self.danger_sign_knowledge_newborn.data_tables_column)

        birth_cpn_group = DataTablesColumnGroup("Birth with CPN",
                                                self.births_cpn0.data_tables_column,
                                                self.births_cpn1.data_tables_column,
                                                self.births_cpn2.data_tables_column,
                                                self.births_cpn4.data_tables_column)

        return DataTablesHeader(self.village.data_tables_column,
                                self.newlyRegisteredPregnant.data_tables_column,
                                self.pregnant_followed_up.data_tables_column,
                                self.postPartumRegistration.data_tables_column,
                                birth_followups_group,
                                birth_cpn_group,
                                self.births_vat2.data_tables_column,
                                self.births_tpi2.data_tables_column,
                                self.referrals_open_30_days.data_tables_column,
                                danger_signs_group,
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
        return [g for g in Group.by_domain(self.domain) if g.name.strip()]

    @property
    @memoized
    def groupnames(self):
        return dict([(group._id, group.name) for group in self.groups])


class Nurse(BasicTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    name = "Relais"
    slug = "cb_nurse"
    field_classes = (GroupField, DatespanField)
    datespan_default_days = 30

    couch_view = "care/form"

    default_column_order = (
        'nurse',
        'cpn_exam_rate',
    )

    nurse = Column(
        "Nurse", calculate_fn=username)

    cpn_exam_total = KeyView(key="cpn_exam_total")

    cpn_exam_rate_view = AggregateKeyView(combine_indicator,
                                     KeyView(key="cpn_exam_answered"),
                                     cpn_exam_total)

    cpn_exam_rate = Column(
        "CPN Exam Rate", key=cpn_exam_rate_view, rotate=True)

    @property
    def start_and_end_keys(self):
        return ([self.datespan.startdate_param_utc],
                [self.datespan.enddate_param_utc])

    @property
    def keys(self):
        for user in self.users:
            yield [user['user_id']]

class Outcomes(BasicTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    name = "Outcomes"
    slug = "cb_outcomes"
    field_classes = (DatespanField,)
    datespan_default_days = 30

    couch_view = "care/form"

    default_column_order = (
        'gapta',
    )

    gapta = Column("Numbre of births at clinic with GATPA performed", key="birth_gapta", rotate=True)

    @property
    def start_and_end_keys(self):
        return ([self.datespan.startdate_param_utc],
                [self.datespan.enddate_param_utc])

    @property
    def keys(self):
        return [[]]



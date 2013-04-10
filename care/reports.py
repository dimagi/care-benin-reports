from numbers import Number
from corehq.apps.reports.basic import BasicTabularReport, Column, GenericTabularReport
from corehq.apps.reports.datatables import DataTablesHeader, DataTablesColumnGroup, \
    DataTablesColumn, DTSortType, DTSortDirection
from corehq.apps.reports.standard import ProjectReportParametersMixin, CustomProjectReport, DatespanMixin
from corehq.apps.reports.fields import FilterUsersField, DatespanField, GroupField
from corehq.apps.groups.models import Group
from couchdbkit_aggregate import KeyView, AggregateKeyView, fn
from dimagi.utils.decorators.memoized import memoized
from couchdbkit_aggregate.fn import NO_VALUE
from dimagi.utils.couch.database import get_db


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
        'high_risk_pregnancy',
        'anemic_pregnancy',
        'stillborns',
        'failed_pregnancy',
        'maternal_death',
        'child_death_7_days',
        'births_one_month_ago_follow_up_x0',
        'births_one_month_ago_follow_up_x1',
        'births_one_month_ago_follow_up_x2',
        'births_one_month_ago_follow_up_x3',
        'births_one_month_ago_follow_up_x4',
        'births_one_month_ago_follow_up_gt4',
        'danger_sign_count_pregnancy',
        'danger_sign_count_newborn',
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
        'births_one_month_ago_bcg_polio',
    )

    village = Column(
        "Village", calculate_fn=groupname)

    # pregnancy
    newlyRegisteredPregnant = Column("Newly Registered Women who are Pregnant",
                                     key="newly_registered_pregnant", rotate=True)

    pregnant_followed_up = Column("Pregnant Women", key="pregnant_followed_up",
                                  rotate=True, startkey_fn=lambda: [])

    high_risk_pregnancy = Column("High risk pregnancies", key="high_risk_pregnancy", rotate=True,
                                 couch_view="care/form", startkey_fn=lambda: [])
    anemic_pregnancy = Column("Anemic pregnancies", key="anemic_pregnancy", rotate=True,
                                 couch_view="care/form", startkey_fn=lambda: [])


    # birth
    postPartumRegistration = Column(
        "Post-partum mothers/newborn registrations", key="post_partum_registration", rotate=True)

    stillborns = Column("Stillborns", key="stillborn", rotate=True,
                        couch_view="care/form", startkey_fn=lambda: [])

    failed_pregnancy = Column("Failed pregnancies", key="pregnancy_failed", rotate=True,
                        couch_view="care/form", startkey_fn=lambda: [])

    maternal_death = Column("Maternal deaths", key="maternal_death", rotate=True,
                        couch_view="care/form", startkey_fn=lambda: [])

    child_death_7_days = Column("Babies died before 7 days", key="child_death_7_days", rotate=True,
                        couch_view="care/form", startkey_fn=lambda: [])

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

    pregnancy_followup = KeyView(key="pregnancy_followup")

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

    births_one_month_ago_bcg_polio = Column("Births 2 months ago that got BCG polio",
                                             key='births_one_month_ago_bcg_polio', rotate=True)

    referrals_open_30_days = Column(
        "Referrals open for more than one month", key="referrals_open_30_days", rotate=True, startkey_fn=lambda x: [])

    #danger signs
    danger_sign_count_pregnancy = Column("Pregnancy danger sign count",
                                             key="danger_sign_count_pregnancy", rotate=True)
    danger_sign_count_newborn = Column("Newborn danger sign count",
                                           key="danger_sign_count_birth", rotate=True)

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

        danger_sign_count_group = DataTablesColumnGroup("Danger sign counts",
                                                   self.danger_sign_count_pregnancy.data_tables_column,
                                                   self.danger_sign_count_newborn.data_tables_column)

        danger_sign_knowledge_group = DataTablesColumnGroup("Danger sign knowledge",
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
                                self.high_risk_pregnancy.data_tables_column,
                                self.anemic_pregnancy.data_tables_column,
                                self.stillborns.data_tables_column,
                                self.failed_pregnancy.data_tables_column,
                                self.maternal_death.data_tables_column,
                                self.child_death_7_days.data_tables_column,
                                self.postPartumRegistration.data_tables_column,
                                birth_followups_group,
                                birth_cpn_group,
                                self.births_vat2.data_tables_column,
                                self.births_tpi2.data_tables_column,
                                self.births_one_month_ago_bcg_polio.data_tables_column,
                                self.referrals_open_30_days.data_tables_column,
                                danger_sign_knowledge_group,
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

class Referrals(BasicTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    name = "Referrals"
    slug = "cb_referrals"
    field_classes = (GroupField, DatespanField)
    datespan_default_days = 30

    couch_view = "care/care_benin"

    default_column_order = (
        'referrals_transport_pied',
        'referrals_transport_velo',
        'referrals_transport_barque_simple',
        'referrals_transport_barque_ambulance',
        'referrals_transport_vehicule_simple',
        'referrals_transport_vehicule_ambulance',
        'referrals_transport_moto_simple',
        'referrals_transport_moto_ambulance',
        'referrals_by_type_enceinte',
        'referrals_by_type_accouchee',
        'referrals_by_type_nouveau_ne',
    )

    referrals_total_view = KeyView(key="referrals_total")

    referrals_transport_pied_view = AggregateKeyView(combine_indicator,
                                                     KeyView(key="referrals_transport_pied"),
                                                     referrals_total_view)
    referrals_transport_velo_view = AggregateKeyView(combine_indicator,
                                                     KeyView(key="referrals_transport_velo"),
                                                     referrals_total_view)
    referrals_transport_barque_simple_view = AggregateKeyView(combine_indicator,
                                                              KeyView(key="referrals_transport_barque_simple"),
                                                              referrals_total_view)
    referrals_transport_barque_ambulance_view = AggregateKeyView(combine_indicator,
                                                                 KeyView(key="referrals_transport_barque_ambulance"),
                                                                 referrals_total_view)
    referrals_transport_vehicule_simple_view = AggregateKeyView(combine_indicator,
                                                                KeyView(key="referrals_transport_vehicule_simple"),
                                                                referrals_total_view)
    referrals_transport_vehicule_ambulance_view = AggregateKeyView(combine_indicator,
                                                                   KeyView(key="referrals_transport_vehicule_ambulance"),
                                                                   referrals_total_view)
    referrals_transport_moto_simple_view = AggregateKeyView(combine_indicator,
                                                            KeyView(key="referrals_transport_moto_simple"),
                                                            referrals_total_view)
    referrals_transport_moto_ambulance_view = AggregateKeyView(combine_indicator,
                                                               KeyView(key="referrals_transport_moto_ambulance"),
                                                               referrals_total_view)

    referrals_transport_pied = Column("Pied", key=referrals_transport_pied_view, rotate=True)
    referrals_transport_velo = Column("Velo", key=referrals_transport_velo_view, rotate=True)
    referrals_transport_barque_simple = Column("Barque simple", key=referrals_transport_barque_simple_view, rotate=True)
    referrals_transport_barque_ambulance= Column("Barque ambulance", key=referrals_transport_barque_ambulance_view, rotate=True)
    referrals_transport_vehicule_simple = Column("Vehicule simple", key=referrals_transport_vehicule_simple_view, rotate=True)
    referrals_transport_vehicule_ambulance = Column("Vehicule ambulance", key=referrals_transport_vehicule_ambulance_view, rotate=True)
    referrals_transport_moto_simple = Column("Moto simple", key=referrals_transport_moto_simple_view, rotate=True)
    referrals_transport_moto_ambulance = Column("Moto ambulance", key=referrals_transport_moto_ambulance_view, rotate=True)

    referrals_by_type_enceinte = Column("Enceinte", key="referral_per_type_enceinte", rotate=True)
    referrals_by_type_accouchee = Column("Accouchee", key="referral_per_type_accouchee", rotate=True)
    referrals_by_type_nouveau_ne = Column("Nouveau Ne", key="referral_per_type_nouveau_ne", rotate=True)

    references_to_clinic_view = AggregateKeyView(combine_indicator,
                                                 KeyView(key="reference_to_clinic_went"),
                                                 KeyView(key="references_to_clinic"))
    references_to_clinic = Column("Rate of references that which went to clinic",
                                  key=references_to_clinic_view,rotate=True)

    @property
    def headers(self):
        referrals_transport_group = DataTablesColumnGroup(self.referrals_transport_pied.data_tables_column,
                                                          self.referrals_transport_velo.data_tables_column,
                                                          self.referrals_transport_barque_simple.data_tables_column,
                                                          self.referrals_transport_barque_ambulance.data_tables_column,
                                                          self.referrals_transport_vehicule_simple.data_tables_column,
                                                          self.referrals_transport_vehicule_ambulance.data_tables_column,
                                                          self.referrals_transport_moto_simple.data_tables_column,
                                                          self.referrals_transport_moto_ambulance.data_tables_column,
                                                          )

        referrals_type_group = DataTablesColumnGroup(self.referrals_by_type_enceinte.data_tables_column,
                                                     self.referrals_by_type_accouchee.data_tables_column,
                                                     self.referrals_by_type_nouveau_ne.data_tables_column)
        return DataTablesHeader(referrals_transport_group,
                                referrals_type_group,
                                self.references_to_clinic.data_tables_column)

    @property
    def start_and_end_keys(self):
        return ([self.datespan.startdate_param_utc],
                [self.datespan.enddate_param_utc])

    @property
    def keys(self):
        return ['village']
        #for group in self.groups:
        #    yield [group._id]

    @property
    def groups(self):
        return [g for g in Group.by_domain(self.domain) if g.name.strip()]

    @property
    @memoized
    def groupnames(self):
        return dict([(group._id, group.name) for group in self.groups])

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


class DangerSigns(GenericTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    name = "Danger Signs"
    slug = "cb_danger"
    fields = ('corehq.apps.reports.fields.DatespanField',)
    datespan_default_days = 30

    @property
    def start_and_end_keys(self):
        return (self.datespan.startdate_param_utc,
                self.datespan.enddate_param_utc)

    @property
    def keys(self):
        return [row['key'][1] for row in get_db().view("care/form",
                                                       startkey=['danger_sign'],
                                                       endkey=['danger_sign', {}],
                                                       reduce=True, group=True, group_level=2)]

    @property
    def headers(self):
        return DataTablesHeader(DataTablesColumn("Danger sign"),
            DataTablesColumn("Count")) #, sort_type=DTSortType.NUMERIC)) TODO fix sorting

    @property
    def rows(self):
        reduce_fn = fn.sum()
        startkey, endkey = self.start_and_end_keys

        for key in self.keys:
            row = get_db().view("care/form",
                                startkey=['danger_sign', key, startkey],
                                endkey=['danger_sign', key, endkey, {}],
                                reduce=True,
                                wrapper=lambda r: r['value']
                                )

            row = row.first()
            yield [key, reduce_fn(row)]


# coding=utf-8

from numbers import Number
from corehq.apps.reports.basic import BasicTabularReport, Column, GenericTabularReport
from corehq.apps.reports.datatables import DataTablesHeader, DataTablesColumnGroup, \
    DataTablesColumn, DTSortType, DTSortDirection
from corehq.apps.reports.standard import ProjectReportParametersMixin, CustomProjectReport, DatespanMixin
from corehq.apps.reports.fields import DatespanField
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


class CareGroupReport(BasicTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    field_classes = (DatespanField,)
    datespan_default_days = 30
    exportable = True

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
        return [g for g in Group.by_domain(self.domain) if not g.reporting]

    @property
    @memoized
    def groupnames(self):
        return dict([(group._id, group.name) for group in self.groups])


class MeanHours(fn.mean):
    def __call__(self, stats):
        millis = super(MeanHours, self).__call__(stats, 0)
        return millis / 60 * 60 * 1000 if isinstance(millis, Number) else millis


class MEGeneral(CareGroupReport):
    name = "M&E General"
    slug = "cb_gen"
    couch_view = "care/by_village_case"

    default_column_order = (
        'village',
        'referrals_open_30_days',
        'ref_counter_ref_time',
        'danger_sign_knowledge_pregnancy',
        'danger_sign_knowledge_post_partum',
        'danger_sign_knowledge_newborn',
        'birth_place_mat_isolee',
        'birth_place_cs_arrondissement',
        'birth_place_cs_commune',
        'birth_place_hopital',
        'birth_place_domicile',
        'birth_place_clinique_privee',
        'birth_place_autre',
    )

    village = Column(
        "Village", calculate_fn=groupname)

    ref_counter_ref_time = Column("Mean time between reference and counter reference", key="ref_counter_ref_time",
                                  rotate=True, reduce_fn=MeanHours())

    # birth
    birth_place_group = DataTablesColumnGroup("Birth place")
    birth_place_mat_isolee = Column("Maternite Isolee", key="birth_place_mat_isolee",
                                    rotate=True, group=birth_place_group)
    birth_place_cs_arrondissement = Column("CS Arrondissement", key="birth_place_CS_arrondissement",
                                           rotate=True, group=birth_place_group)
    birth_place_cs_commune = Column("CS Commune", key="birth_place_CS_commune",
                                    rotate=True, group=birth_place_group)
    birth_place_hopital = Column("Hopital de zone", key="birth_place_hopital",
                                 rotate=True, group=birth_place_group)
    birth_place_domicile = Column("Domicile", key="birth_place_domicile",
                                  rotate=True, group=birth_place_group)
    birth_place_clinique_privee = Column("Clinique Privee", key="birth_place_clinique_privee",
                                         rotate=True, group=birth_place_group)
    birth_place_autre = Column("Autre lieu", key="birth_place_autre",
                               rotate=True, group=birth_place_group)

    referrals_open_30_days = Column("Referrals open for more than one month", key="referrals_open_30_days",
        rotate=True, startkey_fn=lambda x: [])

    #danger signs
    danger_sign_knowledge_group = DataTablesColumnGroup("Danger sign knowledge")
    danger_sign_knowledge_pregnancy = Column("Pregnancy danger sign knowledge",
                                             key="danger_sign_knowledge_pregnancy", rotate=True,
                                             startkey_fn=lambda x: [], group=danger_sign_knowledge_group)
    danger_sign_knowledge_post_partum = Column("Post-partum danger sign knowledge",
                                               key="danger_sign_knowledge_post_partum", rotate=True,
                                               startkey_fn=lambda x: [], group=danger_sign_knowledge_group)
    danger_sign_knowledge_newborn = Column("Newborn danger sign knowledge",
                                           key="danger_sign_knowledge_newborn", rotate=True,
                                           startkey_fn=lambda x: [], group=danger_sign_knowledge_group)


class MEMedical(CareGroupReport):
    name = "M&E Medical"
    slug = "cb_med"

    couch_view = "care/by_village_case"

    default_column_order = (
        'village',
        'newlyRegisteredPregnant',
        'postPartumRegistration',
        'pregnant_followed_up',
        #'high_risk_pregnancy', #requires village in form
        #'anemic_pregnancy', #requires village in form
        #'stillborns', #requires village in form
        #'failed_pregnancy', #requires village in form
        #'maternal_death', #requires village in form
        #'child_death_7_days', #requires village in form
        'births_one_month_ago_bcg_polio',
        'births_vat2',
        'births_tpi2',
        'births_one_month_ago_follow_up_x0',
        'births_one_month_ago_follow_up_x1',
        'births_one_month_ago_follow_up_x2',
        'births_one_month_ago_follow_up_x3',
        'births_one_month_ago_follow_up_x4',
        'births_one_month_ago_follow_up_gt4',
        #'danger_sign_count_pregnancy', #requires village in form
        #'danger_sign_count_newborn', #requires village in form
        'births_cpn0',
        'births_cpn1',
        'births_cpn2',
        'births_cpn4',
    )

    village = Column(
        "Village", calculate_fn=groupname)

    # pregnancy
    newlyRegisteredPregnant = Column("Newly Registered Women who are Pregnant",
                                     key="newly_registered_pregnant", rotate=True)

    pregnant_followed_up = Column("Pregnant women followed up on", key="pregnant_followed_up",
                                  rotate=True, startkey_fn=lambda x: [], endkey_fn=lambda x: [{}])

    high_risk_pregnancy = Column("High risk pregnancies", key="high_risk_pregnancy", rotate=True,
                                 couch_view="care/by_village_form", startkey_fn=lambda x: [])
    anemic_pregnancy = Column("Anemic pregnancies", key="anemic_pregnancy", rotate=True,
                                 couch_view="care/by_village_form", startkey_fn=lambda x: [])

    # birth
    postPartumRegistration = Column(
        "Post-partum mothers/newborn registrations", key="post_partum_registration", rotate=True)

    stillborns = Column("Stillborns", key="stillborn", rotate=True,
                        couch_view="care/by_village_form", startkey_fn=lambda x: [])

    failed_pregnancy = Column("Failed pregnancies", key="pregnancy_failed", rotate=True,
                        couch_view="care/by_village_form", startkey_fn=lambda x: [])

    maternal_death = Column("Maternal deaths", key="maternal_death", rotate=True,
                        couch_view="care/by_village_form", startkey_fn=lambda x: [])

    child_death_7_days = Column("Babies died before 7 days", key="child_death_7_days", rotate=True,
                        couch_view="care/by_village_form", startkey_fn=lambda x: [])

    births_total_view = KeyView(key="birth_one_month_ago")

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
                                       KeyView(key="birth_one_month_ago_followup_gt4"),
                                       births_total_view)

    births_one_month_ago_follow_up_group = DataTablesColumnGroup("Birth followup percentages")
    births_one_month_ago_follow_up_x0 = Column(
        "Birth followups X0", key=births_view_x0, rotate=True, group=births_one_month_ago_follow_up_group)
    births_one_month_ago_follow_up_x1 = Column(
        "Birth followups X1", key=births_view_x1, rotate=True, group=births_one_month_ago_follow_up_group)
    births_one_month_ago_follow_up_x2 = Column(
        "Birth followups X2", key=births_view_x2, rotate=True, group=births_one_month_ago_follow_up_group)
    births_one_month_ago_follow_up_x3 = Column(
        "Birth followups X3", key=births_view_x3, rotate=True, group=births_one_month_ago_follow_up_group)
    births_one_month_ago_follow_up_x4 = Column(
        "Birth followups X4", key=births_view_x4, rotate=True, group=births_one_month_ago_follow_up_group)
    births_one_month_ago_follow_up_gt4 = Column(
        "Birth followups >4", key=births_view_gt4, rotate=True, group=births_one_month_ago_follow_up_group)

    birth_cpn_total = KeyView(key="birth_cpn_total")

    births_cpn0_view = AggregateKeyView(combine_indicator,
                                        KeyView(key='birth_cpn_0'),
                                        birth_cpn_total)
    births_cpn1_view = AggregateKeyView(combine_indicator,
                                        KeyView(key='birth_cpn_1'),
                                        birth_cpn_total)
    births_cpn2_view = AggregateKeyView(combine_indicator,
                                        KeyView(key='birth_cpn_2'),
                                        birth_cpn_total)
    births_cpn4_view = AggregateKeyView(combine_indicator,
                                        KeyView(key='birth_cpn_4'),
                                        birth_cpn_total)

    birth_cpn_group = DataTablesColumnGroup("Birth with CPN")
    births_cpn0 = Column("Birth with CPN0", key=births_cpn0_view, rotate=True, group=birth_cpn_group)
    births_cpn1 = Column("Birth with CPN1", key=births_cpn1_view, rotate=True, group=birth_cpn_group)
    births_cpn2 = Column("Birth with CPN2", key=births_cpn2_view, rotate=True, group=birth_cpn_group)
    births_cpn4 = Column("Birth with CPN4", key=births_cpn4_view, rotate=True, group=birth_cpn_group)

    births_vat2 = Column("Birth with VAT2", key="birth_vat_2", rotate=True)
    births_tpi2 = Column("Birth with TPI2", key="birth_tpi_2", rotate=True)

    births_one_month_ago_bcg_polio = Column("Births 2 months ago that got BCG polio",
                                             key='birth_one_month_ago_bcg_polio', rotate=True)

    #danger signs
    danger_sign_count_group = DataTablesColumnGroup("Danger sign counts")
    danger_sign_count_pregnancy = Column("Pregnancy danger sign count", key="danger_sign_count_pregnancy",
                                         rotate=True, group=danger_sign_count_group)
    danger_sign_count_newborn = Column("Newborn danger sign count", key="danger_sign_count_birth",
                                       rotate=True, group=danger_sign_count_group)

class Nurse(BasicTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
        name = "Nurse"
        slug = "cb_nurse"
        field_classes = (DatespanField,)
        datespan_default_days = 30

        couch_view = "care/by_user_form"

        default_column_order = (
            'nurse',
            'cpn_exam_rate',
            'post_natal_followups_15m', #requires xform_xmlns in case actions
            'post_natal_followups_6h', #requires xform_xmlns in case actions
            'post_natal_followups_sortie', #requires xform_xmlns in case actions
            'post_natal_followups_none', #requires xform_xmlns in case actions
        )

        nurse = Column(
            "Nurse", calculate_fn=username)

        cpn_exam_total = KeyView(key="cpn_exam_total")

        cpn_exam_rate_view = AggregateKeyView(combine_indicator,
                                              KeyView(key="cpn_exam_answered"),
                                              cpn_exam_total)

        cpn_exam_rate = Column(
            "CPN Exam Rate", key=cpn_exam_rate_view, rotate=True)

        post_natal_followups_total_view = KeyView(key="post_natal_followups_total")
        post_natal_followups_15m_view = AggregateKeyView(combine_indicator,
                                                     KeyView(key="post_natal_followups_15m"),
                                                     post_natal_followups_total_view)
        post_natal_followups_6h_view = AggregateKeyView(combine_indicator,
                                                     KeyView(key="post_natal_followups_6h"),
                                                     post_natal_followups_total_view)
        post_natal_followups_sortie_view = AggregateKeyView(combine_indicator,
                                                     KeyView(key="post_natal_followups_sortie"),
                                                     post_natal_followups_total_view)
        post_natal_followups_none_view = AggregateKeyView(combine_indicator,
                                                     KeyView(key="post_natal_followups_none"),
                                                     post_natal_followups_total_view)

        pnf_group = DataTablesColumnGroup("Post-natal followups")
        post_natal_followups_15m = Column("15 min follow up", key=post_natal_followups_15m_view,
                                          rotate=True, group=pnf_group)
        post_natal_followups_6h = Column("6 hour follow up", key=post_natal_followups_6h_view,
                                         rotate=True, group=pnf_group)
        post_natal_followups_sortie = Column("Sortie follow up", key=post_natal_followups_sortie_view,
                                             rotate=True, group=pnf_group)
        post_natal_followups_none = Column("No follow up", key=post_natal_followups_none_view,
                                           rotate=True, group=pnf_group)

        @property
        def start_and_end_keys(self):
            return ([self.datespan.startdate_param_utc],
                    [self.datespan.enddate_param_utc])

        @property
        def keys(self):
            for user in self.users:
                yield [user['user_id']]

class Referrals(CareGroupReport):
    name = "Referrals"
    slug = "cb_referrals"

    couch_view = "care/by_village_form"

    # NOTE: all require village to be loaded into the forms
    default_column_order = (
        'village',
        'references_to_clinic',
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

    village = Column("Village", calculate_fn=lambda key, report: 'Total')#groupname)

    referrals_total_view = KeyView(key="referrals_transport_total")

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

    referrals_transport_group = DataTablesColumnGroup("Referrals by mode of transport")
    referrals_transport_pied = Column("Pied", key=referrals_transport_pied_view, rotate=True,
                                      group=referrals_transport_group)
    referrals_transport_velo = Column("Velo", key=referrals_transport_velo_view, rotate=True,
                                      group=referrals_transport_group)
    referrals_transport_barque_simple = Column("Barque simple", key=referrals_transport_barque_simple_view,
                                               rotate=True, group=referrals_transport_group)
    referrals_transport_barque_ambulance= Column("Barque ambulance", key=referrals_transport_barque_ambulance_view,
                                                 rotate=True, group=referrals_transport_group)
    referrals_transport_vehicule_simple = Column("Vehicule simple", key=referrals_transport_vehicule_simple_view,
                                                 rotate=True, group=referrals_transport_group)
    referrals_transport_vehicule_ambulance = Column("Vehicule ambulance",
                                                    key=referrals_transport_vehicule_ambulance_view,
                                                    rotate=True, group=referrals_transport_group)
    referrals_transport_moto_simple = Column("Moto simple", key=referrals_transport_moto_simple_view,
                                             rotate=True, group=referrals_transport_group)
    referrals_transport_moto_ambulance = Column("Moto ambulance", key=referrals_transport_moto_ambulance_view,
                                                rotate=True, group=referrals_transport_group)

    referrals_type_group = DataTablesColumnGroup("Referrals by patient type")
    referrals_by_type_enceinte = Column("Enceinte", key="referral_per_type_enceinte",
                                        rotate=True, group=referrals_type_group)
    referrals_by_type_accouchee = Column("Accouchee", key="referral_per_type_accouchee",
                                         rotate=True, group=referrals_type_group)
    referrals_by_type_nouveau_ne = Column("Nouveau Ne", key="referral_per_type_nouveau_ne",
                                          rotate=True, group=referrals_type_group)

    references_to_clinic_view = AggregateKeyView(combine_indicator,
                                                 KeyView(key="reference_to_clinic_went"),
                                                 KeyView(key="references_to_clinic"))
    references_to_clinic = Column("Rate of references which went to clinic",
                                  key=references_to_clinic_view, rotate=True)

    @property
    def keys(self):
        return [['village']]

class Outcomes(GenericTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    name = "Outcomes"
    slug = "cb_outcomes"
    fields = ('corehq.apps.reports.fields.DatespanField',)
    datespan_default_days = 30

    couch_view = "care/outcomes"

    row_list = (
        {"name": "Cases closed (enceinte)",
            "view": KeyView(key="case_closed_enceinte")},
        {"name": "Cases closed (accouchee)",
            "view": KeyView(key="case_closed_accouchee")},
        {"name": "Numbre of births at clinic with GATPA performed",
            "view": KeyView(key="birth_gapta")},
        {"name": "Total references to clinic (enceinte)",
            "view": KeyView(key="references_to_clinic_total_enceinte")},
        {"name": "Total references to clinic (accouchee)",
            "view": KeyView(key="references_to_clinic_total_accouchee")},
    )

    @property
    def start_and_end_keys(self):
        return ([self.datespan.startdate_param_utc],
                [self.datespan.enddate_param_utc])

    @property
    def headers(self):
        return DataTablesHeader(DataTablesColumn(""),
                                DataTablesColumn("Value")) #, sort_type=DTSortType.NUMERIC)) TODO fix sorting

    @property
    def rows(self):
        db = get_db()
        startkey, endkey = self.start_and_end_keys
        for row in self.row_list:
            yield [row["name"], row["view"].get_value([], startkey=startkey, endkey=endkey,
                                                          couch_view=self.couch_view, db=db)]


class DangerSigns(GenericTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    name = "Danger sign distribution"
    slug = "cb_danger"
    fields = ('corehq.apps.reports.fields.DatespanField',)
    datespan_default_days = 30

    @property
    def start_and_end_keys(self):
        return (self.datespan.startdate_param_utc,
                self.datespan.enddate_param_utc)

    @property
    def keys(self):
        return [row['key'][1] for row in get_db().view("care/danger_signs",
                                                       #startkey=['danger_sign'],
                                                       #endkey=['danger_sign', {}],
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
            row = get_db().view("care/danger_signs",
                                startkey=['danger_sign', key, startkey],
                                endkey=['danger_sign', key, endkey, {}],
                                reduce=True,
                                wrapper=lambda r: r['value']
                                )

            row = row.first()
            yield [key, reduce_fn(row)]
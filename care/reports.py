import datetime
import dateutil
import pytz
from corehq.apps.fixtures.models import FixtureDataItem, FixtureDataType
from corehq.apps.reports.basic import BasicTabularReport
from corehq.apps.reports.standard import ProjectReportParametersMixin, DatespanMixin, CustomProjectReport
from corehq.apps.reports.fields import FilterUsersField, DatespanField
from corehq.apps.reports.basic import BasicTabularReport, Column
from corehq.apps.reports.datatables import DataTablesColumn, DataTablesHeader
from corehq.apps.reports.generic import GenericTabularReport
from couchforms.models import XFormInstance
from dimagi.utils.couch.database import get_db
from corehq.apps.reports import util

def username(key, report):
    return report.usernames[key[0]]

class MonitoringAndEvaluation(BasicTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    """fields = ['corehq.apps.reports.fields.FilterUsersField',
              'corehq.apps.reports.fields.DatespanField']

    name = "M&E"
    slug = "core_benin_m_e"

    @property
    def headers(self):
        return DataTablesHeader(DataTablesColumn("Name of FIDA"),
                                DataTablesColumn("Name of DCTL"))

    @property
    def rows(self):
        print self.users, self.datespan
        rows = []
        rows.append([
            "simon",
            "kelly"
        ])
        return rows"""

    name = "CATI Performance Report"
    slug = "cati_performance"
    field_classes = (FilterUsersField, DatespanField)

    filter_group_name = "CATI"

    couch_view = "care/care_benin"

    default_column_order = (
        'user',
        'newlyRegisteredPregnant',
    )

    user = Column(
        "Case Owner", calculate_fn=username)

    newlyRegisteredPregnant = Column(
        "Newly Registered Women who are Pregnant", key="newly_registered_pregnant")

    @property
    def start_and_end_keys(self):
        return ([self.datespan.startdate_utc.year, self.datespan.startdate_utc.month-1],
                [self.datespan.enddate_utc.year, self.datespan.enddate_utc.month-1])

    @property
    def keys(self):
        for user in self.users:
            yield [user['user_id']]


class MonitoringAndEvaluation(GenericTabularReport, CustomProjectReport, ProjectReportParametersMixin, DatespanMixin):
    fields = ['corehq.apps.reports.fields.FilterUsersField',
              'corehq.apps.reports.fields.DatespanField']

    name = "M&E"
    slug = "core_benin_m_e"

    @property
    def headers(self):
        return DataTablesHeader(DataTablesColumn("Name of FIDA"),
                                DataTablesColumn("Name of DCTL"))

    @property
    def rows(self):
        print self.users, self.datespan
        rows = []
        rows.append([
            "simon",
            "kelly"
        ])
        return rows
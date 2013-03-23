/* handle xforms */
function get_form_filled_duration(xform_doc) {
    // in milliseconds
    var meta = xform_doc.form.meta;
    if (meta && meta.timeEnd && meta.timeStart)
        return new Date(meta.timeEnd).getTime() - new Date(meta.timeStart).getTime();
    return null;
}

/* CARE related */

function CARECaseEntry(doc) {
    var self = this;
    self.doc = doc;
    self.form = (doc.form) ? doc.form : doc;
    self.case = (self.form.case) ? self.form.case : self.form;

    self.data = {};
    self.getCaseDetails = function() {
        if (self.case['@user_id']){
            self.data.case_owner = self.case['@user_id'];
        } else if (self.case.create) {
            self.data.case_owner = self.case.create.user_id;
        }
    }
}

function dateBreakdown(dateString, breakdown) {
    var date = new Date(dateString);
    var ret = new Array();
    for (i in breakdown) {
        var elem = breakdown[i];
        if (elem === 'y') {
            ret.push(date.getUTCFullYear());
        } else if (elem === 'm') {
            ret.push(date.getUTCMonth());
        } else if (elem === 'd') {
            ret.push(date.getUTCDay());
        }
    }
    return ret;
}
/* handle xforms */
function get_form_filled_duration(xform_doc) {
    // in milliseconds
    var meta = xform_doc.form.meta;
    if (meta && meta.timeEnd && meta.timeStart)
        return new Date(meta.timeEnd).getTime() - new Date(meta.timeStart).getTime();
    return null;
}

/* CARE related */

function isCAREForm(doc) {
    return (doc.doc_type === 'XFormInstance'
            && doc.domain === 'project');
}

function isACLRC_Enregistrement(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/5A457301-7D57-4332-8CAC-44E17B5ADBB2");
}

function isACLRC_SuiviDeEnceinte(doc) {
    return (doc.xmlns === "http://www.commcarehq.org/example/hello-world");
}

function isACLRC_Accouchement(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/2BA7D4F1-E6F4-4EF2-9F00-5A02A28D9410");
}

function isACLRC_SuiviDeNouveau(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/E93DB604-C511-463F-B0C2-25952C71A50F");
}

function isACLRC_SuiviDeAccouchee(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/9D6BFE31-1613-4D10-8772-1AC3C6979004");
}

function isACLRC_Reference(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/B1E6BBC1-ACD3-408B-B3AB-783153063D56");
}

function isACLRC_SuiviDeReference(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/A2EEC8AA-4761-4C68-BCFF-B6C0287DAA51");
}

function isACLRC_FermerLeDossier(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/09149C06-4933-4EF9-ACC6-40A966D05FD7");
}

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
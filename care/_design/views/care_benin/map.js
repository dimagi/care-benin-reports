function(doc) {
    // !code util/care.js
    // !code util/emit_array.js

    if (isCAREForm(doc) && isACLRC_Enregistrement(doc)){
        var form = (doc.form) ? doc.form : doc;
        if (form.status === 'enceinte') {
            var entry = new CARECaseEntry(doc);
            entry.getCaseDetails();

            var data = {};
            data.newly_registered_pregnant = 1

            emit_array([entry.data.case_owner], dateBreakdown(form.meta.timeEnd, ['y','m']), data);
        }
    }
}
function(doc) {
    // !code util/forms_checks.js
    // !code util/care_form.js
    // !code util/emit_array.js

    if (isCAREForm(doc)){
        var form = new CareForm(doc);
        form.rc_suivi_de_reference();
        form.rc_fermer_le_dossier();
        form.rc_reference();
        form.as_examen();
        form.as_accouchement();
        form.as_contre_reference_aux_ralais();
        form.as_completer_enregistrement();
        form.emit_data();
    }
}
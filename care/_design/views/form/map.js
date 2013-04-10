function(doc) {
    // !code util/forms_checks.js
    // !code util/care.js
    // !code util/emit_array.js

    function emit_danger_signs(doc, village_data, key, danger_signs) {
        if (!danger_signs) {
            return;
        }
        var date = doc.received_on;
        var signs = danger_signs.trim().split(" ");
        for (var i = 0, len = signs.length; i < len; i++) {
            var s = signs[i];
            if (s) {
                emit(['danger_sign', s, date], 1);
                village_data[key] = 1;
            }
        }
    }

    if (isCAREForm(doc)){
        var form = (doc.form) ? doc.form : doc;

        var user_data = {};
        var village_data = {};
        if (isRC_SuiviDeReference(doc)) {

            village_data.reference_to_clinic = 1;

            var reference = form.pas_de_contre_reference;
            if (reference && reference.es_tu_allee && reference.es_tu_allee === 'oui') {
                village_data.reference_to_clinic_went = 1;
            }
        }

        if (isAS_Examen(doc)) {
            var exclude = ['case', 'meta'];
            var not_containing = ['@', 'data_node', '#']
            var total = 0, non_blank = 0;
            for (var key in form) {
                if (form.hasOwnProperty(key) &&
                    not_containing.every(function(v) { return key.indexOf(v) === -1; }) &&
                    exclude.indexOf(key) === -1) {
                    total++;
                    if (form[key].trim()) {
                        non_blank++;
                    }
                }
            }
            user_data.cpn_exam_total = total;
            user_data.cpn_exam_answered = non_blank;

            if (form.classifier_anemie_severe === 'ok' || form.classifier_anemie_modere === 'ok'){
                village_data.anemic_pregnancy = 1;
            }
        }

        if (isAS_Accouchement(doc)) {
            if (form.question108 && form.question108.delivrance === 'GAPTA') {
                emit(['birth_gapta', doc.received_on], 1);
            }

            if (form.etat_enfant === 'decedee') {
                village_data.stillborn = 1;
            } else if (form.etat_mere === 'decedee') {
                village_data.maternal_death = 1;
            }
        }

        if (isRC_FermerLeDossier(doc)) {
            switch (form.raison) {
                case 'grossesse_echouee':
                    village_data.pregnancy_failed = 1;
                    break;
                case 'enc_morte':
                case 'acc_morte':
                case 'acc_et_nne_morts':
                    village_data.maternal_death = 1;
                    break;
            }

            if (form['nne-mort_age_jours'] < 7) {
                village_data.child_death_7_days = 1;
            }
        }

        if (isRC_Reference(doc)) {
            emit_danger_signs(doc, village_data, 'danger_sign_count_pregnancy', form.signe_danger_enceinte);
            emit_danger_signs(doc, village_data, 'danger_sign_count_accouchee', form.signe_danger_accouchee);
            emit_danger_signs(doc, village_data, 'danger_sign_count_birth', form.signe_danger_nne);

            var condition = form.condition_data_node;
            if (condition === 'enceinte') {
                village_data.referral_per_type_enceinte = 1;
            } else if (condition === 'accouchee') {
                if (form.lequel_referer) {
                    if (form.lequel_referer === 'mere') {
                        village_data.referral_per_type_accouchee = 1;
                    } else if (form.laquel_referer === 'bebe') {
                        village_data.referral_per_type_nouveau_ne = 1;
                    }
                }
            }
        }

        if (isAS_ContreReferenceDuneFemmeEnceinte(doc) ||
            isAS_ContreReferenceDunNouveauNe(doc) ||
            isAS_ContreReferenceDuneAccouche(doc)) {

            village_data.referrals_transport_total = 1;
            emit(['village', 'referrals_transport_total', doc.received_on], 1);
            if (form.moyen_transport) {
                village_data['referrals_transport_'+form.moyen_transport] = 1;
            }
        }

        if (isAS_CompleterEnregistrement(doc)) {
            if (form.Alerte_GARE === 'ok' || form.avis_mort_ne === 'ok') {
                village_data.high_risk_pregnancy = 1;
            }
        }

        emit_array([form.meta.userID], [doc.received_on], user_data);
        // TODO: get village
        emit_array(['village'], [doc.received_on], village_data);
    }
}
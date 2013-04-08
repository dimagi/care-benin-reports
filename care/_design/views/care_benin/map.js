function(doc) {
    // !code util/forms_checks.js
    // !code util/care.js
    // !code util/emit_array.js

    function updateBirths(births, a, properties) {
        if (properties.condition === 'enceinte') {
            births.push({
                conception: new Date(a.date)
            })
        } else if (properties.condition === 'accouchee') {
            if (births.length > 0) {
                births[births.length-1].birth = new Date(a.date);
            }
        }

        return births;
    }

    function count_matching_props(doc, keys, value) {
        var count = 0;
        var len = keys.length;
        for (var i = 0; i < len; i++) {
            var key = keys[i];
            if (doc[key] && doc[key] === value) {
                count++;
            }
        }

        return count;
    }

    function adjust_date(date, days) {
        var adjusted_date = new Date(date);
        adjusted_date.setDate(adjusted_date.getDate() + days);
        return adjusted_date;
    }

    if (isCAREWomanCase(doc)) {
        var opened_on_date = new Date(doc.opened_on);
        var status = doc.condition;
        var owner_id = doc.owner_id;
        var data = {};

        if (status === 'enceinte') {
            data.newly_registered_pregnant = 1;
            if (!doc.closed) {
                data.pregnant_followed_up = 1;
            }
        } else if (status === 'accouchee') {
            data.post_partum_registration = 1;

            if (doc.suivi_count_enc && doc.suivi_count_enc > 0) {
                data.pregnancy_followup = 1;

                if (doc.CPN4 === 'oui') {
                    emit([owner_id, 'birth_cpn_4', doc.DA], 1);
                } else if (doc.CPN2 === 'oui') {
                    emit([owner_id, 'birth_cpn_2', doc.DA], 1);
                } else if (doc.CPN1 = 'oui') {
                    emit([owner_id, 'birth_cpn_1', doc.DA], 1);
                } else if (count_matching_props(doc, ['CPN1','CPN2','CPN3','CPN4'], 'non') === 4) {
                    emit([owner_id, 'birth_cpn_0', doc.DA], 1);
                }
            }
        }

        if (doc.closed) {
            emit(['case_closed_'+status, new Date(doc.closed_on)], 1)
        }

        function emit_referral(date) {
            var adjusted_date = adjust_date(new Date(date).getTime(), 30);
            emit([owner_id, 'referrals_open_30_days', adjusted_date], 1);
        }

        if (doc.RC_nne_referee_quand) {
            emit_referral(doc.RC_nne_referee_quand);
        }
        if (doc.RC_acc_referee_quand) {
            emit_referral(doc.RC_acc_referee_quand);
        }
        if (doc.RC_enc_referee_quand) {
            emit_referral(doc.RC_enc_referee_quand);
        }

        // danger signs
        var danger_signs_pregnant = ['connais_bebe_bouge_moins',
             'connais_convulsions',
             'connais_fatigue_important',
             'connais_fievre',
             'connais_maux_de_ventre_violents connais_maux_tete_violent',
             'connais_pertes_eaux',
             'connais_respiration_difficile',
             'connais_saignement',
             'connais_visage_ou_mains_enfles connais_vision_floue',
             'connais_vomissements_importants'];
        if (count_matching_props(doc, danger_signs_pregnant, 'oui') >= 3){
            data.danger_sign_knowledge_pregnancy = 1;
        }

        var danger_signs_post_partum= ['connais_convulsions',
            'connais_fievre',
            'connais_maux_tete',
            'connais_maux_ventre_violents_douleur_pelvienne',
            'connais_mollets_sensibles',
            'connais_perte_connaissance',
            'connais_perte_urines',
            'connais_respiration_difficile',
            'connais_saignement',
            'connais_sang_mauvais',
            'connais_seins_douleureux',
            'connais_tristesse',
            'connais_vision_floue',
            'connais_fatigue_importante'];
        if (count_matching_props(doc, danger_signs_post_partum, 'oui') >= 3){
            data.danger_sign_knowledge_post_partum = 1;
        }

        var danger_signs_newborn = ['connais_corps_chaud_ou_froid',
            'connais_lethargie',
            'connais_signe_coloration_jaune',
            'connais_signe_convulsions',
            'connais_signe_infections_cordon',
            'connais_signe_malformations',
            'connais_signe_pustules',
            'connais_signe_troubles_respiratoires',
            'connais_signe_vomit_diarrhee',
            'connais_teter'];
        if (count_matching_props(doc, danger_signs_newborn, 'oui') >= 3){
            data.danger_sign_knowledge_newborn = 1;
        }

        // birth follow ups
        var actions = doc.actions;
        var births = [];
        var vat2_date;
        var tpi2_date;
        for (var i = 0, l = actions.length; i < l; i++){
            var a = actions[i];
            var properties = a.updated_unknown_properties;

            // TODO: not sure if this is necessary - might be enough to just get the birth date (especially if there is
            // only one birth per case)
            births = updateBirths(births, a, properties);

            if (properties.VAT2 === 'oui') {
                vat2_date = new Date(a.date);
            }

            if (properties.TPI2 === 'oui') {
                tpi2_date = new Date(a.date);
            }
        }

        for (var i = 0, l = births.length; i < l; i++) {
            var b = births[i];
            // not sure if this full check is necessary or just check for 'birth'
            if (b.hasOwnProperty('conception') && b.hasOwnProperty('birth')
                && b.conception.getTime() < b.birth.getTime()){

                var adjusted_date = adjust_date(b.birth.getTime(), 30);
                emit([owner_id, 'births_one_month_ago', adjusted_date], 1);

                if (vat2_date < b.birth) {
                    emit([owner_id, 'birth_vat_2', b.birth], 1);
                }

                if (tpi2_date < b.birth) {
                    emit([owner_id, 'birth_tpi_2', b.birth], 1);
                }

                if (doc.BCG_et_polio === 'oui') {
                    emit([owner_id, 'births_one_month_ago_bcg_polio', adjusted_date], 1);
                }

                // follow ups
                if (doc.suivi_count_nne !== undefined){
                    switch (+doc.suivi_count_nne) {
                        case 0:
                            emit([owner_id, 'birth_one_month_ago_followup_x0', adjusted_date], 1)
                            break;
                        case 1:
                            emit([owner_id, 'birth_one_month_ago_followup_x1', adjusted_date], 1);
                            break;
                        case 2:
                            emit([owner_id, 'birth_one_month_ago_followup_x2', adjusted_date], 1);
                            break;
                        case 3:
                            emit([owner_id, 'birth_one_month_ago_followup_x3', adjusted_date], 1);
                            break;
                        case 4:
                            emit([owner_id, 'birth_one_month_ago_followup_x4', adjusted_date], 1);
                            break;
                        default:
                            emit([owner_id, 'birth_one_month_ago_followup_x4+', adjusted_date], 1);
                    }
                } else {
                    emit([owner_id, 'birth_one_month_ago_followup_x0', adjusted_date], 1)
                }
            }
        }

        emit_array([owner_id], [opened_on_date], data);
    }
}
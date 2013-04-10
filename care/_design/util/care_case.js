function CareCase(doc) {
    var self = this;
    self.case = doc;
    self.opened_on_date = new Date(self.case.opened_on);
    self.status = doc.condition;
    self.owner_id = doc.owner_id;
    self.data_open = {};

    self.general = function () {
        if (self.status === 'enceinte') {
            if (!self.case.closed) {
                self.data_open.pregnant_followed_up = 1;
            }
        } else if (self.status === 'accouchee') {
            if (self.case.suivi_count_enc && self.case.suivi_count_enc > 0) {
                self.data_open.pregnancy_followup = 1;

                if (self.case.CPN4 === 'oui') {
                    emit([self.owner_id, 'birth_cpn_4', self.case.DA], 1);
                } else if (self.case.CPN2 === 'oui') {
                    emit([self.owner_id, 'birth_cpn_2', self.case.DA], 1);
                } else if (self.case.CPN1 = 'oui') {
                    emit([self.owner_id, 'birth_cpn_1', self.case.DA], 1);
                } else if (count_matching_props(self.case, ['CPN1','CPN2','CPN3','CPN4'], 'non') === 4) {
                    emit([self.owner_id, 'birth_cpn_0', self.case.DA], 1);
                }
            }
        }

        if (self.case.closed) {
            emit(['case_closed_'+self.status, new Date(self.case.closed_on)], 1)
        }
    }

    self.referrals = function () {
        if (self.case.RC_nne_referee_quand) {
            _emit_referral(self.case.RC_nne_referee_quand);
        }
        if (self.case.RC_acc_referee_quand) {
            _emit_referral(self.case.RC_acc_referee_quand);
        }
        if (self.case.RC_enc_referee_quand) {
            _emit_referral(self.case.RC_enc_referee_quand);
        }
    }

    self.danger_signs = function () {
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
        if (count_matching_props(self.case, danger_signs_pregnant, 'oui') >= 3){
            self.data_open.danger_sign_knowledge_pregnancy = 1;
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
        if (count_matching_props(self.case, danger_signs_post_partum, 'oui') >= 3){
            self.data_open.danger_sign_knowledge_post_partum = 1;
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
        if (count_matching_props(self.case, danger_signs_newborn, 'oui') >= 3){
            self.data_open.danger_sign_knowledge_newborn = 1;
        }
    }

    self.process_actions = function () {
        var actions = self.case.actions;
        var forms_completed ={};
        var update_count = 0;
        for (var i = 0, l = actions.length; i < l; i++) {
            var a = actions[i];
            var is_update = a.action_type === 'update';
            var properties = a.updated_unknown_properties;

            if (is_update) {
                update_count++;
            }

            forms_completed[a.xform_xmlns] = true;

            // first update
            if (update_count === 1) {
                if (properties.condition === 'enceinte') {
                    self.data_open.newly_registered_pregnant = 1;
                } else if (properties.condition === 'accouchee') {
                    self.data_open.post_partum_registration = 1;
                }
            }
        }

        if (forms_completed[ns_as_accouchement] && self.case.DA) {
            emit([self.owner_id, 'post_natal_followups_total', self.case.DA], 1);
            if (forms_completed[ns_as_surveillanceLorsDeLaSortieDuCS]) {
                emit([self.owner_id, 'post_natal_followups_sortie', self.case.DA], 1);
            } else if (forms_completed[ns_as_surveillanceA6h]) {
                emit([self.owner_id, 'post_natal_followups_6h', self.case.DA], 1);
            } else if (forms_completed[ns_as_surveillanceA15m]) {
                emit([self.owner_id, 'post_natal_followups_15m', self.case.DA], 1);
            } else {
                emit([self.owner_id, 'post_natal_followups_none', self.case.DA], 1);
            }
        }
    }

    self.check_birth = function () {
        // assume presence of DA means birth
        if (self.case.DA) {
            var dob = new Date(self.case.DA);
            if (self.case.VAT2 === 'oui') {
                emit([self.owner_id, 'birth_vat_2', dob], 1);
            }

            if (self.case.TPI2 === 'oui') {
                emit([self.owner_id, 'birth_tpi_2', dob], 1);
            }

            if (self.case.lieu_acc) {
                emit([self.owner_id, 'birth_place_'+self.case.lieu_acc, dob], 1);
            }

            var adjusted_date = adjust_date(dob.getTime(), 30);
            emit([self.owner_id, 'births_one_month_ago', adjusted_date], 1);

            if (self.case.BCG_et_polio === 'oui') {
                emit([self.owner_id, 'births_one_month_ago_bcg_polio', adjusted_date], 1);
            }

            // follow ups
            if (self.case.suivi_count_nne !== undefined){
                switch (+self.case.suivi_count_nne) {
                    case 0:
                        emit([self.owner_id, 'birth_one_month_ago_followup_x0', adjusted_date], 1)
                        break;
                    case 1:
                        emit([self.owner_id, 'birth_one_month_ago_followup_x1', adjusted_date], 1);
                        break;
                    case 2:
                        emit([self.owner_id, 'birth_one_month_ago_followup_x2', adjusted_date], 1);
                        break;
                    case 3:
                        emit([self.owner_id, 'birth_one_month_ago_followup_x3', adjusted_date], 1);
                        break;
                    case 4:
                        emit([self.owner_id, 'birth_one_month_ago_followup_x4', adjusted_date], 1);
                        break;
                    default:
                        emit([self.owner_id, 'birth_one_month_ago_followup_x4+', adjusted_date], 1);
                }
            } else {
                emit([self.owner_id, 'birth_one_month_ago_followup_x0', adjusted_date], 1)
            }
        }
    }

    self.emit_data = function () {
        emit_array([self.owner_id], [self.opened_on_date], self.data_open);
    }

    function _emit_referral(date) {
        var adjusted_date = adjust_date(new Date(date).getTime(), 30);
        emit([self.owner_id, 'referrals_open_30_days', adjusted_date], 1);
    }

    function count_matching_props(object, keys, value) {
        var count = 0;
        var len = keys.length;
        for (var i = 0; i < len; i++) {
            var key = keys[i];
            if (object[key] && object[key] === value) {
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
}
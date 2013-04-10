function CareForm(doc) {
    var self = this;
    self.doc = doc;
    self.form = (doc.form) ? doc.form : doc;
    self.received_on = doc.received_on;
    self.user_data = {};
    self.village_data = {};

    self.rc_suivi_de_reference = function () {
        if (isRC_SuiviDeReference(self.doc)) {

            self.village_data.reference_to_clinic = 1;

            var ref = self.form.pas_de_contre_reference;
            if (ref && ref.es_tu_allee && ref.es_tu_allee === 'oui') {
                self.village_data.reference_to_clinic_went = 1;
                emit(['references_to_clinic_total', self.received_on], 1);
            } else if (self.form.satisfait) {
                emit(['references_to_clinic_total', self.received_on], 1);
            }
        }
    }

    self.rc_fermer_le_dossier = function () {
        if (isRC_FermerLeDossier(self.doc)) {
            switch (self.form.raison) {
                case 'grossesse_echouee':
                    self.village_data.pregnancy_failed = 1;
                    break;
                case 'enc_morte':
                case 'acc_morte':
                case 'acc_et_nne_morts':
                    self.village_data.maternal_death = 1;
                    break;
            }

            if (self.form['nne-mort_age_jours'] < 7) {
                self.village_data.child_death_7_days = 1;
            }
        }
    }

    self.rc_reference = function () {
        if (isRC_Reference(self.doc)) {
            _emit_danger_signs('danger_sign_count_pregnancy', self.form.signe_danger_enceinte);
            _emit_danger_signs('danger_sign_count_accouchee', self.form.signe_danger_accouchee);
            _emit_danger_signs('danger_sign_count_birth', self.form.signe_danger_nne);

            var condition = self.form.condition_data_node;
            if (condition === 'enceinte') {
                self.village_data.referral_per_type_enceinte = 1;
            } else if (condition === 'accouchee') {
                if (self.form.lequel_referer) {
                    if (self.form.lequel_referer === 'mere') {
                        self.village_data.referral_per_type_accouchee = 1;
                    } else if (self.form.laquel_referer === 'bebe') {
                        self.village_data.referral_per_type_nouveau_ne = 1;
                    }
                }
            }
        }
    }

    self.as_completer_enregistrement = function() {
        if (isAS_CompleterEnregistrement(self.doc)) {
            if (self.form.Alerte_GARE === 'ok' || self.form.avis_mort_ne === 'ok') {
                self.village_data.high_risk_pregnancy = 1;
            }
        }
    }

    self.as_contre_reference_aux_ralais = function () {
        if (isAS_ContreReferenceDuneFemmeEnceinte(self.doc) ||
            isAS_ContreReferenceDunNouveauNe(self.doc) ||
            isAS_ContreReferenceDuneAccouche(self.doc)) {

            self.village_data.referrals_transport_total = 1;
            emit(['village', 'referrals_transport_total', self.received_on], 1);
            if (self.form.moyen_transport) {
                self.village_data['referrals_transport_'+self.form.moyen_transport] = 1;
            }
        }
    }

    self.as_examen = function () {
        if (isAS_Examen(self.doc)) {
            var exclude = ['case', 'meta'];
            var not_containing = ['@', 'data_node', '#']
            var total = 0, non_blank = 0;
            for (var key in self.form) {
                if (self.form.hasOwnProperty(key) &&
                    not_containing.every(function(v) { return key.indexOf(v) === -1; }) &&
                    exclude.indexOf(key) === -1) {
                    total++;
                    if (self.form[key].trim()) {
                        non_blank++;
                    }
                }
            }
            self.user_data.cpn_exam_total = total;
            self.user_data.cpn_exam_answered = non_blank;

            if (self.form.classifier_anemie_severe === 'ok' || self.form.classifier_anemie_modere === 'ok'){
                self.village_data.anemic_pregnancy = 1;
            }
        }
    }

    self.as_accouchement = function () {
        if (isAS_Accouchement(self.doc)) {
            if (self.form.question108 && self.form.question108.delivrance === 'GAPTA') {
                emit(['birth_gapta', self.received_on], 1);
            }

            if (self.form.etat_enfant === 'decedee') {
                self.village_data.stillborn = 1;
            }

            if (self.form.etat_mere === 'decedee') {
                self.village_data.maternal_death = 1;
            }
        }
    }

    self.emit_data = function () {
        emit_array([self.form.meta.userID], [self.received_on], self.user_data);
        // TODO: get village
        emit_array(['village'], [self.received_on], self.village_data);
    }

    function _emit_danger_signs(key, danger_signs) {
        if (!danger_signs) {
            return;
        }
        var signs = danger_signs.trim().split(" ");
        for (var i = 0, len = signs.length; i < len; i++) {
            var s = signs[i];
            if (s) {
                emit(['danger_sign', s, self.received_on], 1);
                self.village_data[key] = 1;
            }
        }
    }
}
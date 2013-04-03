function(doc) {
    // !code util/forms_checks.js
    // !code util/care.js
    // !code util/emit_array.js

    if (isCAREWomanCase(doc)) {
        var opened_on_date = new Date(doc.opened_on);
        var status = doc.condition;
        var owner_id = doc.owner_id;
        var data = {};

        if (status === 'enceinte') {
            data.newly_registered_pregnant = 1;
            if (!doc.closed) {
                emit([owner_id, "pregnant_followed_up"], 1)
            }
        } else if (status === 'accouchee') {
            data.post_partum_registration = 1;

            // birth follow ups
            var actions = doc.actions;
            var births = [];
            for (var i = 0, l = actions.length; i < l; i++){
                var a = actions[i];
                var properties = a.updated_unknown_properties;
                if (properties.condition === 'enceinte') {
                    births.push({
                        conception: new Date(a.date)
                    })
                } else if (properties.condition === 'accouchee') {
                    if (births.length > 0) {
                        births[births.length-1].birth = new Date(a.date);
                    }
                }
            }
            for (var i = 0, l = births.length; i < l; i++) {
                var b = births[i];
                if (b.hasOwnProperty('conception') && b.hasOwnProperty('birth')
                    && b.conception.getTime() < b.birth.getTime()){
                    var adjusted_date = new Date(b.birth.getTime());
                    adjusted_date.setDate(adjusted_date.getDate() + 30);
                    emit([owner_id, 'births_one_month_ago', adjusted_date], 1);

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
        }


        emit_array([owner_id], [opened_on_date], data);
    }
}
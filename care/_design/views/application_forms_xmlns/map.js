function(doc){
    if((doc.doc_type == 'Application' || doc.doc_type == 'RemoteApp') && doc.copy_of == null) {
        for (var mod_index in doc.modules) {
            var module = doc.modules[mod_index];
            for (var form_index in module.forms) {
                var form = module.forms[form_index];
                emit([doc.domain, doc.name], {
                    module_name: module.name,
                    form_name: form.name,
                    form_xmlns: form.xmlns
                });
            }
        }

    }
}
function isCAREForm(doc) {
    return (doc.doc_type === 'XFormInstance'
        && doc.domain === 'project');
}

function isCARECase(doc) {
    return (doc.doc_type === 'CommCareCase'
        && doc.domain === 'project');
}

function isCAREWomanCase(doc) {
    return (isCARECase(doc) && doc.type === 'Woman');
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

function isADS_Accouchement(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/EF3DF425-CCCB-4768-8C8E-9E8DB9692F07");
}

function isADS_BilanDesAnalysesLabo(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/FDEE073D-A136-46D2-8BC8-66B54AA34C07");
}

function isADS_Counseling(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/05651B2B-DEBA-4708-8D50-34582BAA64D4");
}

function isADS_Examen(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/FEEB3365-DFED-4B61-898D-6E8B9BC3DC26");
}

function isADS_PlanDAccouchement(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/D37C874D-4117-477D-B1DD-FD0DAFC27A1D");
}

function isADS_ClotureLeDossier(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/FD88BB2B-5375-456A-921A-8C853FD1A429");
}

function isADS_CompleterEnregistrement(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/EBAECEBF-E225-4464-BCC0-340E229C28AD");
}

function isADS_ContreReferenceDunNouveauNe(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/2f1d76d4d0fcec7b474239f5f209f705736d3bb0");
}

function isADS_ContreReferenceDuneAccouche(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/6581d0a691eef1d0ba97b9a41bd1fa9ebace5d23");
}

function isADS_ContreReferenceDuneFemmeEnceinte(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/10c78d5a567b53fc504dc1e6a4bdede14bf12040");
}

function isADS_EnregistrementDeBase(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/585ca2d786e0a26b0fdcddbbf992f5ab114d6824");
}

function isADS_CounselingLorsDeLaSortieDuCS(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/cb780e6e3b40db0cff0e524741371466fc0210e0");
}

function isADS_EnregistrementduNouveauNe(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/A4FCED7D-DC8B-470E-8FC6-D30ADE4131DE");
}

function isADS_SurveillanceLorsDeLaSortieDuCS(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/fb01c7e9a965c32a6aa73bac222e4c79c8bae40");
}

function isADS_SurveillanceA15m(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/516AC5E5-0DC0-4CD9-96F8-6DAFCD11CA0F");
}

function isADS_SurveillanceA6h(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/B3BBEF61-866D-4663-B9B9-EF484FC56478");
}

function isADS_ReferenceAUnNiveauSuperieur(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/9484c334281a914f73a7f8797d7378d069925e18");
}

function isADS_SuiviDUneReferenceUnNiveauSuperieur(doc) {
    return (doc.xmlns === "http://openrosa.org/formdesigner/a6c69d4244d53e87f6279b7a5ac6c6255ebfce9c");
}
function doPost(e) {

  const data = JSON.parse(e.postData.contents);

  const title = data.title;
  const concepts = data.concepts;

  // ==========================================
  // CRIA FORMULÁRIO
  // ==========================================

  const form = FormApp.create(title);

  form.setDescription(
    "Formulário acadêmico gerado automaticamente."
  );

  // ==========================================
  // CRIA PLANILHA
  // ==========================================

  const spreadsheet = SpreadsheetApp.create(
    title + " - Respostas"
  );

  // ==========================================
  // VINCULA FORM ↔ SHEETS
  // ==========================================

  form.setDestination(
    FormApp.DestinationType.SPREADSHEET,
    spreadsheet.getId()
  );

  // ==========================================
  // GERA PERGUNTAS
  // ==========================================

  for (let i = 0; i < concepts.length; i++) {

    for (let j = i + 1; j < concepts.length; j++) {

      const c1 = concepts[i];
      const c2 = concepts[j];

      form.addScaleItem()
        .setTitle(
          `Relação entre ${c1} e ${c2}`
        )
        .setBounds(1, 10)
        .setLabels(
          "Fraca",
          "Forte"
        )
        .setRequired(true);
    }
  }

  // ==========================================
  // RETORNO
  // ==========================================

  return ContentService
    .createTextOutput(
      JSON.stringify({
        success: true,
        formUrl: form.getPublishedUrl(),
        editUrl: form.getEditUrl(),
        sheetUrl: spreadsheet.getUrl()
      })
    )
    .setMimeType(ContentService.MimeType.JSON);
}
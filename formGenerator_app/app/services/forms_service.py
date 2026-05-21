from googleapiclient.discovery import build

from formGenerator_app.app.utils.combinations import generate_pairs


def _build_form(service, title, concepts):
    form = {
        "info": {
            "title": title,
            "documentTitle": title
        }
    }

    created_form = service.forms().create(body=form).execute()
    form_id = created_form["formId"]
    
    requests = []
    index = 0

    # 1. Nome Completo
    requests.append({
        "createItem": {
            "item": {
                "title": "Nome Completo",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {"paragraph": False}
                    }
                }
            },
            "location": {"index": index}
        }
    })
    index += 1

    # 2. Grupo
    requests.append({
        "createItem": {
            "item": {
                "title": "Grupo",
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": "RADIO",
                            "options": [
                                {"value": "Aluno"},
                                {"value": "Professor"}
                            ]
                        }
                    }
                }
            },
            "location": {"index": index}
        }
    })
    index += 1

    # 3. Nível de Familiaridade
    requests.append({
        "createItem": {
            "item": {
                "title": "Nível de Familiaridade",
                "questionItem": {
                    "question": {
                        "required": False,
                        "textQuestion": {"paragraph": False}
                    }
                }
            },
            "location": {"index": index}
        }
    })
    index += 1

    # 4. Perguntas de Relação
    pairs = generate_pairs(concepts)
    total = len(pairs)
    
    for i, (c1, c2) in enumerate(pairs, 1):
        requests.append({
            "createItem": {
                "item": {
                    "title": f"{i:02d}/{total} - {c1} e {c2}",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "scaleQuestion": {
                                "low": 1,
                                "high": 10,
                                "lowLabel": "Fraca",
                                "highLabel": "Forte"
                            }
                        }
                    }
                },
                "location": {"index": index}
            }
        })
        index += 1

    service.forms().batchUpdate(
        formId=form_id,
        body={"requests": requests}
    ).execute()

    return created_form["responderUri"]


def create_forms(creds, concepts, base_title="Questionário Acadêmico"):
    service = build("forms", "v1", credentials=creds)

    pre_url = _build_form(service, f"{base_title} (Pré-teste)", concepts)
    pos_url = _build_form(service, f"{base_title} (Pós-teste)", concepts)

    return {
        "pre_url": pre_url,
        "pos_url": pos_url
    }
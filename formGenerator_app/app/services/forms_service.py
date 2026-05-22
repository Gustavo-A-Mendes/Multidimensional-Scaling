from googleapiclient.discovery import build

from formGenerator_app.app.utils.combinations import generate_pairs, gerar_divisao_secao


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

    # 0. Ajustes no Formulário:
    # Adicionar Descrição no Formulário:
    str_list_concepts = ""
    for i in range(len(concepts) - 1):
        str_list_concepts += f" - {concepts[i]}\n"
    str_list_concepts += f" - {concepts[-1]}"

    requests.append({
        "updateFormInfo":{
            "info": {
                "description": f"Classifique numa escala de 1 a 10 as distância dos conceitos físicos apresentados:"
                               f"\n"
                               f"\n1 = Conceitos distantes / totalmente diferentes"
                               f"\n10 = Conceitos próximos / fortemente relacionados"
                               f"\n\n"
                               f"\nOs conceitos analisados serão:"
                               f"\n{str_list_concepts}",
            },
            "updateMask": "description"
        }
    })

    # 1. Nome Completo
    requests.append({
        "createItem": {
            "item": {
                "title": "Código de Identificação",
                "description": "Escolha uma palavra ou código para ser usado para te identificar. Esse mesmo código será usado em uma pesquisa futura, é importante que você se lembre dele.",
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
                "description": "Qual o seu nível de familiaridade com os conceitos abordados?",
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": "DROP_DOWN",
                            "options": [
                                {"value": "Nenhum"},
                                {"value": "Baixo"},
                                {"value": "Médio"},
                                {"value": "Alto"},
                                {"value": "Avançado"}
                            ]
                        }
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

    secao_id = 1
    num_questoes_por_secao = gerar_divisao_secao(total)

    for i, (c1, c2) in enumerate(pairs):

        if i % num_questoes_por_secao == 0:
            requests.append({
                "createItem": {
                    "item": {
                        "title": f"Parte {secao_id}",
                        "pageBreakItem": {}
                    },
                    "location": {"index": index}
                }
            })
            index += 1
            secao_id += 1

        requests.append({
            "createItem": {
                "item": {
                    "title": f"{(i+1):02d}/{total} - {c1} e {c2}",
                    "description": f"Qual a relação de entre os conceitos de {c1} e {c2}? "
                                   f"\n(Quanto maior, mais próximo)",
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

    pre_url = _build_form(service, f"{base_title} (Pré-aulas)", concepts)
    pos_url = _build_form(service, f"{base_title} (Pós-aulas)", concepts)

    return {
        "pre_url": pre_url,
        "pos_url": pos_url
    }
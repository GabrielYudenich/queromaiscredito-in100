import requests, json, random

class QueroMaisCreditoApi(object):

    # Inicialização de objeto com o login do usuário.
    def __init__(self, login):
        self.login = login 

    def solicitar_autorização(self, cpf, beneficio, cpf_rep=None):
        try:
            # Chamada da função para a solicitação
            json_autorização = self.get_autorizacao(cpf, beneficio, self.login, cpf_rep)

            try:
                # Tratativa de string caso não retorne em formato json
                json_autorização = json_autorização.replace(' ', '')
            except:
                pass

            # Tratativas de erro do sistema emissor

            if str(json_autorização).find('encontradonabaseouCPFdebenef') != -1:
                return 'Número de beneficio ou cpf incorreto.' 

            if str(json_autorização).find('representantelegal') != -1:
                return 'Necessário CPF do representante legal.'
            
            if str(json_autorização).find('inexistente') != -1:
                return 'Benefício inexistente.'

            if json_autorização == 0:
                return 'Erro na solicitação, verifique seu login.'
            
            if not json_autorização:
                return 'Erro na parte emissora, tente novamente mais tarde.'

            # Caso não haja erro, ele retorna o resultado positivo
            return json_autorização
        
        except Exception as erro:
            print('[SOLICITAR AUTORIZAÇÃO] Erro na função:', erro)

    def get_autorizacao(self, cpf, cod_beneficio, usuario_cod, cpf_rep=None):

        try:
            # Cada seção é diferenciada pelo sistema
            session = requests.Session()

            # Gerador de telefone não verificado
            ddd = '81'
            tel = random.randint(900000000, 999999999)

            # Headers de solicitação
            headers = {
                'Content-Type':'application/json; charset=UTF-8',
                'X-Requested-With':'XMLHttpRequest'
                }

            # Json de solicitação de dados é gerado conforme há CPF representante ou não.
             
            if cpf_rep:

                data = {"system":"FUNCAO","cod_operator":f"{usuario_cod}",
                            "name":f"{cpf}",
                            "cpf":f"{cpf}",
                            "cpf_represent":f"{cpf_rep}",
                            "tel":f"({ddd}){tel}",
                            "cod_beneficio":f"{cod_beneficio}",
                            "enviar_sms": "false",
                            "enviar_whatsapp": "true",
                            "enviar_email": "false"
                            }
                
            else:

                data = {"system":"FUNCAO","cod_operator":f"{usuario_cod}",
                        "name":f"{cpf}",
                        "cpf":f"{cpf}",     
                        "tel":f"({ddd}){tel}",
                        "cod_beneficio":f"{cod_beneficio}",
                        "enviar_sms": "false",
                        "enviar_whatsapp": "true",
                        "enviar_email": "false"
                        }
            
            # O certificado é passado pela solicitação via POST para conseguir uma autenticação melhor e sem contratempos para solicitações em massa.
            res = session.post("https://queromaiscredito.app/DataPrev/e-consignado/beneficios/cartao_consulta_in100.php", json=data, headers=headers, verify='queromaiscredito_certificado.pem')

            # Na maioria dos casos, o encoding "latin1" funcionou melhor para todos os resultados do site.
            texto_decoded = res.text.encode('latin1').decode('unicode-escape')

            # Na primeira solicitação de POST ele é somente feito a solicitação de consulta in100 solicitando a autorização, na segunda solicitação é feito um
            # GET simples para conseguir o resumo e os dados de cada solicitação feita para ter o resultado de margem de crédito e outros dados pessoais do
            # cliente de forma prática. O mesmo JSON é gerado um PDF no sistema original, na qual pode ser visto pelo identificador de rede do navegador.

            if res.status_code == 200:

                try:
                    headers = {'Content-Type': 'text/html', 'charset':'utf-8'}
                    resumo = session.get(f'https://armazem.capitalbank.systems/_dataPrev/{cpf}/Resumo-{cpf}-{cod_beneficio}.json')
                    resumo.encoding = "latin"
                    resumo_json = json.loads(resumo.text)

                    return resumo_json, 
            
                except Exception as erro:

                    # Segunda tratativa de erro do sistema que o site não possui na API própria.

                    if res.text == '         Erro':
                        return 0
                    elif texto_decoded.find('benefício inelegível') != -1:
                        return 106

                    elif res.text.find('erro') != -1:
                        return 0
                    
                    elif texto_decoded.find('DV inválido') != -1:
                        return 0
                    
                    return res.text
                
        except Exception as erro:
            print('[GET AUTORIZAÇÃO] Erro na função:', erro)
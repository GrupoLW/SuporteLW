centralizadores_uf_param_consulta = {'PA': 'pa', 'PE': 'detranpe', 'RS': 'rs', 'MG': 'mg', 'GO': 'detrango', 'AL': 'al', 'SC': 'sc', 
                          'RN': 'rn', 'DF': 'df', 'ES': 'detranes', 'PI': 'pi', 'PR': 'pr', 'CE': 'detrancemulta', 'RR': 'detranrr',
                          'AM': 'am', 'RJ': 'rj', 'MT': 'mt', 'MA': 'ma', 'MS': 'ms'}


consulta_uf_de_fora_centralizadores = {'PA': 'pa', 'PE': 'detranpe', 'RS': 'rs', 'MG': 'mg', 'GO': 'detrangouf', 'AL': 'al', 'SC': 'sc', 
                                        'RN': 'rn', 'DF': 'df', 'ES': 'detranes', 'PI': 'pi', 'PR': 'pr', 'CE': 'detrance', 'RJ': 'bradesco'}

param_ignore = ['ecrv', 'senatran', 'antt', 'detranbapdf']


federal_agencies = ['dprf', 'dnit']



especificidades = {
    'prefeiturarj': ['radar', 'bradesco'],
    'cariocadigital': ['radar', 'bradesco'],
}


centralizadores_uf_fonte_consulta = {'PA': 'detran_pa', 'PE': 'detran_pe', 'RS': 'detran_rs', 'MG': 'detran_mg', 'GO': 'detran_go', 'AL': 'detran_al', 'SC': 'detran_sc', 
                          'RN': 'detran_rn', 'DF': 'detran_df', 'ES': 'detran_es', 'PI': 'detran_pi', 'PR': 'pr', 'CE': 'detran_ce_multa', 'RR': 'detran_rr',
                          'AM': 'detran_am', 'BA': 'detranba_pdf', 'RJ': 'detran_rj', 'MT': 'detran_mt', 'MA': 'detran_ma', 'MS': 'detran_ms'}

centralizadores_estaduais_fonte_consulta = {'PA': 'detran_pa', 'PE': 'detran_pe', 'RS': 'detran_rs', 'MG': 'detran_mg', 'GO': 'detran_gouf', 'AL': 'detran_al', 'SC': 'detran_sc', 
                          'RN': 'detran_rn', 'DF': 'detran_df', 'ES': 'detran_es', 'PI': 'detran_pi', 'PR': 'pr', 'CE': 'detran_ce', 'RJ': 'bradesco'}



cod_orgao_fonte_consulta_especificidade = {'260010': 'radar', }

def fetch_orgaos_homologados_query(client_id):
    """
    órgãos homologados
    """
    query = f"""
        SELECT cliente.id_cliente, cliente.id_grupo,
               agenda.data_hora_cadastro, cliente.id_cliente, agenda.id, agenda.descricao, 
               CONCAT('java -jar LWDataMiner-2.jar ', orgao.parametro_miner, ' ', cliente.id_cliente,
                      CASE WHEN item.todos = 1 THEN ' +todos' ELSE '' END) AS comando_consulta,
               orgao.miner AS consulta, agenda.ativo, orgao.cod_orgao, 
               item.id, item.id_miner_orgao, item.tipo_consulta, item.recibo, item.todos, 
               item.ordem, item.parametro_item, orgao.status, orgao.status_executor
        FROM consulta_miner_agenda AS agenda
        INNER JOIN consulta_miner_item AS item ON (item.id_consulta_miner_agenda = agenda.id)
        INNER JOIN consulta_miner_cliente AS cliente ON (cliente.id_consulta_miner_agenda = agenda.id)
        INNER JOIN miner_orgao AS orgao ON (orgao.id = item.id_miner_orgao)
        WHERE cliente.id_cliente IN ({client_id})
        ORDER BY item.id DESC;
    """
    return query

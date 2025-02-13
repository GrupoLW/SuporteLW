from utils.vehicle import Vehicle
from models.db_model import execute_the_query


def simple_extract_fine(id_multa, column_name):
    pass

def search_fine_in_db (id_veiculo, AIT):
    result = execute_the_query(db_config, f"""select v.id as id_veic, v.uf_veic, v.placa, v.renavam, v.chassi, m.autoInfracao, m.autoInfracao2, m.AIIPMulta, m.id
    from multaDetalhada m
    inner join veiculos v on (v.id = m.id_veiculo)
    where v.id = {id_veiculo} and m.autoInfracao = '{AIT}';""")
    return result if result else None
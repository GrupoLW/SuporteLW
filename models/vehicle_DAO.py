from utils.vehicle import Vehicle
from models.db_model import execute_the_query
import pandas as pd


def find_vehicle_in_db(connection, column_name_in_db: str, list_data : list):
    placeholder_sequence = ', '.join(['%s'] * len(list_data))
    query = f"SELECT v.id as id_veic, v.placa, v.placaMercosul, v.renavam, v.chassi, v.uf_veic, case when v.status = 0 then 'ATIVO' when v.status = 5 then 'Erro no Cadastro' else 'INATIVO' end as status FROM veiculos v WHERE v.{column_name_in_db} IN ({placeholder_sequence})"
    cursor = connection.cursor()
    cursor.execute(query, tuple(list_data))
    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    cursor.close() 
    results = pd.DataFrame(results, columns=column_names)
    return results


def get_the_vehicle_data_in_db(connection, id_veiculo):
    result = execute_the_query(connection, f"""select v.id, v.placa, v.placaMercosul, v.renavam, v.chassi, v.uf_veic from veiculos v where v.id = '{id_veiculo}';""")
    return result


def find_vehicle_in_db_with_Vehicle(connection ,vehicle: Vehicle):
    result = search_for_the_old_plate_pattern(connection, vehicle.plate_old_pattern)
    if result is None:
        result = search_for_the_mercosul_plate_pattern(connection, vehicle.plate_mercosul_pattern)
        if result is None:
            result = search_for_the_renavam(connection, vehicle.renavam)
            if result is None:
                result = search_for_the_chassi(connection, vehicle.chassi)

    return result


def search_for_the_old_plate_pattern(connection, old_plate):
    result = execute_the_query(connection, f"SELECT v.id FROM veiculos v WHERE v.placa = '{old_plate}';")
    return result if result else None

def search_for_the_mercosul_plate_pattern(connection, mercosul_plate):
    result = execute_the_query(connection, f"SELECT v.id FROM veiculos v WHERE v.placa = '{mercosul_plate}';")
    return result if result else None

def search_for_the_renavam(connection, renavam):
    result = execute_the_query(connection, f"SELECT v.id FROM veiculos v WHERE v.renavam = '{renavam}';")
    return result if result else None

def search_for_the_chassi(connection, chassi):
    result = execute_the_query(connection, f"SELECT v.id FROM veiculos v WHERE v.chassi = '{chassi}';")
    return result if result else None



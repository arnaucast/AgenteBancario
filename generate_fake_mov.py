import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
def generate_bank_movements_for_contracts():
    # Categories list
    categories = ['RESTAURANTES COMIDA RÁPIDA', 'RESTAURANTES BARES Y CAFETERÍAS',
                  'SUPERMERCADOS, PEQUEÑO COMERCIO', 'RETIRADA EFECTIVO', 'INGRESO EFECTIVO',
                  'TRANSFERENCIA EMITIDA', 'TRANSFERENCIA RECIBIDA', 'ASOCIACIONES Y ONGs',
                  'ESTANCO', 'ELECTRODOMÉSTICOS, INFORMÁTICA Y ELECTRÓNICA',
                  'JOYAS Y COMPLEMENTOS', 'LOTERÍAS Y APUESTAS', 'REGALOS', 'ROPA Y CALZADO',
                  'MATERIAL DEPORTIVO', 'CENTROS DEPORTIVOS', 'ASOCIACIONES DE PADRES Y MADRES',
                  'EDUCACIÓN', 'UNIVERSIDAD Y ESTUDIOS SUPERIORES', 'AGUA Y SANEAMIENTO',
                  'ENERGÍA Y GAS', 'HOGAR', 'GASTOS DE ALQUILER', 'INGRESOS DE ALQUILER',
                  'NOMINA', 'PENSION SS', 'PENSION ALIMENTICIA', 'FONDOS DE INVERSIÓN',
                  'VALORES', 'CRIPTOMONEDAS', 'AMAZON', 'ALIEXPRESS', 'NEOBANCOS',
                  'MUSICA E INSTRUMENTOS', 'OCIO Y CULTURA', 'PRESTAMO', 'HIPOTECA',
                  'RENTING/LEASING', 'SEGUROS', 'COMBUSTIBLE Y RECARGA', 'PARKING Y GARAJE',
                  'TRANSPORTE', 'PEAJES', 'TRANSPORTE TREN', 'TRANSPORTE AVION', 'TRANSPORTE TAXI']

    positive_categories = {'PENSION ALIMENTICIA', 'INGRESOS DE ALQUILER', 'TRANSFERENCIA RECIBIDA', 
                          'INGRESO EFECTIVO', 'NOMINA', 'PENSION SS'}
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 4, 30)
    all_movements = []
    
    # Client types
    client_types = {
        1: "Increasing Salary Worker",
        2: "Heavy Investor",
        3: "Night Owl",
        4: "Pensionist with New Gambling",
        5: "Restaurant Enthusiast",
        6: "Traveler and Crypto Enthusiast",
        7: "Wealthy General Client",
        8: "Wealthy General Client"
    }

    # Define PENSION ALIMENTICIA behavior per contract
    pension_alimenticia_config = {
        1: 'positive',    # Increasing Salary Worker - receives pension
        2: 'negative',    # Heavy Investor - pays pension
        3: 'none',        # Night Owl - no pension
        4: 'positive',    # Pensionist - receives pension
        5: 'negative',    # Restaurant Enthusiast - pays pension
        6: 'none',        # Traveler - no pension
        7: 'positive',    # Wealthy Client 1 - receives pension
        8: 'negative'     # Wealthy Client 2 - pays pension
    }

    # Night-specific categories for Night Owl
    night_categories = ['OCIO Y CULTURA', 'FONDOS DE INVERSIÓN', 'LOTERÍAS Y APUESTAS', 'TRANSFERENCIA EMITIDA']

    # Generate 8 contracts
    for contract_id in range(1, 9):
        movements = []
        used_categories = set()

        # Helper function for random transactions
        def add_random_transaction(date, preferred_categories, weight, min_amount, max_amount):
            category = np.random.choice(preferred_categories, p=weight) if preferred_categories else np.random.choice(categories)
            used_categories.add(category)
            
            if contract_id == 3 and category in night_categories:
                hour = np.random.randint(22, 23) if np.random.random() < 0.5 else np.random.randint(0, 3)
            else:
                hour = np.random.randint(0, 23)
                
            # Set sign based on positive_categories
            sign = 1 if category in positive_categories else -1
            # Special handling for PENSION ALIMENTICIA based on contract config
            if category == 'PENSION ALIMENTICIA':
                if pension_alimenticia_config[contract_id] == 'negative':
                    sign = -1
                elif pension_alimenticia_config[contract_id] == 'none':
                    return None  # Skip this transaction
            
            return {
                'identificador_contrato': f'CON{contract_id:03d}',
                'fechahora': date.replace(hour=hour),
                'categoria': category,
                'id_signo': sign,
                'importe': np.random.uniform(min_amount, max_amount),
                'client_type': client_types[contract_id]
            }

        # Add PENSION ALIMENTICIA where applicable
        if pension_alimenticia_config[contract_id] != 'none':
            for month in range(28):
                current_date = start_date + relativedelta(months=month)
                transaction = add_random_transaction(
                    current_date + timedelta(days=np.random.randint(1, 28)),
                    ['PENSION ALIMENTICIA'], [1.0], 500, 2000
                )
                if transaction is not None:  # Only append if not None
                    movements.append(transaction)

        # Contract 1: Increasing Salary Worker
        if contract_id == 1:
            base_nomina = 10000
            for month in range(28):
                current_date = start_date + relativedelta(months=month)
                movements.append({
                    'identificador_contrato': f'CON{contract_id:03d}',
                    'fechahora': current_date.replace(day=5, hour=9),
                    'categoria': 'NOMINA',
                    'id_signo': 1,
                    'importe': base_nomina * (1 + 0.05 * (month / 12)),
                    'client_type': client_types[contract_id]
                })
                used_categories.add('NOMINA')
                for _ in range(np.random.randint(5, 10)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        ['SUPERMERCADOS, PEQUEÑO COMERCIO', 'ENERGÍA Y GAS', 'ROPA Y CALZADO'],
                        [0.5, 0.3, 0.2], 50, 500
                    )
                    if transaction is not None:
                        movements.append(transaction)

        # Contract 2: Heavy Investor
        elif contract_id == 2:
            base_nomina = 12000
            for month in range(28):
                current_date = start_date + relativedelta(months=month)
                movements.append({
                    'identificador_contrato': f'CON{contract_id:03d}',
                    'fechahora': current_date.replace(day=5, hour=9),
                    'categoria': 'NOMINA',
                    'id_signo': 1,
                    'importe': base_nomina,
                    'client_type': client_types[contract_id]
                })
                used_categories.add('NOMINA')
                for _ in range(np.random.randint(2, 4)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        ['FONDOS DE INVERSIÓN', 'VALORES', 'CRIPTOMONEDAS'],
                        [0.5, 0.3, 0.2], 5000, 20000
                    )
                    if transaction is not None:
                        movements.append(transaction)
                for _ in range(np.random.randint(5, 10)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        [], None, 100, 1000
                    )
                    if transaction is not None:
                        movements.append(transaction)

        # Contract 3: Night Owl
        elif contract_id == 3:
            base_nomina = 9000
            for month in range(28):
                current_date = start_date + relativedelta(months=month)
                movements.append({
                    'identificador_contrato': f'CON{contract_id:03d}',
                    'fechahora': current_date.replace(day=5, hour=9),
                    'categoria': 'NOMINA',
                    'id_signo': 1,
                    'importe': base_nomina,
                    'client_type': client_types[contract_id]
                })
                used_categories.add('NOMINA')
                for _ in range(np.random.randint(10, 15)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        ['OCIO Y CULTURA', 'RESTAURANTES BARES Y CAFETERÍAS', 'TRANSPORTE TAXI', 'FONDOS DE INVERSIÓN', 
                         'LOTERÍAS Y APUESTAS', 'TRANSFERENCIA EMITIDA'],
                        [0.3, 0.3, 0.1, 0.1, 0.1, 0.1], 50, 1000
                    )
                    if transaction is not None:
                        movements.append(transaction)

        # Contract 4: Pensionist with New Gambling
        elif contract_id == 4:
            base_pension = 8000
            for month in range(28):
                current_date = start_date + relativedelta(months=month)
                movements.append({
                    'identificador_contrato': f'CON{contract_id:03d}',
                    'fechahora': current_date.replace(day=10, hour=9),
                    'categoria': 'PENSION SS',
                    'id_signo': 1,
                    'importe': base_pension * (1 + 0.03 * (month / 12)),
                    'client_type': client_types[contract_id]
                })
                used_categories.add('PENSION SS')
                if current_date.year == 2025:
                    for _ in range(np.random.randint(1, 3)):
                        transaction = add_random_transaction(
                            current_date + timedelta(days=np.random.randint(1, 28)),
                            ['LOTERÍAS Y APUESTAS', 'CRIPTOMONEDAS'],
                            [0.7, 0.3], 1000, 5000
                        )
                        if transaction is not None:
                            movements.append(transaction)
                for _ in range(np.random.randint(5, 10)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        ['SUPERMERCADOS, PEQUEÑO COMERCIO', 'ENERGÍA Y GAS'],
                        [0.6, 0.4], 50, 500
                    )
                    if transaction is not None:
                        movements.append(transaction)

        # Contract 5: Restaurant Enthusiast
        elif contract_id == 5:
            base_nomina = 11000
            for month in range(28):
                current_date = start_date + relativedelta(months=month)
                movements.append({
                    'identificador_contrato': f'CON{contract_id:03d}',
                    'fechahora': current_date.replace(day=5, hour=9),
                    'categoria': 'NOMINA',
                    'id_signo': 1,
                    'importe': base_nomina,
                    'client_type': client_types[contract_id]
                })
                used_categories.add('NOMINA')
                for _ in range(np.random.randint(10, 15)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        ['RESTAURANTES COMIDA RÁPIDA', 'RESTAURANTES BARES Y CAFETERÍAS'],
                        [0.3, 0.7], 100, 1500
                    )
                    if transaction is not None:
                        movements.append(transaction)
                for _ in range(np.random.randint(3, 5)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        [], None, 50, 500
                    )
                    if transaction is not None:
                        movements.append(transaction)

        # Contract 6: Traveler and Crypto Enthusiast
        elif contract_id == 6:
            base_nomina = 12000
            for month in range(28):
                current_date = start_date + relativedelta(months=month)
                movements.append({
                    'identificador_contrato': f'CON{contract_id:03d}',
                    'fechahora': current_date.replace(day=5, hour=9),
                    'categoria': 'NOMINA',
                    'id_signo': 1,
                    'importe': base_nomina * (1 + 0.04 * (month / 12)),
                    'client_type': client_types[contract_id]
                })
                used_categories.add('NOMINA')
                for _ in range(np.random.randint(2, 4)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        ['TRANSPORTE TREN', 'TRANSPORTE AVION', 'TRANSPORTE TAXI'],
                        [0.3, 0.5, 0.2], 100, 5000
                    )
                    if transaction is not None:
                        movements.append(transaction)
                for _ in range(np.random.randint(1, 2)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        ['CRIPTOMONEDAS'], [1.0], 2000, 15000
                    )
                    if transaction is not None:
                        movements.append(transaction)
                for _ in range(np.random.randint(3, 5)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        [], None, 50, 1000
                    )
                    if transaction is not None:
                        movements.append(transaction)

        # Contracts 7-8: Wealthy General Clients
        else:
            base_nomina = 20000
            for month in range(28):
                current_date = start_date + relativedelta(months=month)
                movements.append({
                    'identificador_contrato': f'CON{contract_id:03d}',
                    'fechahora': current_date.replace(day=5, hour=9),
                    'categoria': 'NOMINA',
                    'id_signo': 1,
                    'importe': base_nomina * (1 + 0.04 * (month / 12)),
                    'client_type': client_types[contract_id]
                })
                used_categories.add('NOMINA')
                for _ in range(np.random.randint(15, 20)):
                    transaction = add_random_transaction(
                        current_date + timedelta(days=np.random.randint(1, 28)),
                        ['JOYAS Y COMPLEMENTOS', 'ROPA Y CALZADO', 'OCIO Y CULTURA', 'TRANSPORTE AVION'],
                        [0.3, 0.3, 0.2, 0.2], 500, 10000
                    )
                    if transaction is not None:
                        movements.append(transaction)

        # Ensure at least 15 categories
        while len(used_categories) < 15:
            date = start_date + timedelta(days=np.random.randint(0, 850))
            transaction = add_random_transaction(date, [], None, 100, 1000)
            if transaction is not None:
                movements.append(transaction)

        # Limit to 500 transactions per contract
        movements = movements[:500]
        all_movements.extend(movements)

    # Create DataFrame
    df = pd.DataFrame(all_movements)
    df = df.sort_values('fechahora')
    return df

# Generate the dataset
bank_movements_df = generate_bank_movements_for_contracts()

# Print the first few rows to verify
print(bank_movements_df.head())

# Save to Excel
bank_movements_df.to_excel('Fuentes\MOVEMENTS.xlsx', index=False)
import pandas as pd

def xlsx_to_csv(input_file, output_file, sheet_name=0):
    # Einlesen der Excel-Datei (standardmäßig das erste Blatt)
    df = pd.read_excel(input_file, sheet_name=sheet_name, engine='openpyxl')

    # Speichern der Daten als CSV-Datei
    df.to_csv(output_file, index=False)

    print(f"Die Datei wurde erfolgreich von {input_file} nach {output_file} konvertiert.")


xlsx_to_csv('data/ED_Waypoints_2024-09-05_2024-09-05_snapshot.xlsx',
            'data/ED_Waypoints_2024-09-05_2024-09-05_snapshot.csv',
            sheet_name='Waypoints')

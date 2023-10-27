import requests
import os
import json
import boto3
import logging

logging.basicConfig(level=logging.INFO)

api_key = '68d6bd5cbb93df86acf951076da8ac08'
country_code = 'br'

if __name__ == "__main__":
    current_dir = os.getcwd()
    new_path = current_dir + '/data/raw/landing'
    
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    
    zip_code_rj_list = [
        '23900-000', '25845-000', '28495-000', '28950-000', '28970-000', '28930-000', '27000-000', '27300-000', '26100-000',
        '28660-000', '28360-000', '28900-000', '28680-000', '28430-000', '28000-000', '28500-000', '27998-000', '28180-000',
        '28640-000', '28860-000', '25870-000', '28740-000', '28540-000', '28650-000', '25000-000', '26650-000', '25940-000',
        '28960-000', '24800-000', '23800-000', '28250-000', '28570-000', '28300-000', '27580-000', '26400-000', '28350-000',
        '27900-000', '28545-000', '25900-000', '23860-000', '24900-000', '26700-000', '26900-000', '28460-000', '28380-000',
        '26500-000', '24000-000', '28600-000', '26000-000', '26600-000', '25850-000', '23970-000', '26950-000', '25600-000',
        '27197-000', '27175-000', '28390-000', '27570-000', '27400-000', '26300-000', '28735-000', '27500-000', '28800-000',
        '27460-000', '27660-000', '28890-000', '20000-000', '28770-000', '28470-000', '28400-000', '28230-000', '24400-000',
        '28200-000', '25500-000', '28455-000', '25780-000', '28940-000', '28550-000', '25880-000', '28990-000', '23890-000',
        '28820-000', '28637-000', '24890-000', '25950-000', '28750-000', '25800-000', '27600-000', '28375-000', '27700-000',
        '27200-000']
    
    for zip_code in zip_code_rj_list:
        url = f'https://api.openweathermap.org/data/2.5/forecast?zip={zip_code},{country_code}&appid={api_key}'
        r = requests.get(url)
        data = r.json()
        
        try:
            with open(f'{new_path}\\{zip_code}.json', 'w') as outfile:
                json.dump(data, outfile)
                logging.info(f'SALVO LOCALMENTE - {zip_code}')
        except:
            logging.info('Não foi possível salvar o arquivo localmente')
        
        s3_client = boto3.client('s3')
        
        try:
            s3_client.upload_file(
                Bucket = 'openweather-amadeu',
                Filename = f'{new_path}\\{zip_code}.json',
                Key = f'raw/landing/json/{zip_code}.json'
            )
            logging.info(f'SALVO NO BUCKET - {zip_code}')
            
            os.remove(f'{new_path}\\{zip_code}.json')
            logging.info(f'REMOVIDO DA MÁQUINA LOCAL - {zip_code}')
        except:
            logging.info('Não foi possível fazer o upload do arquivo no bucket')
import mysql.connector
import asyncio
import time
import datetime
import re #<== Regular Cheak Group Text
import random
import requests
from paramiko import SSHClient
from paramiko.client import AutoAddPolicy

ping = ['1.1.1.1','1.0.0.1','8.8.8.8','8.8.4.4']

timestr = datetime.datetime.now()
date = timestr.strftime("%d-%m-%Y")
time_now = timestr.strftime("%X")
time_stamp = date + ' ' + time_now

url = 'https://notify-api.line.me/api/notify'
token = 'xoQZ0Qaq5e0lf4eFraNNs7bOVwOioE9YyNNq8zqBLjw' #<-- Token line
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}

async def check_db():  #<<<เอามาแค่ IP
    fetch_db = mysql.connector.connect(host="10.0.0.243",user="admin",password="1qaz2wsx",database="automation")
    db_python = fetch_db.cursor()
    db_python.execute(f"select * from frist_check where status='000';")
    id_list = []
    ip_list = []
    for firsh_fetch in db_python:
        get_id = firsh_fetch[0]
        get_ip = firsh_fetch[1]
        id_list.append(get_id)
        ip_list.append(get_ip)
    fetch_db.close()
    return id_list,ip_list

async def check_wan_ros(_get):
    try:
        ip = _get
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(ip, port=22,username='admin',password='1qaz2wsx',timeout=0.2)
        stdin,stdout,stderr = client.exec_command(f"ping count=10 {random.choice(ping)} interval=200ms")
        time.sleep(1.5)
        client.close()
        for output_from_stdout in stdout:
            output_from_stdout.strip()
        output_ = output_from_stdout
        output_check = r"(ms)"
        if re.search(output_check, output_):
            result = 1
            result_ip = _get
        else:
            result = 2
            result_ip = _get
    except:
        return 9
    return result

async def main_check_again():
    fetch = asyncio.create_task(check_db())
    proc_fetch = await fetch
    curo = [check_wan_ros(ip) for ip in proc_fetch[1]]
    get_result = await asyncio.gather(*curo)
    return get_result,proc_fetch[0],proc_fetch[1]

if __name__ == '__main__':
    time1 = time.time()
    main_return = asyncio.run(main_check_again())
    main_index_0 = main_return[0]   #<<< Result
    main_index_1 = main_return[1]   #<<< ID
    main_index_2 = main_return[2]   #<<< IP
    db_automation = mysql.connector.connect(host="10.0.0.243",user="admin",password="1qaz2wsx",database="automation")
    update_tables = db_automation.cursor()
##########################################################################################################################
    for result_from_ros,result_id,result_ip in zip(main_index_0 , main_index_1 , main_index_2):
        if result_from_ros == 1:
            update_tables.execute(f"UPDATE frist_check set status_text = 'Check Already',status = '001' WHERE id = '{result_id}';")
            update_tables.execute(f"insert into check_again_finish (ip,status_text,datetime) values ('{result_ip}','Can Internet','{time_stamp}');")
            db_automation.commit()
        elif result_from_ros == 2:
            update_tables.execute(f"UPDATE frist_check set status_text = 'Check Already',status = '001' WHERE id = '{result_id}';")
            update_tables.execute(f"insert into still_problem (ip,status_text,datetime) values ('{result_ip}','Can Not Internet','{time_stamp}');")
            db_automation.commit()
        elif result_from_ros == 9:
            msg = result_ip + " \nDown & Can't SSH"+ " " + time_stamp
            requests.post(url, headers=headers, data = {'message':msg})
        else:
            db_automation.close()
            break
    db_automation.close()   
    time2 = time.time() - time1
    print(f'{time2:0.2f}')

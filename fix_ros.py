import time
import datetime
import mysql.connector
import re
import random
import requests
from paramiko import SSHClient
from paramiko import AutoAddPolicy

ping = ['1.1.1.1','1.0.0.1','8.8.8.8','8.8.4.4']

timestr = datetime.datetime.now()
date = timestr.strftime("%d-%m-%Y")
time_now = timestr.strftime("%X")
time_stamp = date + ' ' + time_now

url = 'https://notify-api.line.me/api/notify'
token = 'xoQZ0Qaq5e0lf4eFraNNs7bOVwOioE9YyNNq8zqBLjw' #<-- Token line
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}

def fetch_db():
    fetch_db = mysql.connector.connect(host="10.0.0.243",user="admin",password="1qaz2wsx",database="automation")
    db_python = fetch_db.cursor()
    db_python.execute(f"select * from still_problem where status='000';")
    id_list = []
    ip_list = []
    status_list = []
    for firsh_fetch in db_python:
        get_id = firsh_fetch[0]
        get_ip = firsh_fetch[1]
        get_status = firsh_fetch[4]
        id_list.append(get_id)
        ip_list.append(get_ip)
        status_list.append(get_status)
    fetch_db.close()
    return id_list,ip_list,status_list

def reset_dhcp(_get):
    try:
        ip = _get
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(ip, port=22,username='admin',password='1qaz2wsx',timeout=0.2)
        stdin,stdout,stderr = client.exec_command("/ip dhcp-client")
        time.sleep(4)
        stdin,stdout,stderr = client.exec_command("renew 0")
        time.sleep(2)
        stdin,stdout,stderr = client.exec_command("..")
        stdin,stdout,stderr = client.exec_command("..")
        stdin,stdout,stderr = client.exec_command(f"ping count=10 {random.choice(ping)} interval=200ms")
        time.sleep(1.5)
        client.close()
        for output_from_stdout in stdout:
            output_from_stdout.strip()
        output_ = output_from_stdout
        output_check = r"(ms)"
        if re.search(output_check, output_):
            result = 1
        else:
            result = 2
    except:
        return 9
    return result

def reset_pppoe(_get):
    try:
        ip = _get
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(ip, port=22,username='admin',password='1qaz2wsx',timeout=0.2)
        stdin,stdout,stderr = client.exec_command("/interface pppoe-client disable 0")
        time.sleep(4)
        stdin,stdout,stderr = client.exec_command("/interface pppoe-client enable 0")
        time.sleep(2)
        stdin,stdout,stderr = client.exec_command("..")
        stdin,stdout,stderr = client.exec_command("..")
        stdin,stdout,stderr = client.exec_command(f"ping count=10 {random.choice(ping)} interval=200ms")
        time.sleep(1.5)
        client.close()
        for output_from_stdout in stdout:
            output_from_stdout.strip()
        output_ = output_from_stdout
        output_check = r"(ms)"
        if re.search(output_check, output_):
            result = 1
        else:
            result = 2
    except:
        return 9
    return result

def main(_get):
    if _get == '172.22.2.18': value_data = reset_dhcp(_get)
    elif _get == '172.22.2.22': value_data = reset_dhcp(_get)
    elif _get == '172.22.2.24': value_data = reset_dhcp(_get)
    elif _get == '172.22.2.26': value_data = reset_dhcp(_get)
    elif _get == '172.22.2.27': value_data = reset_dhcp(_get)
    elif _get == '172.22.2.32': value_data = reset_dhcp(_get)
    elif _get == '172.22.2.37': value_data = reset_dhcp(_get)
    else:
        value_data = reset_pppoe(_get)
    return value_data

if __name__ == '__main__':
    display = fetch_db()
    main_index_id = display[0]
    main_index_ip = display[1]
    main_index_status = display[2]
    db_automation = mysql.connector.connect(host="10.0.0.243",user="admin",password="1qaz2wsx",database="automation")
    update_tables = db_automation.cursor()
    for result_id,result_ip,result_status in zip(main_index_id,main_index_ip,main_index_status):
        if result_status == '000':
            result_from_reset = main(result_ip)
            if result_from_reset == 1: #<-- Check result from function
                update_tables.execute(f"UPDATE still_problem set status = '001' WHERE id = '{result_id}';")
                update_tables.execute(f"insert into check_again_finish (ip,status_text,datetime) values ('{result_ip}','Can Internet','{time_stamp}');")
                db_automation.commit()
            elif result_from_reset == 2:
                msg = result_ip + " \nยังใช้งานไม่ได้" + ' ' + time_stamp + "\n" + "DB_still_problem"
                requests.post(url, headers=headers, data = {'message':msg})
            elif result_from_reset == 9:
                msg = result_ip + " \nCan't SSH" + ' ' + time_stamp + "\n" + "DB_still_problem"
                requests.post(url, headers=headers, data = {'message':msg})
        else:
            db_automation.close()
            pass
    db_automation.close()

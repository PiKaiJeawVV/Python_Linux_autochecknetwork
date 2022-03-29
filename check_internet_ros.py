import mysql.connector
import requests
import time
import datetime
import random
import subprocess
import re

with open("//root//host_ros//ip_all_isp.txt",) as ip_ros:
    ip_list = ip_ros.read().splitlines()

url = 'https://notify-api.line.me/api/notify'
token = 'xoQZ0Qaq5e0lf4eFraNNs7bOVwOioE9YyNNq8zqBLjw' #<-- Token line
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}

ping = ['1.1.1.1','1.0.0.1','8.8.8.8','8.8.4.4']

db_frist_check = mysql.connector.connect(host="172.18.0.2",user="root",password="benz4466",database="automation")
insert_3 = db_frist_check.cursor()

timestr = datetime.datetime.now()
date = timestr.strftime("%d-%m-%Y")
time_now = timestr.strftime("%X")
time_stamp = date + " " + time_now
create_file = "output_" + time_stamp + ".txt"

time_hour =  timestr.strftime("%H")
time_hour_int = int(time_hour)

def insert_db_down(_get):
    add_query = ("insert into frist_check (ip, status_text, datetime) values (%s, %s, %s)")
    add_data = (_get, "Wait Check", time_stamp)
    insert_3.execute(add_query, add_data)
    db_frist_check.commit()

def clear_routing(_get_):
    command_clear_default_route = subprocess.run(f"route del -net 0.0.0.0 netmask 0.0.0.0 gw {_get_}",shell=True,stdout=subprocess.PIPE,encoding='utf-8')


def command_ping_eno2():
    command_ping = subprocess.run(f"ping -i 0.2 -c 10 -I eno2 {random.choice(ping)} | awk -F '[:=]' 'NF==5{{print $5}}' ",shell=True,stdout=subprocess.PIPE,encoding='utf-8')
def command_ping_eno3():
    command_ping = subprocess.run(f"ping -i 0.2 -c 10 -I eno3 {random.choice(ping)} | awk -F '[:=]' 'NF==5{{print $5}}' ",shell=True,stdout=subprocess.PIPE,encoding='utf-8')


def default_route_eno2(_get):
    command_default_route = subprocess.run(f'route add -net 0.0.0.0 netmask 0.0.0.0 gw {_get} metric 10',shell=True,stdout=subprocess.PIPE,encoding='utf-8')
    command_ping = subprocess.run(f"ping -i 0.2 -c 10 -I eno2 {random.choice(ping)} | awk -F '[:=]' 'NF==5{{print $5}}' ",shell=True,stdout=subprocess.PIPE,encoding='utf-8')
    output_data = command_ping.stdout
    output_data.strip()
    output_check = r"(ms)"
    recheck_txt = re.search(output_check, output_data)
    if recheck_txt:
        status_check_wan = 1
    else:
        status_check_wan = 2
        insert_db_down(_get)
    clear_routing(_get)

def default_route_eno3(_get):
    command_default_route = subprocess.run(f'route add -net 0.0.0.0 netmask 0.0.0.0 gw {_get} metric 10',shell=True,stdout=subprocess.PIPE,encoding='utf-8')
    command_ping = subprocess.run(f"ping -i 0.2 -c 10 -I eno3 {random.choice(ping)} | awk -F '[:=]' 'NF==5{{print $5}}' ",shell=True,stdout=subprocess.PIPE,encoding='utf-8')
    output_data = command_ping.stdout
    output_data.strip()
    output_check = r"(ms)"
    recheck_txt = re.search(output_check, output_data)
    if recheck_txt:
        status_check_wan = 1
    else:
        status_check_wan = 2
        insert_db_down(_get)
    clear_routing(_get)

def main(_get):
    if _get == "172.22.1.1": default_route_eno3(_get)
    elif _get == "172.22.1.2": default_route_eno3(_get)
    elif _get == "172.22.1.3": default_route_eno3(_get)
    elif _get == "172.22.1.4": default_route_eno3(_get)
    elif _get == "172.22.1.5": default_route_eno3(_get)
    elif _get == "172.22.1.6": default_route_eno3(_get)
    else:
        default_route_eno2(_get)

if __name__ == '__main__':
    t1 = time.time()
    if time_hour_int != 4:
        for data_ip in ip_list:
            try:
                main(data_ip)
            except:
                pass
    else:
        pass
    t2 = time.time() - t1
    db_frist_check.close()
    if time_hour_int >= 10 and time_hour_int <= 20: 
        msg = 'Check already\n' + f'Run Program {t2:0.2f} Sec.'
        requests.post(url, headers=headers, data = {'message':msg})
    else:
        pass
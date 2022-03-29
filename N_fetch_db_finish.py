# N_fetch_db_finish.py
import datetime
import time
import requests
import mysql.connector

class Autimation_option:
    def _timeline(self):
        timestr = datetime.datetime.now()
        date = timestr.strftime("%d-%m-%Y")
        time_now = timestr.strftime("%X")
        time_stamp = date + ' ' + time_now
        return date,time_now,time_stamp

    def _send(self,*args):
        url = 'https://notify-api.line.me/api/notify'
        token = 'xoQZ0Qaq5e0lf4eFraNNs7bOVwOioE9YyNNq8zqBLjw' #<-- Token line
        headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
        meassage = args
        requests.post(url, headers=headers, data = {'message':meassage})

class Connect_database:
    def _fetch_db(self):
        fetch_db = mysql.connector.connect(host="172.18.0.2",user="root",password="benz4466",database="automation")
        db_python = fetch_db.cursor()
        db_python.execute(f"select * from check_again_finish where status='000';")
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
    
    def _update_db(self,_get_id):
        update_db = mysql.connector.connect(host="172.18.0.2",user="root",password="benz4466",database="automation")
        update_tables = update_db.cursor()
        update_tables.execute(f"UPDATE check_again_finish set status = '001' WHERE id = '{_get_id}';")
        update_db.commit()
        update_db.close()

if __name__ == "__main__":
    option1 = Autimation_option()
    option2 = Connect_database() #<-- Class Database
    timeoption = option1._timeline()
    index_time = timeoption[2]
    result = option2._fetch_db()
    index1 = result[0]
    index2 = result[1]
    index3 = result[2]

    for result_id,result_ip,result_status in zip(index1,index2,index3):
        #print(result_id,result_ip,result_status)
        if result_status == '000':
            option2._update_db(result_id)
            option1._send(f"{result_ip} Can Internet \nTime: {index_time} \nDB_check_again_finish")
        else:
            break
    
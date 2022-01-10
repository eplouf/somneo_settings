__version__ = "0.1"

import logging
from flask import Flask, make_response, render_template, redirect, request, jsonify
from sommeilsunset import libs
from random import randrange

logging.basicConfig()

app = Flask(__name__)

somlib = libs.somlib()


def runrun():
    app.run(host="127.0.0.1", port="8080")


@app.route('/')
def index():
    return render_template("device_info.html")


@app.route('/alarms', methods=['GET'])
def alarms():
    alarms = [{'index': 0, 'enabled': False, 'ayear': 0, 'amnth': 0, 'alday': 0, 'daynm': [['Lundi', True], ['Mardi', True], ['Mercredi', True], ['Jeudi', True], ['Vendredi', True], ['Samedi', True], ['Dimanche', True]], 'almhr': 7, 'almmn': 0}, {'index': 1, 'enabled': False, 'ayear': 0, 'amnth': 0, 'alday': 0, 'daynm': [['Lundi', True], ['Mardi', True], ['Mercredi', True], ['Jeudi', True], ['Vendredi', True], ['Samedi', False], ['Dimanche', False]], 'almhr': 6, 'almmn': 30}]
    try:
        alarms = somlib.getAlarms()
    except Exception as e:
        return render_template("alarms.html",
                               alarms1=alarms[0],
                               alarms2=alarms[1],
                               error_text=e.__str__())
    for alarm in alarms:
        hour = alarm['almhr']
        minute = alarm['almmn']
        suffix = "AM"
        if hour > 12:
            suffix = "PM"
            hour %= 12
        clock = "{:>02d}:{:>02d} {}".format(hour, minute, suffix)
        alarm['clock'] = clock
    return render_template("alarms.html",
                           alarms1=alarms[0],
                           alarms2=alarms[1])


@app.route('/alarms', methods=['POST'])
def alarmsSet():
    data = request.json
    # data is like:
    # [{"clock":"05:42 PM","enabled": true, "1_Lundi":false,"1_Mardi":true,"1_Mercredi":false,"1_Jeudi":true,"1_Vendredi":false,"1_Samedi":false,"1_Dimanche":true},{"clock":"10:03 PM","2_Lundi":true,"2_Mardi":true,"2_Mercredi":true,"2_Jeudi":true,"2_Vendredi":true,"2_Samedi":true,"2_Dimanche":true}]
    # would have to be changed to:
    # alarm[0] = {'enabled': true, 'year': 0, 'mnth': 0, 'lday': 0, 'daynm': [list of weekdays names], 'lmhr': 7, 'lmmn': 30}
    # the clock field have to be expanded to lmhr and lmmn in that function
    alarm_struct = []
    for alarmdata in data:
        alarm = {'daynm': [],
                 'year': 0,
                 'mnth': 0,
                 'lday': 0}
        for field in alarmdata:
            if field == 'clock':
                alarm['lmhr'] = int(alarmdata[field][:2])
                alarm['lmmn'] = int(alarmdata[field][3:5])
                if 'PM' in alarmdata[field]:
                    alarm['lmhr'] += 12
                    alarm['lmhr'] %= 24
            elif field == 'enabled':
                alarm['enabled'] = alarmdata[field]
            else:
                # then it is a weekday
                if alarmdata[field] is True:
                    weekday = field[2:]
                    alarm['daynm'].append(weekday)
        alarm_struct.append(alarm)
    try:
        somlib.setAlarms(alarm_struct)
    except Exception as e:
        logging.exception("somlib.setAlarms")
        return ("problème" + e.__str__(), 500)
    return redirect('/alarms')


@app.route('/light')
def light():
    try:
        results = somlib.Light()
        light_status = results['onoff']
        night_status = results['ngtlt']
    except:
        light_status = "N/A"
        night_status = "N/A"
    return render_template("light.html",
                           light_status=light_status,
                           night_status=night_status)


@app.route('/api/probes')
def apiProbes():
    results = {'temperature': randrange(1, 50),
              'humidity': randrange(1, 50),
              'luminance': randrange(1, 50),
              'noise': randrange(1, 50)}
    try:
        results = somlib.Probes()
    except Exception as e:
        results['error'] = e.__str__()
    return ((jsonify(results), 200))


@app.route('/probes')
def probes():
    results = {'temperature': 0,
              'humidity': 0,
              'luminance': 0,
              'noise': 0}

    try:
        results = somlib.Probes()
    except:
        return render_template("sensors.html",
                               error_text="issue fetching probes",
                               temperature=results['temperature'],
                               humidity=results['humidity'],
                               luminance=results['luminance'],
                               noise=results['noise'])

    return render_template("sensors.html",
                           temperature=results['temperature'],
                           humidity=results['humidity'],
                           luminance=results['luminance'],
                           noise=results['noise'])


@app.route('/radio')
def radio():
    return render_template("radio.html")


@app.route('/relax')
def relax():
    return render_template("relax.html")


@app.route("/_wutim")
def wutim():
    # {"yrltm":2017,"moltm":1,"dtltm":7,"hrltm":11,"miltm":22,"scltm":50,"daynm":6}
    result = somlib.get("/wutim")
    return make_response((jsonify(result), 200))


@app.route("/_wualm")
def wualm():
    # {"snztm":9,"aenvs":{},"aalms":{},"prfsh":0}
    result = somlib.get("/wualm")
    return make_response((jsonify(result), 200))


@app.route("/_wudsk")
def wudsk():
    # {"onoff":false,"curve":18,"durat":30,"ctype":0,"sndtp":0,"snddv":"off","sndch":"","sndlv":12,"sndss":0}
    result = somlib.get("/wudsk")
    return make_response((jsonify(result), 200))


@app.route("/_wufmp")
def wufmp():
    result = somlib.get("/wufmp")
    return make_response((jsonify(result), 200))


@app.route("/_wufmr")
def wufmr():
    # {"fmfrq":"87.80","fmcmd":"set","fmsts":false,"fmspc":100,"prstn":1,"chtot":5}
    return make_response(("", 200))


@app.route("/_wulgt")
def wulgt():
    # {"ltlvl":10,"onoff":false,"tempy":false,"ctype":0,"ngtlt":false,"wucrv":[],"pwmon":false,"pwmvs":[0,0,0,0,0,0],"diman":0}
    # {"ltlvl":10,"onoff":false,"tempy":false,"ctype":0,"ngtlt":true,"wucrv":[],"pwmon":false,"pwmvs":[0,0,0,0,0,0],"diman":0}
    return make_response(("", 200))


@app.route("/_wumem")
def wumem():
    # {"mutyp":"mp3","mutot":0,"muusa":0,"muuse":[1,3000]}
    return make_response(("", 200))


@app.route("/_wumus")
def wumus():
    # {"mutyp":0,"muind":0}
    return make_response(("", 200))


@app.route("/_wungt")
def wungt():
    # {"ntstr":"","ntend":"07:00","ntlen":"07:00","night":false,"gdngt":false,"gdday":false,"tg2bd":"2017-01-07T07:14:30+00:00","tendb":"2017-01-07T07:14:31+00:00"}
    return make_response(("", 200))


@app.route("/_wuply")
def wuply():
    # {"onoff":false,"tempy":false,"sdvol":8,"sndss":0,"snddv":"off","sndch":"1"}
    return make_response(("", 200))


@app.route("/_wurlx")
def wurlx():
    # {"durat":10,"onoff":false,"maxpr":7,"progr":1,"rtype":0,"intny":20,"sndlv":12,"sndss":0,"rlbpm":[4,5,6,7,8,9,10],"pause":[2000,2000,2000,2000,1000,1000,1000]}
    return make_response(("", 200))


@app.route("/_wusnd")
def wusnd():
    # {"sdvol":8,"softst":0,"chifn":0,"softst":false}
    return make_response(("", 200))


@app.route("/_wusrd")
def wusrd():
    # {"mslux":70.0,"mstmp":21.7,"msrhu":38.9,"mssnd":25,"avlux":65.7,"avtmp":21.5,"avhum":37.7,"avsnd":25,"enscr":0}
    return make_response(("", 200))


@app.route("/_wutmr")
def wutmr():
    # {"stime":"2017-01-07T11:26:32+00:00","rlxmn":0,"rlxsc":0,"dskmn":0,"dsksc":0}
    return make_response(("", 200))


@app.route("/_wutms")
def wutms():
    # {"fmthr":true,"fmtwk":false,"tmupd":0,"tzhrm":[0,0],"dstwu":0,"tmsrc":"dis","tmsyn":"","tmser":"","locat":""}
    return make_response(("", 200))

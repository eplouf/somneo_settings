import logging
import requests
from requests.adapters import HTTPAdapter
import json

logging.basicConfig()

class somlib(object):

    #def __init__(self, host="192.168.1.1", weekdays=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']):
    def __init__(self, host="192.168.1.1", weekdays=[None, 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']):
        self.rs = requests.session()
        self.rs.verify = False
        HTTPopts = HTTPAdapter(max_retries=0)
        self.rs.mount("https://" + host, HTTPopts)
        self.producturi = "/di/v1/products/1/"
        self.url = "https://" + host + self.producturi
        self.wualm = {"snztm": 9, "aenvs": {}, "aalms": {}, "prfsh":0}
        self.aenvs = {'prfen': [bool() for i in range(16)],
                'prfvs': [bool() for i in range(16)],
                'pwrsv': [int() for i in range(16)]}
        self.aenvs['prfen'][0] = False
        self.aenvs['prfen'][1] = False
        self.aalms = { 'ayear': [int() for i in range(16)],
                'amnth': [int() for i in range(16)],
                'alday': [int() for i in range(16)],
                'daynm': [int(0xfe) for i in range(16)],
                'almhr': [int() for i in range(16)],
                'almmn': [int() for i in range(16)]}
        self.prfwu = {'prfen': bool(),
                'prfnr': int(),
                'pname': str(),
                'prfen': bool(),
                'prfvs': bool(),
                'almhr': int(),
                'almmn': int(),
                'ctype': int(),
                'daynm': int(),
                'pwrsz': int(),
                #'pszhr': int(),
                #'pszmn': int(),
                #'curve': 15,
                #'durat': 10,
                #'snddv': 'wus',
                #'sndch': 6,
                #'sndlv': 6,
                #'sndss': 0
                }
        self.wualm = {'prfnr': int()}
        self.anxday = weekdays
        self.mask2idx = []
        j = 1
        for i in range(7):
            j<<=1
            self.mask2idx.append(j)

    def _get(self, urifunc):
        urlfunc = self.url + urifunc
        try:
            req = self.rs.get(urlfunc, timeout=5)
        except requests.ConnectionError:
            logging.error("ConnectionError")
            raise
        except requests.ConnectTimeout:
            logging.error("ConnectTimeout")
            raise
        except requests.HTTPError:
            logging.error("HTTPError")
            raise
        try:
            json = req.json()
        except:
            logging.error("Not a json")
            raise
        return json

    def _put(self, urifunc, data):
        headers = {'Content-Type': 'application/json'}
        urlfunc = self.url + urifunc
        try:
            req = self.rs.put(urlfunc, data=data, headers=headers, timeout=30)
        except requests.ConnectionError:
            logging.exception("ConnectionError")
            raise
        except requests.ConnectTimeout:
            logging.exception("ConnectTimeout")
            raise
        except requests.HTTPError:
            logging.exception("HTTPError")
            raise
        return req.status_code

    def getAlarms(self):
        alarms = []
        idx = 0
        try:
            self.aenvs = self._get('wualm/aenvs')
            self.aalms = self._get('wualm/aalms')
        except:
            logging.exception("getAlarms")
            raise
        for enabled in self.aenvs['prfen']:
            alarm = {'index': idx}
            alarm['enabled'] = enabled
            for key in self.aalms:
                if key == 'daynm':
                    alarm[key] = self.daysAnded(self.aalms[key][idx])
                else:
                    alarm[key] = self.aalms[key][idx]
            alarms.append(alarm)
            del alarm
            idx+=1
        return alarms

    def setAlarms(self, alarms_struct):
        idx = 0
        for alarm in alarms_struct:
            idx+=1
            prfwu = {}
            if 'enabled' not in alarm:
                continue
            prfwu['prfnr'] = idx
            prfwu['prfen'] = alarm['enabled']
            prfwu['ayear'] = alarm['year']
            prfwu['amnth'] = alarm['mnth']
            prfwu['alday'] = alarm['lday']
            prfwu['daynm'] = self.daysOred(alarm['daynm'])
            prfwu['almhr'] = alarm['lmhr']
            prfwu['almmn'] = alarm['lmmn']
            try:
                exit = self._put('wualm/prfwu', json.dumps(prfwu))
            except:
                logging.exception("setAlarms {}".format(idx))
                raise

        return exit

    # returns a list of human readable days name and enabled flag
    # against the natural or'ed field of hf3672 SmartSleep Philips
    def daysAnded(self, daynm):
        days = []

        idx = 0
        for day in self.mask2idx:
            test = daynm & day
            if test:
                days.append([self.anxday[idx%7+1], True])
            else:
                days.append([self.anxday[idx%7+1], False])
            idx+=1

        return days

    # returns an int with all days
    # from a list of human readable days name
    # 1 = Monday is the starts
    def daysOred(self, days):
        daynm = int()
        for day in days:
            iday = self.anxday.index(day)
            daynm |= pow(2, iday)
        return daynm

    def Probes(self):
        results = {}
        results['temperature'] = 0
        results['humidity'] = 0
        results['luminance'] = 0
        results['noise'] = 0
        try:
            probes = self._get('wusrd')
        except:
            logging.exception("probes")
            raise
        results['temperature'] = probes['mstmp']
        results['humidity'] = probes['msrhu']
        results['luminance'] = probes['mslux']
        results['noise'] = probes['mssnd']
        return results

    def Light(self):
        try:
            lights = self._get('wulgt')
        except:
            logging.exception("lights")
            raise
        return lights

import requests
from time import sleep

class Pyplan(object):
    """Class for comunicate with pyplan via rest api"""

    def __init__(self, pyplan_host):
        self.pyplan_host = pyplan_host
        self.model_info = None
        self.token = None
        self.session_key = None
        self.model_info = None

    def login(self, user, password, company_id=2):
        #sleep(10)
        auth_response = requests.post(
            f'{self.pyplan_host}/api/token-auth/', {'username': user, 'password': password})
        auth_response.raise_for_status()
        res = auth_response.json()
        if res and "token" in res:
            self.token = res["token"]
            session_response = requests.post(
                f'{self.pyplan_host}/api/security/createSession', {'companyId': company_id}, headers={'Authorization': f"Token {self.token}"})
            session_response.raise_for_status()
            res = session_response.json()
            if res and "session_key" in res:
                self.session_key = res["session_key"]

                return True

        raise ValueError('The user or password is incorrect')

    def open_model(self, model):
        open_response = requests.get(
            f'{self.pyplan_host}/api/modelManager/openModel/?file={model}&new_instance=1', headers={'Authorization': f"Token {self.token}", "session-key": self.session_key})
        open_response.raise_for_status()
        self.model_info = open_response.json()

    def is_ready(self):
        return not self.model_info is None

    def getResult(self, node_id):
        res = requests.post(
            f'{self.pyplan_host}/api/modelManager/callFunction/', json={"node": "get_result", "params": {"node_id":node_id}}, headers={'Authorization': f"Token {self.token}", "session-key": self.session_key})
        res.raise_for_status()
        return res.json()

    def getStatus(self, nodes):
        res = requests.post(
            f'{self.pyplan_host}/api/dashboardManager/isResultComputed/', json={"nodes": nodes}, headers={'Authorization': f"Token {self.token}", "session-key": self.session_key})
        res.raise_for_status()
        if res.status_code==204:
            return []
        return res.json()

    def setSelectorValue(self, node_id, value):
        res = requests.post(
            f'{self.pyplan_host}/api/modelManager/setSelectorValue/', json={"nodeId": node_id, "value": value}, headers={'Authorization': f"Token {self.token}", "session-key": self.session_key})
        res.raise_for_status()
        return res.text

        
            

        

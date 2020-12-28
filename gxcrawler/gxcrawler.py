import json
import datetime

import requests
from lxml import etree


class GxCrawler():
    '''
    Crawler data in genexus server 16
    '''

    def __init__(self, user_login, user_password, url_base, kb_name):
        '''
        Class responsible for obtaining data from the genexus server
        Params:
        ------
        user_login:     String (user login server)
        user_password:  String (password login server)
        url_base:       String (initial url of address of gxserver)
        kb_name:        String (name of kb of data)
        Returns:
        -------
        revision_data:  List<Dict> (List of revision)

        Ex: gxcrawler = GxCrawler('user', 'password',
                                http://192.168.1.1/GeneXusServer16',
                                kb_name='App')
        '''
        self.session = requests.Session()
        self.user = user_login
        self.password = user_password
        self.url_base = url_base
        self.kb_name = kb_name
        self.host = self.__get_host(url_base)
        self.X_GXAUTH_TOKEN = None
        self.GX_AUTH_ACTIVITY = None
        self.prefix_gx = [
                        'vREVISIONDATE_', 'vSECONDS_', 'vUSER_', 'vCOMMENT_', 
                        'vREVISIONNAME_', 'vOPERATION_', 'vBUILD_']
        self.prefix_gx_objects = [
                        'W0077vTYPE_', 'W0077vNAMEAUX_', 
                        'W0077vENTITYGUID_', 'W0077vENTITYID_', 
                        'W0077vOBJOPERATION_']
        self.LIMIT_PAGES = 1000
        self.LIMITE_PER_REVISION = 1000

        self.descriptions = {
            'vREVISIONDATE_': 'revision_date',
            'vSECONDS_': 'revision_seconds',
            'vUSER_': 'revision_user',
            'vCOMMENT_': 'revision_comment',
            'vREVISIONNAME_': 'revision_name',
            'vOPERATION_': 'revision_operation',
            'vBUILD_': 'revision_build'
        }

        self.descriptions_objects = {
            'W0077vTYPE_': 'object_type',
            'W0077vNAMEAUX_': 'object_name',
            'W0077vENTITYGUID_': 'object_gu_id',
            'W0077vENTITYID_': 'object_entity_id',
            'W0077vOBJOPERATION_': 'object_operation'
        }

    def __format_date_req_param(self, date_time):
        '''
        Method for return date hour in format expected in request.
        Ex: 10/26/20 11:51 AM to 2020/10/26 13:13:00
        '''
        return (date_time[3:5]+'/'+date_time[0:2]+'/'+'20'+date_time[6:8]
                + ' ' + date_time[9:14]+':00')

    def __get_x_auth_token(self, response):
        '''
        Method get token
        Params:
        ------
            response: Request
        Returns:
        -------
            x-auth-token: String
        '''
        tree = etree.HTML(response.text)
        tree = tree.xpath('./body/form/div[2]//input')[0]
        response_json = json.loads(tree.attrib.get('value'))
        return response_json.get('GX_AUTH_W0010MAINLOGIN')

    def __get_gx_auth_activity(self, response):
        '''
        Method get token page activity
        Params:
        ------
            response: Request
        Returns:
        -------
            x-auth-token: String
        '''
        tree = etree.HTML(response.text)
        tree = tree.xpath('./body/script')[0]
        index = tree.text.index('GX_AUTH_ACTIVITY')
        index_final = tree.text.index('"', index+19)
        return tree.text[index+19: index_final]

    def __get_host(self, url_base):
        '''
        Method of get host in url base
        Params:
        ------
        url_base: String

        Returns:
        -------
        host: String (host of url base)
        '''
        if url_base:
            index = url_base.index('//')+2
            return url_base[index: url_base.index('/', index)]
        return None

    def get_data(self, initial_date=None, final_date=None):
        '''
        Método para obtenção dos dados
        Parametros:
        ----------
            None
        Retorno:
        -------
            List ou Array.
        '''
        url = f'{self.url_base}/main.aspx'
        headers = {
            'Host': self.host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = self.session.get(url, headers=headers)

        self.X_GXAUTH_TOKEN = self.__get_x_auth_token(response)

        # login page
        url = f'{self.url_base}/main.aspx?gxfullajaxEvt,gx-no-cache=1603735860022'
        headers = {
            'Host': self.host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'GxAjaxRequest': '1',
            'Content-Type': 'application/json',
            'X-GXAUTH-TOKEN': self.X_GXAUTH_TOKEN,
            'Content-Length': '230',
            'Connection': 'keep-alive',
            'Referer': f'{self.url_base}/main.aspx',
        }
        payload = '{"MPage":false,"cmpCtx":"W0010","parms":[{"s":"Local","v":[["Local","Local"]]},"Local","'+self.user+'","'+self.password+'","",false,false],"hsh":[],"objClass":"mainlogin","pkgName":"Artech.GeneXusServer","events":["ENTER"],"grids":{}}'

        response = self.session.get(url, headers=headers, data=payload)
        # Expected {"gxCommands":[{"redirect":{"url":"/GeneXusServer16/dashboard.aspx"}}]}

        # Page after login (dashboard)
        url = f'{self.url_base}/dashboard.aspx'
        headers = {
            'Host': self.host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'X-SPA-MP': 'masterpagebeforelogin',
            'X-SPA-REQUEST': '1',
            'Connection': 'keep-alive',
            'Referer': f'{self.url_base}/main.aspx',
        }
        response = self.session.get(url, headers=headers)
        url = f'{self.url_base}/activity.aspx?{self.kb_name}'
        headers = {
            'Host': self.host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'X-SPA-MP': 'masterpage',
            'X-SPA-REQUEST': '1',
            'Connection': 'keep-alive',
            'Referer': f'{self.url_base}/dashboard.aspx',
        }
        response = self.session.get(url, headers=headers)

        # Defining the authentication key to obtain the list of objects 
        # in the event activity
        self.GX_AUTH_ACTIVITY = self.__get_gx_auth_activity(response)

        if initial_date is None or final_date is None:
            current_timestamp = datetime.datetime.today()
            initial_data_parm = f'{current_timestamp.year}{current_timestamp.month}{str(current_timestamp.day).zfill(2)}'
            final_data_parm = initial_data_parm
        else:
            initial_data_parm = f'{initial_date.year}{initial_date.month}{str(initial_date.day).zfill(2)}'
            final_data_parm = f'{final_date.year}{final_date.month}{str(final_date.day).zfill(2)}'

        return list(self.__get_data_by_data(initial_date=initial_data_parm,
                                            final_date=final_data_parm))

    def __get_data_by_data(self, initial_date=None, final_date=None):
        '''
        Method to get data with date filter
        Params:
        ------
        initial_date: String (Date format YYYYMMMDD)
        final_date: String (Date format YYYYMMMDD)

        Returns:
        -------
        revisions: List<Dict>

        Ex: revisions = gxcrawler.get_data_by_data('20201024', '20201024')
        '''
        count = 1
        pagina = 1
        while pagina <= self.LIMIT_PAGES:
            url = f'{self.url_base}/activity.aspx?gxajaxGridRefresh_Activitygrid,10,{pagina},{initial_date},{final_date},,1633,false,gx-no-cache=1603737012264'
            headers = {
                'Host': self.host,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
                'Accept': '*/*',
                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'GxAjaxRequest': '1',
                'Connection': 'keep-alive',
                'Referer': f'{self.url_base}/activity.aspx?{self.kb_name}',
            }
            response = self.session.get(url, headers=headers)
            count = self.__get_count_commits(response)
            if count == 0:
                pagina = self.LIMIT_PAGES + 1
            else:
                yield list(self.__get_commit_json(response, count))
                pagina += 1

    def __get_count_commits(self, response):
        '''
        Method to return the number of operations returned in the request
        Params:
        ------
        response: Request

        Returns:
        -------
        count_returns: int
        '''
        response_json = json.loads(response.text)
        response_json = response_json.get('gxGrids')
        if response_json:
            return response_json[0]['Count']
        else:
            return 0

    def __get_commit_json(self, response, quantidade_operacoes=10):
        '''
        Metodo para retornar os dados do commit em json junto com a lista de objetos
        Parâmetros:
        ----------
            response: Request
            quantidade_operacoes: int (Quantidade de commits que retornou da requisição)
        Retorno:
        -------
            List<Dict>
        '''
        response_json = json.loads(response.text)
        response_json = response_json['gxValues']
        try:
            for res in response_json:
                for commit in range(1, quantidade_operacoes+1):
                    commit_dados = {}
                    tags_gx = [f'{tag}{str(commit).zfill(4)}' for tag in self.prefix_gx]
                    tags_res = [self.descriptions.get(key) for key in self.prefix_gx]
                    for i in range(0, len(self.prefix_gx)):
                        commit_dados[tags_res[i]] = res[tags_gx[i]]

                    commit_dados['revision_objects'] = list(
                        self.__get_commit_objects(
                            param0=commit_dados[tags_res[4]],
                            param1=self.__format_date_req_param(
                                commit_dados[tags_res[0]]
                            ),
                            param2=commit_dados[tags_res[5]],
                            param3=commit_dados[tags_res[6]],
                            param4=commit_dados[tags_res[2]],
                            param5=commit_dados[tags_res[3]],
                            grid_row=commit)
                    )

                    yield commit_dados

        except KeyError:
            raise 'Tag de dados incorreta.'

    def __get_commit_objects(self, param0=None, param1=None, param2=None, param3=None, param4=None, param5=None, grid_row=None):
        '''
        Method to return the list of objects related to a server operation
        Params:
        ------
        param0:     String
        param0:     String
        param1:     String
        param2:     String
        param3:     String
        param4:     String
        param5:     String
        grid_row:   String

        Returns:
        -------
        revision_obj:   List<Dict>
        '''

        url = f'{self.url_base}/activity.aspx?gxfullajaxEvt,{self.kb_name},gx-no-cache=1603740836511'
        headers = {
            'Host': self.host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'GxAjaxRequest': '1',
            'Content-Type': 'application/json',
            'X-GXAUTH-TOKEN': self.GX_AUTH_ACTIVITY,
            'Content-Length': '358',
            'Connection': 'keep-alive',
            'Referer': f'{self.url_base}/activity.aspx?{self.kb_name}',
        }
        payload = (
            '{"MPage":false,"cmpCtx":"",'
            '"parms":["'+param0+'","'+param1+'","'+param2+'",'+param3+','
            '"'+param4+'","'+param5+'",true],'
            '"hsh":[],"objClass":"activity","pkgName":"Artech.GeneXusServer",'
            '"events":["ACTIVITYGRID.ONLINEACTIVATE"],"grid":45,'
            '"grids":{"Activitygrid":{"id":45,"lastRow":2,"pRow":""}},'
            '"row":"'+str(grid_row).zfill(4)+'","pRow":""}')

        response = self.session.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            response_json = json.loads(response.text)
            response_json = response_json['gxValues'][1]

            revision_obj = 1
            while revision_obj < self.LIMITE_PER_REVISION:
                tag = f'{self.prefix_gx_objects[0]}{str(revision_obj).zfill(4)}' #f'W0077vTYPE_{str(objeto).zfill(4)}'
                if tag in response_json.keys():
                    commit_dados = {}
                    for tag in self.prefix_gx_objects:
                        tag_full = f'{tag}{str(revision_obj).zfill(4)}'
                        commit_dados[self.descriptions_objects.get(tag)] = response_json[tag_full]
                    revision_obj += 1

                    yield commit_dados
                else:
                    revision_obj = self.LIMITE_PER_REVISION + 1

        return None

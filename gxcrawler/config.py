'''
Class of configuration the enviroment to client

Configure enviroment
'''

import os


class Config():
    '''
    Class Config
    '''
    def __init__(self, method=None):
        '''
        Class for securely configuring the genexus server.
        The possible methods to configure are environment
        and .env file variables (ENV and FILE respectively)
        Params:
        ------
            method: String
        '''
        self.user = None
        self.password = None
        self.url = None
        self.kb_name = None

        if method is None:
            self.__get_config_enviroment()
            if self.user is None:
                self.__get_config_file()
        else:
            if method == 'FILE':
                self.__get_config_file()
            else:
                self.__get_config_enviroment()

        if self.user is None:
            raise Exception('Not found configuration')

    def __get_config_enviroment(self):
        '''
        Set the configuration for environment variables
        '''
        self.user = os.getenv('GX_USER')
        self.password = os.getenv('GX_PASSWORD')
        self.url = os.getenv('GX_URL')
        self.kb_name = os.getenv('GX_KBNAME')

    def __get_config_file(self):
        '''
        Set the configuration for .env file
        '''
        # Path of file run in the project
        configure_file = os.path.dirname(os.path.abspath(__file__))
        configure_file += os.sep + '.env'
        with open(configure_file, 'r') as f_config:
            while True:
                line = f_config.readline()
                if line:
                    key, value = self.__get_key_value(line)
                    if key == 'GX_USER':
                        self.user = value
                    elif key == 'GX_PASSWORD':
                        self.password = value
                    elif key == 'GX_URL':
                        self.url = value
                    elif key == 'GX_KBNAME':
                        self.kb_name = value
                else:
                    break

    def __get_key_value(self, var_env):
        '''
        Get key and value for a line from the .env file
        Params:
        ------
            var_env: String (Line of .env file)
        '''
        # Cleaning line after read of file
        var_env = var_env.replace('\r\n', '').replace('\n', '')
        key = var_env[:var_env.index('=')]
        value = var_env[var_env.index('=')+1:]
        return key, value

    def get_configuration(self):
        '''
        Get the configuration result
        '''
        return {
            'user': self.user,
            'password': self.password,
            'url': self.url,
            'kb_name': self.kb_name
        }

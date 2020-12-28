from gxcrawler import GxCrawler
from database import DataBase
from config import Config


class Process():
    def __init__(self):
        '''
        Class capture data and incluse in db
        '''
        self.__initial_date = None
        self.__final_date = None

    def capture_data(self, initial_date=None, final_date=None, config=None):
        if config is None:
            config = Config(method='FILE')

        configuration = config.get_configuration()
        gxcrawler = GxCrawler(
            configuration['user'],
            configuration['password'],
            configuration['url'],
            configuration['kb_name']
        )

        try:
            self.__initial_date = initial_date
            self.__final_date = final_date
            data = gxcrawler.get_data(initial_date, final_date)
            self.__inject_db(data)
        except KeyboardInterrupt as ke_interrupt:
            raise Exception('Operação interrompida.') from ke_interrupt

    def __inject_db(self, data):
        '''
        Injecting data into the database
        '''
        database = DataBase()
        print(f'Injecting data into the database: {self.__initial_date} to {self.__final_date}')
        for page in data:
            for rev in page:
                database.insert_revision(rev)

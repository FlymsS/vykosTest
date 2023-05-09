from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import Session

from decouple import config


class DbConection:
    user = config("MYSQL_USER")
    password = config("MYSQL_PASSWORD")
    host = config("MYSQL_HOST")
    database = config("MYSQL_DATABASE")
    connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database}"
    engine = None
    connection = None
    session = None

    def conect(self):
        if (not self.engine):
            self.engine = create_engine(self.connection_string)
        self.connection = self.engine.connect()
        self.session = Session(self.engine)

    def disconect(self):
        self.connection.close()

    def getSession(self):
        if not self.session or self.connection.closed or not self.connection:
            self.conect()
        return self.session

    def getConection(self):
        if not self.connection:
            self.conect()
        return self.connection

    def getEngine(self):
        self.conect()
        return self.engine

    def restarTable(tableName: str, self):
        table_to_drop = Table(tableName, autoload=True)
        table_to_drop.drop(self.engine)

    def consult(self, query: str, params: dict):
        if (not self.connection or self.connection.closed):
            self.conect()
        res = self.connection.execute(query, params)
        self.disconect()
        return res

    def saveRecord(self, record: object, tableName: str):
        if (not self.connection or self.connection.closed):
            self.conect()
        self.session.add(record)
        self.session.commit()
        self.disconect()

    def saveMultiplesRecords(self, records: list[object], tableName: str):
        self.conect()
        session = Session(self.engine)
        session.add_all(records)
        session.commit()
        self.disconeect()

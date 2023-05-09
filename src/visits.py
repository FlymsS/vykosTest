from datetime import datetime

from dbConection import DbConection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, text


Base = declarative_base()


class Visits(Base):
    __tablename__ = "visitas"

    email = Column(String(255), primary_key=True)
    fechaPrimeraVisita = Column(Date(), default=datetime.now())
    fechaUltimaVisita = Column(Date(), default=datetime.now())
    visitasTotales = Column(Integer(), default=1)
    visitasAnioActual = Column(Integer(), default=1)
    visitasMesActual = Column(Integer(), default=1)
    db = None

    def __init__(
        self,
        email: str,
        fechaPrimeraVisita: str,
        visitasTotales: int = 1,
        visitasAnioActual: int = 1,
        visitasMesActual: int = 1,
        fechaUltimaVisita: str = None,
    ):
        self.email = email
        self.fechaPrimeraVisita = fechaPrimeraVisita
        self.fechaUltimaVisita = fechaUltimaVisita if fechaUltimaVisita else fechaPrimeraVisita
        self.visitasTotales = visitasTotales
        self.visitasAnioActual = visitasAnioActual
        self.visitasMesActual = visitasMesActual

        self.changeFormatLastVisit()

        self.db = DbConection()

    def changeFormatLastVisit(self):
        aux = datetime.strptime(self.fechaUltimaVisita, '%d/%m/%Y %H:%M')
        self.fechaUltimaVisita = aux.strftime('%Y/%m/%d')

    def saveRecord(self):
        unicEmail = self.verifyUnicRecord()
        if unicEmail:
            self.db.saveRecord(self, "visitas")

    def verifyUnicRecord(self):
        connection  = self.db.getConection()
        query = text(f"SELECT * FROM visitas WHERE email = '{self.email}'")
        res = connection.execute(query)
        rows = res.fetchone()
        if not rows:
            return True
        self.updateRecord(rows)
        self.db.disconect()
        return False

    def updateRecord(self, row:tuple):
        self.verifyInfo(row)        
        session = self.db.getSession()
        registro = session.query(Visits).filter_by(email=self.email).first()
        registro.fechaUltimaVisita = self.fechaUltimaVisita
        registro.visitasTotales = self.visitasTotales
        registro.visitasAnioActual = self.visitasAnioActual
        registro.visitasMesActual = self.visitasMesActual

        session.commit()

    def verifyInfo(self, row):
        auxDate = self.fechaUltimaVisita
        self.fechaUltimaVisita = row[2]
        self.visitasTotales = row[3] + 1
        isThisYear = self.verifyVisitsActualYear(row[4])
        if isThisYear:
            self.verifyVisitsActualMonth(row[5])
        else:
            self.visitasAnioActual = 1
            self.visitasMesActual = 1
        self.verifyLastvisit(auxDate)

    def verifyLastvisit(self, auxDate):
        if(self.fechaPrimeraVisita > self.fechaUltimaVisita):
            self.fechaPrimeraVisita = self.fechaUltimaVisita
            self.fechaUltimaVisita = auxDate

    def verifyVisitsActualYear(self, visitsThisYear:int):
        registeredYear = datetime.strptime(self.fechaUltimaVisita, '%Y/%m/%d').year
        currentYear = datetime.strptime(self.fechaPrimeraVisita, '%d/%m/%Y %H:%M').year
        if registeredYear == currentYear:
            self.visitasAnioActual = visitsThisYear +1
            return True
        return False

    def verifyVisitsActualMonth(self, visitsThisMonth:int):
        registeredMonth = datetime.strptime(self.fechaUltimaVisita, '%Y/%m/%d').month
        currentMonth = datetime.strptime(self.fechaPrimeraVisita, '%d/%m/%Y %H:%M').month
        if registeredMonth == currentMonth:
            self.visitasMesActual = visitsThisMonth +1
        else:
            self.visitasMesActual = 1

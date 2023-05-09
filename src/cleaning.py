import os
import calendar
import pandas as pd
from datetime import datetime
from error import Error
from visits import Visits
from statisticsClass import Statistics

path = "./uncleanedFiles/"
pathLog: str = "./logs/"
regexEmail = r'^[\w\.-]+@[\w\.-]+\.[\w]{2,}$'


class Cleaning:

    emailFilteredDF: pd.DataFrame
    invalidEmailDF: pd.DataFrame
    invalidDateDF1: pd.DataFrame
    invalidDateDF2: pd.DataFrame
    dateFilteredDF: pd.DataFrame
    originalDF: pd.DataFrame

    invalidEmail: int
    invalidDate: int
    invalidDate2: int
    dateFiltered: int
    invalidTotal: int
    validTotal: int

    messageToLog: str

    file: str

    def __init__(self, file: str):
        self.file = "./uncleanedFiles/"+file
        self.emailFilteredDF = pd.DataFrame
        self.invalidEmailDF = pd.DataFrame
        self.invalidDateDF1 = pd.DataFrame
        self.invalidDateDF2 = pd.DataFrame
        self.dateFilteredDF = pd.DataFrame
        self.originalDF = pd.DataFrame
        self.readFile()

    def readFile(self):
        self.originalDF = pd.read_csv(self.file, delimiter=",")
        self.originalDF = self.originalDF.fillna(value="null")
        self.originalDF = self.originalDF.replace(to_replace="-", value="null")

    def cleanFile(self):
        self.cleanEmail()
        self.verifyDateFechaAbierto()
        self.verifyDateFechaSend()
        
        self.invalidTotal = self.invalidEmail + self.invalidDate + self.invalidDate2
        
        self.validTotal = self.dateFilteredDF.shape[0]

    def verifyDateFechaAbierto(self):
        dfAux = self.emailFilteredDF.copy()
        dfAux["fecha_valida"] = pd.to_datetime(
            self.emailFilteredDF["Fecha envio"], format='%d/%m/%Y %H:%M', errors='coerce')
        self.dateFilteredDF = self.emailFilteredDF[dfAux['fecha_valida'].notna()]
        self.invalidDateDF1 = self.emailFilteredDF[dfAux['fecha_valida'].isna()]
        self.invalidDate = self.invalidDateDF1.shape[0]

    def verifyDateFechaSend(self):
        dfAux = self.dateFilteredDF.copy()
        dfAux2 = self.dateFilteredDF.copy()
        dfAux["fecha_valida"] = pd.to_datetime(
            self.dateFilteredDF["Fecha open"], format='%d/%m/%Y %H:%M', errors='coerce')
        self.dateFilteredDF = dfAux2[dfAux['fecha_valida'].notna()]
        self.invalidDateDF2 = dfAux2[dfAux['fecha_valida'].isna()]
        self.invalidDate2 = self.invalidDateDF2.shape[0]

    def verifyDate(self, dfInvalid: int):
        dfAux = self.dateFilteredDF.copy()
        dfAux["fecha_valida"] = pd.to_datetime(
            self.dateFilteredDF["Fecha open"], format='%d/%m/%Y %H:%M', errors='coerce')
        self.dateFilteredDF = self.dateFilteredDF[dfAux['fecha_valida'].notna()]
        self.invalidDateDF2 = self.dateFilteredDF[dfAux['fecha_valida'].isna()]
        return self.invalidDateDF2.shape[0]

    def cleanEmail(self):
        condition = self.originalDF['email'].str.contains(regexEmail, na=False)
        self.invalidEmailDF = self.originalDF[~condition]
        self.emailFilteredDF = self.originalDF[condition]
        self.invalidEmail = self.invalidEmailDF.shape[0]

    def registryResultsInLog(self, pathLog: str, log: str):
        self.verifyIfLogExists(pathLog, log)
        self.generateTextToLog()
        aux = self.file.split("/")
        with open(pathLog+log, "a") as log:
            log.write(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - {aux[-1]}{self.messageToLog}\n")

    def verifyIfLogExists(self, pathLog, log):
        if not os.path.exists(pathLog+log):
            self.createLog(pathLog+log)

    def generateTextToLog(self):
        self.messageToLog = f"\n\t Registros totales: {self.invalidTotal+self.validTotal}\
            \n\t Registros invalidos por email: {self.invalidEmail} \
            \n\t Registros invalidos por fecha de envio: {self.invalidDate} \
            \n\t Registros invalidos por fecha de apertura: {self.invalidDate2} \
            \n\t Total de registros invalidos: {self.invalidTotal} \
            \n\t Total de registros validos: {self.validTotal}"

    def createLog(self, pathLog):
        header = self.getHeaderToLog()
        with open(pathLog, "w") as log:
            log.write(f"{header}\n")

    def getHeaderToLog(self):
        month = datetime.now().month
        monthStr = calendar.month_name[month]
        year = datetime.now().year
        return f"Bitacora de {monthStr} {year} - Creada {datetime.now().strftime('%Y-%m-%d %H:%M')} - "

    def saveInDB(self):
        self.saveVisitsInDB()
        self.saveStatisticsInDB()
        self.saveErrorsInDB(self.invalidEmailDF)
        if self.invalidDateDF1.shape[0] > 0:
            self.saveErrorsInDB(self.invalidDateDF1)
        if self.invalidDateDF2.shape[0] > 0:
            self.saveErrorsInDB(self.invalidDateDF2)

    def saveStatisticsInDB(self):
        jyv = self.checkJyv(self.dateFilteredDF)
        for index, row in self.dateFilteredDF.iterrows():
            statistics = Statistics(
                row["email"],
                row[jyv],
                row["Badmail"],
                row["Baja"],
                row["Fecha envio"],
                row["Fecha open"],
                row["Opens"],
                row["Opens virales"],
                row["Fecha click"],
                row["Clicks"],
                row["Clicks virales"],
                row["Links"],
                row["IPs"],
                row["Navegadores"],
                row["Plataformas"])
            statistics.saveRecord()

    def saveErrorsInDB(self, df: pd.DataFrame):
        jyv = self.checkJyv(df)
        for index, row in df.iterrows():
            error = Error(
                row["email"],
                row[jyv],
                row["Badmail"],
                row["Baja"],
                row["Fecha envio"],
                row["Fecha open"],
                row["Opens"],
                row["Opens virales"],
                row["Fecha click"],
                row["Clicks"],
                row["Clicks virales"],
                row["Links"],
                row["IPs"],
                row["Navegadores"],
                row["Plataformas"])
            error.saveRecord()

    def checkJyv(self, df: pd.DataFrame):
        if 'jyv' in df.columns:
            return 'jyv'
        if 'jk' in df.columns:
            return "jk"
        if 'fgh' in df.columns:
            return "fgh"
        return

    def saveVisitsInDB(self):
        for index, row in self.dateFilteredDF.iterrows():
            visit = Visits(row["email"], row["Fecha envio"])
            visit.saveRecord()

    def registryErrorInLog(self):
        aux = self.file.split("/")
        with open(pathLog+"log.txt", "a") as log:
            log.write(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - {aux[-1]} - No se pudo guardar en la base de datos, revisar el archivo \n")

def fileSelection():
    for file in os.listdir(path):
        fileInCleaning = Cleaning(file)
        fileInCleaning.cleanFile()
        try:
            fileInCleaning.saveInDB()
            fileInCleaning.registryResultsInLog(pathLog, "log.txt")
        except:
            fileInCleaning.registryErrorInLog()
            continue



if __name__ == "__main__":
    fileSelection()

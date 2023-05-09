from datetime import datetime

from dbConection import DbConection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Text, Boolean, Float

Base = declarative_base()

class Error(Base):
    __tablename__ = "errores"

    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    Navegadores = Column(String(255))
    Plataformas = Column(String(255))
    jyv = Column(Integer())
    Badmail = Column(String(16))
    Baja = Column(Boolean())
    Opens = Column(Integer())
    Opens_virales = Column(Integer())
    Clicks = Column(Integer())
    Clicks_virales = Column(Integer())
    Links = Column(Integer())
    IPs = Column(Text())
    Fecha_open = Column(String(16))
    Fecha_envio = Column(String(16))
    Fecha_click = Column(String(16))

    def __init__(
        self,
        email: str,
        jyv: int,
        Badmail: int,
        Baja: int,
        Fecha_envio: str,
        Fecha_open: str,
        Opens: int,
        Opens_virales: int,
        Fecha_click: str,
        Clicks: int,
        Clicks_virales: int,
        Links: int,
        IPs: str,
        Navegadores: str,
        Plataformas: str,
    ):
        self.email = email if not email == "null" else None
        self.Navegadores = Navegadores if not Navegadores == "null" else None
        self.Plataformas = Plataformas if not Plataformas == "null" else None
        self.jyv = jyv if not jyv == "null" else None
        self.Badmail = Badmail if not Badmail == "null" else None
        self.Baja = False if not Baja == "null" else True if Baja == "SI" else False
        self.Opens = Opens if not Opens == "null" else None
        self.Opens_virales = Opens_virales  if not Opens_virales == "null" else None
        self.Clicks = Clicks if not Clicks == "null" else None
        self.Clicks_virales = Clicks_virales if not Clicks_virales == "null" else None
        self.Links = round(float(Links.replace(",","."))) if not Links == "null" else None
        self.IPs = IPs if not IPs == "null" else None
        self.Fecha_open = Fecha_open if not Fecha_open == "null" else None
        self.Fecha_envio = Fecha_envio if not Fecha_envio == "null" else None
        self.Fecha_click = Fecha_click if not Fecha_click == "null" else None

    def saveRecord(self):
        db = DbConection()
        db.saveRecord(self, "errores")
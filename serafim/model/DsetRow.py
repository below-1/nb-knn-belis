import enum
from datetime import date
from datetime import datetime
from datetime import timedelta

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import String

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from serafim.model.base import Base
from serafim.model.ThreeLevelEnum import ThreeLevelEnum
from serafim.model.rules import prediksi

TLE_LOW = ThreeLevelEnum.RENDAH
TLE_MID = ThreeLevelEnum.SEDANG
TLE_HI = ThreeLevelEnum.TINGGI

class TingkatPendidikan(enum.Enum):
    TIDAK_SEKOLAH = 'TIDAK_SEKOLAH'
    SD = 'SD'
    SMP = 'SMP'
    SMA = 'SMA'
    D3 = 'D3'
    S1 = 'S1'
    S2 = 'S2'
    S3 = 'S3'

class StatusAdat(enum.Enum):
    HAMBA = 'HAMBA'
    BIASA = 'BIASA'
    MARAMBA = 'MARAMBA'
    BANGSAWAN = 'BANGSAWAN'

class Pekerjaan(enum.Enum):
    PETANI = 'PETANI'
    TENUN_IKAT = 'TENUN_IKAT'
    HONORER_PTT = 'HONORER_PTT'
    PNS = 'PNS'

class TingkatEkonomi(enum.Enum):
    RENDAH = 'RENDAH'
    SEDANG = 'SEDANG'
    TINGGI = 'TINGGI'

class DsetRow(Base):
    __tablename__ = 'dset_row'
    id = Column(Integer, primary_key=True)
    nama = Column(String(250), nullable=False)
    tanggal_lahir = Column(Date, nullable=False)
    status_adat = Column(Enum(StatusAdat), nullable=False)
    tingkat_pendidikan = Column(Enum(TingkatPendidikan), nullable=False)
    tingkat_ekonomi = Column(Enum(TingkatEkonomi), nullable=False)
    pekerjaan = Column(Enum(Pekerjaan), nullable=False)
    hub_kel = Column(Boolean, nullable=False)

    mamuli_kaki = Column(SmallInteger, nullable=False)
    mamuli_polos = Column(SmallInteger, nullable=False)
    kuda = Column(SmallInteger, nullable=False)
    kerbau = Column(SmallInteger, nullable=False)
    sapi = Column(SmallInteger, nullable=False)
    uang = Column(BigInteger, nullable=False)

    kecamatan = Column(String(250), nullable=True)
    location_latitude = Column(String(250), nullable=True)
    location_longitude = Column(String(250), nullable=True)
    
    facebook_target_id = Column(String(250), nullable=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="records")

    is_kasus = Column(Boolean, nullable=False)
    is_record = Column(Boolean, nullable=False)

    similarity = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    @hybrid_property
    def tanggal_html_string(self):
        return self.tanggal_lahir.strftime('%Y-%m-%d')

    @hybrid_property
    def usia(self):
        tgl_lahir = self.tanggal_lahir
        if type(tgl_lahir) is datetime:
            tgl_lahir = tgl_lahir.date()
        result = (date.today() - tgl_lahir) // timedelta(days=365.2425)
        return result

    @hybrid_property
    def mamulu_kaki_code(self):
        if self.mamuli_kaki <= 0: return ThreeLevelEnum.RENDAH
        if 1 <= self.mamuli_kaki <= 2: return ThreeLevelEnum.SEDANG
        if self.mamuli_kaki > 3: return ThreeLevelEnum.TINGGI

    @hybrid_property
    def mamulu_polos_code(self):
        if self.mamuli_polos < 20: return ThreeLevelEnum.RENDAH
        if 20 <= self.mamuli_polos <= 40: return ThreeLevelEnum.SEDANG
        if self.mamuli_polos > 40: return ThreeLevelEnum.TINGGI

    @hybrid_property
    def kuda_code(self):
        if self.kuda < 15: return ThreeLevelEnum.RENDAH
        if 15 <= self.kuda <= 30: return ThreeLevelEnum.SEDANG
        if self.kuda > 30: return ThreeLevelEnum.TINGGI

    @hybrid_property
    def kerbau_code(self):
        val = self.kerbau
        if val < 5: return ThreeLevelEnum.RENDAH
        if 5 <= val <= 10: return ThreeLevelEnum.SEDANG
        if val > 10: return ThreeLevelEnum.TINGGI

    @hybrid_property
    def sapi_code(self):
        val = self.sapi
        if val < 5: return ThreeLevelEnum.RENDAH
        if 5 <= val <= 10: return ThreeLevelEnum.SEDANG
        if val > 10: return ThreeLevelEnum.TINGGI

    @hybrid_property
    def uang_code(self):
        val = self.uang
        if val < 5_000_000: return ThreeLevelEnum.RENDAH
        if 5_000_000 <= val <= 10_000_000: return ThreeLevelEnum.SEDANG
        if val > 10_000_000: return ThreeLevelEnum.TINGGI

    @hybrid_property
    def prediksi_code(self):
        row = ( self.mamulu_kaki_code, self.mamulu_polos_code, self.kuda_code, self.kerbau_code, self.sapi_code, self.uang_code )
        # row_raw = ( self.mamuli_kaki,
        #             self.mamuli_polos,
        #             self.kuda,
        #             self.kerbau,
        #             self.sapi,
        #             self.uang )
        # print('Row=', row)
        # print('Raw=', row_raw)
        # print()
        return prediksi(row)

    @hybrid_property
    def pekerjaan_str(self):
        return ' '.join(s.capitalize() for s in self.pekerjaan.name.split('_'))

    def __repr__(self):
        return f"(id={self.id}, " \
            f"pendidikan={self.tingkat_pendidikan}," \
            f"usia={self.usia}," \
            f"hub_keluarga={self.hub_kel}," \
            f"tingkat_ekonomi={self.tingkat_ekonomi}," \
            f"status_adat={self.status_adat}," \
            f"pekerjaan={self.pekerjaan}," \
            f"mamulu_kaki={self.mamuli_kaki}, " \
            f"mamulu_polos={self.mamuli_polos})"

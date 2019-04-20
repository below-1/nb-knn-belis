import csv
import os
from collections import namedtuple
from serafim.model import DsetRow
from serafim.model import TingkatEkonomi
from serafim.model import TingkatPendidikan
from serafim.model import StatusAdat
from serafim.model import Pekerjaan
from datetime import date

# Named Tuple. Because string is dangerous.
CsvRow = namedtuple('CsvRow', [
    'nama',
    'usia',
    'pendidikan',
    'pekerjaan',
    'tingkat_eko',
    'hubkel',
    'keturunan',
    'kecamatan',
    'lokasi',
    'mamuli_kaki',
    'mamuli_polos',
    'kuda',
    'kerbau',
    'sapi',
    'uang'
])

def seed(**kwargs):
    # Make sure we got everything we need.
    print(os.getcwd())
    if 'session' not in kwargs:
        raise Exception("Need session")
    if 'filename' not in kwargs:
        raise Exception("Need filename to open")
    if 'user_id' not in kwargs:
        raise Exception("Need user_id")

    session = kwargs['session']
    filename = kwargs['filename']
    user_id = kwargs['user_id']

    # Construct list of DsetRow
    data = list(_load_data(filename))

    # Set user_id on each row
    _add_user_id(data, user_id)

    # Bulk saving it
    session.bulk_save_objects(data)

    session.commit()

def _add_user_id(dataset, user_id):
    for row in dataset:
        row.user_id = user_id

def _load_data(filename):
    with open(filename) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        data = [ line for line in reader ]
        just_body = data[1:]
        as_raw_csv = ( CsvRow(*row) for row in just_body )
        as_dset = ( _CsvRow_to_DsetRow(row) for row in as_raw_csv )
        return as_dset

def _CsvRow_to_DsetRow(csv_row: CsvRow):
    dset_row = DsetRow()
    dset_row.nama = csv_row.nama

    # Every  attributes of csv_row is string.
    # Convert to int when necessary
    dset_row.tanggal_lahir = tanggal_from_usia(int(csv_row.usia))
    dset_row.tingkat_pendidikan = pendidikan_from_int(int(csv_row.pendidikan))
    dset_row.pekerjaan = pekerjaan_from_int(int(csv_row.pekerjaan))
    dset_row.tingkat_ekonomi = tingkat_eko_from_int(int(csv_row.tingkat_eko))
    dset_row.status_adat = status_adat_from_int(int(csv_row.keturunan))
    dset_row.hub_kel = csv_row.hubkel == '1'
    dset_row.is_kasus = True
    dset_row.is_record = True

    dset_row.kecamatan = csv_row.kecamatan

    # Parse location
    lokasi = csv_row.lokasi
    try:
        # All the location attributes are optional
        long, lat = list(map(lambda s: s.strip(),  lokasi.split(',')))
        dset_row.location_longitude = long
        dset_row.location_latitude = lat
    except:
        pass

    dset_row.mamuli_kaki = int(csv_row.mamuli_kaki)
    dset_row.mamuli_polos = int(csv_row.mamuli_polos)
    dset_row.kuda = int(csv_row.kuda)
    dset_row.kerbau = int(csv_row.kerbau)
    dset_row.sapi = int(csv_row.sapi)
    dset_row.uang = int(csv_row.uang) * 1_000_000
    return dset_row

def tanggal_from_usia(usia):
    if usia == 1: return date(2004, 1, 1)
    elif usia == 2: return date(2000, 1, 1)
    elif usia == 3: return date(1995, 1, 1)
    elif usia == 4: return date(1989, 1, 1)
    else: return date(1980, 1, 1)

def pendidikan_from_int(p):
    if p == 1: return TingkatPendidikan.TIDAK_SEKOLAH
    elif p == 2: return TingkatPendidikan.SD
    elif p == 3: return TingkatPendidikan.SMP
    elif p == 4: return TingkatPendidikan.SMA
    elif p == 5: return TingkatPendidikan.D3
    elif p == 6: return TingkatPendidikan.S1
    elif p == 7: return TingkatPendidikan.S2
    elif p == 8: return TingkatPendidikan.S3
    else:
        raise Exception(f"Unknown pendidikan: {p}")

def pekerjaan_from_int(p):
    if p == 1: return Pekerjaan.PETANI
    elif p == 2: return Pekerjaan.TENUN_IKAT
    elif p == 3: return Pekerjaan.HONORER_PTT
    elif p == 4: return Pekerjaan.PNS
    else:
        raise Exception(f"Unknown pekerjaan: {p}")

def tingkat_eko_from_int(t):
    if t == 1: return TingkatEkonomi.RENDAH
    elif t == 2: return TingkatEkonomi.SEDANG
    elif t == 3: return TingkatEkonomi.TINGGI
    else:
        raise Exception(f"Unknown pekerjaan: {t}")

def status_adat_from_int(s):
    if s == 1: return StatusAdat.HAMBA
    elif s == 2: return StatusAdat.BIASA
    elif s == 3: return StatusAdat.MARAMBA
    elif s == 4: return StatusAdat.BANGSAWAN
    else:
        raise Exception(f"Unknown status: {s}")


from serafim.model.DsetRow import DsetRow
from serafim.model.DsetRow import TingkatPendidikan
from serafim.model.DsetRow import TingkatEkonomi
from serafim.model.DsetRow import Pekerjaan
from serafim.model.DsetRow import StatusAdat
from serafim.model.DsetRow import ThreeLevelEnum
import datetime

def datetime_from_html_input(s: str):
    return datetime.datetime.strptime(s, "%Y-%m-%d")

def dset_from_dict(dset_row: DsetRow, data: dict, is_kasus=True, is_record=False):
    dset_row.nama = data['nama']

    # Parse the string to Python datetime object
    dset_row.tanggal_lahir = datetime_from_html_input(data['tanggal_lahir'])

    dset_row.status_adat = StatusAdat[data['status_adat']]
    dset_row.tingkat_pendidikan = TingkatPendidikan[data['tingkat_pendidikan']]
    dset_row.tingkat_ekonomi = TingkatEkonomi[data['tingkat_ekonomi']]
    dset_row.pekerjaan = Pekerjaan[data['pekerjaan']]

    dset_row.hub_kel = data['hub_kel'] == '1'

    # Here is the Integer inputs
    # Each field is optional. so we need guards.
    if 'mamuli_kaki' in data:
        dset_row.mamuli_kaki = int(data['mamuli_kaki'])
    if 'mamuli_polos' in data:
        dset_row.mamuli_polos = int(data['mamuli_polos'])
    if 'kuda' in data:
        dset_row.kuda = int(data['kuda'])
    if 'kerbau' in data:
        dset_row.kerbau = int(data['kerbau'])
    if 'sapi' in data:
        dset_row.sapi = int(data['sapi'])
    if 'uang' in data:
        dset_row.uang = int(data['uang'])

    dset_row.is_kasus = is_kasus
    dset_row.is_record = is_record
    return dset_row

def prediksi_code_to_int(prediksi_code):
    prediksi = prediksi_code
    if prediksi == ThreeLevelEnum.RENDAH: prediksi = 0
    if prediksi == ThreeLevelEnum.SEDANG: prediksi = 1
    if prediksi == ThreeLevelEnum.TINGGI: prediksi = 2
    else:
        prediksi = None

def dset_to_vector(dset_row: DsetRow):
    '''
    Convert the given dset_row to vector reprentation.
    :param dset_row:
    :return:
    '''
    usia = dset_row.usia
    pend = dset_row.tingkat_pendidikan
    pekerjaan = dset_row.pekerjaan
    tingkat_ekonomi = dset_row.tingkat_ekonomi
    hub_keluarga = 1 if dset_row.hub_kel else 0
    status = dset_row.status_adat

    if usia < 17: usia = 1
    elif 17 <= usia <= 22: usia = 2
    elif 23 <= usia <= 28: usia = 3
    elif 29 <= usia <= 34: usia = 4

    if pend == TingkatPendidikan.TIDAK_SEKOLAH: pend = 0
    elif pend == TingkatPendidikan.SD: pend = 1
    elif pend == TingkatPendidikan.SMP: pend = 2
    elif pend == TingkatPendidikan.SMA: pend = 3
    elif pend == TingkatPendidikan.D3: pend = 4
    elif pend == TingkatPendidikan.S1: pend = 5
    elif pend == TingkatPendidikan.S2: pend = 6
    elif pend == TingkatPendidikan.S3: pend = 7
    else:
        raise Exception(f"Unknown pendidikan: {pend} in dset --> {dset_row}")

    if pekerjaan == Pekerjaan.TENUN_IKAT: pekerjaan = 0
    elif pekerjaan == Pekerjaan.HONORER_PTT: pekerjaan = 1
    elif pekerjaan == Pekerjaan.PETANI: pekerjaan = 2
    elif pekerjaan == Pekerjaan.PNS: pekerjaan = 3
    else:
        raise Exception(f"Unknown pekerjaan: {pekerjaan}")

    if tingkat_ekonomi == TingkatEkonomi.RENDAH: tingkat_ekonomi = 0
    elif tingkat_ekonomi == TingkatEkonomi.SEDANG: tingkat_ekonomi = 1
    elif tingkat_ekonomi == TingkatEkonomi.TINGGI: tingkat_ekonomi = 2
    else:
        raise Exception(f"Unknown tingkat ekonomi: {tingkat_ekonomi}")

    if status == StatusAdat.HAMBA: status = 0
    elif status == StatusAdat.BIASA: status = 1
    elif status == StatusAdat.MARAMBA: status = 2
    elif status == StatusAdat.BANGSAWAN: status = 3
    else:
        raise Exception(f"Unknown status: {status}")

    prediksi = None
    try:
        pcode = dset_row.prediksi_code
        if pcode == ThreeLevelEnum.RENDAH: prediksi = 0
        if pcode == ThreeLevelEnum.SEDANG: prediksi = 1
        if pcode == ThreeLevelEnum.TINGGI: prediksi = 2
    except:
        pass
    # It's an optional we dont need exception whatsoever

    return [
        [usia, pend, pekerjaan, tingkat_ekonomi, hub_keluarga, status],
        prediksi,
        dset_row.id
    ]
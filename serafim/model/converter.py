from serafim.model.DsetRow import DsetRow
import datetime

def datetime_from_html_input(s: str):
    return datetime.datetime.strptime(s, "%Y-%m-%d")

def kasus_from_dict(data: dict):
    dset_row = DsetRow()
    dset_row.nama = data['nama']

    # Parse the string to Python datetime object
    dset_row.tanggal_lahir = datetime_from_html_input(data['tanggal_lahir'])

    dset_row.status_adat = data['status_adat']
    dset_row.tingkat_pendidikan = data['tingkat_pendidikan']
    dset_row.tingkat_ekonomi = data['tingkat_ekonomi']
    dset_row.pekerjaan = data['pekerjaan']

    dset_row.hub_kel = data['hub_kel'] == '1'

    # Here is the Integer inputs
    dset_row.mamuli_kaki = int(data['mamuli_kaki'])
    dset_row.mamuli_polos = int(data['mamuli_polos'])
    dset_row.kuda = int(data['kuda'])
    dset_row.kerbau = int(data['kerbau'])
    dset_row.sapi = int(data['sapi'])
    dset_row.uang = int(data['uang'])

    dset_row.is_kasus = False
    dset_row.is_record = True
    return dset_row
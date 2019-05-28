var vueApp = new Vue({
    el: '#vue-app',
    data: {
        user: {
        },
        isResult: false,
        result: {
            status: 'idle',
            mamuli_kaki: 0,
            mamuli_polos: 0,
            kuda: 0,
            kerbau: 0,
            sapi: 0,
            uang: 0,
            jumlah_belis: undefined
        },
        item: {
            user_id: undefined,
            nama: 'Sera',
            tanggal_lahir: '1997-05-12',
            tingkat_pendidikan: 'S1',
            pekerjaan: 'PNS',
            tingkat_ekonomi: 'TINGGI',
            status_adat: 'BIASA',
            hub_kel: '1'
        },
        options: {
            pendidikan: [
                { value: 'TIDAK_SEKOLAH', text: 'Tidak Sekolah' },
                { value: 'SD', text: 'SD' },
                { value: 'SMP', text: 'SMP' },
                { value: 'SMA', text: 'SMA' },
                { value: 'D3', text: 'D3' },
                { value: 'S1', text: 'S1' },
                { value: 'S2', text: 'S2' },
                { value: 'S3', text: 'S3' }
            ],
            pekerjaan: [
                { value: 'PETANI', text: 'Petani' },
                { value: 'TENUN_IKAT', text: 'Tenun Ikat' },
                { value: 'HONORER_PTT', text: 'Honorer Ptt' },
                { value: 'PNS', text: 'PNS' }
            ],
            status_adat: [
                { value: 'HAMBA', text: 'Hamba' },
                { value: 'BIASA', text: 'Biasa' },
                { value: 'MARAMBA', text: 'Maramba' }
            ],
            ekonomi: [
                { value: 'RENDAH', text: 'Rendah' },
                { value: 'SEDANG', text: 'Sedang' },
                { value: 'TINGGI', text: 'Tinggi' }
            ]
        }
    },
    methods: {
        formInvalid () {
            var item = this.item
            if (item.nama == undefined || item.nama == '') {
                return 'Nama invalid'
            }
            if (item.tanggal_lahir == undefined) return 'Tanggal Lahir invalid'
            if (item.tingkat_pendidikan == undefined) return 'Tingkat pendidikan invalid'
        },
        submit () {
            var invalid = this.formInvalid()
            if (invalid) {
                alert(invalid);
                return;
            }
            var payload = this.item;;
            return axios.post('/prediksi', payload)
                .then(predResult => predResult.data)
                .then(result => {
                    if (result.status == 'invalid') {
                        alert('Data yang dimasukan dibawah threshold!');
                    }
                    this.isResult = true;
                    this.result = result;
                })
                .catch(err => {
                    console.log('Fail to run prediksi');
                    console.log(err);
                });
        },
        repeat () {
            this.isResult = false;
        }
    }
});

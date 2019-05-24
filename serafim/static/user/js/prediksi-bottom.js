var vueApp = new Vue({
    el: '#vue-app',
    data: {
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
                { value: 'MARAMBA', text: 'Maramba' },
                { value: 'BANGSAWAN', text: 'Bangsawan' }
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
        fbGetLoginStatus () {
            return new Promise((resolve, reject) => {
                FB.getLoginStatus((response) => {
                    if (response.status == 'not_authorized') {
                        return reject(response);
                    } else if (response.status == 'connected'){
                        return resolve(response);
                    }
                })
            });
        },
        fbLogin () {
            return new Promise((resolve, reject) => {
                FB.login(function (loginResponse) {
                    return resolve(loginResponse);
                });
            });
        },
        fbLogout () {
            FB.getLoginStatus(function(response) {
                if (response && response.status === 'connected') {
                    FB.logout(function(response) {
                        console.log(response);
                        document.location.reload();
                    });
                }
            });
        },
        submit () {
            var invalid = this.formInvalid()
            if (invalid) {
                alert(invalid);
                return;
            }
            this.fbGetLoginStatus()
                .catch(err => {
                    console.log("You're not authenticated");
                    return this.fbLogin();
                })
                .then(response => response.authResponse.userID)
                .then(fb_id => axios.get('/addUserIfNeeded/' + fb_id).then(resp => resp.data))
                .catch(err => {
                    console.log(`Fail to add user data in database`);
                    throw err;
                })
                .then(userID => {
                    var payload = this.item;
                    payload.user_id = userID;
                    return axios.post('/prediksi', payload);
                })
                .then(predResult => predResult.data)
                .then(result => {
                    this.result = result;
                })
                .catch(err => {
                    console.log('Fail to run prediksi');
                    console.log(err);
                });
        }
    }
});

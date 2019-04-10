$(document).ready(function () {
    var VUE_APP = new Vue({
       el: '#vue_app',
       data: {
            column_filter: {
                detail_belis: D_BELIS,
                detail_profile: D_PROFILE
            }
       },
       methods: {
            toggle_profile () {
                var val = !this.column_filter.detail_profile;
                var qs = [
                  val ? 'show_detail_profile' : '',
                  this.column_filter.detail_belis ? 'show_detail_belis' : ''
                ].join('&');
                window.location =  `/admin/dataset?${qs}`;
            },
            toggle_belis () {
                var val = !this.column_filter.detail_belis;
                var qs = [
                  this.column_filter.detail_profile ? 'show_detail_profile' : '',
                  val ? 'show_detail_belis' : ''
                ].join('&');
                window.location =  `/admin/dataset?${qs}`;
            }
       }
    });
});
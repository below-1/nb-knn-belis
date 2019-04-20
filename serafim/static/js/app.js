function saveUserToLocalStorage (user) {
    window.localStorage.setItem('sibelis.user', JSON.stringify(user));
}

function loadUserFromLocalStorage () {
    var rawString = localStorage.getItem('sibelis.user');
    var user = JSON.parse(rawString);
    return user;
}

function sendFBRespToServer (fbResp) {
    return axios('/api/fb_login', fbResp);
}

// This is called with the results from from FB.getLoginStatus().
function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.

      // Now, pass the facebook response to server
      var userProm = sendFBRespToServer(response);
      userProm.then(saveUserToLocalStorage).catch(err => {
        console.log('Fail to validated user in server');
        console.log(err);
      })
    } else {
      // The person is not logged into your app or we are unable to tell.
      document.getElementById('status').innerHTML = 'Please log ' +
        'into this app.';
    }
}

function checkLoginStatus () {
    var user = undefined;
    try {
        var user = loadUserFromLocalStorage();
    } catch (err) {
        console.log(err);
    }
    return user;
}

function getDataPrediksi () {
    $('#prediksi-nama').val();
}

function prediksi () {
    var data = {};
}

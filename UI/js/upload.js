var fs = require('fs');

function foo(){
    var str = document.getElementById('studentregno').value;
    if(str.length>1){
        fs.writeFileSync('py/helper.txt', str);
        var python = require('child_process').spawn('python', ['py/capture.py']);
        python.stdout.on('data',function(data){
            console.log("data: ",data.toString('utf8')+ " from Python ");
        });
    }
    else{
        M.toast({html:'All field are mandatory!'});
    }
}
function Train(){
    var preloader = document.getElementById('preloader');
    if (preloader) preloader.style.visibility = "visible";
    var python = require('child_process').spawn('python', ['py/train.py']);
    python.stdout.on('data',function(data){
        if (preloader) preloader.style.visibility = 'hidden';
        document.getElementById('trainfield').style.backgroundColor='red';
    });
}
//manual file upload
var selectedFile;

var config = {
    apiKey: "AIzaSyAlkTeBTBPtnVAaOnNmwiwsFVDIWKhfp5M",
    authDomain: "hackathon-mozofest-2019.firebaseapp.com",
    databaseURL: "https://hackathon-mozofest-2019.firebaseio.com",
    storageBucket: 'gs://hackathon-mozofest-2019.appspot.com/'
};
firebase.initializeApp(config);
var database = firebase.database();

function logOut(){
    firebase.auth().signOut().then(function() {
        document.location.href = "facultyLogin.html";
    }).catch(function(error) {
        // Optionally handle error
    });
}

function uploadFile(){
    var filename = selectedFile.name;
    var storageRef = firebase.storage().ref('/' + 'models' + '/' + filename);
    var uploadTask = storageRef.put(selectedFile);

    uploadTask.on('state_changed', function(snapshot){
        var progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        document.getElementById("bar").style.width=progress+100;
    }, function(error) {
        // Optionally handle unsuccessful uploads
    }, function() {
        uploadTask.snapshot.ref.getDownloadURL().then(function(downloadURL) {
            document.getElementById("bar").style.width="100%";
        });
    });
};

function writeUserData() {
    var studregno = document.getElementById('studentregno').value;
    var studname = document.getElementById('studentname').value;
    if(studregno.length>2 && studname.length>2){
        firebase.database().ref('Students/' + studregno).set({
            RegNo: studregno,
            name: studname,
            hours_conducted: 0,
            hours_present:0,
            dayorder:{
                DO1:0,
                DO2:0,
                DO3:0,
            },
        });
        // --- Append to students.csv if not already present ---
        const studentsPath = require('path').join(__dirname, 'students.csv');
        const fs = require('fs');
        fs.readFile(studentsPath, 'utf8', (err, data) => {
            let alreadyExists = false;
            if (!err && data) {
                alreadyExists = data.split('\n').some(line => line.startsWith(studregno + ','));
            }
            if (!alreadyExists) {
                if (!err && data.trim().length === 0) {
                    fs.appendFileSync(studentsPath, 'RegNo,Name\n');
                }
                fs.appendFileSync(studentsPath, `${studregno},${studname}\n`);
            }
        });
    }
}

$("#file").on("change",function(event){
    selectedFile = event.target.files[0];
    uploadFile();
});


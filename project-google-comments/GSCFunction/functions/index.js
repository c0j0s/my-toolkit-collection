const admin = require('firebase-admin');
const functions = require('firebase-functions');

admin.initializeApp(functions.config().firebase);

var db = admin.firestore();

// var gsc = 'gsc'
var gsc = "gscTest"

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions
//
// exports.helloWorld = functions.https.onRequest((request, response) => {
//  response.send("Hello from Firebase!");
// });

exports.getComments = functions.https.onRequest((request, response) => {
    var host = request.host
    var docRef = db.collection(gsc+"/"+host+"/comments");
    var result = docRef.orderBy("votes").limit(5).get().then(querySnapshot => {
        let comments = [];
        querySnapshot.forEach((doc) => {
            comments.push(doc.data());
        });
        console.log(comments)
        return {h:host,c:comments};
    }).catch(error => {
        console.log("Error getting document:", error);
    });
    response.send(result);
});

exports.postComment = functions.https.onRequest((request, response) => {
    var host = request.data.host
    var comment = request.data.comment
    var user = request.data.user
    var result = "";

    if(host !== "" && comment !== ""){
        console.log(user)
        var commentObj = {
            'content':comment,
            'country':'sg',
            'created_on':new Date(),
            'user': {
                'displayName':user.displayName,
                'email':user.email,
                'photoURL':user.photoURL,
                'uid':user.uid
                },
            'votes':0
        }
        console.log(commentObj)
        result = db.collection(gsc).doc(host).collection("comments").add(commentObj)
        .then(() => {
            console.log("Document successfully written!");
            commentContainer[host].push(commentObj)
            return {status:true,data:commentObj}
        })
        .catch(error => {
            console.error("Error writing document: ", error);
            return {status:false,data:commentObj}
        });
    }

    response.send(result);
});

exports.makeVote = functions.https.onRequest((request, response) => {
    response.send("Hello from Firebase!");
});
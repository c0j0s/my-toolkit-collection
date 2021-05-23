// Copyright 2018 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

'use strict';

firebase.initializeApp({
  apiKey: "AIzaSyC9LDdguhpkx7R1Nwjm4lD0ENxdqG-HW_w",
  authDomain: "gscomments-2018.firebaseapp.com",
  databaseURL: "https://gscomments-2018.firebaseio.com",
  projectId: "gscomments-2018",
  storageBucket: "gscomments-2018.appspot.com",
  messagingSenderId: "780329099121"
});

var db = firebase.firestore();
// var gsc = 'gsc'
var gsc = "gscTest"

chrome.runtime.onInstalled.addListener(function (details) {
    if (details.reason == "install") {
        // this logic never gets executed
    } else if(details.reason == "update") {
        // perform some logic
    }
});

let commentContainer = {};
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.function === "getComments") {
        var host= request.data
        if(commentContainer[host] === undefined){
        var docRef = db.collection(gsc+"/"+host+"/comments");
        docRef.orderBy("votes").limit(5).get().then(function(querySnapshot) {
            let comments = [];
            querySnapshot.forEach(function(doc) {
                comments.push(doc.data());
            });

            //first load data all from database
            console.log("get from db" + request.data)
            console.log(comments)
            commentContainer[host] = comments
            sendResponse({h:host,c:comments})
        }).catch(function(error) {
            console.log("Error getting document:", error);
        });

        }else{
            //subsequent page load from cahce
            console.log("get from cache" + request.data)
            console.log(commentContainer[host])
            sendResponse({h:host,c:commentContainer[host]})
        }
    }else if(request.function === "postComment"){
        var host = request.data.host
        var comment = request.data.comment
        if(host !== "" && comment !== ""){
            console.log("Connecting port")
            getUdentification(true,function(user){
                if (user===undefined) {
                    sendResponse({status:'not_login'})
                }
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
                db.collection(gsc).doc(host).collection("comments").add(commentObj)
                .then(function() {
                    console.log("Document successfully written!");
                    commentContainer[host].push(commentObj)
                    sendResponse({status:true,data:commentObj})
                })
                .catch(function(error) {
                    console.error("Error writing document: ", error);
                    sendResponse({status:false,data:commentObj})
                });
            })
        }
    }else if(request.function === "isLogin"){
        chrome.identity.getAuthToken({interactive: !!false}, function(token) {
            console.log("getting auth callback " + token)
            if (token) {
              sendResponse({status:true})
            } else {
              console.error('The OAuth Token was null or error occur');
              sendResponse({status:false})
            }
        });
    }
    return true;
});

function getUdentification(interactive,callback){
    console.log("getting auth")
    chrome.identity.getAuthToken({interactive: !!interactive}, function(token) {
        console.log("getting auth callback " + token)
        if (chrome.runtime.lastError && !interactive) {
          console.log('It was not possible to get a token programmatically.');
        } else if(chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError);
        } else if (token) {
          // Authorize Firebase with the OAuth Access Token.
          var credential = firebase.auth.GoogleAuthProvider.credential(null, token);
          firebase.auth().signInAndRetrieveDataWithCredential(credential).then(function(result){
            var currentUser = result.user;
            console.log(currentUser)
            if (firebase.auth().currentUser) {
                console.log("get user")
                callback(currentUser)
            }else{
                
            }
          }).catch(function(error) {
            // The OAuth token might have been invalidated. Lets' remove it from cache.
            if (error.code === 'auth/invalid-credential') {
              console.log("Incalid token, please sign in again")
            }
          });
        } else {
          console.error('The OAuth Token was null');
        }
    });
}

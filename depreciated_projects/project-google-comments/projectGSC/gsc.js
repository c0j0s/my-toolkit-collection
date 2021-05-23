//global variables
var isLogin = false;

//initial functions
onload()

//function declaration
function onload(){
	var hostlist = []

	//Check with login
	chrome.runtime.sendMessage({function:"isLogin"}, function(response) {
		if (chrome.runtime.lastError) {
			console.log("ERROR: ", chrome.runtime.lastError);
		} else {
			//get host from all search results
			isLogin = response.status
			var searchContains = document.querySelectorAll( "div.g > div > div.rc");
			for (let index = 0; index < searchContains.length; index++) {
				const element = searchContains[index];
				var link = element.querySelectorAll( ".r > a")[0].host;
				//TODO handle url without prefix
				var host = link.replace(/\./g,'_')
				if (!hostlist.includes(host)) {
					hostlist.push(host)
				}

				appendCommentContainer(element,host,response.status)
			}
		}
	});
}

function appendCommentContainer(element,host,isLogin){
	var html = 
			'<div class="gsc-container" data-host="'+ host +'" data-status="hide">'+
				'<div class="gsc-toggle-button">'+
				'<img class="gsc-logo gsc-comment-item-userImg" src="'+chrome.extension.getURL("images/icon.png")+'"/>'+
				'GSComments <span class="gsc-toggle-button-down-arrow"></span></div>'+
				'<div class="gsc-container-detail">'+
					'<div class="gsc-container-comment"></div>'+
					'<div class="gsc-container-button">'+
					'</div>'+
				'</div>'+
			'</div>'

	var item = htmlToElements(html);
	item.addEventListener('mouseover',showCommentContainer)
	item.querySelector('.gsc-add-comment-btn')
	if(isLogin){
		var html="<button class='gsc-add-comment-btn' data-host='"+ host +"'>post my comment</button>";
		var postCommentBtn = htmlToElements(html)
		postCommentBtn.addEventListener('click',addComment)
		item.querySelector('.gsc-container-button').append(postCommentBtn)
	}
	element.append(item);
}

function loadAllComments(hostlist){
	hostlist.forEach(host => {
		chrome.runtime.sendMessage({function:"getComments",data:host}, function(response) {
			if (chrome.runtime.lastError) {
				console.log("ERROR: ", chrome.runtime.lastError);
			} else {
				console.log(response.h)
				var gscContainerId = createGscContainer(element,response.h)
				attachComments(element,gscContainerId, response.c)
				attachButtons(element,response.h)
			}
		});
	});
}

function toggleCommentContainer(e){
	console.log('toogle')
	var status = e.target.parentNode.getAttribute('data-status')
}
function showCommentContainer(e){
	
	var host = e.target.parentNode.getAttribute('data-host')
	var commentHolder = e.target.parentNode.querySelector('.gsc-container-comment')
	e.target.parentNode.removeEventListener('mouseover',showCommentContainer)

	console.log('show for' + host)

	chrome.runtime.sendMessage({function:"getComments",data:host}, function(response) {
		if (chrome.runtime.lastError) {
			console.log("ERROR: ", chrome.runtime.lastError);
		} else {
			var comments = response.c
			var gdiv = e.target.parentNode.parentNode.parentNode.parentNode
			if(comments.length > 0){
				console.log(response.c)
				calculateNewOutlineHeight(gdiv,comments.length)
				for (let index = 0; index < comments.length; index++) {
					const element = comments[index];
					attachCommentElement(commentHolder,element)
				}
			}else{
				//NO COMMENTS
			}
		}
	});
}

function attachCommentElement(commentHolder,commentObj){
	var upVoteBtn = "<span class='gsc-vote gsc-vote-up-btn'>^</span>";
	var downVoteBtn = "<span class='gsc-vote gsc-vote-down-btn'>v</span>";
	var figure = "<span class='gsc-vote-figure'>"+commentObj.votes+"</span>"
	var voteContainer = '<span class="gsc-comment-item-vote-container">'+ upVoteBtn + figure + downVoteBtn +'</span>'
	console.log(commentObj)
	// <span class="gsc-comment-item-userName">'+ commentObj.user.displayName +'</span>: 
	var item = htmlToElements('<div class="gsc-comment-item"><img class="gsc-comment-item-userImg" src="'+ commentObj.user.photoURL +'"/>'+voteContainer+'<span class="gsc-comment-item-content">'+commentObj.content+'</span></div>');
	if (isLogin) {
		item.querySelector('.gsc-vote-up-btn').addEventListener('click',upVote)
		item.querySelector('.gsc-vote-down-btn').addEventListener('click',downVote)
	}
	commentHolder.append(item)
}

function hideCommentContainer(e){
	console.log('hide')
	var commentHolder = e.target.parentNode.querySelector('.gsc-container-comment')
	commentHolder.innerHTML = '';

}

function calculateNewOutlineHeight(gdiv,mutiple){
	if(gdiv.querySelector('.exp-outline') !== null){
		var base = gdiv.querySelector('.exp-outline').style.height.replace('px','')
		var newHeight = parseInt(base) + (mutiple * 40);
		gdiv.querySelector('.exp-outline').style.height = newHeight + 'px';
	}
}

// function getCommentList(host){
// 	chrome.runtime.sendMessage({function:"getComments",data:host}, function(response) {
// 		if (chrome.runtime.lastError) {
// 			console.log("ERROR: ", chrome.runtime.lastError);
// 		} else {
// 			var comments = response.c
// 			for (let index = 0; index < comments.length; index++) {
// 				const element = comments[index];
// 				var upVoteBtn = "";
// 				var downVoteBtn = "";
// 				var item = htmlToElements('<ul class="gsc-comment-list"><li><p>'+ element.user.name +': '+element.content+'</p></li></ul>');
// 				return item;
// 			}
// 		}
// 	});
// }



//====================================++++++++++++======+++++==++=+++++++++++++++=
//walk(); 

// function walk(){
// 	var searchContains = document.querySelectorAll( "div.g > div > div.rc");
// 	for (let index = 0; index < searchContains.length; index++) {
// 		const element = searchContains[index];
// 		var link = element.querySelectorAll( ".r > a")[0].host;
// 		var url = link.split(".")
// 		var host = url[1] + "_" + url[2];

// 		chrome.runtime.sendMessage({function:"getComments",data:host}, function(response) {
// 			if (chrome.runtime.lastError) {
// 				console.log("ERROR: ", chrome.runtime.lastError);
// 			} else {
// 				console.log(response.h)
// 				var gscContainerId = createGscContainer(element,response.h)
// 				attachComments(element,gscContainerId, response.c)
// 				attachButtons(element,response.h)
// 			}
// 		});

// 	}
// }

// function createGscContainer(element,host){
// 	var gscContainerId = 'gsc-' + host
// 	var item = htmlToElements('<div id="'+ gscContainerId +'" ><h4>Comments</h4><div id="'+ gscContainerId +'-comments"></div><div id="'+ gscContainerId +'-button"></div></div>');
// 	element.append(item);
// 	return gscContainerId
// }

// function attachComments(container, gscContainerId, comments){
// 	// console.log('attaching comment to ' + gscContainerId)
// 	// console.log(comments)
// 	for (let index = 0; index < comments.length; index++) {
// 		const element = comments[index];
// 		var upVoteBtn = "";
// 		var downVoteBtn = "";
// 		var item = htmlToElements('<ul class="gsc-comment-list"><li><p>'+ element.user.name +': '+element.content+'</p></li></ul>');
// 		container.querySelectorAll('#'+gscContainerId+'-comments')[0].append(item); 
// 	}
// }

// function attachButtons(container,host){
// 	console.log('attaching button to gsc-' + host)
// 	var createCommentBtn = "<button class='gsc-add-comment-btn' data-host='"+ host +"'>post my comment</button>";
// 	var item = htmlToElements(createCommentBtn);
// 	item.addEventListener("click", addComment);
// 	var container = container.querySelectorAll('#gsc-'+host+'-button')[0];
// 	if (!container.hasChildNodes()) {
// 		container.append(item);
// 	}
// }


/*
 * Button Listeners
 */
function addComment(e){
	var host = e.target.getAttribute('data-host')
	var container = e.target.parentNode
	var form = "<input placeholder='what is your comment' class='gsc-"+host+"-comment-input' type='text' max='100'></input>";
	var item = htmlToElements(form)
	e.target.innerHTML = "post"
	e.target.removeEventListener("click", addComment)
	e.target.addEventListener("click", postComment);
	container.prepend(item);
}

function postComment(e){
	var host = e.target.getAttribute('data-host')
	var input = e.target.parentNode.querySelector('.gsc-'+host+'-comment-input')

	//disable the fields
	e.target.parentNode.querySelector('input').disabled = true;
	e.target.disabled = true;

	if (input.value !== '') {
		console.log(input.value)
		chrome.runtime.sendMessage({function:"postComment",data:{'host':host,'comment':input.value}}, function(response) {
			if (chrome.runtime.lastError) {
				console.log("ERROR: ", chrome.runtime.lastError);
			} else {
				if(response.status){
					var gdiv = e.target.parentNode.parentNode.parentNode.parentNode.parentNode
					calculateNewOutlineHeight(gdiv,1)
					attachCommentElement(e.target.parentNode.parentNode.querySelector('.gsc-container-comment'), response.data)
					e.target.parentNode.querySelector('input').remove()
					e.target.innerHTML = "post my comment"
					e.target.removeEventListener("click", postComment)
					e.target.addEventListener("click", addComment);
					e.target.disabled = false;
				}else{
					//enable the fields if error occurs
					e.target.parentNode.querySelector('input').disabled = false;
					e.target.disabled = false;
				}
			}
		});
	}
}

function upVote(e){
	e.target.disabled = true;
	var figureElement = e.target.parentNode.querySelector('.gsc-vote-figure')
	var figure = parseInt(figureElement.innerHTML)
	chrome.runtime.sendMessage({function:"makeVote",data:'up'},function(response){
		if (chrome.runtime.lastError) {
			console.log("ERROR: ", chrome.runtime.lastError);
		} else {
			figureElement.innerHTML = figure + 1;
			e.target.disabled = false;
		}
	})
}

function downVote(e){
	e.target.disabled = true;
	var figureElement = e.target.parentNode.querySelector('.gsc-vote-figure')
	var figure = parseInt(figureElement.innerHTML)
	chrome.runtime.sendMessage({function:"makeVote",data:'down'},function(response){
		if (chrome.runtime.lastError) {
			console.log("ERROR: ", chrome.runtime.lastError);
		} else {
			figureElement.innerHTML = figure - 1;
			e.target.disabled = false;
		}
	})
}

function report(e){
	console.log(e)
}

/*
 * Utilities
 */

function htmlToElements(html) {
    var template = document.createElement('template');
    template.innerHTML = html;
    return template.content.firstChild;
}

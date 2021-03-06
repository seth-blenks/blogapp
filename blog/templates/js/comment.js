
{% if current_user.is_authenticated %}
let comment_submit = document.querySelector('#comment-submit')
let comment_message = document.querySelector('#comment-message')

let comment_csrf = document.querySelector('#comment-csrf')

comment_submit.addEventListener('click',function(){
	console.log('comment submit clicked')
	let comment = comment_message.value
	let post = comment_post.value
	let csrf = comment_csrf.value
	if(comment && post && csrf){
		let formdata = new FormData()
		formdata.append('csrf-token',csrf)
		formdata.append('post-id',post)
		formdata.append('comment',comment)

		fetch('{{url_for("client.comment")}}',{
			'method': 'POST',
			'body': formdata
		}).then(response => {
			response.json().then( data => {
				if(response.status == 302) location.href = data;
				comment_message.value = ''
				display_comments(data);
			})
			
		})
	}
})

{% endif %}


let comment_box = document.querySelector('#blog-comment-box')
let comment_post = document.querySelector('#comment-post')
function comment_delete(){
	console.log(this);
	let comment_id = this.getAttribute('data-comment-id')
	let formdata = new FormData()
	formdata.append('csrf-token', comment_csrf.value)
	formdata.append('comment-id', comment_id)
	fetch('{{url_for("client.delete_comment")}}',{
		'method': 'POST',
		'body': formdata
	}).then( response => response.json()).then(data => {
		if(data == true){
			window.location.reload()
		}
	})
}

function display_comments(data){
	let new_comment = ``
	if(data.length == 1){new_comment += `<h4 class="comments-count">${data.length} Comment</h4>`}
		else if(data.length == 0){ new_comment += `<h4 class="comments-count">Leave a Comment.</h4>`}
	else{ new_comment += `<h4 class="comments-count">${data.length} Comments</h4>`
		}
			for(let i = 0; i < data.length; i++){
				new_comment += `
				<div id="comment_${data[i]['comment-id']}" class="comment">
                  <div class="d-flex">
                    <div class="comment-img"><img src="${data[i]['image']}" alt=""></div>
                    <div>
                      <h5>${data[i]['username']}</h5>
                      <time datetime="${data[i]['date']}">${data[i]['date']}</time>
                      <p>
                        ${data[i]['comment']}
                        <div class="filter">
				                  <a class="icon" href="#" data-bs-toggle="dropdown"><i class="bi bi-three-dots-vertical text-muted"></i></a>
				                  <ul class="dropdown-menu dropdown-menu-end dropdown-menu-arrow">
				                    <li><a data-comment-id='${data[i]['comment-id']}' class='comment-delete-button dropdown-item mr-2 ${(data[i]['comment-user-id'] == data[i]['user-id']) ||  data[i]['admin'] ? 'admin' : 'collapse'}'>Delete</a></li>
				                   </ul>
				                </div>
                      </p>
                    </div>
                  </div>
                </div>`
			}

			comment_box.innerHTML = new_comment

	let delete_buttons = document.querySelectorAll('.comment-delete-button')
	delete_buttons.forEach( button => {
		button.addEventListener('click', comment_delete)
	})
}


window.addEventListener('DOMContentLoaded', function(){
	fetch('{{url_for("client.comment")}}' + '?post_id=' + comment_post.value).then(response => response.json()).then( data => {
		display_comments(data);
	})
})

setTimeout(function(){
	let formdata = new FormData()
	let blog_id = document.querySelector('#comment-post').value
	formdata.append('csrf-token', '{{csrf_token}}')
	formdata.append('blog-id', blog_id)

	fetch('{{url_for("client.reads")}}', {
		'method': 'POST',
		'body': formdata
	}).then( response => {
		if(response.status == 200){
			console.log('article reads updated');
		}
	})
}, 20000)


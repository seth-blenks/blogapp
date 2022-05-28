{% if current_user.is_authenticated %}
reaction_button.addEventListener('click', function(){
	let formdata = new FormData()
	formdata.append('user-id', {{current_user.id}})
	formdata.append('csrf-token', comment_csrf.value)
	formdata.append('blogpost-id', {{blog.id}})
	fetch('/react',{
		'method': 'POST',
		'body': formdata
	})
})

{% endif %}
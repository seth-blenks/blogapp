let tag_csrf_token = document.querySelector('#tags-csrf-token')
let tag_title = document.querySelector('#tags-name')
let tag_select = document.querySelector('#tags-select')
let tag_submit = document.querySelector('#tags-submit')
let message = document.querySelector('.modal .modal-body')
let modal_launcher = document.querySelector('#modal-launcher')

tag_submit.addEventListener('click',function(){
	let csrf = tag_csrf_token.value
	let name = tag_title.value
	let select = tag_select.selectedOptions[0].value

	if(csrf && name && select){
		let form = new FormData()
		form.append('csrf-token', csrf)
		form.append('name', name)
		form.append('select', select)

		fetch('{{url_for("tags")}}',{
			'method': 'POST',
			'body': form,
		}).then(response => response.json()).then(data => {
			message.innerText = data['message']
			modal_launcher.click();
		})
	}
	

})
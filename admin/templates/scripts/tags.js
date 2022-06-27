let tag_csrf_token = document.querySelector('#tags-csrf-token')
let tag_title = document.querySelector('#tags-name')
let tag_select = document.querySelector('#tags-select')
let tag_submit = document.querySelector('#tags-submit')
let message = document.querySelector('.modal .modal-body')
let modal_launcher = document.querySelector('#modal-launcher')
let tag_delete_buttons = document.querySelectorAll('.tag-delete-button')
let category_delete_buttons = document.querySelectorAll('.category-delete-button')

tag_submit.addEventListener('click',function(){
	let csrf = tag_csrf_token.value
	let name = tag_title.value
	let select = tag_select.selectedOptions[0].value

	if(csrf && name && select){
		let form = new FormData()
		form.append('csrf-token', csrf)
		form.append('name', name)
		form.append('select', select)

		fetch('{{url_for("administrator.tags")}}',{
			'method': 'POST',
			'body': form,
		}).then(response => response.json()).then(data => {
			message.innerText = data['message']
			modal_launcher.click();
		})
	}
	

})


tag_delete_buttons.forEach(button => {
	button.addEventListener('click', function(){
		let _widget = this;
		let form = new FormData()
		form.append('csrf-token', "{{csrf_token}}")
		form.append('name', button.getAttribute('data-tag-name'))
		form.append('category', false)
		fetch('{{url_for("administrator.tags")}}', {
			'method': 'DELETE',
			'body': form
		}).then( response => response.json()).then( data => {
			message.innerText = data
			modal_launcher.click();
			_widget.parentElement.classList.add('bounceOutAnimation');
		})
	})
})

category_delete_buttons.forEach(button => {
	button.addEventListener('click', function(){
		let _widget = this;
		let form = new FormData()
		form.append('csrf-token', "{{csrf_token}}")
		form.append('name', button.getAttribute('data-category-name'))
		form.append('category', true)
		fetch('{{url_for("administrator.tags")}}', {
			'method': 'DELETE',
			'body': form
		}).then( response => {
			if(response.status == 200){
				response.json().then( data => {
					message.innerText = data
					modal_launcher.click();
					_widget.parentElement.classList.add('bounceOutAnimation');
				})
			}else{
				response.json().then( data => {
					message.innerText = data
					modal_launcher.click();
				})
			}
		})
	})
})
let compose_email_select_field = document.querySelector('#compose-email select')
let compose_email_csrf = document.querySelector('#compose-email input[name="csrf-token"]')
let compose_email_subject = document.querySelector('#compose-email input[name="compose-email-subject"]')
let compose_email_content = document.querySelector('#compose-email textarea')
let compose_email_user_email = document.querySelector('#compose-email input[name="compose-email-user-email"]')
let compose_email_submit_button = document.querySelector('#compose-email button')
let compose_email_all_users = true

compose_email_select_field.addEventListener('input',function(){
	let option = this.selectedOptions[0].value
	if(option == 'Specific User'){
		compose_email_all_users = false
		compose_email_user_email.classList.remove('collapse')
	}else{
		compose_email_all_users = true
		compose_email_user_email.classList.add('collapse');
	}
})
compose_email_submit_button.addEventListener('click', function(){
	let _button = this;
	_button.innerHTML = '<i class="bi bi-arrow-repeat fa-spin"></i>'

	let csrf = compose_email_csrf.value
	let subject = compose_email_subject.value
	let content = compose_email_content.value
	if(csrf && subject && content){
		let formdata = new FormData()
		if(compose_email_all_users){
			fetch('{{url_for("administrator.users_all")}}').then( response => response.json()).then( data => {
				console.log('list of known users with emails')
				console.log(data);
				data.forEach( user_email => {
					formdata.append('to',user_email);
				})

				formdata.append('csrf-token', csrf)
					formdata.append('subject', subject)
					formdata.append('content', content)

					fetch('{{url_for("administrator.compose_email")}}', {
						'method': 'POST',
						'body': formdata
					}).then( response => response.json()).then( data => {
						_button.innerHTML = "<span> Create </span><i class='bi bi-node-plus-fill'></i>"
						document.querySelector('.modal-body').innerText = data
						new bootstrap.Modal('#smallModal').show();
					})
			})
		}else{
			let email = compose_email_user_email.value
			if(email){
				formdata.append('to', email)
				formdata.append('subject', subject)
				formdata.append('csrf-token', csrf)
				formdata.append('content', content)

				fetch('/admin/compose/email', {
					'method': 'POST',
					'body': formdata
				}).then( response => response.json()).then( data => {
						_button.innerHTML = "<span> Create </span><i class='bi bi-node-plus-fill'></i>"
						document.querySelector('.modal-body').innerText = data
						new bootstrap.Modal('#smallModal').show();
					})
			}
			
		}
	}

})

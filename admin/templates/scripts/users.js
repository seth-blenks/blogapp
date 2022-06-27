console.log('post script activated')
let datatable = document.querySelector('.datatable')
new simpleDatatables.DataTable(datatable);

let list_of_restricted_user_ids = []
let list_of_unrestricted_user_ids = []

let users = document.querySelectorAll('.form-check-input-not-restricted')
let restricted_users = document.querySelectorAll('.form-check-input-restricted')
users.forEach( user => {
	user.addEventListener('input', function(){
		if(this.checked){
			list_of_restricted_user_ids.push(this.getAttribute('data-user-id'))
			}
			else{
			list_of_restricted_user_ids.pop(this.getAttribute('data-user-id'))
			}
	})
})

restricted_users.forEach( user => {
	user.addEventListener('input', function(){
		if(this.checked){
			list_of_restricted_user_ids.pop(this.getAttribute('data-user-id'))
			console.log(list_of_unrestricted_user_ids)
			}
			else{
			list_of_unrestricted_user_ids.push(this.getAttribute('data-user-id'))
			console.log(list_of_unrestricted_user_ids)
			}
	})
})

let save_changes_button = document.querySelector('#users-save-changes-button')
let csrf_token = document.querySelector('#users-csrf-token-input')
save_changes_button.addEventListener('click', function(){
	fetch('{{url_for("administrator.users")}}', {
		'method': 'POST',
		'headers': {
			'Content-Type': 'application/json'
		},
		'body': JSON.stringify({
			'unrestrict-ids': list_of_unrestricted_user_ids,
			'restrict-ids': list_of_restricted_user_ids,
			'csrf-token': csrf_token.value
		})
	}).then( response => response.json()).then( data => {
		let modal_launcher = document.querySelector('#modal-launcher')
		document.querySelector('.modal .modal-body').innerText = data
		modal_launcher.click();
	})
})

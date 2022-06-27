let notification_board = document.querySelector('#notifications-board')
let notification_widget = document.querySelector('.notification-load-widget')
let notification_nav = null
let mark_all = null


function get_notifications(page){
	fetch(`{{url_for("administrator.notification_view",page="${parseInt(page)}")}}`).then(response => {
		if(response.status == 200){
			response.text().then( content => {
				notification_board.innerHTML = content;
			})
		}
	})
}

function mark_all_as_read(){
	console.log('marking all notifications as read')
	fetch('{{url_for("administrator.mark_all_notifications")}}', {
		'method': 'POST'
	})
}

window.addEventListener('DOMContentLoaded', function(){
	get_notifications(1)
})

notification_widget.addEventListener('click', function(){
	notification_nav = document.querySelectorAll('.notification-navs')
	mark_all = document.querySelector('#notification-mark-all')
	mark_all.addEventListener('click', mark_all_as_read)

	notification_nav.forEach( nav => {
	nav.addEventListener('click', function(){
			console.log('getting next notifications for page ' + this.getAttribute('data-page'))
			get_notifications(parseInt(this.getAttribute('data-page')));
		})
	})

	let items = document.querySelectorAll('#notifications-board .notification-item')
	items.forEach( item => {
		item.addEventListener('click', function(){
			let formdata = new FormData()
			formdata.append('notification-id', item.getAttribute('data-id'))
			fetch('{{url_for("administrator.seen_notifications")}}',{
				'method':'POST',
				'body': formdata
			}).then( response => {
				if(response.status == 200){
					location.href = item.getAttribute('data-link');
				}
			})
		})
	})
})




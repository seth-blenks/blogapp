let copy_buttons = document.querySelectorAll('.images-copy-buttons')
let page_navigation = document.querySelectorAll('.page-item')
let delete_buttons = document.querySelectorAll('.images-delete-buttons')
let csrf_token = document.querySelector('#images-csrf')



copy_buttons.forEach(button => {
	button.addEventListener('click',function(){
		navigator.clipboard.writeText(this.getAttribute('data-imageName'))

		let former = document.querySelector('.images-copy-buttons.active')
		if(former){
			former.classList.remove('active')
			former.firstElementChild.className = 'ri-file-copy-2-line'
		}
		this.classList.add('active')
		this.firstElementChild.className = 'ri-checkbox-line'
	})
})

delete_buttons.forEach(button => {
	button.addEventListener('click', function(){
		let image_widget = this;
		let image_id = this.getAttribute('data-image-id')
		let formdata = new FormData()
		formdata.append('image-id', image_id)
		formdata.append('csrf-token', csrf_token.value)
		fetch('{{url_for("administrator.images")}}',{
			'method': 'DELETE',
			'body': formdata
		}).then( response => response.json()).then( data => {
			image_widget.firstElementChild.className = 'ri-delete-bin-5-fill'
		})
	})
})

page_navigation.forEach( item => {
	item.addEventListener('click',function(){
		let page_number = this.getAttribute('data-page')
		fetch('{{url_for("administrator.images")}}?page=' + page_number).then( response => response.text()).then( data => {
			document.querySelector('#main').innerHTML = data
			fetch('/admin/assets/scripts/images.js').then( response => response.text()).then( data => {
				eval(data)
			})
		})
	})
})

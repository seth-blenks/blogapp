
let images_submit = document.querySelector('#image-submit')
let image_csrf = document.querySelector('#image-submit-csrf').value
let images = document.querySelector('#image-upload')
let label = document.querySelector('#image-upload-label')

images.addEventListener('input', function(){
	label.innerText = 'Selected ' + images.files.length.toString() + ' Images'
})
images_submit.addEventListener('click',function(){
	let image_button = this
	image_button.firstElementChild.className = 'ri-refresh-line'

	let files = images.files
	let formdata = new FormData()
	if(files && image_csrf){
		formdata.append('csrf-token',image_csrf)
		for (var i = files.length - 1; i >= 0; i--) {
		formdata.append('images',files[i])
	}

	fetch('{{url_for("administrator.upload_image")}}',{
		'method': 'POST',
		'body': formdata
	}).then(response => {
		if(response.status == 200){
			response.json().then( data => {
				image_button.firstElementChild.className = 'ri-upload-cloud-2-line'

				document.querySelector('#alert-box').innerHTML = `
				<div class="alert ${data['category']} alert-dismissible fade show" role="alert">
			        ${data['message']}
			        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
			      </div>
		              `
			});
		}else if (response.status == 413){
			console.log('response status code is 413')
			image_button.firstElementChild.className = 'ri-upload-cloud-2-line'
			document.querySelector('#alert-box').innerHTML = `
				<div class="alert alert-info alert-dismissible fade show" role="alert">
			        File too large. Maximum upload size is <b>3MB</b>
			        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
			      </div>
		              `
		}
	})

	}
	
})

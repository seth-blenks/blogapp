let user_profile_csrf = document.querySelector('.edit-profile input[name="csrf-token"]');
let fullname = document.querySelector('.edit-profile input[name="fullname"]');
let about = document.querySelector('.edit-profile textarea[name="about"]');
let company = document.querySelector('.edit-profile input[name="company"]');
let job = document.querySelector('.edit-profile input[name="job"]');
let country = document.querySelector('.edit-profile input[name="country"]');
let address = document.querySelector('.edit-profile input[name="address"]');
let phone = document.querySelector('.edit-profile input[name="phone"]');
let twitter_profile = document.querySelector('.edit-profile input[name="twitter-profile"]');
let facebook_profile = document.querySelector('.edit-profile input[name="facebook-profile"]');
let instagram_profile = document.querySelector('.edit-profile input[name="instagram-profile"]');
let linkedin_profile = document.querySelector('.edit-profile input[name="linkedin-profile"]');
let profile_alert = document.querySelector('.edit-profile .alert-box');
let user_profile_submit_button = document.querySelector('.edit-profile button[type="submit"]');

user_profile_submit_button.addEventListener('click',function(){
	let formdata = new FormData()

	let csrf_token = user_profile_csrf.value
	let about_value = about.value
	let fullname_value = fullname.value
	let company_value = company.value
	let job_value = job.value
	let country_value = country.value
	let address_value = address.value
	let phone_value = phone.value
	let twitter_profile_value = twitter_profile.value
	let facebook_profile_value = facebook_profile.value
	let instagram_profile_value = instagram_profile.value
	let linkedin_profile_value = linkedin_profile.value


	if(csrf_token && twitter_profile_value && instagram_profile_value && linkedin_profile_value && facebook_profile_value){
		formdata.append('csrf-token', csrf_token)
		formdata.append('twitter-profile',twitter_profile_value)
		formdata.append('instagram-profile', instagram_profile_value)
		formdata.append('linkedin-profile', linkedin_profile_value)
		formdata.append('facebook-profile', facebook_profile_value)

		/* mercilaneous data */
		formdata.append('fullname', fullname_value)
		formdata.append('about', about_value)
		formdata.append('job', job_value)
		formdata.append('country', country_value)
		formdata.append('address', address_value)
		formdata.append('phone', phone_value)
		formdata.append('company', company_value)

		
		fetch('{{url_for("update_user_profile")}}', {
			'method': 'POST',
			'body': formdata,
		}).then(response => response.json()).then( data => {
			console.log(data)
		});

	}else{
		profile_alert.innerHTML = `
			<div class="alert alert-info alert-dismissible fade show" role="alert">
             Social Media links must be set.
              <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
		`
	}

	})
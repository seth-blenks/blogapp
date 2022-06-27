let website_visitors_view = document.querySelector('#website-visitors')
let website_filter = document.querySelectorAll('.visitors-filter')

function get_visitors(timeFrame){
	/*
	where timeframe is: perDay, perMonth or perYear
	*/

	website_visitors_view.innerHTML = '<b> Loading ... </b>';
	fetch(`{{url_for("administrator.visitors")}}?timeFrame=${timeFrame}`).then(response => response.json()).then( data => {
	website_visitors_view.innerHTML = ''
	data.forEach( data => {
		console.log(data)
		let tr = document.createElement('tr')
		tr.innerHTML = ` <td> ${data[0]} </td>
						<td> ${data[1]} </td>`;
		website_visitors_view.appendChild(tr);
	});

	})
}

website_filter.forEach( filter => {
	filter.addEventListener('click', function(){
		get_visitors(this.getAttribute('data-filter'));
	})
})

document.addEventListener('DOMContentLoaded', function(){
	get_visitors('perDay');
})
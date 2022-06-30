console.log('post script activated')
let datatable = document.querySelector('.datatable')
new simpleDatatables.DataTable(datatable);


let pagination_widgets = document.querySelectorAll('.blog-pagination-link')
pagination_widgets.forEach(widget => {
	widget.addEventListener('click', function(){
		fetch('{{url_for("administrator.blogs")}}?page=' + widget.getAttribute('data-page')).then(response => response.text()).then( data => {
		document.querySelector('#main').innerHTML = data
		fetch('{{url_for("administrator.dynamic_js",filename="blogs.js")}}').then(response => response.text()).then( text => {
			eval(text);
		})
	})
	})
	
})
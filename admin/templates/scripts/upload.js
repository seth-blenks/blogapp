let composition_csrf = document.querySelector('input[name="composition-csrf-token"]')
let message = document.querySelector('.modal .modal-body')
console.log(message)
let modal_launcher = document.querySelector('#modal-launcher');



function image_upload_function(blobinfo, success, failure, progress){
    let xhr, formdata;

    xhr = new XMLHttpRequest();
    console.log('image upload function called')
    xhr.open('post', '{{url_for("administrator.upload_image")}}')
    xhr.withCredentials = true
    xhr.upload.onprogress =  function(e){
      progress(e.loaded / e.total * 100)
    }

    xhr.onload = function(){
      let json;

      if(xhr.status === 403){
        failure('HTTP ERROR: ' + xhr.status, {remove: true})
        return;
      }

      if(xhr.status < 200 || xhr.status >= 300){
        failure('HTTP ERROR: ' + xhr.status );
        return;
      }

      json = JSON.parse(xhr.responseText);
      if(!json || typeof json.location != 'string'){
        failure('Invalid JSON: ' + xhr.responseText);
        return;
      }

      success(json.location)
    };

    xhr.onerror = function(){
      failure('Image upload failed due to xhr transport error. Code: ' + xhr.status);
    };

    formdata = new FormData()
    formdata.append('images', blobinfo.blob(), blobinfo.filename())
    formdata.append('csrf-token',composition_csrf.value)
    xhr.send(formdata)
  }

  tinymce.init({
    selector: '#composition-editor',
    plugins: 'print preview paste importcss searchreplace autolink autosave save directionality code visualblocks visualchars fullscreen image link media template codesample table charmap hr pagebreak nonbreaking anchor toc insertdatetime advlist lists wordcount imagetools textpattern noneditable help charmap quickbars emoticons',
    imagetools_cors_hosts: ['picsum.photos'],
    menubar: 'file edit view insert format tools table help',
    toolbar: 'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist | forecolor backcolor removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media template link anchor codesample | ltr rtl',
    toolbar_sticky: true,
    autosave_ask_before_unload: true,
    autosave_interval: '30s',
    autosave_prefix: '{path}{query}-{id}-',
    autosave_restore_when_empty: false,
    autosave_retention: '2m',
    image_advtab: true,
    images_upload_handler: image_upload_function,
    link_list: [{
        title: 'My page 1',
        value: 'https://www.tiny.cloud'
      },
      {
        title: 'My page 2',
        value: 'http://www.moxiecode.com'
      }
    ],
    image_list: [{
        title: 'My page 1',
        value: 'https://www.tiny.cloud'
      },
      {
        title: 'My page 2',
        value: 'http://www.moxiecode.com'
      }
    ],
    image_class_list: [{
        title: 'None',
        value: ''
      },
      {
        title: 'Some class',
        value: 'class-name'
      }
    ],
    importcss_append: true,
    file_picker_callback: function(callback, value, meta) {
      /* Provide file and text for the link dialog */
      if (meta.filetype === 'file') {
        callback('https://www.google.com/logos/google.jpg', {
          text: 'My text'
        });
      }

      /* Provide image and alt text for the image dialog */
      if (meta.filetype === 'image') {
        callback('https://www.google.com/logos/google.jpg', {
          alt: 'My alt text'
        });
      }

      /* Provide alternative source and posted for the media dialog */
      if (meta.filetype === 'media') {
        callback('movie.mp4', {
          source2: 'alt.ogg',
          poster: 'https://www.google.com/logos/google.jpg'
        });
      }
    },
    templates: [{
        title: 'New Table',
        description: 'creates a new table',
        content: '<div class="mceTmpl"><table width="98%%"  border="0" cellspacing="0" cellpadding="0"><tr><th scope="col"> </th><th scope="col"> </th></tr><tr><td> </td><td> </td></tr></table></div>'
      },
      {
        title: 'Starting my story',
        description: 'A cure for writers block',
        content: 'Once upon a time...'
      },
      {
        title: 'New list with dates',
        description: 'New List with dates',
        content: '<div class="mceTmpl"><span class="cdate">cdate</span><br /><span class="mdate">mdate</span><h2>My List</h2><ul><li></li><li></li></ul></div>'
      }
    ],
    template_cdate_format: '[Date Created (CDATE): %m/%d/%Y : %H:%M:%S]',
    template_mdate_format: '[Date Modified (MDATE): %m/%d/%Y : %H:%M:%S]',
    height: 600,
    image_caption: true,
    quickbars_selection_toolbar: 'bold italic | quicklink h2 h3 blockquote quickimage quicktable',
    noneditable_noneditable_class: 'mceNonEditable',
    toolbar_mode: 'sliding',
    contextmenu: 'link image imagetools table',
    content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
  });

let composition_title = document.querySelector('input[name="composition-title"]')
let composition_description = document.querySelector('input[name="composition-description"]')
let composition_content = document.querySelector('#composition-editor')
let composition_image = document.querySelector('input[name="composition-image"]')
let composition_category = document.querySelector('select[name="composition-category"]')
let composition_tags = document.querySelector('select[name="composition-tags"]')
let composition_submit_button = document.querySelector('button[name="composition-submit"]')
let image_selection_modal = new bootstrap.Modal('#image-selection-modal')

composition_image.addEventListener('input', function(){
  document.querySelector('label[for="composition-image"]').innerText = this.files[0].name
})

composition_submit_button.addEventListener('click',function(){
  console.log('uploading file to database')
  let title = composition_title.value
  let description = composition_description.value
  let content = tinymce.get('composition-editor').getContent()
  let image = composition_image.files[0]
  let csrf = composition_csrf.value
  let category = composition_category.selectedOptions[0].value

  if(title && description && csrf && image && content && category){
    let tags = [] 
    for (var i = composition_tags.selectedOptions.length - 1; i >= 0; i--) {
      tags.push(composition_tags.selectedOptions[i].value);
    }

    let formdata = new FormData()
    formdata.append('title', title)
    formdata.append('description', description)
    formdata.append('content', content)
    formdata.append('csrf-token',csrf)
    formdata.append('image', image)
    formdata.append('category', category)
    for (var i = tags.length - 1; i >= 0; i--) {
      formdata.append('tags',tags[i])
    }

    fetch('{{url_for("administrator.upload_article")}}',{
      method: 'POST',
      'body': formdata
    }).then(response => {
      if(response.status < 500){
        response.json().then( data => {
          message.innerText = data['message']
        })
        }
      else{
        message.innerText = 'Server Error!'
        }
   
        modal_launcher.click();

      }) // end of fetch
  }
})// end of event listener function




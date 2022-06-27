class DashboardController{

  setup(screen, buttonclass){
    let dashboardcontroller = this;
    dashboardcontroller.screen = screen

    let buttons = document.querySelectorAll(buttonclass)
    buttons.forEach(button => { button.addEventListener("click", function(){
      let previous_active = document.querySelector('.nav-link.active')
      previous_active.classList.remove('active')
      button.classList.add('active');
      dashboardcontroller.request_data(this); 
    })});

  }

  setup_data(data){
    let div = document.createElement("div")
    div.innerHTML = data
    this.screen.innerHTML = ""
    this.screen.appendChild(div)
  }

  request_data(object){
    let dashboardcontroller = this;
    let data_location = object.getAttribute("data-href")
    let data_script = object.getAttribute("data-script")


    if(!data_location) throw Error("data-href not defined for this link");

    fetch(data_location).then(response => response.text()).then( data => {
      dashboardcontroller.setup_data(data);

      if(data_script){
        let scripts = data_script.split(",")
        console.log(scripts)
        for (var i = 0; i < scripts.length; i++) {
          fetch(scripts[i]).then(response => response.text()).then(
            data => {
              eval(data);
            })
        }
        
      }

    })
  }

}


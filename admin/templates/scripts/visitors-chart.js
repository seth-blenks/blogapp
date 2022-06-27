let apexchart_config = {
    series: [ ],
    chart: {
      height: 350,
      type: 'area',
      toolbar: {
        show: false
      },
    },
    markers: {
      size: 4
    },
    colors: ['#0d6efd',],
    fill: {
      type: "gradient",
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.3,
        opacityTo: 0.4,
        stops: [0, 90, 100]
      }
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'smooth',
      width: 2
    },
    xaxis: {
      type: 'numeric'
    },
    tooltip: {
      x: {
        format: 'dd/MM/yy'
      },
    },
    noData: {
      text: 'Loading ...',
      align: 'center',
      verticalAlign: 'middle',
      offsetX: 0,
      offsetY: 0,
      style: {
        color: '#ccc',
        fontSize: '14px',
        fontFamily: 'ubuntu'
      }
    }
  }

let apexcharts = new ApexCharts(document.querySelector("#reportsChart"), apexchart_config)
apexcharts.render();

function updateData(chart, series) {
    chart.updateSeries(series)
}

// apex time
let apexcharts_options = document.querySelectorAll('.apexcharts-options')

apexcharts_options.forEach( button => {
  button.addEventListener('click', function(){
    // clearing the chart view
    updateData(apexcharts, [{'name':'Visitors','data': []}])

    // getting data ...
    let time = button.getAttribute('data-time')
    fetch(`{{url_for("administrator.visitors_charts")}}?timeFrame=${time}`).then( response => {
      if(response.status == 200){
        response.json().then( series => {
          updateData(apexcharts, series);
        })
      }
    })
  })
})



document.addEventListener("DOMContentLoaded", () => {
  fetch(`{{url_for("administrator.visitors_charts",timeFrame="week")}}`).then( response => {
    if(response.status == 200){
      response.json().then( series => {
        updateData(apexcharts, series);
      })
    }
  })

})
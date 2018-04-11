$.getJSON( "/static/data/treemap.json", function( treemap_data ) {
      google.charts.load('current', {'packages':['treemap']});
      google.charts.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable(treemap_data);

        tree = new google.visualization.TreeMap(document.getElementById('treemap'));

        tree.draw(data, {
          minColor: '#bf212f',
          midColor: '#f2f2f2',
          maxColor: '#006f3c',
          minColorValue: -0.5,
          maxColorValue: 0.5,
          headerHeight: 15,
          maxDepth: 2,
          fontColor: 'black',
          showScale: true
        });

      }
});
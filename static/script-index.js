function percentChangeRenderer(instance, td, row, col, prop, value, cellProperties) {
    Handsontable.renderers.NumericRenderer.apply(this, arguments);

    if (parseFloat(value) > 0.0) {
        td.className += ' text-success';
    }

    if (parseFloat(value) < 0.0) {
        td.className += ' text-danger';
    }
}

function buySellRenderer(instance, td, row, col, prop, value, cellProperties) {
    Handsontable.renderers.TextRenderer.apply(this, arguments);

    if (value == 'buy') {
        td.className += ' text-success';
    }

    if (value == 'sell') {
        td.className += ' text-danger';
    }
}

Handsontable.renderers.registerRenderer('percentChangeRenderer', percentChangeRenderer);
Handsontable.renderers.registerRenderer('buySellRenderer', buySellRenderer);


$.getJSON( "/static/data/summary.json", function( data ) {
    $('#total-btc').html(String(Math.round(data["total_btc"]*10)/10) + " ₿");
    $('#24h-chg-btc').html(String(Math.round(data["24h_chg_btc"]*10000)/100) + " %");
    $('#24h-chg-btc').addClass(data["24h_chg_btc"] < 0.0 ? 'text-danger' : data["24h_chg_btc"] > 0.0 ? 'text-success' : '');
    $('#total-btc').prop("title", String(Math.round(data["total_usd"])) + " $ " + String(Math.round(data["24h_chg_usd"]*10000)/100) + " %");
    $('[data-toggle="tooltip"]').tooltip();

    var ctx = document.getElementById("myChart").getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data["30d_labels"],
            datasets: [{
                data: data["30d_performance_btc"],
                fill: false,
                borderColor: data["30d_performance_btc"][0] > data["30d_performance_btc"][29] ? 'red' : 'green',
            }]
        },
        options: {
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    display: false
                }],
                xAxes: [{
                    display: false
                }]
            },
            elements: { point: { radius: 0 } },
        }
    });

    var container = document.getElementById('transactions');
    var hot = new Handsontable(container, {
        data: data["recent_transactions"],
        filters: true,
        stretchH: 'all',
        columns: [
            {
            },
            {
            },
            {
            },
            {
                type: 'numeric',
                numericFormat: {
                    pattern: '0,0',
                    culture: 'en-US'
                },
            },
            {
            },
        ],
        cells: function (row, col, prop) {
            var cellProperties = {};
            if (col === 2) {
                cellProperties.renderer = "buySellRenderer";
            }
            if (col == 3 || col == 4) {
                cellProperties.className = "htRight";
            }
            return cellProperties;
        },
    });
});

$.getJSON( "/static/data/portfolio.json", function( data ) {
    searchField = document.getElementById('search_field')
    var container = document.getElementById('portfolios');
    var hot = new Handsontable(container, {
        data: data,
        colHeaders: ['Symbol', 'Market Cap ($)', '% 24h', '% 7d', 'Balance', 'Value ($)', 'Price (₿)', 'Value (₿)', 'P/L %'],
        currentRowClassName: 'currentRow',
        columnSorting : true,
        filters: true,
        search: true,
        dropdownMenu: true,
        stretchH: 'all',
        columns: [
            {
            },
            {
                type: 'numeric',
                numericFormat: {
                    pattern: '0,0',
                    culture: 'en-US'
                },
            },
            {
                type: 'numeric',
                numericFormat: {
                    pattern: '0.00%',
                    culture: 'en-US'
                },
            },
            {
                type: 'numeric',
                numericFormat: {
                    pattern: '0.00%',
                    culture: 'en-US'
                },
            },
            {
                type: 'numeric',
                numericFormat: {
                    pattern: '0,0.0000',
                    culture: 'en-US'
                },
            },
            {
                type: 'numeric',
                numericFormat: {
                    pattern: '0,0.00',
                    culture: 'en-US'
                },
            },
            {
                type: 'numeric',
                numericFormat: {
                    pattern: '0,0.0000',
                    culture: 'en-US'
                },
            },
            {
                type: 'numeric',
                numericFormat: {
                    pattern: '0,0.0000',
                    culture: 'en-US'
                },
            },
            {
                type: 'numeric',
                numericFormat: {
                    pattern: '0.00%',
                    culture: 'en-US'
                },
            },
        ],
        cells: function (row, col, prop) {
            var cellProperties = {};
            if (col === 2 || col === 3 || col === 8) {
                cellProperties.renderer = "percentChangeRenderer";
            }
            return cellProperties;
        }
    });

    Handsontable.dom.addEvent(searchField, 'keyup', function (event) {
        var queryResult = hot.search.query(this.value);

        hot.render();
    });
});


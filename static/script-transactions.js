function buySellRenderer(instance, td, row, col, prop, value, cellProperties) {
    Handsontable.renderers.TextRenderer.apply(this, arguments);

    if (value == 'buy') {
        td.className += ' text-success';
    }

    if (value == 'sell') {
        td.className += ' text-danger';
    }
}

Handsontable.renderers.registerRenderer('buySellRenderer', buySellRenderer);


$.getJSON( "/static/data/transactions.json", function( data ) {
    var container = document.getElementById('transactions');
    var hot = new Handsontable(container, {
        data: data,
        colHeaders: ['ID', 'Time', 'Symbol', 'Type', 'Amount', 'Price (₿)'],
        columnSorting : true,
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
        ],
        cells: function (row, col, prop) {
            var cellProperties = {};
            if (col === 3) {
                cellProperties.renderer = "buySellRenderer";
            }
            return cellProperties;
        },
    });
});
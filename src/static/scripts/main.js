$(document).ready(function() {
  fetchDatabases();

  $(".tile").on("click", "#refresh-databases", function(){
    fetchDatabases();
  });
  $(".tile").on("click", "#database", function(){
    var databaseName = $(this).text();
    $.ajax({
      url: 'api/get-tables/',
      method: 'GET',
      data: { database: databaseName },
      success: function(data) {
        generateTablesTable(data);
      },
      error: function(error) {
        console.error('Error fetching tables:', error);
      }
    });
  });
});

function fetchDatabases() {
  $.ajax({
    url: 'api/get-databases',
    type: 'GET',
    dataType: 'json',
    success: function(data) {
      displayDatabases(data.databases, data.host);
    },
    error: function(xhr, status, error) {
      console.error('Error: ', status, error);
    }
  });
}

function displayDatabases(databases, host) {
  var databaseList = $('#database-list');
  var databasesElement = '<h3>Databases<img id="refresh-databases" src="static/icons/refresh.png" alt="refresh"></h3>';
  var content = '<h2>' + host + '</h2>' + databasesElement;
  var listHTML = '<ul>';
  
  databases.forEach(function(database) {
      listHTML += '<li><a id="database">' + database + '</a></li>';
  });

  listHTML += '</ul>';
  content += listHTML;
  databaseList.hide().fadeOut();
  databaseList.html(content);
  databaseList.hide().fadeIn();
}

function generateTablesTable(data) {
  var tableHTML = '<table>' +
    '<thead>' +
      '<tr class="head">' +
        '<th>table</th>' +
        '<th>rows</th>' +
        '<th>size</th>' +
        '<th>collation</th>' +
      '</tr>' +
    '</thead>' +
    '<tbody>';

  $.each(data.tables, function(tableName, tableData) {
    tableHTML += '<tr>' +
      '<td>' + tableName + '</td>' +
      '<td>' + tableData.rows + '</td>' +
      '<td>' + tableData.size + '</td>' +
      '<td>' + tableData.collation + '</td>' +
    '</tr>';
  });

  tableHTML += '</tbody></table>';

  $('#table-container').hide().fadeOut();
  $('#database-name').html(data.database);
  $('#table-container').html(tableHTML);
  $('#table-container').hide().fadeIn();
}
$(document).ready(function() {
  fetchDatabases();

  $(".tile").on("click", "#refresh-databases", function(){
    fetchDatabases();
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
  var content = '<h2>' + host + '</h2>' + '<h3>Databases<img id="refresh-databases" src="static/icons/refresh.png" alt="refresh"></h3>'
  var listHTML = '<ul>';
  
  databases.forEach(function(database) {
      listHTML += '<li><a href="/">' + database + '</a></li>';
  });

  listHTML += '</ul>';
  content += listHTML;
  databaseList.html(content);
  databaseList.hide().slideDown(500);
}
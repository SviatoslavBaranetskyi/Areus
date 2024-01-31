$(document).ready(function() {
    console.log("loaded")
    $.ajax({
      url: 'get_databases',
      type: 'GET',
      dataType: 'json',
      success: function(data) {
        console.log(JSON.stringify(data))
      },
      error: function(xhr, status, error) {
        console.error('Error: ', status, error);
      }
    });
  });
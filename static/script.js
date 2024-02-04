function myFunction() {
  // Get the snackbar DIV
  var x = document.getElementById("snackbar");

  // Add the "show" class to DIV
  x.className = "show";

  // After 3 seconds, remove the show class from DIV
  setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
}

$(document).ready(function() {
  $('#delete-button').click(function() {
    if (confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
      $('#delete-form').submit();
    }
  });
});

$(document).ready(function() {
  $('#search').on('keyup', function() {
      var query = $(this).val();
      if (query.length >= 3) {
          $.ajax({
              url: '/search',
              data: {q: query},
              success: function(data) {
                  $('#search-results').html(data);
              }
          });
      }
  });
});

function deletePost(postId) {
  // Send an AJAX request to delete the post
  $.ajax({
    url: "/delete_post",
    type: "POST",
    data: { post_id: postId },
    success: function (response) {
      // Reload the page or update the UI as needed
      location.reload();
    },
    error: function (error) {
      console.log("Error deleting post:", error);
    }
  });
}

$(document).ready(function() {
  $(".option-button").click(function() {
    $(".dropdown").toggle();
  });
});

$(document).ready(function() {
  // Attach a click event handler to the like icon
  $(".like-icon").click(function() {
    var postId = $(this).data("post-id"); // Get the post ID from the data attribute
    var likeCount = $(this).siblings(".like-count"); // Get the like count element

    // Send an AJAX POST request to the server
    $.ajax({
      type: "POST",
      url: "/like",
      data: { post_id: postId },
      success: function(response) {
        // Update the like count on success
        likeCount.text(response.likes);

        // Toggle the like icon color
        $(this).toggleClass("text-danger");
      },
      error: function(xhr, status, error) {
        // Handle the error case
        console.log("An error occurred:", error);
      }
    });
  });
});

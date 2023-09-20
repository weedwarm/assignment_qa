  $(document).ready(function () {
    // Zebra striping for table rows
    $("table tr:even").css("background-color", "#f2f2f2");

    // Hover effect for table rows
    $("table tr").hover(
      function () {
        $(this).css("background-color", "#d9d9d9");
      },
      function () {
        if ($(this).index() % 2 === 0) {
          $(this).css("background-color", "#f2f2f2");
        } else {
          $(this).css("background-color", "#ffffff");
        }
      }
    );

    // Animated button hover effects
    $("button").hover(
      function () {
        $(this).stop().animate({ opacity: 0.7 }, "fast");
      },
      function () {
        $(this).stop().animate({ opacity: 1 }, "fast");
      }
    );
  });

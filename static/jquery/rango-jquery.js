$(document).ready(function() {
  $("#about-btn").click(function(event) {
    alert("You clicked the button using JQeury!");
    msgstr = $("#msg").html();
    msgstr = msgstr + "too";
    $("#msg").html(msgstr);
  });

  $("p").hover(
    function() {
      $(this).css("color", "red");
    },
    function() {
      $(this).css("color", "blue");
    }
  );
});

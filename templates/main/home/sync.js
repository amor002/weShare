var FriendRequestsLength = 0;
var FriendSuggestionLength = 0;

function sync() {
    $.ajax({
       url: "{% url 'main:sync' %}",
       dataType: "json",
       type: "get",
       success: function(requests) {

           $("#friends-requests").html(requests.html);
           if(requests.friend_requests_length != FriendRequestsLength) {
               FriendRequestsLength = requests.friend_requests_length;
               $("#pending-friend-request").prop("hidden", false);
           }

           if(FriendRequestsLength == 0) {
               $("#pending-friend-request").prop("hidden", true);
           }

           $("#pending-friend-request").html(FriendRequestsLength);

           if(requests.suggestions_length != FriendSuggestionLength) {
               FriendSuggestionLength = requests.suggestions_length;
               $("#invitation-count").prop("hidden", false);
           }

           if(FriendSuggestionLength == 0) {
               $("#invitation-count").prop("hidden", true);
           }

           $("#invitation-count").html(FriendSuggestionLength);
       }
   });
}


function removeInvitation(invitation) {
    $.ajax({
        url: "{% url 'main:remove-invitation' %}",
        data: {
            id: invitation.id
        }

    })
}

function acceptRequest(request) {
    request.disabled = true;
    $("#decline-"+request.id).prop("disabled", true);

    $.ajax({
        url: "{% url 'main:accept-request' %}",
        data: {
           id: parseInt(request.id.substring(7))
        },
        success: function() {
            request.parentElement.remove();
        }
    });
}

function declineRequest(request) {
    request.disabled = true;
    $("#accept-"+request.id).prop("disabled", true);

    $.ajax({
       url: "{% url 'main:decline-request' %}",
       data: {
           id: parseInt(request.id.substring(8))
        },
       success: function() {
          request.parentElement.remove();
       }
    });

}

$(document).ready(function () {
   setInterval(sync, 10000);

});


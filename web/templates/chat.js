var currentUserId = 0;
var currentClickedId = 0;

function whoami(){
        $.ajax({
            url:'/current',
            type:'GET',
            contentType: 'application/json',
            dataType:'json',
            success: function(response){
                //alert(JSON.stringify(response));
                $('#cu_username').html(response['username']);
                var name = response['name']+" "+response['fullname'];
                currentUserId = response['id'];
                $('#cu_name').html(name);
                allusers();
            },
            error: function(response){
                alert(JSON.stringify(response));
            }
        });
    }

    function allusers() {
        $.ajax({
            url:'/users',
            type:'GET',
            contentType: 'application/json',
            dataType:'json',
            success: function(response){
                var i = 0;
                $.each(response, function() {
                    // if (response[i].id != currentUserId) {
                        f = '<div class="alert alert-secondary" role="alert" onclick=loadMessages(' + currentUserId + ',' + response[i].id + ') >';
                        f = f + response[i].username;
                        f = f + '</div>';
                        i = i + 1;
                        $('#allusers').append(f);
                    // }
                });
            },
            error: function(response){
                alert(JSON.stringify(response));
            }
        });
    }

    function loadMessages(user_from_id, user_to_id) {
        currentClickedId = user_to_id;
        $.ajax({
            url:'/messages/'+user_from_id+"/"+user_to_id,
            type:'GET', // get request, no data will be passed to the server, just retrieved
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                $('#messages-record').empty();
                var i = 0;
                $.each(response, function() { // loop through the messages array
                    f = '<div class="message">';
                    f = f + response[i].content;
                    f = f + '</div>';
                    $('#messages-record').append(f); // create a div for each message and append it to the #messages-record
                    i += 1;
                });
            },
            error: function(response) {
                alert(JSON.stringify(response));
            }
        });
    }

    function sendMessage() {
        var message = $('#postmessage').val();

        if (!message.replace(/\s/g, '').length) { // check if message has only whitespaces
            alert("Message is empty!");
        }

        $('#postmessage').val('');

        var data = JSON.stringify({
                "user_from_id": currentUserId,
                "user_to_id": currentClickedId,
                "content": message
            }); // packing all data into JSON format

        $.ajax({
            url:'/gabriel/messages', // will handle what '/gabriel/messages' returns
            type:'POST',
            contentType: 'application/json',
            data : data, // request data
            dataType:'json',
            success: function (response) { // handle response from the server
                loadMessages (currentUserId, currentClickedId);
            },
            error: function(response) {
                alert(JSON.stringify(response));
            }
        });

    }

    function deleteAllMessages() {
        var message = $('#postmessage').val();
        $('#postmessage').val('');

        $.ajax({
            url:'/messages/'+currentUserId+"/"+currentClickedId,
            type:'DELETE',
            contentType: 'application/json',
            dataType:'json',
            success: function(response) {
                if (response['status'] == 'deleted') {
                    alert("All Messages Deleted!");
                    $('#messages-record').empty();
                } else {
                    alert(JSON.stringify(response));
                }
            },
            error: function(response) {
                alert(JSON.stringify(response));
            }
        });
    }
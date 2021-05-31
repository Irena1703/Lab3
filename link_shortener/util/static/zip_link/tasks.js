
class chat_control {
    constructor() {
        this.msg_list = $('.msg-group');
    }




    receive_msg(name, args, result, time) {
        this.msg_list.append(this.get_msg_html(name, args, result, time));
        this.scroll_to_bottom(); 
    }

    get_msg_html(name, args, result, time) {
        return `
        <tr>
            <td> ${name} </td>
            <td> ${args} </td>
            <td> ${result} </td>
            <td> ${time} </td>
        </tr>
                `
    }


        scroll_to_bottom() {
            this.msg_list.scrollTop(this.msg_list[0].scrollHeight);
        }
    }

        const chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/task/ws/')

        var chat = new chat_control();

        share_button = $('#send') 

        chatSocket.onopen = function(e) {
            chat.receive_msg("Server", "Connected to task queue", 0, 0)
        }
        chatSocket.onerror = function(e) {
            chat.receive_msg("Server", "Сonnection error occurred. Please try again later", 0 ,0)
            send_button.prop('disabled', true)    
        }
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            chat.receive_msg(data.name, data.args, data.result, data.time)
        }

        function link_list() {  
            jQuery('#listmodal').modal('toggle')
        }
        
        function get_groups_and_render(link) {
            fetch(link)
            .then((response) => {
                return response.json();
             })
            .then((data) => {
                for (obj of data.results) {
                list.append(
                    `
                    <button type="button" class="list-group-item list-group-item-action dont-break-out" 
                    onclick=
                    "
                    handler('${obj.url}')
                    "
                    >
                    Mail to ${obj.name}
                    </button>
                    `)   
                }
                if (data.next)
                    get_links_and_render(data.next) 
            });
        }

        $('document').ready(function() {
            share_button.on('click', link_list);
            $("#closeb").on('click', link_list)
            $('#listmodal').on('show.bs.modal', function(e) {
                list = $("#modal-body")
                list.empty()
                list.append('<div class="list-group">')
                api_url = "http://" + window.location.host + "/api/groups/"
                get_groups_and_render(api_url)
                list.append('</div>')
            })
        })
        
        function handle_msg(msg) {
            msg = msg.trim()
            msg = msg.replace(/(?:\r\n|\r|\n)/g, '<br>')
            return msg
        }

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        async function postData(url = '', data = {}) {
            // Default options are marked with *
            const response = await fetch(url, {
              method: 'POST', // *GET, POST, PUT, DELETE, etc.
              credentials: "include",
              headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(data) // body data type must match "Content-Type" header
            }); 
            res = await response.json(); // parses JSON response into native JavaScript objects
        }

        function handler(url){
            text = handle_msg($("#input-box").val())
            subject = handle_msg($("#input-box2").val())
            postData(url + "mail-send/", { "text": text, 'subject' : subject})
            .then((data) => { 
                link_list()
            })
        }
document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port = 65432;
var server_addr = "192.168.68.106";   // the IP address of your Raspberry PI

function greetings(){
    var name = document.getElementById("myName").value;
    document.getElementById("greet").innerHTML = "<h3>Hello " + name + "!</h3>";
    setInterval(function(){
        // get image from python server
        client_mgr();
    }, 1000);
}

function drive(dir){
    client_mgr(dir+2);
    document.getElementById("drive").innerHTML = (dir+2).toString();   
}

function client_mgr(caller=0){ //callers-> 1: engine, 2: forward, 3: right, 4: back, 5: right
    
    input = null;
    if (caller == 2){
        input = 'forward';
    } else if (caller == 3){
        input = 'right';
    } else if (caller == 4){
        input = 'down';
    } else if (caller == 5){
        input = 'left';
    } else if (caller ==6){
        input = 'stop';
    }
    client(input);
}

function client(send){
    
    const net = require('net');
    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('connected to server!');
        // send the message
        client.write(`${send}\r\n`);
        
    });
    
    // get the data from the server
    client.on('data', (data) => {
        raw_str = String(data);
        data_str = raw_str.slice(1,raw_str.length-1);
        const data_ls = data_str.split(", ");
        document.getElementById('valid_inpt').innerHTML = data_ls[0];
        document.getElementById("obs_dist_diag").innerHTML = data_ls[1];
        document.getElementById("speed_diag").innerHTML = data_ls[2];
        document.getElementById("power_diag").innerHTML = data_ls[3];
        document.getElementById("temp_diag").innerHTML = data_ls[4];
            
        
        client.end();
        client.destroy();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });


}

function bt_client(){
    
}


// for detecting which key is been pressed w,a,s,d
function updateKey(e) {

    e = e || window.event;

    if (e.keyCode == '87') {
        // up (w)
        document.getElementById("upArrow").style.color = "green";
        send_data("87");
    }
    else if (e.keyCode == '83') {
        // down (s)
        document.getElementById("downArrow").style.color = "green";
        send_data("83");
    }
    else if (e.keyCode == '65') {
        // left (a)
        document.getElementById("leftArrow").style.color = "green";
        send_data("65");
    }
    else if (e.keyCode == '68') {
        // right (d)
        document.getElementById("rightArrow").style.color = "green";
        send_data("68");
    }
}

// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";
}


// update data for every 50ms
function update_data(){
    setInterval(function(){
        // get image from python server
        client();
    }, 50);
}

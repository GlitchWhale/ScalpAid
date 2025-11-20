// PubNub Frontend Listener

const pubnub = new PubNub({
    publishKey: "demo",          // You can replace "demo" if needed
    subscribeKey: "demo",
    uuid: "frontend-dashboard"
});

pubnub.subscribe({
    channels: ["scalpaid_sensor_stream"]
});

pubnub.addListener({
    message: function(event) {
        const data = event.message;

        console.log("PubNub Message Received:", data);

        document.getElementById("device").innerText = data.device_id || "--";
        document.getElementById("temp").innerText = data.temperature || "--";
        document.getElementById("moist").innerText = data.moisture || "--";
        document.getElementById("time").innerText = data.timestamp || "--";
    }
});

// register some listeners to help debugging
pc.addEventListener('icegatheringstatechange', function() {
    console.log('icegatheringstatechange -> ' + pc.iceGatheringState);
}, false);

pc.addEventListener('iceconnectionstatechange', function() {
    console.log('iceconnectionstatechange -> ' + pc.iceConnectionState);
}, false);

pc.addEventListener('signalingstatechange', function() {
    console.log('signalingstatechange -> ' + pc.signalingState);
}, false);

// connect CNN Video
pc.addEventListener('track', function(evt) {
    if (evt.track.kind == 'video')
        console.log("Added element")
        evnStreamCNN = evt.streams[0];
});



function negotiate() {
    return pc.createOffer().then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        var offer = pc.localDescription;
        var codec = 'default'
        /*
         * Options: VP8/90000 or H264/90000 or 'default'
        */
        if (codec !== 'default') {
            offer.sdp = sdpFilterCodec(codec, offer.sdp);
        }
        console.log("Offer SDP: " + offer.sdp)
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function(response) {
        return response.json();
    }).then(function(answer) {
        console.log("Answer SDP: " + answer.sdp)
        return pc.setRemoteDescription(answer);
    }).catch(function(e) {
        alert(e);
    });
}

function startDataChannels() {
    // For transmitting data.
    dc = pc.createDataChannel('chat');
    dc.onclose = function() {
        clearInterval(dcInterval);
        console.log('DC: Close')
    };
    dc.onopen = function() {
        console.log('dc - open')
        dc.send("Connected!")
    };
    dc.onmessage = function(evt) {
      // Receive Data
      tempData = evt.data;
      // Send the data.
      dc.send(JSON.stringify({'image_properties':{'height':wc_coords[3],
                                         'width':wc_coords[2],
                                        }
                              }));
        console.log('message received: ' + tempData)
        
    };

   
    var constraints = {
        audio: false,
        video: true
    };


    /*
        Resolutions: 640x480, 1280x720
    */

    constraints.video = {
        width: parseInt(videoWidth, 0),
        height: parseInt(videoHeight, 0)
    };


    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        stream.getTracks().forEach(function(track) {
            console.log("Track: " + track)
            console.log("Stream: " + stream)
            pc.addTrack(track, stream);
            video.srcObject = stream;
        });
        return negotiate();
    }, function(err) {
        alert('Could not acquire media: ' + err);
    });
}

function stoptDataChannels() {
    // close data channel
    if (dc) {
        dc.close();
    }
    // close transceivers
    if (pc.getTransceivers) {
        pc.getTransceivers().forEach(function(transceiver) {
            transceiver.stop();
        });
    }
    // close local video
    pc.getSenders().forEach(function(sender) {
        sender.track.stop();
    });

    // close peer connection
    setTimeout(function() {
        pc.close();
    }, 500);
}

function sdpFilterCodec(codec, realSpd){
    var allowed = []
    var codecRegex = new RegExp('a=rtpmap:([0-9]+) '+escapeRegExp(codec))
    var videoRegex = new RegExp('(m=video .*?)( ([0-9]+))*\\s*$')
    
    var lines = realSpd.split('\n');

    var isVideo = false;
    for(var i = 0; i < lines.length; i++){
        if (lines[i].startsWith('m=video ')) {
            isVideo = true;
        } else if (lines[i].startsWith('m=')) {
            isVideo = false;
        }

        if (isVideo) {
            var match = lines[i].match(codecRegex)
            if (match) {
                allowed.push(parseInt(match[1]))
            }
        }
    }

    var skipRegex = 'a=(fmtp|rtcp-fb|rtpmap):([0-9]+)'
    var sdp = ""

    var isVideo = false;
    for(var i = 0; i < lines.length; i++){
        if (lines[i].startsWith('m=video ')) {
            isVideo = true;
        } else if (lines[i].startsWith('m=')) {
            isVideo = false;
        }

        if (isVideo) {
            var skipMatch = lines[i].match(skipRegex);
            if (skipMatch && !allowed.includes(parseInt(skipMatch[2]))) {
                continue;
            } else if (lines[i].match(videoRegex)) {
                sdp+=lines[i].replace(videoRegex, '$1 '+allowed.join(' ')) + '\n'
            } else {
                sdp += lines[i] + '\n'
            }
        } else {
            sdp += lines[i] + '\n'
        }
    }

    return sdp;
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}
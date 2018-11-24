var intervalWebcamFrame = setInterval(function(){
    // This draws the video then updates the bounding boxes. First offscreen rendering.
    ctxWcVideo.drawImage(video, 0, 0, wc_coords[2], wc_coords[3]);
    currentData = JSON.parse(tempData);
      var PADDING = 0;
      var x,y,w,h;
        // Draw the bounding boxes

    var data = currentData;
    if (data.type == "detection_data"){
        for (var j = 0, len2 = data.bbs.length; j < len2; ++j ){
            var bb = data.bbs[j];
            var text = data.classes[j];
            // Draw the rectangle that will contain the object name.
            ctxWcVideo.fillStyle="#000000";
            x = bb[1];
            // Ensure that the rectangle is inside the allowable area.
            y = bb[0] + 0;
            w = bb[3] - bb[1];
            h = TEXT_BOX_HEIGHT;
            ctxWcVideo.fillRect(x,y,w,h);
            // Draw the text inside the rectangle
            ctxWcVideo.font = bbTextSize + "pt Arial";
            ctxWcVideo.fillStyle = '#FFFFFF'
            ctxWcVideo.fillText(text,
                         x + 0, 
                         y + bbTextHPadding);
            // Draw the bounding box around the given obect
            ctxWcVideo.strokeRect(bb[1],
                           bb[0],
                           bb[3] - bb[1] - PADDING,
                           bb[2] - bb[0] - PADDING);
        }
    }
        
      // Update the entire canvas
      ctx.drawImage(wcVideoCanvas, wc_coords[0], wc_coords[1], wc_coords[2], wc_coords[3]);
},webcamUpdateIntervalMS);
    









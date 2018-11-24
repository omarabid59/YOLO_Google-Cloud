function setupScreenSizes(){
       
        wc_x = 0, wc_y = 0, wc_x_ = 1, wc_y_ = 1;
        


        console.log("Screen WIDTH " + screenWidth + " Screen height " + screenHeight);
        canvas.width = 640;
        canvas.height = 480;
   
    
        // Update the Webcam Values wrt the canvas dimensions
        wc_x = Math.floor(wc_x*canvas.width);
        wc_x_ = Math.floor(wc_x_*canvas.width) - wc_x;
        wc_y = Math.floor(wc_y*canvas.height);
        wc_y_ = Math.floor(wc_y_*canvas.height) - wc_y;
        wc_coords = [wc_x,wc_y,wc_x_,wc_y_];
      
}



function loadWebcam(){
   
    context = canvas.getContext('2d');
    wcVideoCanvas.height = wc_y_;
    wcVideoCanvas.width = wc_x_;

    wcSendVideoCanvas.height = videoHeight;
    wcSendVideoCanvas.width = videoWidth;
    ctxSendVideo = wcSendVideoCanvas.getContext('2d');
    console.log('finished loading');

}


function initScreen(){
    setupScreenSizes();
    loadWebcam();
}
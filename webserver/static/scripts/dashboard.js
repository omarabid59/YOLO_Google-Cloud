function drawClassLabelFrame(label_list){
        /*
        REQUIRE: LabelList has been converted to a SET!
        */
        ctxLabels.fillStyle = "#FF0000";
        ctxLabels.fillRect(0,0,labelCanvas.width, labelCanvas.height); 

        var WIDTH = Math.floor(labelCanvas.width*0.1);
        function gen_dynamic_image_label(text){
            fontFace = cv.FONT_HERSHEY_SIMPLEX;
            fontScale = 30;

            fontColor = (255,255,255);
            fontThicknes = 6;
            padding = 40;
            fixed_height = 70;
            text_width = WIDTH + 1;
            if ((text.indexOf("barrel") > -1)){
                text = text.split('-')[-1]
            }
            text = text.replace('-',' ')

            var dynamiclabelCanvas = document.createElement('canvas');
            dynamiclabelCanvas.width = fixed_height + 'px';
            dynamiclabelCanvas.height = Math.floor(text_width + padding) + 'px';
            var tmpCtx = dynamiclabelCanvas.getContext('2d');

            tmpCtx.fillStyle = "#FF0000"; // Change To: [ 13, 176,  37]
            tmpCtx.fillRect(0, 0, dynamiclabelCanvas.width, dynamiclabelCanvas.height); 

            tmpCtx.font = fontScale + "px Arial";
            tmpCtx.fillText(text,Math.floow(padding/2), 55);

            return dynamiclabelCanvas;
        }


        var x_offset = 10;
        var y_offset = 10;

        var x_coordinate = x_offset;       
        var y_coordinate = y_offset;


        var padding_x = 15;
        var padding_y = 15;

        var FIRST_ELEMENT = True;
        for(var i = 0; i < label_list.length; i++){
            LABEL = label_list[i];
            if (LABEL.indexOf("person_count") > -1) {
                count = LABEL.split(':')[1];
                if (count > 1){
                    dynamiclabelCanvas = gen_dynamic_image_label(count+ " Persons");
                }
                else{
                    dynamiclabelCanvas = gen_dynamic_image_label(count + " Person");
                }
            }
            else{
                dynamiclabelCanvas = self.gen_dynamic_image_label(LABEL)
            }
            var h = dynamiclabelCanvas.height;
            var w = dynamiclabelCanvas.width;

            if (FIRST_ELEMENT == True){
                FIRST_ELEMENT = False;
                y_coordinate_end = y_coordinate + h;
            }

            x_coordinate_end = x_coordinate + w;
            if (x_coordinate_end > WIDTH){
                x_coordinate = x_offset;
                x_coordinate_end = x_coordinate + w;
                y_coordinate =  y_coordinate_end + padding_y;
                y_coordinate_end = y_coordinate + h;
            }

            ctxLabels.drawImage(dynamiclabelCanvas,x_coordinate,y_coordinate);
            x_coordinate = x_coordinate_end + padding_x;
        }      
    }
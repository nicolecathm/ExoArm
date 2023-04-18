#include <stdio.h>
#include <stdlib.h>

///
int PEAK_HEIGHT_FLX = 335;
int PEAK_HEIGHT_EXT = 295;
int MID = 50;
int WINDOW = 100;
int POOR_PREDICTION_THRESHOLD = 1000000;
int flx_aligned[100];
int ext_aligned[100];
int CONVOLUTION[100];
float alpha = 0.5;
/// 
// int count = 0;
const int analogInPin = A0;

int ema(int exp, int actual, float alpha){
  return (int) (alpha * (float)exp + (1 - alpha) * (float)actual);
}

void convolve(int* A, int* B){

  float large_conv;
  for(int i = 0; i < WINDOW-1; i++)
  {
    CONVOLUTION[i] = 0;
    for(int j = 0; j < WINDOW-1; j++){ // THIS MAY NOT WORK, HAD TO DO IT TO USE INT INSTEAD OF
      large_conv = ((float)(A[i-j]) * (float)(B[j]));
      // cout<<"LARGE CONV: "<< large_conv<<'\n';
      // cout<<"INT CONV: "<< (int)(large_conv/1000)<<'\n';
      CONVOLUTION[i] += (int)(large_conv/1000);

    }
  }
}

int find_peaks(int *data, int max_height){
  // iterate through data file, comparing each pt until peak obtained larger than peak_height
  int MAX_INDEX = 0;
  int PREV = data[0]; //handle both negative and pos peak starts
  for(int i = 0; i < WINDOW-1; i++){
    if ((data[i] >= PREV) && (data[i] >= max_height) && (data[i] >= data[MAX_INDEX])){
      MAX_INDEX = i;
    }
  }
  return MAX_INDEX;
}

void align_signal(int *data){
  int max_height;
  int peak_index, gap, endpoint;
  int DC_COMPONENT = 60;
  int neg_data[100];
  
  max_height = PEAK_HEIGHT_FLX;

  peak_index = find_peaks(data, max_height); // find maximum peak

  if (peak_index){
    if (peak_index > MID){
        gap = peak_index - MID;

        for(int i = 0; i < (WINDOW-1 - gap); i++){
          flx_aligned[i] = data[gap]; // save starting at gap up to window end
          gap++;
        }
        for(int i = gap; i < WINDOW-1; i++){
          flx_aligned[i] = DC_COMPONENT; // make the rest of the window DC component flat
        }

    }
    else if (peak_index <= MID){
        gap = MID - peak_index;

        for(int i = 0; i < gap; i++){
          flx_aligned[i] = DC_COMPONENT; // make the beginning of the window DC component flat
        }
        endpoint = (WINDOW-1-gap);
        for(int i = 0; i < endpoint; i++){
          flx_aligned[gap] = data[i]; // make from gap to window end the data 
          gap++;
        }
    }
    else{
      for(int i = 0; i < WINDOW-1; i++){
        flx_aligned[i] = data[i]; // IF NO PEAKS ARE FOUND AT THE SPECIFIED HEIGHT, RETURN ORIGINAL WAVE
      }
    }
  }

  max_height = PEAK_HEIGHT_EXT;
  for(int i = 0; i < WINDOW-1; i++){
    neg_data[i] = -(data[i]);
  }

  peak_index = find_peaks(neg_data, -max_height); // find minimum peak

  if (peak_index){
    if (peak_index > MID){
        gap = peak_index - MID;

        for(int i = 0; i < (WINDOW-1 - gap); i++){
          ext_aligned[i] = data[gap]; // save starting at gap up to window end
          gap++;
        }
        for(int i = gap; i < WINDOW-1; i++){
          ext_aligned[i] = DC_COMPONENT; // make the rest of the window DC component flat
        }

    }
    else if (peak_index <= MID){
        gap = MID - peak_index;

        for(int i = 0; i < gap; i++){
          ext_aligned[i] = DC_COMPONENT; // save as dc component up to gap
        }
        endpoint = WINDOW-1-gap;
        for(int i = 0; i < endpoint; i++){
          ext_aligned[gap] = data[i]; // make rest of signal align with window
          gap++;
        }
    }
    else{
      for(int i = 0; i < WINDOW-1; i++){
        ext_aligned[i] = data[i]; // IF NO PEAKS ARE FOUND AT THE SPECIFIED HEIGHT, RETURN ORIGINAL WAVE
      }
    }
  }

}

int find_max(int *data){ // find max value , not peak
  int MAX_VALUE = 0;
  int PREV = 0;
  for(int i = 0; i < WINDOW-1; i++){
    if ((data[i] > PREV)){
      MAX_VALUE = i;
    }
  }
  return MAX_VALUE;
}

int match_filter_prediction(int *d){
    // THIS IS CONVERTED TO ARDUINO CODE/CPP


  int FLEX_FILTER[100] = {298, 298, 298, 298, 298, 298, 296, 294, 291, 287, 284, 279, 274, 267, 260, 252, 244, 235, 228, 220, 211, 201, 190, 178, 164, 152, 140, 127, 117, 110, 108, 113, 124, 140, 160, 179, 197, 216, 237, 260, 284, 309, 332, 355, 379, 404, 429, 453, 476, 495, 511, 526, 538, 549, 558, 566, 572, 576, 578, 578, 577, 574, 570, 566, 561, 555, 550, 544, 538, 531, 524, 517, 511, 504, 498, 491, 485, 478, 472, 466, 460, 454, 448, 443, 438, 432, 427, 422, 418, 414, 409, 405, 402, 397, 394, 391, 388, 384, 381, 378};
  int EXT_FILTER[100] = {433, 430, 427, 423, 419, 416, 413, 411, 412, 412, 412, 412, 414, 420, 427, 433, 434, 431, 424, 413, 395, 375, 352, 328, 306, 288, 277, 272, 273, 279, 288, 300, 313, 326, 340, 353, 363, 373, 380, 386, 391, 396, 400, 405, 409, 413, 416, 419, 423, 427, 430, 433, 436, 437, 438, 437, 435, 433, 430, 428, 425, 423, 420, 416, 412, 407, 402, 397, 392, 387, 381, 376, 371, 367, 363, 359, 355, 350, 347, 344, 342, 339, 337, 334, 332, 331, 330, 328, 327, 325, 324, 323, 322, 322, 321, 320, 319, 319, 319, 318};
  int RST_FILTER[100] = {322, 322, 321, 321, 320, 320, 319, 319, 318, 318, 318, 318, 317, 317, 317, 317, 317, 317, 317, 316, 317, 316, 316, 317, 317, 317, 317, 317, 317, 317, 317, 317, 317, 317, 317, 318, 318, 318, 319, 319, 319, 319, 320, 320, 320, 321, 321, 321, 321, 322, 322, 322, 322, 322, 322, 322, 322, 322, 322, 323, 323, 323, 323, 324, 324, 324, 324, 325, 325, 325, 325, 325, 325, 326, 326, 326, 327, 327, 327, 327, 327, 327, 327, 327, 327, 328, 328, 328, 328, 328, 328, 328, 328, 328, 329, 329, 329, 329, 329, 330};

  int cnv_flx_aligned[100];
  int cnv_ext_aligned[100];
  int cnv_rst_aligned[100];

  int MAX_FLX;
  int MAX_EXT;
  int MAX_RST;
  int FLX_OR_EXT[2];
  int DIFF_EXT_RST;
  int DIFF_FLX_RST;
  int AVG_DIFF;

  int PRED;

  align_signal(d); // ALIGN AS YOU CONVOLVE

  convolve(flx_aligned, FLEX_FILTER);
  for(int i = 0; i< WINDOW-1; i++){
    cnv_flx_aligned[i] = CONVOLUTION[i];
  }

  convolve(ext_aligned, EXT_FILTER);
  for(int i = 0; i< WINDOW-1; i++){
    cnv_ext_aligned[i] = CONVOLUTION[i];
  }

  convolve(ext_aligned, RST_FILTER);
  for(int i = 0; i< WINDOW-1; i++){
    cnv_rst_aligned[i] = CONVOLUTION[i];
  }

  MAX_FLX = find_max(cnv_flx_aligned);
  MAX_EXT = find_max(cnv_ext_aligned);
  MAX_RST = find_max(cnv_rst_aligned);

  FLX_OR_EXT[0] = MAX_FLX;
  FLX_OR_EXT[1] = MAX_EXT;

  PRED = find_max(FLX_OR_EXT);

  // AVG_DIFF = np.average(np.abs(np.diff([MAX_FLX, MAX_EXT, MAX_RST])))

  DIFF_EXT_RST = abs(MAX_RST - MAX_EXT);
  DIFF_FLX_RST = abs(MAX_RST - MAX_FLX);

  AVG_DIFF = (DIFF_EXT_RST + DIFF_FLX_RST) / 2; 
  
  if (AVG_DIFF < POOR_PREDICTION_THRESHOLD){
      PRED = MAX_RST;
  }


  //flexion = 0, extension = 1, sustain = 2, rest = 3
  if (PRED == MAX_FLX){
    // cout<<"PREDICTION: FLEX"<<"\n";
    return 0;
  }
  else if (PRED == MAX_EXT){
    // cout<<"PREDICTION: EXT"<<"\n";
    return 1;
  }
  else if (PRED == MAX_RST){
    // cout<<"PREDICTION: REST"<<"\n";
    return 3;
  }

  return -1;
}

void setup(){
  Serial.begin(9600);
  pinMode(A0, INPUT);
}

void loop(){
  int sensorWindow[100];
  int gap = 20;
  int val = 300;
  int prev_i = 0;

  int actual = 0;
  int ema_actual = 0;
  int prediction = 0;



  // may have an issue with missing part of wave before drop, maybe save a buffer of 5 at all times?
  val = analogRead(analogInPin);
  ema_actual = ema(val, actual, alpha);
  if(((gap + ema_actual) < prev_i) || ((-gap + ema_actual) > prev_i)){
    for(int i = 0; i < WINDOW; i++) {
      val = analogRead(analogInPin);
      ema_actual = ema(val, actual, alpha); //test THIS
      sensorWindow[i] = ema_actual;
      Serial.println(data[i]);
      delay(30);
    }
    Serial.println("PREDICTING...");
    prediction = match_filter_prediction(sensorWindow);
    Serial.println(prediction);
  }
  else{
    Serial.println("POLLING...");
  }

  
}
